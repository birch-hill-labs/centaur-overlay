---
name: bd-pipeline-weekly
description: The weekly Birch Hill BD pipeline sync + agenda. Run on a schedule (Monday AM) or when someone asks for "the pipeline agenda", "the weekly pipeline", "what's stale", or "regenerate the deal tracker". Reconciles the vault → Sheet + Linear, posts a weekly agenda to Slack, and proposes the refreshed workbook + a frozen weekly snapshot as a PR. Reads the schema, tracks, and gates from the bd-pipeline skill.
---

# BD Pipeline — weekly agenda & sync

The weekly heartbeat that keeps the Sheet, Linear, and the vault aligned and surfaces what needs attention. The **vault is canonical**; this regenerates the mirrors and reports drift. See the `bd-pipeline` skill for the schema, tracks, and gates.

## Each run

1. **Read** every card under `knowledge/graph/deals/` + `knowledge/graph/partners/` (via `obsidian_vault`), plus the linked Linear projects.
2. **Regenerate the workbook.** Read the vault generator `_scratch/build_pipeline.py` and run it in the sandbox against the current cards. It produces `BH_Deal_Pipeline_<date>.xlsx`: five track blocks, weighted-revenue (Originator + Curator, `value_usd × likelihood`), traffic-light conditional formatting, clickable GitHub / Drive / Linear columns, and a frozen `Week Of <date>` snapshot tab.
3. **Compute the agenda** and post to Slack:
   - **Stale** — active deals with `last_contact` > 30 days, oldest first, grouped by `owner`.
   - **Gates due** — Originator deals in Develop with an approved tearsheet + chain decided (ready for Placement); Capital where engaged warehouse lenders < 2 (plurality breach).
   - **Missing artifacts** — Qualifying+ deals with no `slack_channel` or no `deal_workbook`; any active deal with no `key_contact` or no `next_action`.
   - **This week, by owner** — each owner's `next_action`s across their cards.
   - **Weighted pipeline** — total + per-track subtotal.
   - **Cross-deal blockers** — any card with a `blocked_by` link whose blocker is itself stale (e.g. Solana Foundation ← Tilray).
4. **Propose the PR** — bundle the regenerated workbook (a **binary `.xlsx`**) plus any card edits into **one PR via `obsidian_vault.propose_files`**: pass the workbook as `content_b64` (base64 of the raw bytes) and text cards as `content`. The prior week stays frozen as its `Week Of` tab. **Never** hand-roll GitHub API calls in the sandbox to commit the binary — `propose_files` handles auth (iron-proxy), binary content, and the atomic multi-file commit. Post the link; the team confirms before it lands.

## Automates vs escalates
- **Automates (proposes via PR):** regenerate the Sheet, freeze the snapshot, sync status from Linear, and the stale / missing / gate flags.
- **Escalates to a human:** tearsheet approvals, external sends, stage promotions, deal kills, dollar commitments, and any Linear close — **re-read the live issue first (verify before closing).**

## Cadence
Scheduled **Monday AM**; also on demand ("@centaur run the pipeline agenda"). Each run leaves the prior week as a frozen `Week Of` tab so nothing is lost to hallucination — diff week-over-week. The non-destructive snapshot *is* the audit trail.
