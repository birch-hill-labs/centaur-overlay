---
name: birch-hill-vault
description: Use whenever a question references Birch Hill's institutional knowledge — counterparty briefs, atlas/rwasp financial model, daily notes, knowledge graph, onboarding docs, deal flow, or anything that would live in `~/Desktop/BIrchHill/obsidian-vault/` on Connor's laptop. Use BEFORE searching the web for anything that might be internal. Also use when the user asks to ADD, UPDATE, APPEND TO, or DELETE vault content — Centaur proposes the change as a GitHub PR rather than writing directly.
---

# Birch Hill Vault

Birch Hill Holdings' institutional memory lives as a markdown obsidian vault, mirrored to `birch-hill-labs/obsidian-vault`. The `obsidian_vault` tool reads from and proposes changes to that repo.

## When to use

**Default posture: take one beat to consider the vault on every Slack mention.** The cost of one extra `obsidian_vault.search` is much lower than the cost of giving a generic answer when the team has internal context on the topic.

Reach for `obsidian_vault` **first**, before websearch, whenever the request involves:
- Birch Hill's own decisions, strategy, deals, counterparties, or operations
- The RWASP financial model, DCV, Engine 1/Engine 2, Lender returns, atlas/rwasp content
- Counterparty briefs (Sky, Ethena, Cap, Andrena, Aon-DeFi, etc.)
- Daily notes / session recaps
- Knowledge-graph nodes (`knowledge/`)
- Onboarding material (`onboarding/`)
- Any `[[wikilink]]`-style references
- ADDING / UPDATING / DELETING vault content

If the question is unambiguously about general world knowledge (public news, third-party docs, current prices, generic how-tos), skip this tool and go to websearch.

### Channel-driven defaults

Use the calling Slack channel as a strong prior:

- **Knowledge / strategy / ops channels** (channel name contains `knowledge`, `strategy`, `ops`, `deal`, `workbench`, `rwasp`, `atlas`, `counterparty`, `briefing`, `research`, `onboarding`, or matches `#team-knowledge` exactly): **vault-first regardless of how the question is phrased.** Start with `tree` or `search` before composing any reply.
- **Casual channels** (`random`, `lunch`, `social`, `fun`, `coffee`): skip the vault unless the question is explicitly internal.
- **Everything else** (`#general`, `#bots`, etc.): use the default reflex — query the vault if the question is plausibly internal, skip it otherwise.

You can resolve a channel's name from its ID via the `slack` tool (`conversations.info`). Look it up once per session; channel mappings don't change mid-thread.

## Read workflow

1. Don't guess paths. Use `obsidian_vault.tree(max_depth=2)` to orient, or `list_dir("<subdir>")` to scope.
2. `obsidian_vault.search(query, path_prefix="<optional>")` for content lookup. Snippets may be missing — follow up with `read` on top results.
3. `obsidian_vault.read(path)` for full content. 256 KiB cap; truncation flagged in response.
4. Binary files (`.docx`, `.pptx`, `.xlsx`, `.pdf`) return `is_binary: true` and an `html_url`. Hand the URL back; do not try to parse.
5. **Always cite the path** in the response (e.g., `from atlas/rwasp/workbench.md`).

## Write workflow — TWO STEPS, ALWAYS CONFIRM

When the user asks to add / update / append / delete content in the vault, **never** call `propose_*` immediately. Instead:

### Step 1 — Draft and confirm
1. Use `read` / `list_dir` / `tree` to understand the vault's current structure for the target area
2. Decide:
   - The exact target path (if appending to an existing note, name it; if creating, propose a path that follows the vault's existing conventions)
   - The exact text to add / change
3. **Post the plan in Slack** as a concrete preview:
   - For append/edit: show the file path and a fenced diff or full content block of what will change
   - For create: show the path and full content
   - For delete: show what's being deleted
4. **Ask the user to confirm explicitly** — e.g., *"Open the PR? Reply 'yes' to proceed or refine the plan."*

### Step 2 — Open the PR (only after explicit confirmation)
Once the user has confirmed in the same Slack thread, call the matching method:
- `propose_create(path, content, message, requested_by="<slack handle>")`
- `propose_edit(path, new_content, message, requested_by="...")`
- `propose_append(path, addition, message, requested_by="...")`
- `propose_delete(path, message, requested_by="...")`

Always pass `requested_by` with the user's display name or Slack handle so the PR body attributes the request.

After the PR opens, reply in Slack with the PR URL and number. Tell the user a reviewer needs to merge on GitHub — Centaur does not bypass review.

### What counts as "explicit confirmation"
- "yes", "confirm", "go", "open the PR", "ship it", "do it"
- A repeated request for the same edit
- NOT: "looks good", "thanks", "interesting" — those are not confirmations

If the user pivots ("actually put it under counterparty-briefs instead"), redraft and re-confirm. Don't just open a PR for the new plan.

### What never gets a PR
- Reading vault content (just answer in Slack with citations)
- Trivial typo questions ("how do you spell X")
- Anything not actually a change request

## v1 limits — say aloud if asked

- Read access is uniform across all Slack users (no path-level RBAC yet).
- Write access is gated by GitHub branch protection, NOT in Centaur — every PR needs a human reviewer to merge.
- Phase 3 adds path-level RBAC driven by a Postgres user-role table: each role gets `allowed_path_prefixes` for both reads and write proposals. Until then, assume any team member can request a change to any path.
