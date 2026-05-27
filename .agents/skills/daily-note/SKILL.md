---
name: daily-note
description: |
  Capture the current Claude conversation as a structured daily note in the Birch Hill
  Obsidian vault, with backlinks to relevant atlas hubs and knowledge-graph nodes, and
  optionally execute Linear updates that came up during the session. Use this skill
  whenever Connor says "save this as a daily note," "log this session," "recap today,"
  "capture what we just decided," "write this up for the vault," "end of session,"
  "what should we save," or any phrase implying a session recap is wanted. Also trigger
  proactively at the natural end of a substantive working session — after a string of
  decisions, vault edits, or Linear changes — by offering to capture the day. Do NOT
  use for ad-hoc memo writing, reports, or one-off documents (those go through
  bh-design); this skill is specifically for the daily session-recap ritual that lands
  in `00-home/daily/`.
---

# Daily Note — Conversation → Vault Recap

## What this skill does

Turns the working context of a Claude conversation into a structured daily note in `00-home/daily/YYYY-MM-DD.md` in the Obsidian vault, and optionally writes back to Linear (creating issues, moving them between projects, marking them done/canceled, adding comments).

**The point is not to transcribe the conversation.** It's to land the *decisions*, *vault changes*, *Linear changes*, and *open follow-ups* in a place where future-Connor and future-Claude can find them — with wikilinks that make the note discoverable from anywhere it's relevant.

## When to trigger

**Explicit triggers:**

* "save this as a daily note" / "log this" / "recap today" / "end of session"
* "capture what we just decided"
* "write this up for the vault"

**Proactive triggers** — at the natural close of a substantive session, offer to capture the day. Specifically when any of the following occurred during the conversation:

* 3+ Linear writes (issue creation, project moves, status changes)
* 2+ vault file edits or deletions
* A decision that resolves an open question (e.g. "let's call it Birch Hill Strategies")
* A counterparty conversation or strategy decision worth surfacing later

The skill is cheap to run; lean toward offering it at session close even if the user didn't ask.

## Where the daily note lives

* **Folder:** `00-home/daily/`
* **Filename:** `YYYY-MM-DD.md` (e.g. `2026-04-25.md`)
* **If a note for today already exists:** append a new dated section — do NOT overwrite. Use a `## HH:MM — <topic>` header for the new section. Multiple sessions per day stack inside one file.

Use `date +%Y-%m-%d` via bash to get today's date — never guess.

## Daily-note structure

Read the template at `assets/daily-note-template.md` and fill it in. The template defines the canonical sections; do not add or rename sections without a reason.

The required frontmatter is:

```yaml
---
type: daily
date: YYYY-MM-DD
session_topic: short-description-kebab-case
tags: [daily, ...domain-tags]
updated: YYYY-MM-DD
---
```

Pick `tags` from the same vocabulary the rest of the vault uses — peek at frontmatter on related files (`atlas/rwasp-platform.md`, `knowledge/graph/strategies/*.md`) for the conventional vocabulary. Common tag families: `linear`, `vault-hygiene`, `lender`, `architecture`, `legal`, `counterparty`, `modeling`, `decks`.

## Writing the body — the rules

### 1. Decisions go first, with rationale

Each decision is one bullet, terse, with the *why* attached. Format:

```markdown
- **<Decision in imperative form>** — <one-line rationale>. Affects: [[file]], BIR-###.
```

Example:

```markdown
- **Brand name is Birch Hill Strategies; legal entity stays BH DAM** — keeps narrative simple while preserving the LLC's legal identity. Affects: [[bh-digital-asset-management]], [[bh-dam]], BIR-111.
```

### 2. Vault changes are mechanical

List every file created, updated, or deleted as a wikilink (or path for folders). Don't editorialize — that goes in Decisions.

```markdown
## Vault changes
- Deleted `voice-notes/`, `sessions/`, `research/` — confirmed-dead scaffolds (BIR-102)
- Created [[daily-note SKILL.md]] in `Birch Hill/skill-updates/`
```

### 3. Linear changes mirror what actually happened

Every Linear write is one bullet with the issue link in markdown form (the daily note renders in Obsidian, where markdown links work fine).

```markdown
## Linear changes
- Created [Project Atlas](https://linear.app/birch-hill/project/project-atlas-f3ce3312a4be) — RWASP buildout container
- Moved BIR-97, 80, 81, 92, 88, 84, 83, 82, 94 → Project Atlas
- Canceled BIR-99, 98, 93, 90, 86, 91 — superseded or out of scope
```

### 4. Follow-ups are owned and linked

Every follow-up bullet includes: who owns it, what's the next concrete action, and a Linear link if a ticket exists (or a flag that one needs to be created).

```markdown
## Follow-ups
- **Connor** — BIR-111 vault sweep: 27 files reference BH DAM, need per-file judgment on brand vs legal context
- **Bhavin** — ping for Paxos / USDG update (BIR-112)
- **New issue needed** — daily-note skill v1 → v2 once dogfooded for a week
```

### 5. Backlinks are explicit at the bottom

End the note with an explicit backlinks block. This is what makes the note discoverable from elsewhere in Obsidian's graph view.

```markdown
## Backlinks
- [[rwasp-platform]] — main hub (Lender matrix discussion)
- [[bh-dam]] — entity affected by naming decision
- [[connor-flanagan]]
```

Pick backlinks generously — anything the conversation *touched* meaningfully. A note linking to 8 things is more useful than one linking to 2.

## Linear write-back

This skill orchestrates Linear changes when the conversation calls for them. The Linear MCP tools are available in the session.

**Confirmation rule:** before any Linear write that the user hasn't already explicitly directed, propose the change in chat first. Don't silently create issues or change states. The skill is allowed to *do* what was already explicitly agreed in the conversation; for anything new it surfaces during recap, ask first.

**Common operations and the right tool:**

| Intent | Tool |
|---|---|
| Create issue | `save_issue` (no `id`, requires `title` + `team`) |
| Update issue (project, status, labels, parent, assignee) | `save_issue` (with `id`) |
| Cancel an issue | `save_issue` with `state: "43e29288-068c-4bb2-85ae-f85007aed31b"` (the Canceled status ID — passing the literal name "Canceled" matches "Duplicate" instead because both are `canceled`-type) |
| Mark done | `save_issue` with `state: "Done"` |
| Add comment | `save_comment` |
| Create new project | `save_project` (requires `name` + `addTeams`) |
| Apply a label | `save_issue` with `labels: [...]` |

After writing, mirror what was done in the daily note's `## Linear changes` section.

## Vault map — what to backlink to

The vault's canonical hubs and knowledge-graph nodes. When the conversation touches a topic, link to the matching file.

### Atlas hubs (root-level, foundational)

* `atlas/rwasp-platform.md` — RWASP platform hub (almost always relevant)
* `atlas/platform-architecture.md` — architecture summary
* `atlas/platform-open-items.md` — legacy open-items log
* `atlas/vault-information-arch.md` — vault structure docs

### Atlas/rwasp/ — structured workbench (YAMLs)

* `entities/` — bh-dam, bh-ds, bh-labs, bh-solutions
* `dcv/` — bh-strategies-llc, dual-engine-strategy, ovo-fund, sizing-rules, usat-series, usdg-series, dynamic-yield-split
* `counterparties/` — sky, ethena, cap, _candidate-matrix
* `modules/` — securitization-tokenization, underwriting-servicing, loan-quality-assurance
* `scenarios/` — base-sky, coc-shock, dcv-constrained-growth
* `gaps.md` — open questions log

### Knowledge graph — atomic nodes (markdown)

`knowledge/graph/{deals, strategies, partners, regulatory, research, design, entities, team, risk-frameworks}/` — link to specific files by name. When in doubt, glob the relevant subfolder for matches before writing the note.

## Workflow — start to finish

1. **Get today's date.** Bash: `date +%Y-%m-%d`.
2. **Check for an existing note** at `00-home/daily/YYYY-MM-DD.md`. If one exists, you're appending; if not, you're creating from the template.
3. **Re-scan the conversation.** What decisions were made? What vault files changed? What Linear writes happened? What's still open?
4. **Identify backlink targets.** Which atlas hubs and knowledge-graph nodes did the conversation touch? `Glob` the relevant folders if you're not sure of filenames.
5. **Detect pending Linear writes.** If the user agreed to changes in chat but they haven't been executed yet (or weren't because the conversation moved on), surface them — propose the writes, get confirmation, execute.
6. **Compose the note.** Use the template structure. Be terse. Use wikilinks generously.
7. **Write via the vault tool.** Use `obsidian_vault.propose_create` for a new note, or `obsidian_vault.propose_append` if today's note already exists. The two-step confirmation flow from the [[birch-hill-vault]] skill applies — draft the content in Slack, wait for the user to confirm (`yes` / `go` / `open the PR`), then call the tool. The tool opens a PR on `birch-hill-labs/obsidian-vault@main`.
8. **Report back to the user** with: the PR URL returned by the tool, a 2-line summary of what landed, and a list of any Linear writes executed.

## Style — tone and voice

* **Bullet-dense, not paragraph-prose.** This is a working log, not an essay. The reader (future-Connor or future-Claude) wants to skim.
* **Imperative for decisions, past tense for changes.** "Brand is Birch Hill Strategies" / "Deleted scaffold folders."
* **No hedging language.** Don't write "we discussed" or "we considered" — write what was *decided*. If something was discussed but not decided, it goes in Open Questions.
* **One line per bullet ideally; two if rationale needs it.** If you're writing three lines, you're writing a paragraph — collapse it.
* **No emojis, no headers beyond the template's, no marketing voice.**

## Anti-patterns — don't do these

* **Don't dump the whole conversation as a transcript.** The skill produces a *recap*, not a *log*. If the user wants a transcript, they'll ask.
* **Don't invent decisions that weren't made.** If the conversation surfaced a question but didn't resolve it, it goes in Open Questions, not Decisions.
* **Don't skip backlinks.** A daily note with no backlinks is dead weight in the graph.
* **Don't silently write to Linear.** Confirm any new write the user didn't already direct.
* **Don't overwrite an existing same-day note.** Append.

## Reference

* **Template:** `assets/daily-note-template.md` — the section structure to fill in.
* **Vault map:** see "Vault map" section above for backlink targets.
* **Linear MCP tools:** the conversation will already have `save_issue`, `save_project`, `save_comment`, `list_issues`, etc. loaded. Use them directly.
