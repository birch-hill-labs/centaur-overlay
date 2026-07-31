---
name: bd-call-note
description: Use when a BD Call Intake form post lands in #bd-intake (posted by the "BD Call Intake" workflow bot) — one external call, one or more counterparties, structured fields — or when someone says "process the call note" / points at a #bd-intake post. Turns the form post into the standard vault + Linear + Sheet update AND fans the result out to the relevant deal and partner Slack channels. The single-call, channel-routing front door to the BD pipeline: reuses the bd-meeting-intake flow for the card / Linear / Sheet mechanics and reads schema, counterparty↔deal resolution, tracks, gates, tools, and the team roster from bd-pipeline. Not for weekly syncs (bd-pipeline-weekly) or multi-deal brain dumps pasted straight into a channel (bd-meeting-intake).
---

# BD Call Note — #bd-intake form → cards + Linear + Sheet, then fan out to channels

`#bd-intake` is the firm's one capture surface for external calls. Each submission is a structured post from the **BD Call Intake** workflow bot: *Counterparty · Associated Deals · Call Date · BH attendees · External attendees · Summary / notes · Required Actions · Deal Stage · Relevant Links · Sensitive?*. Turn it into the standard pipeline update, then push the result out to the channels that own each deal and partner.

This skill owns only two things the rest of the suite doesn't: the **`#bd-intake` trigger** and the **outbound channel fan-out**. Everything else is delegated — read **`bd-pipeline`** for the card schema, counterparty↔deal resolution, the five tracks, the stage-gates, the `linear` tool, and the team roster; reuse the **`bd-meeting-intake`** flow to turn the notes into card edits + a meeting-log block + Linear tasks + the regenerated Sheet, bundled into one PR. A single call is just a 1-to-N-deal instance of that batch flow.

## Trigger
Fire on a **BD Call Intake workflow-bot post in `#bd-intake`**. Also fire when a human @-mentions Centaur on such a post or says "process the call note." Do not fire on ordinary human chatter in the channel.

## Flow
1. **Parse the form** → call_date, counterparties[], associated_deals[], attendees, summary, required_actions, deal_stage, links, sensitive.
2. **Resolve, then run the standard update — per `bd-meeting-intake`.** Resolve each associated deal to its card and the counterparty via `obsidian_vault.search` (deals under `knowledge/graph/deals/`, partners under `knowledge/graph/partners/`). **Counterparty ≠ deal** — a call may touch several cards; split the notes per deal. For each: draft the field changes (`last_contact` = call_date, plus any `next_action` / `key_contact` / `stage` / `status` / `sent_log` / typed `links` the notes imply) and a **`## <call_date> BD sync`** meeting-log block. Required Actions → proposed Linear tasks — re-read the live issue first and **attach to an existing issue rather than duplicating**. No matching card → propose creating one.
3. **Propose once, in the `#bd-intake` thread**, grouped by deal, and include the **fan-out plan** (which channel gets what). End with *"Confirm all, or tell me what to change."* Nothing is applied yet.
4. **On confirmation, apply:**
   - **Vault** → `obsidian_vault.propose_files`: one PR bundling every touched / created card **and** the regenerated BD workbook (`_scratch/build_pipeline.py` in the sandbox, `.xlsx` as `content_b64`). Never hand-roll the GitHub API.
   - **Linear** → the `linear` tool: create / update the confirmed tasks.
   - **Fan out to Slack** (below).
   - Post the PR link + the Linear issues back in the thread.

## Slack fan-out (this skill's net-new job)
Route to up to three surfaces via the Slack post tool:
- **`#bd-intake`** — the full call note stays here as the system of record for the call.
- **Each associated deal → its channel** — a deal-specific slice: high-level points + action items + a link back to the `#bd-intake` post. Resolve from the deal card's `slack_channel` (the `#deal-` / `#project-` prefix follows stage).
- **The counterparty → its `#partnership-*` channel** — a relationship-level pointer + link, not a copy of the deal slice.
- Multi-deal / multi-partner calls fan the relevant slice to each channel.

Partner-channel resolution — **ask, don't guess**:
1. Partner card has `slack_channel` → use it.
2. Obvious, unambiguous `#partnership-<name>` → propose it.
3. Uncertain — e.g. the counterparty has no channel of its own but an ecosystem one may apply (Entropy → `#partnership-arbitrum`) — **ask in the `#bd-intake` thread** which channel, suggesting the best guess.
4. No channel and none requested → **skip** the partner post (the deal + `#bd-intake` posts still happen).
5. Human asks for a new channel → create it (confirm name + public/private first), post, and backfill the partner card's `slack_channel`. **Only on explicit instruction**, never autonomously.

## Rules
- **Reuse, don't re-specify.** Schema, resolution, gates, Linear, and roster live in `bd-pipeline`; the batch mechanics live in `bd-meeting-intake`. This skill adds only the trigger and the fan-out.
- **House meeting-log format:** `## <YYYY-MM-DD> BD sync`, appended to the card body — not a `## Meeting log` section.
- **Propose-then-confirm.** One proposal covering vault + Linear + the fan-out plan; apply nothing before confirmation. Verify before closing any Linear issue.
- **Dedupe channels.** If the resolved partner channel is the same as a deal channel already being posted to, post once.
- **Sensitive == Yes** → the full note stays in `#bd-intake` only; no fan-out to any deal or partner channel.
- **Language guardrails on anything published** (deal- / partner-channel text): design not management, assessment not underwriting, curated not managed, Series not fund, participants not investors.
- **Don't invent.** No field value, contact, figure, or Linear status the notes don't support — flag ambiguity in the proposal instead. Use exact schema field names.
- **Use the tools; never shell out.** `obsidian_vault` and `linear` authenticate at the tool layer (iron-proxy). If a tool isn't authenticated or loaded this session, say so and output the manual step — never fall back to sandbox `gh`, and never post a Slack slice to a channel Centaur isn't a member of (say so instead).
- **Confirm before anything external.** This flow is internal; a Required Action implying an external send is flagged, not executed.
