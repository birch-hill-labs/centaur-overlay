# centaur-acme

Example organization overlay for Centaur.

This repository is intentionally small, forkable, and free of private data. It
shows the extension points an organization normally customizes:

- `tools/` for API-discovered tools
- `workflows/` for durable workflows
- `.agents/skills/` for sandbox-loaded skills
- `services/sandbox/SYSTEM_PROMPT.md` for organization-specific agent guidance

## Build the overlay image

```bash
docker build -t ghcr.io/acme-corp/centaur-acme:local .
```

The image copies this repository to `/overlay`. Centaur's Helm chart mounts that
path at `/app/overlay/org` in the API and `/home/agent/overlay/org` in sandbox
pods.

## Use with Helm

```yaml
overlay:
  image:
    repository: ghcr.io/acme-corp/centaur-acme
    tag: sha-0000000
    pullPolicy: IfNotPresent
    sourcePath: /overlay
```

## Included examples

`tools/acme_crm` is a toy CRM tool with no external credentials. It gives agents
something organization-specific to discover and call.

`workflows/daily_acme_brief.py` is a minimal recurring workflow that asks an
agent for a daily operating summary.

`.agents/skills/acme-support/SKILL.md` is a sandbox skill that demonstrates how
ACME-specific playbooks are packaged.

`services/sandbox/SYSTEM_PROMPT.md` is appended to the base sandbox prompt when
the overlay is mounted.

## Verify in a running deployment

From the API pod:

```bash
echo "$TOOL_DIRS"
echo "$WORKFLOW_DIRS"
ls -la /app/overlay/org
```

From a sandbox:

```bash
echo "$CENTAUR_OVERLAY_DIR"
ls "$CENTAUR_OVERLAY_DIR"
ls "$CENTAUR_OVERLAY_DIR/.agents/skills"
```
