"""Birch Hill Supabase warehouse tool.

Wraps Supabase's PostgREST API for read-only access to Birch Hill's
research-service data warehouse. Used as a data layer for the
`research-data-pull` skill and any other agent flow that needs Morpho
historical markets, vault timeseries, or curation snapshots that aren't
available in public sources like DefiLlama.

## Auth

Iron-proxy injects `BH_SUPABASE_ANON_KEY` into both the `Authorization`
(as `Bearer <key>`) and `apikey` headers on outbound requests to
`*.supabase.co`. The 1P credential field should be the raw anon key
(JWT). Supabase PostgREST requires both headers — `apikey` for project
auth and `Authorization` for role scoping.

## Config

`BH_SUPABASE_URL` env var must be set on the api pod via centaur-infra
`api.extraEnv` — e.g. `https://abcd1234.supabase.co`. Non-sensitive
(it's just the project hostname). Set there so the tool can build URLs
without round-tripping to 1P.

## Schemas

Birch Hill's warehouse uses Supabase's schema feature for organization.
Known schemas:

- `morpho_historical` — Morpho Blue markets and timeseries
- `curation` — vault metadata and curator info
- `public` — Supabase default; rarely used here

Each query takes a `schema` parameter; the tool sends it as the
`Accept-Profile` HTTP header so PostgREST routes to the right schema.

## Pagination

Supabase caps page size at 1000 rows. The `raw_query` method
auto-paginates if you ask for more, by chunking `Range` headers.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

import httpx


# Placeholder string — iron-proxy swaps this on the wire.
SECRET_PLACEHOLDER = "BH_SUPABASE_ANON_KEY"

# Page size cap from Supabase's PostgREST.
PAGE_SIZE = 1000

DEFAULT_TIMEOUT = 30.0


def _get_base_url() -> str:
    """Read the Supabase project URL from env at call time."""
    url = os.getenv("BH_SUPABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "BH_SUPABASE_URL not set on the api pod. Add it to "
            "centaur-infra api.extraEnv and re-apply bootstrap."
        )
    return url.rstrip("/")


def _client() -> "BHSupabaseClient":
    """Factory the centaur runtime calls to instantiate this tool."""
    return BHSupabaseClient()


class BHSupabaseClient:
    """PostgREST client for Birch Hill's Supabase warehouse."""

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self._http = httpx.Client(timeout=timeout)

    # ---- public methods (the agent calls these) ----

    def raw_query(
        self,
        table: str,
        *,
        schema: str = "public",
        filters: dict[str, str] | None = None,
        select: str | None = None,
        order: str | None = None,
        limit: int = PAGE_SIZE,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Run a PostgREST query against any table in any schema.

        Args:
            table: PostgREST table name, e.g. `hist_ethereum_markets`.
            schema: Supabase schema, e.g. `morpho_historical`. Default `public`.
            filters: Map of column → PostgREST filter expression. Examples:
                {"collateral_asset_symbol": "eq.wstETH"}
                {"timestamp": "gte.2024-01-01"}
                {"supply_assets_usd": "gt.10000000"}
            select: Comma-separated column list (PostgREST `select`). If None,
                returns all columns.
            order: PostgREST order expression, e.g. "timestamp.desc".
            limit: Max rows. Auto-paginates if > PAGE_SIZE (1000).
            offset: Starting row offset.

        Returns:
            List of row dicts.

        Examples:
            # All wstETH/USDC markets, latest first
            client.raw_query(
                "hist_ethereum_markets",
                schema="morpho_historical",
                filters={
                    "collateral_asset_symbol": "eq.wstETH",
                    "loan_asset_symbol": "eq.USDC",
                },
                order="supply_assets_usd.desc",
            )

            # Daily timeseries for one market in a date range
            client.raw_query(
                "hist_ethereum_market_timeseries",
                schema="morpho_historical",
                filters={
                    "unique_key": "eq.0xabc...",
                    "timestamp": "gte.2024-06-01",
                },
                order="timestamp.asc",
                limit=10000,
            )
        """
        params: dict[str, str] = {}
        if filters:
            params.update(filters)
        if select:
            params["select"] = select
        if order:
            params["order"] = order

        results: list[dict[str, Any]] = []
        remaining = limit
        page_offset = offset
        while remaining > 0:
            chunk_size = min(remaining, PAGE_SIZE)
            chunk = self._fetch_page(
                table=table,
                schema=schema,
                params=params,
                offset=page_offset,
                count=chunk_size,
            )
            results.extend(chunk)
            if len(chunk) < chunk_size:
                # Server returned a short page — no more rows.
                break
            page_offset += chunk_size
            remaining -= chunk_size
        return results

    def list_known_schemas(self) -> list[dict[str, str]]:
        """Return the documented Birch Hill schemas + their purpose.

        This is a static description (no API call). For runtime
        introspection of available schemas, see `raw_query` against the
        `pg_namespace` system table (advanced).
        """
        return [
            {
                "name": "morpho_historical",
                "description": (
                    "Morpho Blue markets and timeseries. Tables: "
                    "hist_ethereum_markets, hist_ethereum_market_timeseries, "
                    "hist_ethereum_vault_timeseries."
                ),
            },
            {
                "name": "curation",
                "description": (
                    "Vault metadata and curator info. Tables: "
                    "raw_morpho_vaults."
                ),
            },
            {
                "name": "public",
                "description": "Supabase default schema; rarely used at BH.",
            },
        ]

    # ---- internal ----

    def _fetch_page(
        self,
        *,
        table: str,
        schema: str,
        params: dict[str, str],
        offset: int,
        count: int,
    ) -> list[dict[str, Any]]:
        base = _get_base_url()
        url = f"{base}/rest/v1/{table}"
        if params:
            url = f"{url}?{urlencode(params, doseq=True, safe='.,')}"
        # Iron-proxy substitutes the placeholder on the wire.
        headers = {
            "apikey": SECRET_PLACEHOLDER,
            "Authorization": f"Bearer {SECRET_PLACEHOLDER}",
            "Accept-Profile": schema,
            "Accept": "application/json",
            "Range-Unit": "items",
            "Range": f"{offset}-{offset + count - 1}",
        }
        resp = self._http.get(url, headers=headers)
        if resp.status_code >= 400:
            raise RuntimeError(
                f"Supabase {resp.status_code}: {resp.text[:500]} "
                f"(table={table}, schema={schema})"
            )
        data = resp.json()
        if not isinstance(data, list):
            raise RuntimeError(
                f"Supabase returned non-list payload: {type(data).__name__}"
            )
        return data
