# Birch Hill Centaur Overlay

Birch Hill Holdings' Centaur organization overlay. Forked from
[paradigmxyz/centaur-acme](https://github.com/paradigmxyz/centaur-acme).

Carries Birch Hill–specific tools, skills, system prompt, and (eventually)
workflows that the base [Centaur](https://github.com/paradigmxyz/centaur)
deployment mounts at runtime.

## Layout

```
.agents/skills/
  birch-hill-vault/      When + how to use the obsidian_vault tool
tools/
  obsidian_vault/        Read + propose-via-PR access to birch-hill-labs/obsidian-vault
services/sandbox/
  SYSTEM_PROMPT.md       Birch Hill agent voice + posture
```

## Tools

### `obsidian_vault`

Two-way access to Birch Hill's institutional knowledge in the private
[`birch-hill-labs/obsidian-vault`](https://github.com/birch-hill-labs/obsidian-vault)
repo via the GitHub REST API.

**Reads** are immediate:
`read`, `list_dir`, `search`, `tree`.

**Writes** open a pull request against `main`. Centaur never pushes to `main`
directly. The skill enforces a draft-in-Slack → confirm → PR flow so users
review the change before it becomes a PR:
`propose_create`, `propose_edit`, `propose_append`, `propose_delete`, `list_proposals`.

Branch protection on `main` (configure on GitHub) is the actual gate for
what lands in the vault.

#### Required out-of-band setup

1. **1Password vault item** `GITHUB_VAULT_TOKEN` (CONCEALED field `credential`)
   in `Birch Hill Centaur Vault`. Value: `Bearer <ghp_...>` where the token
   is a fine-grained PAT scoped to `birch-hill-labs/obsidian-vault` with:
   - Contents: **Read and write**
   - Pull requests: **Read and write**
   - Metadata: **Read**
2. **Branch protection on `main`** in the vault repo: require at least 1
   reviewer, block direct pushes. (Settings → Branches → Branch protection rules.)

## Phase plan

- **v1 (this commit):** Read + propose-via-PR `obsidian_vault` tool, the
  `birch-hill-vault` skill enforcing draft → confirm → PR, BH-specific
  system prompt. No user-role enforcement at the tool layer; anyone who
  can @mention Centaur can read everything and propose changes to anywhere.
- **Phase 2:** Port Connor's per-seat Claude Code skills into
  `.agents/skills/` so the team shares them via Slack.
- **Phase 3 — vault RBAC:** Postgres-backed `user_roles` table. Each role
  has `allowed_path_prefixes`. `read` / `list_dir` / `search` / `tree`
  filter to allowed prefixes for the calling Slack user; `propose_*` rejects
  changes outside their allowed prefixes. Only admin role can mutate roles
  (Connor's Slack ID hardcoded as bootstrap admin).
- **Phase 4:** `/onboard` Slack slash command + onboarding persona + skill.
- **Phase 5:** Per-user token-usage tracking middleware (chargeback / throttle).

See the parent [centaur-infra](https://github.com/birch-hill-labs/centaur-infra)
fork for cluster + image-tag wiring.

## Build

```bash
docker buildx build --platform linux/amd64 \
  -t ghcr.io/birch-hill-labs/centaur-overlay:sha-$(git rev-parse --short HEAD) \
  --push .
```

The image only needs to contain the contents of this repo; the chart copies
`/overlay/.` into the API and sandbox pods.
