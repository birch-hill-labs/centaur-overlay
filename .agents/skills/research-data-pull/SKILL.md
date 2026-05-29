---
name: research-data-pull
description: |
  Pull DeFi / onchain / market / governance / news data from whichever public Centaur tool has it — DefiLlama, Dune, Etherscan, Coinmetrics, Messari, Token Terminal, Tally, Snapshot, and others. Use whenever a user asks for protocol TVL, lending rates, vault performance, stablecoin metrics, onchain balances, token prices, governance proposals, unlocks, or "fresh market data" of any kind. This skill is the data layer that feeds `research-to-deck` and any analytical conversation. Source-agnostic: pick whichever tool actually has the data the user needs, route accordingly, and combine when one source isn't enough.
---

# Research Data Pull (Centaur edition)

## What this skill does

Centaur has direct access to a stack of DeFi / market / onchain data tools. This skill teaches the agent which tool answers which kind of question and how to combine them when no single source has the full picture. Every data fetch goes through a Centaur tool that calls the upstream API directly through iron-proxy.

## Source map — pick the right tool by the question

| Question shape | First tool to try | Notes |
|---|---|---|
| Protocol TVL, historical TVL, fees, revenue, chain breakdown | `defillama` | Free endpoints cover most of this. `pro-api.llama.fi` endpoints (`pro=True` in the client) need `DEFILLAMA_API_KEY`. |
| Yield pools / DEX pool data / stablecoin market caps | `defillama` | Same tool, different endpoints — `pools_*`, `stablecoins_*`. |
| Morpho / Aave / Compound markets, lending rates, vault metrics | `defillama` (yields + protocol endpoints) or `dune` (custom queries) | DefiLlama has surface-level data; Dune lets you write SQL for anything else. |
| Custom SQL across onchain + protocol data | `dune` | Requires a Dune query ID (build one in dune.com, then call here). |
| Address balances, transactions, ERC-20 transfers, gas | `etherscan` | Free key works. |
| Block-level onchain data, low-level RPC | `alchemy` | When `etherscan` isn't enough or for non-Eth chains. |
| Token prices (free tier) | `coinmetrics` | Community tier no key. CoinGecko in Centaur is pro-only and we're not paying for it — skip. |
| Token narratives, project profiles, fundraising | `messari` | Profile + asset metrics + news. |
| Protocol financials, sectors, project quality | `token-terminal` | Needs `TOKEN_TERMINAL_API_KEY` (paid). |
| DAO governance, proposals, votes | `tally`, `snapshot`, `karma` | Tally onchain, Snapshot offchain. |
| Token unlocks / vesting / emissions | `tokenomist` | For supply-side analysis. |
| Stablecoin reserves, attestations | `defillama` stablecoins endpoints | Or web search if the issuer publishes elsewhere. |
| Crypto news | `coindesk`, `theblock`, `googlenews`, `newsapi` | All work without keys (newsapi excepted). |
| Web search for anything not above | `websearch` | Powered by Exa; needs `EXA_API_KEY`. |

If you don't know which tool, ask: "Is this data point published by a protocol publicly?" — if yes, try `defillama` first. "Custom join I can write SQL for?" — `dune`. "Address-level activity on a specific chain?" — `etherscan` / `alchemy`.

## Combining sources

A typical question crosses sources. Example: "How has Morpho's wstETH-collateral USDC lending tracked the broader stablecoin yield environment over the last 3 months?"

1. `defillama` → pull Morpho protocol yields for wstETH/USDC markets (via the `pools_yieldHistory` endpoint or similar)
2. Compute supply-weighted average per day inline (Python in Bash):
   ```python
   weighted_apy = sum(r["apy"] * r["tvlUsd"]) / sum(r["tvlUsd"])
   ```
3. `defillama` → pull stablecoin market cap timeseries as the macro backdrop (`stablecoins_charts`)
4. Hand the combined dataset to `research-to-deck` for chart generation, or summarize inline

## When to write a CSV vs return inline

- **Small data (< ~200 rows)** — keep it in agent memory, summarize inline, or pass directly to charts
- **Larger data or feeding `research-to-deck`** — write to `/tmp/<filename>.csv` in the sandbox (use Bash + pandas), then reference the path in the handoff. Don't try to inline 50,000 rows in a Slack message.

```bash
# example: write a fetched dataset to a CSV
python3 -c "
import pandas as pd
df = pd.DataFrame(rows)
df.to_csv('/tmp/wsteth_usdc_markets.csv', index=False)
print(f'wrote {len(df)} rows')
"
```

## Anti-patterns

- **Don't ask the user to run anything on their Mac.** Everything available in Centaur runs in the sandbox.
- **Don't pick the most "powerful" tool by default.** Prefer the cheapest source that has the data (free endpoints first). DefiLlama free covers ~80% of public DeFi questions.
- **Don't invent column names.** If you don't see a column documented for a tool, run a small probe (e.g., `defillama.get_protocol(slug="aave-v3", limit=1)`) to inspect what's actually there.
- **Don't paginate by hand** when the tool client has helpers — most do.

## What's NOT available here

- **Birch Hill's internal Supabase warehouse** — explicitly out of scope. If a question needs BH-proprietary cached data (the Sentora vault timeseries, internal Morpho snapshots, curation metadata), say so and route the user to the local research-service on Connor's Mac. Don't try to access BH-internal datasources from Centaur.

## Standard workflow

1. **Parse the question** — what data does the user actually need? Be specific about asset symbols, date ranges, metrics.
2. **Pick the source(s)** using the map above. If unsure, default to `defillama` for public DeFi.
3. **Query**. Use small initial calls (e.g., `limit=10`) to confirm shape before pulling big windows.
4. **Inline-compute** any aggregations (supply-weighted averages, day-over-day deltas, growth %s).
5. **Deliver**: summarize the answer in chat, or write a CSV + hand off to `research-to-deck` if the user wants a deck.
