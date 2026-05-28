---
name: research-data-pull
description: |
  Pull DeFi / onchain / market data from whichever source has it — DefiLlama, Dune, Etherscan, Coinmetrics/Messari, or Birch Hill's own Supabase warehouse via `bh_supabase`. Use whenever a user asks for protocol TVL, lending rates, vault performance, stablecoin metrics, onchain balances, Morpho market data, or "fresh market data" of any kind. This skill is the data layer that feeds `research-to-deck` and any analytical conversation. Source-agnostic: pick whichever tool actually has the data the user needs, route accordingly, and combine when one source isn't enough.
---

# Research Data Pull (Centaur edition)

## What this skill does

Centaur has direct access to a stack of DeFi / market / onchain data tools. This skill teaches the agent which tool answers which kind of question and how to combine them when no single source has the full picture. There's no local research-service to run — every data fetch goes through a Centaur tool that calls the upstream API directly through iron-proxy.

## Source map — pick the right tool by the question

| Question shape | First tool to try | Notes |
|---|---|---|
| Protocol TVL, historical TVL, fees, revenue, chain breakdown | `defillama` | Free endpoints cover most of this. `pro-api.llama.fi` endpoints (`pro=True` in the client) need `DEFILLAMA_API_KEY`. |
| Yield pools / DEX pool data / stablecoin market caps | `defillama` | Same tool, different endpoints — `pools_*`, `stablecoins_*`. |
| Custom SQL across onchain + protocol data | `dune` | Requires a Dune query ID (build one in dune.com, then call here). |
| Address balances, transactions, ERC-20 transfers, gas | `etherscan` | Free key works. |
| Block-level onchain data, low-level RPC | `alchemy` | When `etherscan` isn't enough or for non-Eth chains. |
| Token prices (free tier) | `coinmetrics` | Community tier no key. CoinGecko in Centaur is pro-only and we're not paying for it — skip. |
| Token narratives, project profiles, fundraising | `messari` | Profile + asset metrics + news. |
| Protocol financials, sectors, project quality | `token-terminal` | Needs `TOKEN_TERMINAL_API_KEY` (paid). |
| DAO governance, proposals, votes | `tally`, `snapshot`, `karma` | Tally onchain, Snapshot offchain. |
| Token unlocks / vesting / emissions | `tokenomist` | For supply-side analysis. |
| Crypto news | `coindesk`, `theblock`, `googlenews`, `newsapi` | All work without keys (newsapi excepted). |
| **Morpho historical markets, BH's Sentora vault timeseries, curated vault metadata** | `bh_supabase` | This is Birch Hill's proprietary research warehouse. Not in any public tool. |
| Stablecoin reserves, attestations | `defillama` stablecoins endpoints | Or web search if the issuer publishes elsewhere. |
| Web search for anything not above | `websearch` | Powered by Exa; needs `EXA_API_KEY`. |

If you don't know which tool, ask: "Is this data point published by a protocol publicly?" — if yes, try `defillama` first. "Is it Birch Hill-private?" — use `bh_supabase`. "Custom join I can write SQL for?" — `dune`.

## Using `bh_supabase` (the Birch Hill warehouse)

The single method `bh_supabase.raw_query(table, schema, filters, ...)` is a thin wrapper over Supabase's PostgREST API. It returns a list of JSON dicts. Filter values use PostgREST operators: `eq.`, `gt.`, `gte.`, `lt.`, `lte.`, `in.(a,b,c)`, etc.

### Schemas + key tables

**`morpho_historical`** — Morpho Blue protocol data:
- `hist_ethereum_markets` — All markets (latest state). Columns: `unique_key`, `collateral_asset_symbol`, `loan_asset_symbol`, `supply_assets_usd`, `borrow_assets_usd`, `supply_apy`, `borrow_apy`, `utilization`, `lltv`, `oracle_price_usd`
- `hist_ethereum_market_timeseries` — Daily per-market snapshots. Same columns + `timestamp`
- `hist_ethereum_vault_timeseries` — Daily per-vault data. Columns: `vault_address`, `timestamp`, `total_assets_usd`, `net_apy`, `curators`

**`curation`** — Vault metadata:
- `raw_morpho_vaults` — Columns: `vault_address`, `name`, `curator`, `total_assets_usd`, `net_apy`, `asset_symbol`

### Example queries

All wstETH/USDC Morpho markets, biggest first:
```python
bh_supabase.raw_query(
    "hist_ethereum_markets",
    schema="morpho_historical",
    filters={
        "collateral_asset_symbol": "eq.wstETH",
        "loan_asset_symbol": "eq.USDC",
    },
    order="supply_assets_usd.desc",
)
```

Daily timeseries for one market over a date range:
```python
bh_supabase.raw_query(
    "hist_ethereum_market_timeseries",
    schema="morpho_historical",
    filters={
        "unique_key": "eq.0xabc...",
        "timestamp": "gte.2024-06-01",
        "timestamp": "lte.2025-03-01",  # note: pass these as a list if PostgREST rejects dup keys
    },
    order="timestamp.asc",
    limit=10000,  # auto-paginates past the 1000-row Supabase cap
)
```

Vault metadata by curator:
```python
bh_supabase.raw_query(
    "raw_morpho_vaults",
    schema="curation",
    filters={"curator": "ilike.*Sentora*"},
)
```

## Combining sources

A typical question crosses sources. Example: "What's the supply-weighted average APY across all wstETH-collateral USDC markets on Morpho, and how has it tracked the broader stablecoin yield environment?"

1. `bh_supabase` → pull `hist_ethereum_market_timeseries` for all wstETH/USDC markets in the date range
2. Compute supply-weighted average per day inline (Python in Bash):
   ```python
   weighted_apy = sum(r["supply_apy"] * r["supply_assets_usd"]) / sum(r["supply_assets_usd"])
   ```
3. `defillama` → pull stablecoin market cap timeseries as the macro backdrop
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

- **Don't ask the user to run anything on their Mac.** This used to be the fallback when the local research-service was the only path; now `bh_supabase` removes that need.
- **Don't pick the most "powerful" tool by default.** Prefer the cheapest source that has the data (free endpoints first). DefiLlama free covers ~80% of public DeFi questions.
- **Don't paginate by hand.** `bh_supabase.raw_query(limit=10000)` handles chunking. Same for `defillama` — its client has helpers.
- **Don't invent column names.** If you don't see a column in the schemas above, run a no-filter `raw_query` with `limit=1` to inspect what's actually there.
- **Don't expose anon-key or BH-internal URLs to the user.** They're transparently injected by iron-proxy.

## Standard workflow

1. **Parse the question** — what data does the user actually need? Be specific about asset symbols, date ranges, metrics.
2. **Pick the source(s)** using the map above. If unsure, default to `defillama` for public DeFi and `bh_supabase` for Morpho-specific.
3. **Query**. Use small initial calls (e.g., `limit=10`) to confirm shape before pulling big windows.
4. **Inline-compute** any aggregations (supply-weighted averages, day-over-day deltas, growth %s).
5. **Deliver**: summarize the answer in chat, or write a CSV + hand off to `research-to-deck` if the user wants a deck.
