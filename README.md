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
  obsidian_vault/        Read birch-hill-labs/obsidian-vault via GitHub API
services/sandbox/
  SYSTEM_PROMPT.md       Birch Hill agent voice + posture
```

## Tools

### `obsidian_vault`

Read-only access to Birch Hill's institutional knowledge in the private
[`birch-hill-labs/obsidian-vault`](https://github.com/birch-hill-labs/obsidian-vault)
repo. Iron-proxy injects `GITHUB_VAULT_TOKEN` (a GitHub PAT scoped to that
repo with `contents:read`) on outbound requests to `api.github.com`.

Methods: `read`, `list_dir`, `search`, `tree`.

Required 1Password vault item: `GITHUB_VAULT_TOKEN` (CONCEALED field named
`credential`) in the `Birch Hill Centaur Vault`.

## Phase plan

- **v1 (this commit):** Read-only `obsidian_vault` tool + `birch-hill-vault`
  skill + BH-specific system prompt. Uniform vault access for all Slack
  users.
- **Phase 2:** Port Connor's per-seat Claude Code skills into
  `.agents/skills/` so the team shares them via Slack.
- **Phase 3:** Postgres-backed RBAC table consulted before each
  `obsidian_vault.read` call. Only Connor can mutate roles.
- **Phase 4:** `/onboard` Slack slash command + onboarding persona + skill.
- **Phase 5:** Per-user token-usage tracking middleware so we can
  chargeback / throttle Slack users.

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
