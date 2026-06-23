"""Birch Hill obsidian-vault tool.

Reads from github.com/birch-hill-labs/obsidian-vault via the GitHub REST API.
Writes happen by opening pull requests against `main` — the agent never pushes
to `main` directly. Branch protection on the GitHub side is the actual
permissioning layer for what gets persisted into the vault.

Iron-proxy injects GITHUB_VAULT_TOKEN as a Bearer Authorization header on
outbound requests to api.github.com, so the secret never lives in this
process. The PAT needs `contents:write` (for branches + commits + file
writes), `pull-requests:write` (for opening PRs), and `metadata:read`,
scoped to the single `birch-hill-labs/obsidian-vault` repo.

For v1 there is no user-role enforcement at the tool layer — any Slack
user who can @mention Centaur can call any of these methods on any vault
path. Phase 3 adds path-level RBAC driven by a Postgres user-role table:
each role has a set of `allowed_path_prefixes`, and read / list_dir /
search / tree / propose_* all filter against the calling Slack user's
allowed prefixes. Role mutation is admin-only (Connor). See README.
"""

from __future__ import annotations

import base64
import re
import time
from typing import Any

import httpx

try:
    # Available when the tool runs inside Centaur; gives us thread_key for
    # PR traceability links back to Slack.
    from centaur_sdk import current_thread_key
except ImportError:  # pragma: no cover - allows direct unit testing
    def current_thread_key() -> str:
        raise RuntimeError("centaur_sdk not available")


REPO = "birch-hill-labs/obsidian-vault"
DEFAULT_BRANCH = "main"
API_BASE = "https://api.github.com"

# Slack workspace identifier (team_id, T*) used to build per-thread URLs.
# Lives here rather than as a tool secret because it's not sensitive.
SLACK_TEAM_ID = "T0A2FT7NXEH"  # Birch Hill Holdings

# Files we'll happily return verbatim. Binary office formats (docx/pptx/pdf)
# can be listed but reading them returns a "binary, fetch externally" stub
# rather than a base64 blob the agent can't usefully parse.
_TEXT_SUFFIXES = (
    ".md", ".mdx", ".txt", ".markdown",
    ".json", ".yaml", ".yml", ".toml",
    ".py", ".ts", ".js", ".sh",
    ".csv", ".tsv",
)
_BINARY_SUFFIXES = (".docx", ".pptx", ".xlsx", ".pdf", ".png", ".jpg", ".jpeg", ".gif")

# Cap individual reads so a runaway request can't OOM the agent context.
MAX_READ_BYTES = 256 * 1024  # 256 KiB


def _http() -> httpx.Client:
    return httpx.Client(
        base_url=API_BASE,
        headers={
            # iron-proxy uses REPLACE mode for the GITHUB_TOKEN secret: it scans
            # the Authorization header for the literal string "GITHUB_TOKEN" and
            # substitutes it with the secret value (which lives in 1P as the
            # full Authorization value, e.g. "Bearer github_pat_..."). So we
            # send the placeholder string itself, NOT a Bearer-prefixed version.
            # The substitution happens at the network edge before the request
            # leaves the cluster; this process never sees the real token.
            "Authorization": "GITHUB_TOKEN",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "centaur-obsidian-vault/0.1",
        },
        timeout=20.0,
    )


def _normalize_path(path: str) -> str:
    """Strip leading/trailing slashes; reject path-traversal attempts."""
    cleaned = (path or "").strip().strip("/")
    if ".." in cleaned.split("/"):
        raise ValueError(f"path may not contain '..': {path!r}")
    return cleaned


def _is_text(name: str) -> bool:
    lower = name.lower()
    return any(lower.endswith(s) for s in _TEXT_SUFFIXES)


def _is_binary(name: str) -> bool:
    lower = name.lower()
    return any(lower.endswith(s) for s in _BINARY_SUFFIXES)


class ObsidianVaultClient:
    """Read-only access to Birch Hill's obsidian-vault on GitHub.

    Use this tool whenever the question references institutional knowledge
    that lives in the vault: counterparty briefs, atlas/rwasp financial
    model, daily notes, knowledge graph, onboarding docs, or anything under
    `~/Desktop/BIrchHill/obsidian-vault/` for Connor.
    """

    def read(self, path: str, *, ref: str = DEFAULT_BRANCH) -> dict[str, Any]:
        """Read a single file from the vault.

        Args:
          path: Vault-relative path, e.g. `"counterparty-briefs/sky.md"` or
            `"atlas/rwasp/workbench.md"`. Use list_dir to discover paths.
          ref: Git ref (branch, tag, or commit SHA). Defaults to `main`.

        Returns:
          {
            "path": str,                # the normalized vault-relative path
            "size_bytes": int,          # raw byte count
            "content": str,             # decoded text for text files
            "truncated": bool,          # True if content was capped at MAX_READ_BYTES
            "is_binary": bool,          # True for .docx/.pptx/.xlsx/.pdf/images
            "html_url": str,            # link to view on GitHub
          }

          Binary files return is_binary=True with content empty and an
          html_url the agent can hand back to the user instead.
        """
        clean = _normalize_path(path)
        if not clean:
            raise ValueError("path is required")

        with _http() as http:
            r = http.get(f"/repos/{REPO}/contents/{clean}", params={"ref": ref})
        if r.status_code == 404:
            raise FileNotFoundError(f"vault path not found: {clean}")
        r.raise_for_status()
        payload = r.json()

        # GitHub returns an array for directories; reject here.
        if isinstance(payload, list):
            raise IsADirectoryError(
                f"{clean!r} is a directory. Use list_dir to enumerate it."
            )

        name = payload.get("name", "")
        size = int(payload.get("size") or 0)
        html_url = payload.get("html_url", "")
        is_binary = _is_binary(name) or (
            not _is_text(name) and not payload.get("encoding")
        )

        if is_binary:
            return {
                "path": clean,
                "size_bytes": size,
                "content": "",
                "truncated": False,
                "is_binary": True,
                "html_url": html_url,
            }

        encoded = (payload.get("content") or "").replace("\n", "")
        encoding = payload.get("encoding", "base64")
        if encoding != "base64":
            raise ValueError(f"unexpected content encoding: {encoding}")
        raw = base64.b64decode(encoded)
        truncated = len(raw) > MAX_READ_BYTES
        if truncated:
            raw = raw[:MAX_READ_BYTES]
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")

        return {
            "path": clean,
            "size_bytes": size,
            "content": text,
            "truncated": truncated,
            "is_binary": False,
            "html_url": html_url,
        }

    def list_dir(self, path: str = "", *, ref: str = DEFAULT_BRANCH) -> dict[str, Any]:
        """List files and subdirectories under a vault path.

        Args:
          path: Vault-relative directory, or empty for the vault root.
          ref: Git ref. Defaults to `main`.

        Returns:
          {
            "path": str,
            "entries": [
              {"name": str, "type": "file"|"dir", "size_bytes": int, "path": str},
              ...
            ],
          }
        """
        clean = _normalize_path(path)
        endpoint = f"/repos/{REPO}/contents/{clean}" if clean else f"/repos/{REPO}/contents"
        with _http() as http:
            r = http.get(endpoint, params={"ref": ref})
        if r.status_code == 404:
            raise FileNotFoundError(f"vault path not found: {clean or '<root>'}")
        r.raise_for_status()
        payload = r.json()
        if not isinstance(payload, list):
            raise NotADirectoryError(
                f"{clean!r} is a file, not a directory. Use read to fetch it."
            )

        entries = [
            {
                "name": item.get("name", ""),
                "type": "dir" if item.get("type") == "dir" else "file",
                "size_bytes": int(item.get("size") or 0),
                "path": item.get("path", ""),
            }
            for item in payload
        ]
        entries.sort(key=lambda e: (e["type"] != "dir", e["name"].lower()))
        return {"path": clean, "entries": entries}

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        path_prefix: str | None = None,
    ) -> dict[str, Any]:
        """Search vault content for a query string.

        Uses GitHub's code-search API, scoped to this repo. Supports the same
        qualifiers GitHub search does (e.g. `extension:md`, `path:atlas/`).

        Args:
          query: Free-text terms. Combine with qualifiers if needed.
          limit: Max results (default 20, capped at 50).
          path_prefix: Optional vault subpath to restrict the search to,
            e.g. `"counterparty-briefs"`.

        Returns:
          {
            "query": str,
            "total_count": int,
            "results": [
              {"path": str, "name": str, "html_url": str, "snippet": str | None},
              ...
            ],
          }

        Notes:
          - GitHub's code-search index can lag commits by a few minutes.
          - Snippets aren't always returned by the search API; agents should
            follow up with `read` when a snippet is missing or insufficient.
        """
        limit = max(1, min(int(limit), 50))
        q = (query or "").strip()
        if not q:
            raise ValueError("query is required")
        q_full = f"{q} repo:{REPO}"
        if path_prefix:
            prefix = _normalize_path(path_prefix)
            if prefix:
                q_full += f" path:{prefix}"

        with _http() as http:
            r = http.get(
                "/search/code",
                params={"q": q_full, "per_page": limit},
                headers={"Accept": "application/vnd.github.text-match+json"},
            )
        r.raise_for_status()
        payload = r.json()
        results = []
        for item in payload.get("items", [])[:limit]:
            matches = item.get("text_matches") or []
            snippet = matches[0].get("fragment") if matches else None
            results.append(
                {
                    "path": item.get("path", ""),
                    "name": item.get("name", ""),
                    "html_url": item.get("html_url", ""),
                    "snippet": snippet,
                }
            )
        return {
            "query": q,
            "total_count": int(payload.get("total_count") or 0),
            "results": results,
        }

    def tree(
        self,
        prefix: str = "",
        *,
        max_depth: int = 3,
        ref: str = DEFAULT_BRANCH,
    ) -> dict[str, Any]:
        """Return an ASCII-style tree view of the vault structure.

        Useful when the agent doesn't know the layout yet. Defaults to depth 3
        from the prefix; bump max_depth if the agent needs more granular view.

        Args:
          prefix: Vault-relative path to root the tree at, or empty for the
            whole vault.
          max_depth: How many directory levels to descend (default 3, cap 6).
          ref: Git ref. Defaults to `main`.

        Returns:
          {"prefix": str, "tree": str}   # `tree` is a printable string
        """
        prefix_clean = _normalize_path(prefix)
        max_depth = max(1, min(int(max_depth), 6))
        with _http() as http:
            r = http.get(
                f"/repos/{REPO}/git/trees/{ref}",
                params={"recursive": "1"},
            )
        r.raise_for_status()
        payload = r.json()
        entries = payload.get("tree", []) or []

        # Filter to prefix scope + depth cap
        rows: list[tuple[str, str]] = []
        for e in entries:
            path = e.get("path", "")
            if prefix_clean and not (
                path == prefix_clean or path.startswith(prefix_clean + "/")
            ):
                continue
            rel = path[len(prefix_clean) + 1:] if prefix_clean else path
            depth = rel.count("/")
            if depth >= max_depth:
                continue
            rows.append((path, e.get("type", "blob")))

        rows.sort(key=lambda r: r[0])
        # Render as indented tree
        lines: list[str] = []
        for path, kind in rows:
            rel = path[len(prefix_clean) + 1:] if prefix_clean else path
            depth = rel.count("/")
            marker = "📁 " if kind == "tree" else "📄 "
            indent = "  " * depth
            name = rel.rsplit("/", 1)[-1]
            lines.append(f"{indent}{marker}{name}")
        return {"prefix": prefix_clean, "tree": "\n".join(lines)}


    # ------------------------------------------------------------------
    # Write methods (propose_*). All open a pull request against `main`.
    # The agent MUST NOT call any of these without explicit user
    # confirmation in the same Slack thread. See the birch-hill-vault skill.
    # ------------------------------------------------------------------

    def propose_edit(
        self,
        path: str,
        new_content: str,
        message: str,
        *,
        requested_by: str | None = None,
        description: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Open a PR proposing to REPLACE the content of an existing vault file.

        DO NOT call without explicit user confirmation in Slack. Canonical flow:
          1. read the target file
          2. draft the new content, post a diff/plan in Slack
          3. wait for the user to confirm (e.g., "yes, open the PR")
          4. only then call this method

        Args:
          path: Vault-relative path to an existing file.
          new_content: Full new file content (NOT a diff).
          message: PR title and commit message.
          requested_by: Slack handle/name of the requester for the PR body.
          description: Free-form additional PR body content.
          branch: Custom branch name; defaults to `slack/<slug>-<ts>`.

        Returns:
          {"pr_number": int, "pr_url": str, "branch": str, "commit_sha": str}
        """
        clean = _normalize_path(path)
        with _http() as http:
            file_info = self._get_file_info(http, clean)
            if file_info is None:
                raise FileNotFoundError(
                    f"{clean!r} does not exist; use propose_create instead"
                )
            br = branch or _default_branch_name(message)
            self._create_branch(http, br)
            commit_sha = self._put_file(
                http,
                clean,
                new_content,
                message=message,
                branch=br,
                existing_sha=file_info["sha"],
            )
            pr = self._open_pr(
                http,
                title=message,
                branch=br,
                body=_pr_body(
                    action="edit",
                    path=clean,
                    message=message,
                    description=description,
                    requested_by=requested_by,
                ),
            )
        return {
            "pr_number": pr["number"],
            "pr_url": pr["html_url"],
            "branch": br,
            "commit_sha": commit_sha,
        }

    def propose_create(
        self,
        path: str,
        content: str,
        message: str,
        *,
        requested_by: str | None = None,
        description: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Open a PR proposing to CREATE a new vault file at `path`.

        Same confirm-first contract as propose_edit. Fails if the file
        already exists — use propose_edit for updates.
        """
        clean = _normalize_path(path)
        with _http() as http:
            if self._get_file_info(http, clean) is not None:
                raise FileExistsError(
                    f"{clean!r} already exists; use propose_edit instead"
                )
            br = branch or _default_branch_name(message)
            self._create_branch(http, br)
            commit_sha = self._put_file(
                http, clean, content, message=message, branch=br, existing_sha=None,
            )
            pr = self._open_pr(
                http,
                title=message,
                branch=br,
                body=_pr_body(
                    action="create",
                    path=clean,
                    message=message,
                    description=description,
                    requested_by=requested_by,
                ),
            )
        return {
            "pr_number": pr["number"],
            "pr_url": pr["html_url"],
            "branch": br,
            "commit_sha": commit_sha,
        }

    def propose_append(
        self,
        path: str,
        addition: str,
        message: str,
        *,
        separator: str = "\n\n",
        requested_by: str | None = None,
        description: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Open a PR proposing to APPEND text to the end of an existing vault file.

        Common case for notes and meeting summaries. Same confirm-first contract.

        Args:
          path: Vault-relative path to an existing file.
          addition: Text to append.
          message: PR title / commit message.
          separator: Joined between existing content and addition (default
            `"\\n\\n"` for clean markdown separation).
        """
        clean = _normalize_path(path)
        # Fetch existing content so we can compose the new full body
        current = self.read(clean)
        if current.get("is_binary"):
            raise ValueError(f"cannot append to a binary file: {clean}")
        existing_text = current.get("content") or ""
        new_text = existing_text.rstrip("\n") + separator + addition.lstrip("\n")
        return self.propose_edit(
            clean,
            new_text,
            message,
            requested_by=requested_by,
            description=description,
            branch=branch,
        )

    def propose_delete(
        self,
        path: str,
        message: str,
        *,
        requested_by: str | None = None,
        description: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Open a PR proposing to DELETE a vault file. Same confirm-first contract."""
        clean = _normalize_path(path)
        with _http() as http:
            file_info = self._get_file_info(http, clean)
            if file_info is None:
                raise FileNotFoundError(f"{clean!r} does not exist")
            br = branch or _default_branch_name(f"delete-{message}")
            self._create_branch(http, br)
            commit_sha = self._delete_file(
                http, clean, message=message, branch=br, existing_sha=file_info["sha"],
            )
            pr = self._open_pr(
                http,
                title=message,
                branch=br,
                body=_pr_body(
                    action="delete",
                    path=clean,
                    message=message,
                    description=description,
                    requested_by=requested_by,
                ),
            )
        return {
            "pr_number": pr["number"],
            "pr_url": pr["html_url"],
            "branch": br,
            "commit_sha": commit_sha,
        }

    def list_proposals(self, state: str = "open", limit: int = 20) -> dict[str, Any]:
        """List vault PRs that Centaur has opened.

        Filters by `head` branch prefix `slack/` (the convention used by
        propose_*). Useful for the agent to say "you have N open vault
        proposals" or to follow up on a previous request.

        Args:
          state: "open", "closed", or "all".
          limit: Max results (cap 50).
        """
        if state not in ("open", "closed", "all"):
            raise ValueError("state must be open, closed, or all")
        limit = max(1, min(int(limit), 50))
        with _http() as http:
            r = http.get(
                f"/repos/{REPO}/pulls",
                params={"state": state, "per_page": limit, "sort": "updated", "direction": "desc"},
            )
        r.raise_for_status()
        items = [
            {
                "number": p["number"],
                "title": p["title"],
                "state": p["state"],
                "html_url": p["html_url"],
                "branch": p["head"]["ref"],
                "created_at": p["created_at"],
                "merged_at": p.get("merged_at"),
            }
            for p in r.json()
            if p.get("head", {}).get("ref", "").startswith("slack/")
        ]
        return {"state": state, "count": len(items), "proposals": items}

    def propose_files(
        self,
        files: list[dict[str, Any]],
        message: str,
        *,
        requested_by: str | None = None,
        description: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Open ONE PR that creates/updates/deletes MULTIPLE vault files in a
        single commit — including BINARY files (e.g. a regenerated `.xlsx`).

        Use this whenever a change spans more than one file or touches a binary
        file (the per-file propose_edit/propose_create only handle single UTF-8
        text files). NEVER reimplement the GitHub API in the sandbox to do this:
        this method already handles auth (via iron-proxy), binary content, and
        the atomic multi-file commit. Same confirm-first contract as propose_edit.

        Args:
          files: non-empty list of file specs. Each item is one of:
            - {"path": str, "content": str}      # text file (UTF-8); create or update
            - {"path": str, "content_b64": str}  # binary file; base64 of the raw bytes
            - {"path": str, "delete": True}      # remove the file
          message: PR title and commit message.
          requested_by: Slack handle/name of the requester (PR body).
          description: Free-form additional PR body content.
          branch: Custom branch name; defaults to `slack/<slug>-<ts>`.

        Returns {"pr_number", "pr_url", "branch", "commit_sha", "files": [...]}.
        """
        if not files:
            raise ValueError("files must be a non-empty list")
        specs = [(_normalize_path(f["path"]), f) for f in files]
        br = branch or _default_branch_name(message)
        with _http() as http:
            # Base commit + tree on main.
            ref = http.get(f"/repos/{REPO}/git/refs/heads/{DEFAULT_BRANCH}")
            ref.raise_for_status()
            base_commit_sha = ref.json()["object"]["sha"]
            bc = http.get(f"/repos/{REPO}/git/commits/{base_commit_sha}")
            bc.raise_for_status()
            base_tree_sha = bc.json()["tree"]["sha"]

            # One blob per file; a null sha entry deletes.
            tree: list[dict[str, Any]] = []
            for path, f in specs:
                if f.get("delete"):
                    tree.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
                    continue
                if f.get("content_b64") is not None:
                    blob = http.post(
                        f"/repos/{REPO}/git/blobs",
                        json={"content": f["content_b64"], "encoding": "base64"},
                    )
                else:
                    blob = http.post(
                        f"/repos/{REPO}/git/blobs",
                        json={"content": f.get("content", ""), "encoding": "utf-8"},
                    )
                blob.raise_for_status()
                tree.append({"path": path, "mode": "100644", "type": "blob", "sha": blob.json()["sha"]})

            tr = http.post(
                f"/repos/{REPO}/git/trees",
                json={"base_tree": base_tree_sha, "tree": tree},
            )
            tr.raise_for_status()
            cm = http.post(
                f"/repos/{REPO}/git/commits",
                json={"message": message, "tree": tr.json()["sha"], "parents": [base_commit_sha]},
            )
            cm.raise_for_status()
            new_commit_sha = cm.json()["sha"]

            cr = http.post(
                f"/repos/{REPO}/git/refs",
                json={"ref": f"refs/heads/{br}", "sha": new_commit_sha},
            )
            if cr.status_code == 422 and "already exists" in cr.text.lower():
                http.patch(
                    f"/repos/{REPO}/git/refs/heads/{br}",
                    json={"sha": new_commit_sha, "force": True},
                ).raise_for_status()
            else:
                cr.raise_for_status()

            pr = self._open_pr(
                http,
                title=message,
                branch=br,
                body=_pr_body(
                    action="edit",
                    path=", ".join(p for p, _ in specs),
                    message=message,
                    description=description,
                    requested_by=requested_by,
                ),
            )
        return {
            "pr_number": pr["number"],
            "pr_url": pr["html_url"],
            "branch": br,
            "commit_sha": new_commit_sha,
            "files": [p for p, _ in specs],
        }

    # ------------------------------------------------------------------
    # Internal helpers (not exposed as tool methods because of the leading _)
    # ------------------------------------------------------------------

    def _get_file_info(self, http: httpx.Client, path: str) -> dict[str, Any] | None:
        r = http.get(f"/repos/{REPO}/contents/{path}", params={"ref": DEFAULT_BRANCH})
        if r.status_code == 404:
            return None
        r.raise_for_status()
        payload = r.json()
        if isinstance(payload, list):
            raise IsADirectoryError(f"{path!r} is a directory, not a file")
        return {"sha": payload["sha"]}

    def _create_branch(self, http: httpx.Client, branch: str) -> None:
        # Get main's current commit SHA
        r = http.get(f"/repos/{REPO}/git/refs/heads/{DEFAULT_BRANCH}")
        r.raise_for_status()
        main_sha = r.json()["object"]["sha"]
        r = http.post(
            f"/repos/{REPO}/git/refs",
            json={"ref": f"refs/heads/{branch}", "sha": main_sha},
        )
        if r.status_code == 422 and "already exists" in r.text.lower():
            return  # branch exists, reuse
        r.raise_for_status()

    def _put_file(
        self,
        http: httpx.Client,
        path: str,
        content: str,
        *,
        message: str,
        branch: str,
        existing_sha: str | None,
    ) -> str:
        body: dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if existing_sha:
            body["sha"] = existing_sha
        r = http.put(f"/repos/{REPO}/contents/{path}", json=body)
        r.raise_for_status()
        return r.json()["commit"]["sha"]

    def _delete_file(
        self,
        http: httpx.Client,
        path: str,
        *,
        message: str,
        branch: str,
        existing_sha: str,
    ) -> str:
        r = http.request(
            "DELETE",
            f"/repos/{REPO}/contents/{path}",
            json={"message": message, "sha": existing_sha, "branch": branch},
        )
        r.raise_for_status()
        return r.json()["commit"]["sha"]

    def _open_pr(
        self, http: httpx.Client, *, title: str, branch: str, body: str,
    ) -> dict[str, Any]:
        r = http.post(
            f"/repos/{REPO}/pulls",
            json={"title": title, "head": branch, "base": DEFAULT_BRANCH, "body": body},
        )
        r.raise_for_status()
        return r.json()


# ----------------------------------------------------------------------
# Module-level helpers used by the write methods
# ----------------------------------------------------------------------

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str, max_len: int = 40) -> str:
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return (s[:max_len] or "edit").rstrip("-")


def _default_branch_name(message: str) -> str:
    slug = _slugify(message)
    return f"slack/{slug}-{int(time.time())}"


def _parse_thread_key() -> dict[str, str | None]:
    """Best-effort decode of a Centaur thread_key into Slack metadata.

    thread_key format: `slack:<team_id>:<channel_id>:<thread_ts>`
    Returns Nones if the SDK isn't available or the key isn't a slack thread.
    """
    try:
        tk = current_thread_key()
    except Exception:
        return {"thread_key": None, "channel_id": None, "thread_ts": None, "url": None}
    parts = tk.split(":")
    if len(parts) != 4 or parts[0] != "slack":
        return {"thread_key": tk, "channel_id": None, "thread_ts": None, "url": None}
    _, _team, channel, ts = parts
    # Slack URL: https://<workspace>.slack.com/archives/<channel>/p<ts_without_dot>
    ts_compact = ts.replace(".", "")
    url = f"https://app.slack.com/client/{SLACK_TEAM_ID}/{channel}/thread/{channel}-{ts}"
    return {
        "thread_key": tk,
        "channel_id": channel,
        "thread_ts": ts,
        "url": url,
    }


def _pr_body(
    *,
    action: str,
    path: str,
    message: str,
    description: str | None,
    requested_by: str | None,
) -> str:
    meta = _parse_thread_key()
    lines = [
        f"**Action:** {action} `{path}`",
        "",
        message,
    ]
    if description:
        lines += ["", description]
    lines += [
        "",
        "---",
        "**Audit trail**",
    ]
    if requested_by:
        lines.append(f"- Requested by: **{requested_by}** (via Slack)")
    if meta.get("url"):
        lines.append(f"- Slack thread: {meta['url']}")
    if meta.get("thread_key"):
        lines.append(f"- Centaur thread_key: `{meta['thread_key']}`")
    lines += [
        "",
        "Opened by Centaur on behalf of the requester. Review the diff, "
        "approve / request changes / close as you'd any human PR. Branch "
        "protection on `main` is the gate for what actually lands in the vault.",
    ]
    return "\n".join(lines)


_INSTANCE: ObsidianVaultClient | None = None


def _client() -> ObsidianVaultClient:
    """Centaur tool-loader entry point: returns a cached client instance."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = ObsidianVaultClient()
    return _INSTANCE
