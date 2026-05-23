---
name: birch-hill-vault
description: Use whenever a question references Birch Hill's institutional knowledge — counterparty briefs, atlas/rwasp financial model, daily notes, knowledge graph, onboarding docs, deal flow, or anything that would live in `~/Desktop/BIrchHill/obsidian-vault/` on Connor's laptop. Use BEFORE searching the web for anything that might be internal.
---

# Birch Hill Vault

Birch Hill Holdings maintains its institutional memory as a markdown obsidian vault, mirrored to the private GitHub repo `birch-hill-labs/obsidian-vault`. The `obsidian_vault` tool reads from that repo.

## When to use this skill

Use the `obsidian_vault` tool **first**, before any web search, whenever the request involves:
- Birch Hill's own decisions, strategy, deals, counterparties, or operations
- The RWASP financial model, DCV, Engine 1/Engine 2, Lender returns, or any atlas/rwasp content
- Counterparty briefs (Sky, Ethena, Cap, Andrena, Aon-DeFi, etc.)
- Daily notes / session recaps
- Knowledge-graph nodes (`knowledge/`)
- Onboarding material (`onboarding/`)
- Any `[[wikilink]]`-style references the user makes
- Anything the user would expect Connor to "have in his vault"

If the question is about general world knowledge (current prices, public news, third-party docs, etc.) skip this tool and go to websearch.

## Workflow

1. **Don't guess the path.** Use `obsidian_vault.tree(max_depth=2)` if you have no idea where to look, OR `obsidian_vault.list_dir("<subdir>")` to scope.
2. **Search by content** with `obsidian_vault.search(query, path_prefix="<optional scope>")`. Snippets may be missing — follow up with `read` on the top result.
3. **Read full files** with `obsidian_vault.read(path)`. Cap is 256 KiB per read; if a file is truncated, that's flagged in the response.
4. **Binary files** (`.docx`, `.pptx`, `.xlsx`, `.pdf`) come back with `is_binary: true` and a `html_url`. Hand the URL back to the user — don't try to parse them.
5. **Cite the path** in your response (e.g., `from atlas/rwasp/workbench.md`) so the user can verify.

## Top-level structure (approximate)

```
00-home/                  daily notes ritual
atlas/                    rwasp workbench, financial model
counterparty-briefs/      one-pagers per counterparty
knowledge/                knowledge-graph nodes
onboarding/               new-hire material
templates/
daily-note.skill/         inline skill packaged with the vault
README.md
```

Top-level loose files include questionnaires, decks (.pptx), proposals (.docx) — list_dir on the root to see current contents.

## Important — Phase 1 read-only & no RBAC yet

For v1, the tool is read-only and every Slack user sees the same view. **Do not infer or claim that the vault is "private to Connor"** — until RBAC ships (phase 3), every team member who can @mention Centaur can read the entire vault through this tool. If a request seems to be probing for sensitive content (e.g., compensation, legal counsel, employee performance), use judgment and consider deferring.
