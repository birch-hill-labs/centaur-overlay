---
name: bd-call-note
description: |
  Turn a structured BD call-intake post into durable vault records and routed Slack
  notes. Triggers automatically on any message posted by the BD Call Intake workflow
  bot (B0BM1J5JBEG) in #bd-intake (C0BLZP3D9K3) — no mention or tag required. The skill
  resolves the counterparty and the associated deal(s), appends a deal-specific entry to
  each affected deal card's `## Meeting log`, bumps `last_contact` / `next_action`, posts
  the full note in #bd-intake, a per-deal slice into each `#deal-*` channel, and a
  relationship pointer into the counterparty's `#partnership-*` channel, and proposes one
  Linear task per required action. Every vault, Slack, and Linear write is
  proposed for human confirmation first; the vault lands as a PR a human merges. Use this
  skill whenever a new call-intake post appears, or when Connor/Traver says "process the
  call note," "log this call," or points at a #bd-intake post. Do NOT use for internal
  session recaps (that is `daily-note`) or for document generation (that is `bh-design`).
---

# BD Call Note — Intake → Vault + Slack + Linear

## What this skill does

Converts a single BD call-intake post into three synchronized outputs, from one input:

1. **Obsidian** — a deal-specific entry appended to each associated deal card's `## Meeting log`, plus refreshed `last_contact` / `next_action` frontmatter. Lands as a PR a human merges. The Master CRM then auto-refreshes off the vault.
2. **Slack** — the full canonical note in `#bd-intake`; a high-level slice (points + action items + link back) in each associated `#deal-*` channel; a relationship pointer in the counterparty's `#partnership-*` channel.
3. **Linear** — one proposed task per required action, labeled `BD Pipeline`, carrying a `Source:` line to the deal card.

**The point is not to re-post the call.** It is to land the *decisions*, *next actions*, and *deal-state changes* where the deal team, the vault, and the CRM will all see them — correctly attributed when a call touches more than one deal.

## When to trigger

**Automatic:** any new message from the **BD Call Intake workflow bot** (bot ID `B0BM1J5JBEG`) in **`#bd-intake`** (`C0BLZP3D9K3`). Do not require a `@Centaur` mention or a `[bd-call-note]` tag — the bot's post is the trigger.

**Explicit:** "process the call note," "log this call," or a human pointing at a specific `#bd-intake` post.

**Do not** trigger on human chatter in `#bd-intake` — only on the workflow bot's structured posts (or an explicit human instruction referencing one).

## Input schema — the intake post fields

Parse these labels from the workflow bot's message (they mirror the `/callnote` form):

| Field | Meaning |
|---|---|
| **Counterparty (Organization/Entity)** | the external org(s) on the call |
| **Associated Deals** | the BH deal workstream(s) this call advances — may differ from Counterparty, may be several |
| **Call Date** | ISO date |
| **BH attendees** / **External attendees** | attendee lists |
| **Summary / notes** | the body; may be typed notes or a pasted transcript |
| **Required Actions** | next actions (may name owners) |
| **Deal Stage** | Sourced / Qualifying / Diligence / Legal & Docs, or a stage change |
| **Relevant Links** | Drive / DocSend artifacts |
| **Sensitive?** | No / Yes — gates Slack fan-out |

## Entity resolution — counterparty ≠ deal (read this carefully)

Deals are multi-faceted: the **counterparty** (who was on the call) is frequently **not** the same as the **deal** (the workstream it advances), one counterparty can map to **several** deals, and one call can touch **several** deals. The skill must delineate this and decide where each piece of content belongs.

**Resolution steps:**

1. **Parse both fields independently.** `Counterparty` and `Associated Deals` are separate lists (comma- or newline-separated). Never assume they're the same entity.
2. **Resolve each Associated Deal** to a card in `knowledge/graph/deals/*.md` (match on filename or the `counterparty` / `deal_id` frontmatter; fuzzy-match names). The meeting-log entry is written to the **deal card(s)**, not the counterparty.
3. **Resolve the Counterparty** to a `knowledge/graph/partners/*.md` (or `deals/*.md`) card if one exists. If the counterparty is purely an external party with no card and no deal of its own, name it in the entry but don't create a card unless it clearly warrants one — flag that as a proposal. The counterparty also drives the `#partnership-*` Slack post — see Slack routing for how to resolve that channel (ask when uncertain).
4. **Handle the cases explicitly:**
   - **Counterparty == deal** (e.g., Fulcrum call about Fulcrum): one deal card.
   - **Counterparty ≠ deal, one deal** (e.g., Entropy call about Fulcrum): entry on the Fulcrum card; Entropy named as external party; optionally propose/update an Entropy partner card.
   - **One counterparty, multiple deals:** write a **tailored** entry to *each* associated deal card, containing only that deal's relevant content, and fan a matching slice to each deal channel.
   - **Multiple counterparties:** resolve each; attribute content per counterparty where separable.
   - **Net-new (no card matches):** do **not** guess. Propose a new card from `templates/deal-template.md` and ask for confirmation.
5. **Split the summary by deal.** For multi-deal calls, decide which points, decisions, and actions belong to which deal and split accordingly. **If content can't be cleanly attributed, ask in-thread rather than mis-filing it.**

## Language guardrails — run before any write or post

Birch Hill is pre-registration; word choice in anything that leaves a private working note is a compliance surface. Before drafting the `#bd-intake` note, the deal-channel slices, or the card text, apply the firm substitutions:

| Do not say | Say instead |
|---|---|
| management | design |
| underwriting | assessment |
| managed strategies | curated strategies |
| fund | Series |
| investors | participants |

Raw internal notes may contain the left-column terms; the *published* outputs must use the right column. Flag anything ambiguous rather than silently rewording a substantive claim.

## Outputs — propose all, execute on confirmation

### 1. Vault (PR — never merge yourself)

For **each** associated deal card:

- Append a `## Meeting log` entry (format below), newest first.
- Bump `last_contact` to the call date, set `next_action` from the Required Actions, bump `updated`.
- If a `linear_project` is missing and a project exists, note it (don't invent one).

Open **one PR** covering all affected cards via `obsidian_vault.propose_files`. Summarize the diff in-thread. Do not merge. The Master CRM / BD Sheet refresh off the vault on the next sync once the PR merges — do not separately write the Sheet from this skill.

**Meeting-log entry format:**

```markdown
### {call_date} — {counterparty}: {short topic} (call)
- **Counterparty:** {counterparty} · **Deal:** {deal_id}
- **Attendees:** BH: {bh_attendees} · Ext: {external_attendees}
- **Summary:** {2–4 sentences, this deal's slice, guardrail-clean}
- **Decisions:** {bullets, or "none recorded"}
- **Next actions:** {action — owner — due} {[BIR-###] once created}
- **Artifacts:** {links, or "none"}
- **Source:** [#bd-intake]({slack_permalink})
```

### 2. Slack

Post via the **`slack` tool** (`send_message`; resolve a channel name → ID with `list_channels` when the card only carries a `#name`). Post to up to three surfaces, propose-then-confirm:

- **`#bd-intake`** — the **full** canonical note (all deals, cleaned and guardrail-checked). System of record for the call.
- **Each associated deal → its `#deal-*` channel** — that deal's **slice**: high-level points + action items + a link back to the `#bd-intake` post. Resolve from the deal card's `slack_channel` field; else a `#deal-<name>` name match; else `#team-bd`.
- **The counterparty → its `#partnership-*` channel** — a **relationship-level pointer** (short summary + link back), not a duplicate of the deal slice. Resolution per the rule below.
- **Dedupe:** if the resolved partner channel is the same as, or redundant with, a deal channel already being posted to, post once.
- **Sensitive == Yes** — keep the full note in `#bd-intake` only; do **not** fan out to any deal or partner channel.
- **Never fake a post.** If `send_message` fails, or the target channel can't be resolved / doesn't exist, say so in-thread and flag it (rule 4) — never report a post that didn't land as done.

**Channel resolution — ask, don't guess; flag, don't create:**

1. If the deal/partner card carries a `slack_channel` field, use it.
2. Else, if a `#deal-<name>` / `#partnership-<name>` match is obvious and unambiguous, propose it.
3. **If resolution is uncertain** — e.g. the counterparty has no direct channel but an ecosystem channel may apply (Entropy → `#partnership-arbitrum`) — **ask in the `#bd-intake` thread which channel to use**, suggesting the best guess. Do not guess silently and do not skip silently.
4. **If no channel resolves, do not skip silently and do not create one.** Name the channel you'd expect (e.g. `#partnership-groma`), state that it's missing, and ask a human to create it (public) and invite Centaur. Then continue with every post that *can* land (`#bd-intake` + any resolved deal channels). Once the channel exists, back-fill the card's `slack_channel`.
5. **Centaur does not create Slack channels.** The `slack` tool is post-only by design; channel creation is a deliberate manual human step. Never spin one up, and never treat a missing channel as a silent skip — always flag it per rule 4.

### 3. Linear (propose, then write on confirmation)

- One issue per Required Action (owner + due where given), workstream label `BD Pipeline`, and a `Source:` line pointing at the deal card. Back-fill the `[BIR-###]` into the card's meeting-log entry after creation.
- Never write silently. If the Linear tool isn't loaded this session, output the manual steps instead (see Graceful degradation).

## Graceful degradation

Centaur's Slack deployment intermittently lacks the GitHub, Linear, Slack-post, or Drive tools. If a required tool is missing:

- **Say so explicitly** and complete every step you *can*.
- Output the exact **manual step** for the missing piece (e.g., "Linear tool not loaded — create: *Follow up w/ Matt/Sam re: RWA funding likelihood*, assignee Traver, label BD Pipeline, Source: knowledge/graph/deals/Fulcrum.md"; or "`slack` tool not loaded — post this slice to #deal-fulcrum manually").
- Never fail silently or pretend a write/post happened.

## Governance / anti-patterns

- **Never merge the vault PR.** A human merges.
- **Never contact the counterparty externally.** This flow is internal only. If a Required Action implies an external send, flag it — don't do it.
- **Propose-then-confirm** every vault PR, Slack post, and Linear write the human hasn't already explicitly directed.
- **Don't mis-file multi-deal content.** When unsure which deal a point belongs to, ask.
- **Don't create net-new cards silently.** Propose from the template.
- **Never create Slack channels.** If the right channel doesn't exist, flag it for a human to create (public) and invite Centaur; never spin one up and never silently skip.
- **Don't post raw guardrail-violating text** to any channel or card.
- **Use the tools; never shell out.** `obsidian_vault`, `linear`, and `slack` authenticate at the tool layer (iron-proxy); the credentials do not exist in the sandbox. Never reimplement their APIs in the sandbox.

## Workflow — start to finish

1. **Detect** a new workflow-bot post in `#bd-intake` (or an explicit instruction).
2. **Parse** the fields into the schema.
3. **Resolve** counterparty(ies) and associated deal(s) per the rules above; glob `knowledge/graph/deals/` and `partners/` to match. Ask if ambiguous.
4. **Guardrail-check** all text destined for a write or post.
5. **Draft** the per-card meeting-log entries, the `#bd-intake` full note, the per-deal slices, the partner pointer, and the proposed Linear tasks. Resolve every target channel; flag any that are missing.
6. **Propose** everything in-thread — grouped by deal, including the fan-out plan (which channel gets what, and any missing-channel flags) — and wait for confirmation.
7. **Execute** on confirm: open the vault PR (`obsidian_vault.propose_files`), post to Slack (`slack.send_message`), write Linear. Back-fill BIR-### into the entries.
8. **Report** the PR link, the Slack permalinks, and the Linear issues. Note the Master CRM will refresh on next sync once the PR merges.

## Reference

- **Deal card contract:** `templates/deal-template.md` (carries `## Meeting log`, `last_contact`, `next_action`, `slack_channel`).
- **Intake channel:** `#bd-intake` = `C0BLZP3D9K3`; **workflow bot** = `B0BM1J5JBEG`; **Centaur** = `U0B5JQCKZ2P`.
- **Tools:** `obsidian_vault` (vault read + `propose_files`), `linear` (issues), `slack` (`send_message` / `list_channels` — post-only, no channel creation).
- **Vault ↔ Linear contract:** every issue carries a `Source:` line; every deal card carries `linear_project`. See the vault `README.md`.
