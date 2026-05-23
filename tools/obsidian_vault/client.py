"""Birch Hill obsidian-vault reader.

Reads from the github.com/birch-hill-labs/obsidian-vault repo via the GitHub
REST API. Iron-proxy injects GITHUB_VAULT_TOKEN as a Bearer Authorization
header on outbound requests to api.github.com, so the secret never lives in
this process.

For v1 the tool is read-only and unauthenticated at the application layer
(every Slack user gets the same view). Phase 2 will add per-user RBAC via a
Postgres role table consulted before each read.
"""

from __future__ import annotations

import base64
from typing import Any

import httpx


REPO = "birch-hill-labs/obsidian-vault"
DEFAULT_BRANCH = "main"
API_BASE = "https://api.github.com"

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
            # iron-proxy will overwrite Authorization with the real token at the
            # network edge. Setting any non-empty placeholder ensures the header
            # is present so iron-proxy's match_headers rule fires.
            "Authorization": "Bearer placeholder",
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


_INSTANCE: ObsidianVaultClient | None = None


def _client() -> ObsidianVaultClient:
    """Centaur tool-loader entry point: returns a cached client instance."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = ObsidianVaultClient()
    return _INSTANCE
