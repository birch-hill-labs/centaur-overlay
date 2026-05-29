---
name: research-to-deck
description: |
  Turn DeFi / market / onchain data (from `research-data-pull` or any other tool) into Birch Hill–stylized charts and assemble them into a branded PowerPoint deck. Use when the user asks to "build a deck from the data," "make charts and a presentation," "draft slides for a counterparty," or any request that produces a `.pptx` from analytical data. Always read `birch-hill-pptx` first — that skill owns slide layout, fonts, and template usage. This skill owns chart styling and the data → chart → slide assembly logic.
---

# Research to Deck (Centaur edition)

## Boundaries

| What this skill owns | What it doesn't |
|---|---|
| BH brand chart styling (colors, typography, layout) | Pulling source data — use `research-data-pull` first |
| Multi-line / area / bar / scatter chart conventions | Slide layouts, fonts, master template — that's `birch-hill-pptx` |
| The data → chart → slide assembly choreography | One-off doc formatting — that's `bh-design` |

Always read **`birch-hill-pptx`** before generating any deck. That skill defines template layouts and slide-level brand rules; this skill only governs what goes INSIDE the slide (charts and the data-to-chart mapping).

## Sandbox tooling

The Centaur agent sandbox has `python-pptx`, `openpyxl`, `python-docx`, `PyMuPDF`, `lxml`, `mammoth` preinstalled. `matplotlib` and `pandas` may or may not be on the image — try them first; if the import fails, fall back to the `chart` Centaur tool (limited brand control) or `pip install matplotlib pandas` inline (works if PyPI is reachable through iron-proxy).

There's no `/output/` filesystem convention from the local version. Write artifacts to `/tmp/<name>.png` (charts) and `/tmp/<name>.pptx` (decks), then upload the final deck to the Slack thread.

## BH brand chart palette

| Role | Hex | Use for |
|---|---|---|
| Primary | `#1B3D2F` | Primary data series, titles, axis labels |
| Secondary | `#2D5A3F` | Second data series, gridlines emphasis |
| Tertiary | `#C4963C` | Accent series, highlights, callout annotations |
| Light green | `#4A7A5E` | Third series |
| Muted sage | `#7A9B8A` | Fourth series, reference lines |
| Light fill | `#F5F5F0` | Confidence bands, subtle area fills |
| Background | `#FFFFFF` | Always white |

For 5+ series, cycle through `#1B3D2F → #2D5A3F → #C4963C → #4A7A5E → #7A9B8A`, then repeat with dashed line styles.

## Chart standards

- **Font** — Arial (matches deck body)
- **Title** — 11pt bold, color `#1B3D2F`
- **Axis labels** — 9pt regular, `#333333`
- **Tick labels** — 8pt regular, `#666666`
- **Legend** — 9pt, outside chart area (top-right or bottom)
- **DPI** — 200 minimum on save (`plt.savefig(..., dpi=200)`)
- **Figure size** — `10 × 5.5 in` for full-width slide charts, `6 × 5 in` for half-width
- **Line weight** — 2pt primary, 1.5pt secondary, 1pt reference
- **Grid** — Horizontal only, `#E0E0E0` alpha 0.5; no vertical
- **Axes** — Bottom + left spines only; remove top + right
- **Date formatting** — `%b %Y` (monthly), `%b %d` (≤ 90 days)
- **Y-axis** — Format `8.5%` not `0.085`; `$50M` not `50000000`
- **X-axis** — Always set explicit `set_xlim(start, end)` — never let matplotlib auto-extend

### Matplotlib helper (paste into the sandbox Bash)

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

BH = {
    "dark":  "#1B3D2F",
    "med":   "#2D5A3F",
    "gold":  "#C4963C",
    "light": "#4A7A5E",
    "sage":  "#7A9B8A",
    "fill":  "#F5F5F0",
}
BH_CYCLE = [BH["dark"], BH["med"], BH["gold"], BH["light"], BH["sage"]]

def bh_chart(figsize=(10, 5.5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("white"); fig.patch.set_facecolor("white")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#999999"); ax.spines["bottom"].set_color("#999999")
    ax.grid(axis="y", color="#E0E0E0", alpha=0.5, linewidth=0.5)
    ax.tick_params(colors="#666666", labelsize=8)
    return fig, ax

def pct_axis(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"{x:.1f}%")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)

def usd_axis(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)

def save_chart(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path
```

## Standard chart types

### 1. Ecosystem growth (dual-line, optional dual-axis)
**Use for:** lending TVL vs DEX liquidity, market cap vs holders, etc.
**Style:** Two lines (`BH["dark"]` for primary metric, `BH["gold"]` for secondary). Annotate the final value at the line's right end.

### 2. Supply APY across collateral types (multi-line)
**Use for:** comparing yield streams.
**Style:** One line per collateral, cycling `BH_CYCLE`. Optional shaded reference band for "stablecoin baseline" (`ax.axhspan(3.0, 5.0, color=BH["fill"], alpha=0.5)`).

### 3. Collateral TVL over time (multi-line)
**Use for:** showing growth across asset types.
**Style:** Multi-line over stacked area — easier to read individual trends. End-of-line annotations: `ax.annotate(f"${y/1e6:.0f}M", xy=(x_end, y_end), color=color, fontsize=8)`.

### 4. Historical + forecast with confidence band
**Use for:** projecting forward.
**Style:** Solid line historical, dashed line forecast median, shaded band for CI. Vertical dotted line at the boundary: `ax.axvline(boundary_date, color="#999999", linestyle=":")`.

### 5. Vault allocation (horizontal stacked bar)
**Use for:** showing current or target allocation across collateral types. Color by risk tier (AAA dark green → B sage).

### 6. Risk-return scatter
**Use for:** comparing strategies. X-axis = APY volatility, Y-axis = mean APY. Annotate each point with the strategy name.

## Data → slide mapping

| Slide intent | Recommended data shape | Chart type |
|---|---|---|
| Market overview | `(date, collateral, total_supply_usd)` | Multi-line or stacked area |
| Yield landscape | `(date, collateral, supply_apy, supply_assets_usd)` | Multi-line APY (supply-weighted) |
| Collateral growth | `(collateral, current_usd, ytd_growth_pct)` | Bar or summary table |
| Vault performance | `(date, total_assets_usd, net_apy)` | Dual-axis line |
| Strategy backtest | `(date, blended_apy)` | Single line |
| Forward projection | `(date, median_apy, lower_ci, upper_ci)` | Line + confidence band |
| Risk analysis | `(risk_tier, avg_apy, concentration_pct)` | Grouped bar |
| Ecosystem context | Protocol-level TVL / volume | Dual-line |

## Supply-weighted averaging

When showing "average APY" across multiple markets, always supply-weight:

```python
df["weighted"] = df["supply_apy"] * df["supply_assets_usd"]
grouped = (
    df.groupby(["date", "collateral_asset_symbol"])
      .agg(total_supply=("supply_assets_usd", "sum"),
           weighted_sum=("weighted", "sum"))
      .reset_index()
)
grouped["supply_weighted_apy"] = grouped["weighted_sum"] / grouped["total_supply"]
```

Always footnote: "APYs are supply-weighted averages across all stablecoin loan markets on Morpho Blue."

## Standard workflow

1. **Read `birch-hill-pptx`** — template structure, layouts, fonts, brand rules
2. **Pull data** via `research-data-pull` (or accept user-uploaded CSVs)
3. **Validate** — null check, date-range check, column-name check
4. **Generate chart images** in `/tmp/charts/` at 200 DPI using the helper above
5. **Build the deck** using `python-pptx` per `birch-hill-pptx` layouts. Standard slide order: Cover → Exec Summary → Market Overview → Yield Landscape → Collateral Analysis → Strategy Detail → Backtest → Forward Projection → Risk Analysis → Appendix
6. **Embed chart images** at the right slide positions
7. **QA pass**:
   - Every chart ends at the requested date (no auto-extension)
   - Colors match the palette hex exactly
   - Fonts are 11pt/9pt/8pt as specified
   - No chart is blurry (DPI check)
   - Slide numbers / footers present
   - Numbers in slide text match the chart data
8. **Save** the `.pptx` to `/tmp/` and upload to the Slack thread

## Anti-patterns

- **Don't use named matplotlib colors** (e.g., `'green'`, `'red'`) — copy hex from the palette above.
- **Don't manually type numbers into slide text boxes** — pull them from the same DataFrame that generated the chart.
- **Don't skip the QA pass** — wrong numbers on a counterparty deck damage the relationship more than slow delivery.
- **Don't ask the user to run anything locally** — everything runs in the sandbox now.
