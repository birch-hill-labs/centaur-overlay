"""Birch Hill Linear tool.

Read and write Birch Hill's Linear issues via the Linear GraphQL API
(https://api.linear.app/graphql). Use this for ALL Linear operations: get an
issue, list/search issues, update fields, create issues, and add comments.

Iron-proxy injects the Linear API key as the Authorization header on outbound
requests to api.linear.app, so the secret never lives in this process and is
NOT available in the sandbox. That is precisely why Linear work must go through
this tool, never a sandbox `uv run` / bash call hitting the Linear API: the
credential exists only at the tool/proxy layer.

Out-of-band setup (one-time): add the Linear API key to the Birch Hill Centaur
Vault 1Password item as LINEAR_API_KEY (the full Authorization header value),
and configure iron-proxy to inject it for host api.linear.app. The key must
have write scope (issue create / update).
"""

from __future__ import annotations

import re
from typing import Any

import httpx

API_BASE = "https://api.linear.app"
_IDENTIFIER_RE = re.compile(r"^([A-Za-z]+)-(\d+)$")


def _http() -> httpx.Client:
    return httpx.Client(
        base_url=API_BASE,
        headers={
            # iron-proxy REPLACE mode: substitutes this placeholder in the
            # Authorization header with the real LINEAR_API_KEY value for
            # requests to api.linear.app, at the network edge. This process
            # never sees the real key.
            "Authorization": "LINEAR_API_KEY",
            "Content-Type": "application/json",
            "User-Agent": "centaur-linear/0.1",
        },
        timeout=20.0,
    )


def _gql(http: httpx.Client, query: str, variables: dict | None = None) -> dict[str, Any]:
    resp = http.post("/graphql", json={"query": query, "variables": variables or {}})
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(f"Linear API error: {data['errors']}")
    return data["data"]


_ISSUE_FIELDS = """
  id identifier title description priority url
  state { id name type }
  assignee { id name email }
  team { id key name }
  project { id name }
"""


def _summary(node: dict) -> dict[str, Any]:
    return {
        "id": node.get("id"),
        "identifier": node.get("identifier"),
        "title": node.get("title"),
        "description": node.get("description"),
        "priority": node.get("priority"),
        "state": (node.get("state") or {}).get("name"),
        "state_type": (node.get("state") or {}).get("type"),
        "assignee": (node.get("assignee") or {}).get("email"),
        "team": (node.get("team") or {}).get("key"),
        "project": (node.get("project") or {}).get("name"),
        "url": node.get("url"),
    }


class LinearClient:
    """Read + write access to Birch Hill's Linear workspace.

    Use this tool for ALL Linear operations. NEVER shell out to the sandbox for
    Linear — the API key is injected only at the tool layer (via iron-proxy),
    not in the code-execution sandbox, so a sandbox call will fail to
    authenticate.
    """

    def get_issue(self, identifier: str) -> dict[str, Any]:
        """Fetch a single issue by its identifier (e.g. "BIR-123").

        Returns the issue's id, identifier, title, description, priority,
        state, assignee email, team key, project, and url.
        """
        key, num = self._parse_identifier(identifier)
        query = f"""query($key: String!, $num: Float!) {{
          issues(filter: {{team: {{key: {{eq: $key}}}}, number: {{eq: $num}}}}, first: 1) {{
            nodes {{ {_ISSUE_FIELDS} }}
          }}
        }}"""
        with _http() as http:
            data = _gql(http, query, {"key": key, "num": num})
        nodes = data["issues"]["nodes"]
        if not nodes:
            raise ValueError(f"Issue not found: {identifier}")
        return _summary(nodes[0])

    def list_issues(
        self,
        *,
        query: str | None = None,
        team: str | None = None,
        state: str | None = None,
        assignee: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        """List/search issues with optional filters.

        Args:
          query: substring to match in the issue title (case-insensitive).
          team: team name or key (e.g. "Birch Hill" or "BIR").
          state: workflow state name (e.g. "Backlog", "In Progress", "Done", "Canceled").
          assignee: assignee email (e.g. "bv@birchhill.io").
          limit: max issues to return (default 25, max 100).

        Returns {"issues": [...summaries...], "count": int}.
        """
        filt: dict[str, Any] = {}
        if query:
            filt["title"] = {"containsIgnoreCase": query}
        if team:
            filt["team"] = (
                {"key": {"eq": team}}
                if len(team) <= 5 and team.isupper()
                else {"name": {"containsIgnoreCase": team}}
            )
        if state:
            filt["state"] = {"name": {"eqIgnoreCase": state}}
        if assignee:
            filt["assignee"] = {"email": {"eq": assignee}}
        gql = f"""query($f: IssueFilter, $n: Int!) {{
          issues(filter: $f, first: $n, orderBy: updatedAt) {{
            nodes {{ {_ISSUE_FIELDS} }}
          }}
        }}"""
        with _http() as http:
            data = _gql(http, gql, {"f": filt, "n": min(limit, 100)})
        issues = [_summary(n) for n in data["issues"]["nodes"]]
        return {"issues": issues, "count": len(issues)}

    def update_issue(
        self,
        identifier: str,
        *,
        title: str | None = None,
        description: str | None = None,
        state: str | None = None,
        assignee: str | None = None,
        priority: int | None = None,
    ) -> dict[str, Any]:
        """Update an existing issue (e.g. "BIR-123"). Only provided fields change.

        Args:
          title, description: new text.
          state: workflow state NAME (e.g. "In Progress", "Done", "Canceled");
            resolved against the issue's team's states.
          assignee: assignee NAME or EMAIL (e.g. "Jack" or "jt@birchhill.io"); resolved to the user id.
          priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low.

        CONFIRM with the user before closing/canceling an issue (state ->
        Done / Canceled), and re-read the live issue first (verify before closing).
        """
        current = self.get_issue(identifier)
        inp: dict[str, Any] = {}
        if title is not None:
            inp["title"] = title
        if description is not None:
            inp["description"] = description
        if priority is not None:
            inp["priority"] = priority
        with _http() as http:
            if state is not None:
                inp["stateId"] = self._resolve_state(http, current["id"], state)
            if assignee is not None:
                inp["assigneeId"] = self._resolve_user(http, assignee)
            mutation = (
                "mutation($id: String!, $input: IssueUpdateInput!) {"
                "  issueUpdate(id: $id, input: $input) {"
                f"    success issue {{ {_ISSUE_FIELDS} }}"
                "  }"
                "}"
            )
            data = _gql(http, mutation, {"id": current["id"], "input": inp})
        res = data["issueUpdate"]
        return {"success": res["success"], "issue": _summary(res["issue"])}

    def create_issue(
        self,
        *,
        team: str,
        title: str,
        description: str | None = None,
        assignee: str | None = None,
        priority: int | None = None,
        project: str | None = None,
    ) -> dict[str, Any]:
        """Create a new issue.

        Args:
          team: team name or key (e.g. "Birch Hill" / "BIR").
          title: issue title (required).
          description: markdown body.
          assignee: assignee name or email (e.g. "Jack" or "jt@birchhill.io").
          priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low.
          project: project name (optional).
        """
        with _http() as http:
            inp: dict[str, Any] = {"teamId": self._resolve_team(http, team), "title": title}
            if description is not None:
                inp["description"] = description
            if priority is not None:
                inp["priority"] = priority
            if assignee is not None:
                inp["assigneeId"] = self._resolve_user(http, assignee)
            if project is not None:
                inp["projectId"] = self._resolve_project(http, project)
            mutation = (
                "mutation($input: IssueCreateInput!) {"
                f"  issueCreate(input: $input) {{ success issue {{ {_ISSUE_FIELDS} }} }}"
                "}"
            )
            data = _gql(http, mutation, {"input": inp})
        res = data["issueCreate"]
        return {"success": res["success"], "issue": _summary(res["issue"])}

    def add_comment(self, identifier: str, body: str) -> dict[str, Any]:
        """Add a comment to an issue (e.g. "BIR-123")."""
        current = self.get_issue(identifier)
        with _http() as http:
            mutation = (
                "mutation($input: CommentCreateInput!) {"
                "  commentCreate(input: $input) { success comment { id url } }"
                "}"
            )
            data = _gql(http, mutation, {"input": {"issueId": current["id"], "body": body}})
        res = data["commentCreate"]
        return {"success": res["success"], "url": (res.get("comment") or {}).get("url")}

    def list_users(self, query: str | None = None, limit: int = 50) -> dict[str, Any]:
        """List workspace users (id, name, email), optionally filtered by name.

        `assignee` on update_issue / create_issue already accepts a NAME or an
        email, so you usually don't need this — reach for it only when a name is
        ambiguous or you want to confirm the right person before assigning.
        """
        if query:
            gql = ("query($q: String!, $n: Int!) { users(filter: {or: ["
                   "{name: {containsIgnoreCase: $q}}, {displayName: {containsIgnoreCase: $q}}]}, "
                   "first: $n) { nodes { id name displayName email active } } }")
            variables = {"q": query, "n": min(limit, 100)}
        else:
            gql = "query($n: Int!) { users(first: $n) { nodes { id name displayName email active } } }"
            variables = {"n": min(limit, 100)}
        with _http() as http:
            nodes = _gql(http, gql, variables)["users"]["nodes"]
        users = [
            {"id": u["id"], "name": u.get("displayName") or u.get("name"),
             "email": u.get("email"), "active": u.get("active")}
            for u in nodes
        ]
        return {"users": users, "count": len(users)}

    # ---- resolvers --------------------------------------------------------
    def _parse_identifier(self, identifier: str) -> tuple[str, float]:
        m = _IDENTIFIER_RE.match((identifier or "").strip())
        if not m:
            raise ValueError(f"Invalid issue identifier: {identifier!r} (expected like 'BIR-123')")
        return m.group(1).upper(), float(m.group(2))

    def _resolve_state(self, http: httpx.Client, issue_id: str, name: str) -> str:
        query = "query($id: String!) { issue(id: $id) { team { states { nodes { id name } } } } }"
        data = _gql(http, query, {"id": issue_id})
        states = data["issue"]["team"]["states"]["nodes"]
        for s in states:
            if s["name"].lower() == name.lower():
                return s["id"]
        raise ValueError(f"State {name!r} not found. Available: {[s['name'] for s in states]}")

    def _resolve_user(self, http: httpx.Client, who: str) -> str:
        # Accept a NAME or an email. "@" -> exact email; otherwise match the
        # display/full name (case-insensitive), so "Jack" resolves without a
        # separate lookup.
        who = (who or "").strip()
        if "@" in who:
            flt = "{email: {eq: $v}}"
        else:
            flt = "{or: [{name: {containsIgnoreCase: $v}}, {displayName: {containsIgnoreCase: $v}}]}"
        query = f"query($v: String!) {{ users(filter: {flt}, first: 5) {{ nodes {{ id name displayName email }} }} }}"
        nodes = _gql(http, query, {"v": who})["users"]["nodes"]
        if not nodes:
            raise ValueError(f"User not found: {who!r}. Use list_users to find the right name or email.")
        return nodes[0]["id"]

    def _resolve_team(self, http: httpx.Client, team: str) -> str:
        data = _gql(http, "query { teams { nodes { id key name } } }")
        for t in data["teams"]["nodes"]:
            if team.lower() in (t["key"].lower(), t["name"].lower()):
                return t["id"]
        raise ValueError(f"Team not found: {team}")

    def _resolve_project(self, http: httpx.Client, project: str) -> str:
        query = "query($q: String!) { projects(filter: {name: {containsIgnoreCase: $q}}, first: 1) { nodes { id name } } }"
        data = _gql(http, query, {"q": project})
        nodes = data["projects"]["nodes"]
        if not nodes:
            raise ValueError(f"Project not found: {project}")
        return nodes[0]["id"]
