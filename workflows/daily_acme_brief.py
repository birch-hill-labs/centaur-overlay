from datetime import timedelta

WORKFLOW_NAME = "daily_acme_brief"
CRON = "0 14 * * 1-5"
SLACK_CHANNEL = "acme-centaur-updates"
PROMPT = (
    "Use the ACME example overlay. Summarize sample account health, open risks, "
    "and one recommended next action. Be explicit that this is sample data."
)


async def handler(inp, ctx):
    summary = await ctx.call_tool("acme_crm", "health", {})
    result = await ctx.agent_turn(f"Write the daily ACME sample brief from this data: {summary}")
    await ctx.post_to_slack(SLACK_CHANNEL, result["result_text"])
    await ctx.sleep("cooldown", timedelta(seconds=1))
    return result
