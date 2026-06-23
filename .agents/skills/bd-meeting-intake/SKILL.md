---
name: bd-meeting-intake
description: Use when Connor drops BD meeting notes — a multi-deal brain dump from a sync (e.g. the weekly Bhavin BD meeting) covering several counterparties, action items, and decisions at once. Parses the whole note, maps each deal to its vault card + Linear, drafts ONE consolidated proposal across cards + Linear + the BD sheet, confirms wholesale in Slack, then applies it in a single vault PR (propose_files) plus Linear writes. The batch sibling of bd-pipeline (single-update intake). Reads schema / tracks / gates from bd-pipeline.
---

# BD Meeting Intake — batch notes → cards + Linear + Sheet

When Connor drops notes from a BD meeting (often the weekly Bhavin sync), one message can touch many deals at once. Turn the whole note into a single, reviewable set of updates across the three systems. The **vault is canonical**; the **BD sheet is generated** from it; **Linear is execution**. Read the `bd-pipeline` skill for the card schema, the 5 tracks, the stage-gates, and the channel / workbook conventions — this skill is its batch sibling.

## The flow

1. **Split the note by deal / topic.** Identify every counterparty and cross-cutting item mentioned. Resolve each to a card with `obsidian_vault.search` (deals under `knowledge/graph/deals/`, partners under `knowledge/graph/partners/`).
2. **Handle each deal as an independent unit** — fan out one unit of work per deal and parallelize where the harness supports it (a meeting touching 8 deals is real scale; per-deal focus beats one pass over everything). For each deal, map the notes to:
   - **Card fields** — `last_contact` = the meeting date, plus any `next_action`, `key_contact`, `stage`, `status`, `sent_log`, `value_usd` / `likelihood`, or typed `links` change the notes imply.
   - **A meeting-log entry** — a dated `## <YYYY-MM-DD> BD sync` block appended to the card body, capturing what was discussed and decided (the "why" the structured fields don't hold).
   - **Linear** — action items → proposed **new** tasks; resolved items → status changes / closes.
   - **New opportunity with no card** → propose **creating** one (schema in `bd-pipeline`), included in the same proposal.
3. **Post ONE consolidated summary to Slack**, grouped by deal. Per deal show: the field changes, the meeting-log block, and the Linear actions (➕ new task · ✏️ status change · ✅ close · 🆕 new card). End with: *"Confirm all, or tell me what to change."* **Nothing is applied yet.**
4. **On confirmation, apply it:**
   - **Vault** → `obsidian_vault.propose_files`: **one PR** bundling every touched / created card **and** the regenerated BD workbook (run `_scratch/build_pipeline.py` in the sandbox, pass the `.xlsx` as `content_b64`). Never hand-roll the GitHub API in the sandbox.
   - **Linear** → the `linear` tool: `create_issue` for each confirmed new task; `update_issue` for confirmed status changes.
   - Post the vault PR link + the Linear issues created / updated.

## Rules
- **Wholesale confirm, with redline.** One proposal for the whole meeting; Connor approves it all at once or names the specific deals to change. Never apply before confirmation.
- **New cards ride the wholesale.** A new-counterparty card is proposed inside the same consolidated summary — not as a separate ask.
- **Linear: propose, never auto-apply.** New tasks are auto-**proposed** (Connor confirms them in the wholesale). **Always confirm before any close / status change, and re-read the live issue first** (verify-before-closing).
- **Meeting-log every touched card.** Append the dated `## <date> BD sync` block so the discussion is captured, separate from the field updates.
- **Don't invent.** No field value, contact, email, dollar figure, or Linear status that isn't supported by the notes — if the notes are ambiguous, **flag it in the summary** rather than guessing. Use the **exact** schema field names (e.g. `key_contact`, not invented variants).
- **Use the tools, never reimplement them.** `propose_files` for the vault bundle (cards + the binary workbook); the `linear` tool for Linear. No sandbox GitHub / Linear API reimplementation — the credentials live only at the tool layer.
