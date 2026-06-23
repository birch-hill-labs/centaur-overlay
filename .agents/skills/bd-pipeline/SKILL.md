---
name: bd-pipeline
description: Use whenever someone shares a BD / deal update in Slack — meeting notes, a quick status ("Cantor signed the MNDA"), a new contact, a document we sent, a new opportunity, or a stage change — for any Birch Hill counterparty (originator, curator, capital/lender, ecosystem, or service partner). Centaur parses the update, finds the vault card(s) it touches, drafts the change, confirms in Slack, and opens a PR. Also use for "what's the status of <deal>", "what do we owe <counterparty>", or anything about the BD pipeline, the deal tracker, or the weighted pipeline. This is the canonical knowledge of how the Birch Hill BD pipeline works.
---

# BD Pipeline — intake & process knowledge

Birch Hill's BD pipeline is a knowledge graph in the obsidian vault. Each counterparty has **one card** (the record of record) under `knowledge/graph/deals/` (deals) or `knowledge/graph/partners/` (service/infra). The Google Sheet and Linear are **generated / synced from the vault** — the vault is canonical. Use the `obsidian_vault` tool to read and to propose changes (draft → confirm → PR; never write `main` directly).

## When someone dumps an update

1. **Identify the counterparty(ies). The channel is the strongest signal** — if the update arrives in a deal's dedicated channel, resolve the counterparty directly from the card whose `slack_channel` matches; every message there belongs to that deal unless it names another. Otherwise `obsidian_vault.search` for the name. If no card exists and it's a real new opportunity, propose creating one (schema below).
2. **Extract what changed** and map each fact to its home field (below). Common: a new `key_contact`, the meeting date → `last_contact`, a document we sent → `sent_log`, a next step → `next_action`, a stage move, a status change, a new linkage (chain / warehouse lender / TVL partner).
3. **Draft the edit** with `obsidian_vault.propose_edit` / `propose_append` — frontmatter for structured fields, body for narrative + a dated meeting-log entry.
4. **Post the diff back to Slack** ("I'll set Cantor: `last_contact` → 2026-06-16, log the MNDA in `sent_log`, `next_action` → schedule the structuring call — confirm?") and only open the PR on confirmation.
5. **Cascade where relevant.** If the update creates a trackable next step, propose a Linear task. If it resolves one, propose updating that issue's status. If it trips a stage gate, say so.

## The schema (every card)

Frontmatter fields and who owns them:
- `track` (primary) + `secondary_track` — one of: Originator · Curator · Capital · Ecosystem · Service-Infra
- `oabs_role`, `asset_class`
- `stage` (lifecycle stage, see gates) · `status` (inbox · qualifying · active · paused · closed-won · closed-lost)
- `owner` (BH lead: Connor · Bhavin · Jon · Jack)
- `key_contact` · `last_contact` (date of last real touch — **stale if > 30 days on an active deal**) · `next_followup`
- `value_usd` (BH **revenue** estimate — Originator/Curator only) · `likelihood` (decimal)
- `links` (typed: `chain` · `warehouse_lender` · `tvl_partner` · `custody` · `blocked_by` · `related`)
- `sent_log` (what we sent + when) · `next_action` · `linear_project`
- `deal_workbook` (Drive link to the per-deal economics workbook — created at **Qualifying**; holds deal-size / yield / performance fees / curation split. The card carries only the rolled-up revenue figure; the workbook holds the math.)
- `vault_book` · `tearsheet` (Drive / Google Doc links to the deal's Vault Book and Tear Sheet deliverables — each surfaced as its own clickable column in the generated Sheet. Set these to the **bare** shareable URL — a plain `https://…` string, **not** a markdown link — the column only renders when the value starts with `http`.)
- `slack_channel` (the opportunity's dedicated internal Slack channel — `#deal-<name>` at **Qualifying**, renamed to `#project-<name>` once **Active**. Any update posted in the current channel routes straight to this card.)

## The 5 tracks
- **Originator** — credit clients feeding oABS Circuit 1. Revenue: advisory + securitization + placement.
- **Curator** — BH Labs curates a vault/strategy. Revenue: curation / performance-fee split.
- **Capital** — Warehouse Lenders / oABS Subscribers / Stablecoin Lenders. Tracked by capacity, not fee.
- **Ecosystem / TVL** — chains, foundations, treasuries, distribution. Tracked by TVL / incentives / venue.
- **Service-Infra** — custody, legal, oracle, tranching, audit. Vendor.

## Stage-gates (NOT a strict order — only the gates enforce sequence)
- **Originator:** Intro → Qualify → Develop (Drive + Linear kickoff, then tearsheet / HTML site / economics + the chain decision) → Deal Placement (warehouse capacity lined up) → Live. **Gate to Placement: tearsheet approved AND chain decided.**
- **Capital:** Candidate → Evaluate → Term (LOI) → Committed. Hold **≥ 2 engaged warehouse lenders** at different cost-of-capital (plurality rule).
- **Ecosystem:** Identify → Scope → Develop (partnership doc) → Live (TVL committed).
- **Curator:** Scope → Design (strategy doc + economics) → Launch (vault live) → Operate.
- **Service-Infra:** Identify → Evaluate → Engage (contract) → Active.

## Setting up an opportunity (at Qualifying)
When a deal reaches **Qualifying**, stand up its workspace:
1. **Dedicated Slack channel** — `#deal-<counterparty>` at Qualifying, **renamed to `#project-<counterparty>` when the deal goes Active** (the prefix doubles as a stage signal: `deal-` = pursuing, `project-` = in execution; mirrors the deal→project promotion in Linear). Record the current channel in `slack_channel`. Centaur proposes creating it at Qualifying and proposes the rename at the Active transition, backfilling the field each time; updates in the current channel route straight to the card.
2. **Per-deal economics workbook** in the Drive folder → `deal_workbook` (deal-size / yield / performance fees / curation split).

## Outbound packet (what we send)
The stylized **oABS Product Doc.pdf** goes to every Capital / Ecosystem counterparty; approved **Originator tearsheets** then flow to Capital + Ecosystem parties — that distribution *is* Deal Placement. Log every send in `sent_log`.

## Updating Linear
Use the **`linear`** tool for ALL Linear operations — `get_issue` (e.g. `BIR-123`), `list_issues`, `update_issue` (title / description / state / assignee / priority), `create_issue`, `add_comment`. **Never shell out to the sandbox for Linear** (`uv run` / bash hitting the Linear API will fail — the API key is injected only at the tool layer, not the sandbox). Re-read the live issue with `get_issue` before changing it, and **confirm with the user before closing or canceling** an issue (state → Done / Canceled). When a deal update creates a trackable next step, propose a `create_issue`; when it resolves one, propose the `update_issue`.

## Rules
- **Use the vault tool's write methods — never reimplement them in the sandbox.** Edit text via `propose_edit` / `propose_create` / `propose_append`; bundle multi-file or **binary** changes (e.g. the regenerated `.xlsx` workbook) into one PR via `propose_files` (binary as base64 `content_b64`). Hand-rolling GitHub API calls in the sandbox fails — the credential is injected only at the tool layer, and binary writes break on UTF‑8 encoding. **If a capability is genuinely missing, do the part you can and say what you couldn't — don't improvise.**
- **Weighted-revenue pipeline = Originator + Curator deals only** (`value_usd × likelihood`). Capital / Ecosystem / Service never count as revenue.
- **Verify before closing.** Never close/merge a Linear issue or archive a deal off a pattern match — re-read the live card/issue first.
- **Confirm before sending.** Sending anything external (tearsheets, LOIs, product doc) and any dollar commitment is a human decision — propose, don't act.
