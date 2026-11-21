# Dashboards and Data Visualization

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module defines decision-driven dashboard architecture, KPI modeling, the complete 25-type chart selection & accessibility matrix, renderer scaling (`SVG -> Canvas2D -> WebGL`), statistical honesty, perceptual CVD-safe color engineering, real-time telemetry handling, and Radical Simplicity ("Least Code, Highest Craft").

---

## 1. Decision Framework

### 1.1 Complete 25-Type Chart Selection, Renderer & Accessibility Matrix

Select chart geometry strictly by the analytical question (`task abstraction`), never visual novelty. Render via `SVG` (`< 1,000` marks), `Canvas2D + LTTB/downsampling` (`1,000-10,000` marks), or `WebGL/deck.gl` (`> 10,000` marks or geospatial GPU layers). Every chart with Grade `B` or lower MUST ship with a reachable HTML `<table>` / keyboard stepper fallback:

| # | Analytical Job | Best / Fallback Chart | Default Renderer Threshold | A11y Grade & Mandatory Fallback |
|---|---|---|---|---|
| 1 | **Trend Over Time** | Line / Area (`<= 6` series) or Small Multiples | `< 1,000` pts SVG; `>= 1,000` Canvas2D | `AA`: Direct end labels + arrow-key point stepper + table |
| 2 | **Categorical Compare** | Horizontal or Vertical Bar (`<= 12` bars) | SVG (`zero` baseline mandatory) | `AAA`: Sortable `<table>` + value labels (`tabular-nums`) |
| 3 | **Part-to-Whole** | Stacked Bar (`<= 5` segments) / Donut (`<= 4` slices) | SVG | `B/C`: Never 3D; pair Donut with sorted percentage table |
| 4 | **Correlation** | Scatter Plot (`x, y`) + trend CI | `< 2,000` pts SVG; `>= 2,000` Canvas2D | `B`: Shape/color redundancy + cluster summary table |
| 5 | **Matrix / Density** | 2D Heatmap | `< 1,500` cells SVG; `>= 1,500` Canvas2D | `B`: Sequential CVD-safe ramp + cell hover/focus readout + CSV |
| 6 | **Geospatial** | Choropleth / Proportional Symbol Map | GeoJSON SVG; `> 5,000` features WebGL | `C`: Ranked region `<table>` mandatory alongside map |
| 7 | **Stage Conversion** | Funnel / Horizontal Step Bar | SVG | `AA`: Explicit step count, drop-off `%`, and conversion table |
| 8 | **Target Progress** | Bullet Chart (value + target + ranges) | SVG | `AAA`: `aria-valuenow` / text ratio + target variance chip |
| 9 | **Forecast & Range** | Line + `15%` Confidence Band (solid vs dashed) | SVG / Canvas2D | `AA`: Disclose CI level (`95%`) + numeric bounds in tooltip/table |
| 10 | **Anomaly Detection** | Line + Threshold Band + Marker Callouts | SVG / Canvas2D | `AA`: Distinct marker shape (`diamond`/`ring`) + alert list |
| 11 | **Hierarchy** | Indented Tree Table / Treemap | SVG (`treemap` interactive) | `C`: Mandatory collapsible tree `<table>` for keyboard/SR |
| 12 | **Flow / Attribution** | Sankey / Alluvial Diagram | SVG | `C/D`: Source-target flow `<table>` mandatory (Sankey unreadable to SR) |
| 13 | **Cumulative Delta** | Waterfall Chart | SVG | `B`: Color + `+`/`-` symbol + cumulative ledger table |
| 14 | **Multi-Variable Profile** | Parallel Coordinates / Grouped Small Multiples | SVG / Canvas2D | `C`: Prefer Small Multiples (`AA`); avoid Radar (`> 5` axes) |
| 15 | **Financial OHLC** | Candlestick / OHLC Bar | Canvas2D (`>= 200` candles) | `B`: High/Low/Open/Close numeric table & keyboard scrub |
| 16 | **Network / Topology** | Force-Directed Graph / Adjacency Matrix | `< 300` nodes SVG; `>= 300` WebGL | `D`: Adjacency list / node-edge `<table>` mandatory |
| 17 | **Statistical Distribution** | Histogram / Box-Plot / Violin | SVG | `AA`: Always pair summary mean with `n`, median, IQR, outliers |
| 18 | **Goal Gauge (Single)** | Bullet or Linear Progress (`0-100%`) | SVG | `AAA`: Prefer Bullet over radial speedometer to save vertical space |
| 19 | **Proportional Count** | Waffle Grid (`10x10` = `1%` cells) | SVG (`crispEdges`) | `AA`: Direct percentage headline + exact numerator/denominator |
| 20 | **Nested Part-to-Whole** | Icicle Chart / Sunburst | SVG | `C/D`: Prefer Icicle or indented bar + mandatory hierarchy `<table>` |
| 21 | **Root-Cause Decomposition** | Decomposition Tree / Ranked Contribution Bar | SVG | `AA`: Expandable keyboard tree nodes with `%` contribution |
| 22 | **3D Spatial Telemetry** | 3D Point Cloud / Surface (ONLY when Z is physical) | WebGL (`deck.gl` / Three.js) | `D`: Banned for business KPIs; provide 2D slices + CSV export |
| 23 | **Real-Time Stream (`>= 1Hz`)** | Rolling Ring-Buffer Line + Status Chip | Canvas2D + LTTB (`<= 60 fps`) | `B`: Pause/Resume toggle + `prefers-reduced-motion` freeze + CSV |
| 24 | **Sentiment / Likert** | Diverging Stacked Bar (centered on Neutral) | SVG | `AA`: CVD-safe diverging ramp + exact `%` positive/neutral/negative |
| 25 | **Process Mining** | Directed Stage DAG + Bottleneck Wait Table | SVG | `C`: Mandatory bottleneck path `<table>` with median/p95 duration |

### 1.2 KPI Card & Decision Model Limits

| Dashboard Mode | Cadence | Primary KPI Cap | Driver & Guardrail Cap | Layout Rhythm |
|---|---|---|---|---|
| **Monitoring (Ops / NOC)** | Real-time (`5s-60s`) | `1-3` headline KPIs | `1-2` drivers + `1-2` SLA guardrails | Alert/status strip -> Rolling telemetry -> Incident log |
| **Operating Review** | Daily / Weekly | `1-3` north-star KPIs | `1-2` drivers + `1-2` cost/quality guardrails | Odd-count KPI strip -> Trend + Breakdown -> Detail table |
| **Exploratory Analytics** | Ad-hoc Interactive | `1` anchor metric | Dynamic facet filters + drill-down | Tri-pane: Left facet rail + Dominant canvas + Inspector |

*Odd-Count KPI Rule*: If a product genuinely tracks `3` or `5` primary KPIs, render an odd-count grid (`grid-cols-3` or `grid-cols-5`). Never invent a filler fourth tile just to make a `2x2` or `4`-column row symmetrical.

### 1.3 Simplest High-Craft Option

**Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft")**: Follow the **Renderer Simplicity Ladder**:
1. **HTML `<table>` / Bullet Progress Bar**: Use native HTML first for ranked comparisons, exact ratios, and SLA gauges.
2. **Declarative Grammar (`Vega-Lite` / `Observable Plot` / `Recharts` SVG)**: Render standard time-series, bars, scatter, and confidence bands in `< 40` lines of declarative config.
3. **Custom `D3 + SVG`**: Drop down to custom D3 scales only when bespoke layout geometry (e.g., interactive Sankey or custom brush sync) cannot be expressed declaratively.
4. **`Canvas2D` -> `WebGL`**: Escalate ONLY when point count crosses `>= 1,000` marks or `>= 1 Hz` streaming saturates SVG DOM nodes. Never install Three.js/WebGL for standard business KPIs, and never put dashboard filters in Redux when URL `searchParams` give instant shareability and browser Back support.

---

## 2. Step-by-Step Workflow

### Token Economy Protocol
- Query `design_search.py` for CVD-safe chart palettes and lock `dashboard-spec.md` metric formulas before writing chart JSX.
- Validate totals via SQL/API reconciliation scripts and accessibility via `axe-core` rather than copying raw datasets into prompts.

1. **Lock Decision Model & Reconciled Metric Contract (`Owner: Product / Data / UI Lead`)**
   - **Inputs**: `prd.md`, warehouse/API metric definitions, freshness SLAs.
   - **Action**: Complete Section 1 of `dashboard-spec.md`: define `1-3` primary KPIs, `1-2` drivers, `1-2` guardrails, exact numerator/denominator formulas, UTC time window, grain, and freshness SLA. Enforce **single reconciled semantic queries** so KPI strip totals, chart series totals, and table footers match exactly. If required telemetry or metrics are absent, stop and surface `Missing Data Contract` rather than inventing mock numbers.
   - **Outputs**: Signed-off metric ledger.

2. **Architect Summary-to-Detail Layout & Mobile Chart-First Flow (`Owner: Frontend Engineer`)**
   - **Inputs**: `dashboard-spec.md`, `tokens.json`.
   - **Action**:
     - Structure vertical scan hierarchy strictly as **Summary KPIs -> Time Movement -> Diagnostic Breakdowns -> Lookup Detail Table**.
     - Anatomy of every KPI Card: **1 headline metric** (`tabular-nums`), explicit **denominator & time window**, **delta/target chip**, and **freshness badge**. Never cram sparkline + 3 sub-metrics + action dropdown inside one cramped tile.
     - On mobile (`390x844`): render the **primary visualization BEFORE filter controls** (collapse filters into a clean `"Filters (N)"` button opening a bottom sheet), and on Apply/Reset return scroll position and focus smoothly to the main chart.
   - **Outputs**: Responsive tri-pane / summary-to-detail page layout.

3. **Implement URL-Backed Cross-Filtering & Saved Views (`Owner: Frontend Engineer`)**
   - **Inputs**: Filter dimensions, drill-down paths.
   - **Action**:
     - Store active filters, date range, comparison mode, and selected entity in URL `searchParams`: use `history.replaceState` for rapid brushing/slider/search typing, and `history.pushState` for committed filter/entity drill-down so users can share exact views and step Back cleanly.
     - Persist tiny UI prefs (e.g., collapsed rail) in `localStorage`, and store full named **Saved Views** in `IndexedDB` or a remote user-views endpoint.
     - Enforce interaction parity: `hover` previews values, `click` commits cross-filter selection, and touch devices support tap-to-inspect step-through tooltips (never hover-only insights).
   - **Outputs**: Shareable, cross-filtered analytics workspace.

4. **Enforce Statistical Honesty, CVD-Safe Color & SVG/Canvas Rigor (`Owner: Data Viz Engineer`)**
   - **Inputs**: Dataset distribution, color tokens, SVG/Canvas renderer.
   - **Action**:
     - *Statistical Honesty*: Start bar and area baselines strictly at `0` (or mark broken line-chart scale explicitly with an unmistakable break symbol); pair averages with sample size (`n`), error bars, `15%` confidence bands (solid actual vs dashed forecast), or box/violin spread; disclose smoothing windows (`7d rolling avg`) and render missing intervals as explicit gaps rather than silently interpolating zeros; ban dual Y-axes unless scales are directly comparable with matching callouts; split `> 6`-series spaghetti charts into **Small Multiples**.
     - *Perceptual & CVD-Safe Color*: Maintain a **Semantic Color-Role Ledger** (`neutral grid/context`, `primary focus`, `comparison baseline`, `ordered sequential/diverging ramp`, `alert/stale`). **Never** use rainbow ramps for ordered magnitude or overload one hue across unrelated meanings. Enforce `>= 3:1` non-text contrast between adjacent marks and canvas ground; place **direct end labels** on line series instead of forcing eye-ping-pong to a distant legend.
     - *SVG & Real-Time Polish*: Use `10-12px` `tabular-nums` axis ticks, `0.5-1px` muted gridlines, `1.5-2.25px` data strokes, `shape-rendering: crispEdges` on orthogonal axes/bars/heatmaps, and `vector-effect: non-scaling-stroke`. For `>= 1 Hz` live streams: use bounded ring buffers, LTTB downsampling to viewport pixel width, explicit `live | stale | delayed | partial | offline` status chips, last-known-good value retention on disconnect, and a **Pause / Resume** toggle.
   - **Outputs**: Honest, legible, high-frame-rate visualizations.

5. **Build Accessible Fallbacks & Execute Deletion Pass (`Owner: QA / Frontend Engineer`)**
   - **Inputs**: Rendered charts and telemetry streams.
   - **Action**:
     - Add redundant non-color encodings (dash patterns, point shapes, direct labels), arrow-key chart datum navigation with `aria-live` readout, sortable/downloadable HTML `<table>` fallback (`View as table / CSV`), and `@media (prefers-reduced-motion: reduce)` freezing live auto-scroll into manual refresh.
     - **Deletion Pass**: Strip decorative glowing shadows, 3D tilts, redundant chart legends duplicated by direct labels, and unused vanity widgets. Verify metric reconciliation across cards, charts, and tables.
   - **Outputs**: Verified accessible dashboard ready for release.

### 2.6 Minimal SVG Crispness & Real-Time Stream State Snippet

```css
/* Crisp SVG axes, subtle 0.5px gridlines, and frozen reduced-motion stream */
.viz-axis line, .viz-heatmap rect {
  shape-rendering: crispEdges;
}
.viz-series-line {
  fill: none;
  stroke-width: 2px;
  vector-effect: non-scaling-stroke;
}
.viz-gridline {
  stroke-width: 0.5px;
  stroke: var(--color-border-subtle);
}
```

```ts
// URL state split: replaceState for live typing/brush, pushState for committed drill-down
function syncFilterParam(key: string, val: string, commit: boolean) {
  const url = new URL(window.location.href);
  val ? url.searchParams.set(key, val) : url.searchParams.delete(key);
  window.history[commit ? "pushState" : "replaceState"]({}, "", url);
}
```

---

## 3. Reusable Artifact & Template

Every dashboard or telemetry console MUST instantiate [Dashboard Specification Template](../templates/dashboard-spec.md) prior to implementation.

| Template Field Group | Required Fields | Enforcement Rule |
|---|---|---|
| **Brief & Cadence** | `Spec ID`, `Decision Mode`, `Audience & Cadence`, `Primary Renderer` | Mode dictates refresh SLA and stream vs batch contract |
| **Metric Model** | `1-3 Primary KPIs`, `1-2 Drivers`, `1-2 Guardrails`, `Formula`, `Grain`, `Reconciles With` | Zero unowned metrics; cards/charts/tables share single query definition |
| **Workspace & URL State** | `Shell Position`, `State Owner`, `push vs replace URL Params`, `Mobile Chart-First Order` | Filter state reloadable via URL; mobile places chart before filter drawer |
| **Chart & Rigor Inventory** | `Chart ID`, `Job`, `25-Type Pick`, `Renderer Threshold`, `Statistical Encoding`, `Color Role`, `Table/SR Fallback` | Mandatory table fallback for `C`/`D` grade charts; zero rainbow ramps |
| **Resilience Sign-Off** | `Simplest High-Craft Check`, `Reconciliation Verified`, `Live/Stale/Offline Retention` | Last-known-good data preserved with timestamp badge on disconnect |

---

## 4. Verification Checklist

- [ ] Dashboard models `1-3` primary KPIs, `1-2` drivers, and `1-2` guardrails with explicit denominators, time windows, and odd-count strip integrity.
- [ ] KPI card totals, chart aggregates, and detail table footers reconcile from one canonical semantic metric definition.
- [ ] Bar and area charts start cleanly at zero baseline, averages disclose sample size `n`/spread, and missing data renders as honest gaps.
- [ ] Zero dual Y-axes, zero `3D` decorative business charts, zero `> 6`-series unsplit spaghetti lines, and zero rainbow magnitude ramps appear.
- [ ] Chart marks achieve `>= 3:1` contrast against background, encode categories with redundant shape/dash/labels (never color alone), and use direct series labels.
- [ ] Active filters, ranges, and selected entities round-trip cleanly through URL `searchParams` (`replaceState` transient vs `pushState` committed).
- [ ] Every chart provides keyboard traversal or a sortable HTML `<table>`/CSV fallback (mandatory for Pie, Treemap, Sankey, Choropleth, Network).
- [ ] Real-time streams (`>= 1 Hz`) use Canvas2D ring buffers, display `live/stale/delayed/offline` status, keep last-known-good values, and pause under `prefers-reduced-motion`.
- [ ] Mobile viewport (`390x844`) renders the primary chart above collapsed filter triggers and restores scroll/focus when closing the filter sheet.

---

## 5. Hard Quality Gate

- **`PASS`**:
  - `dashboard-spec.md` is complete, all KPI/chart/table totals reconcile cleanly, and zero dual-axis or zero-truncated bar distortions exist.
  - All charts pass `>= 3:1` mark contrast, provide reachable `<table>`/CSV and keyboard/tap inspection fallbacks, and achieve `0` `axe-core` errors.
  - Mobile `390x844` chart-first flow, URL filter reload persistence, and live/stale reconnect handling pass Playwright verification.
- **`FAIL`**:
  - Truncated bar baselines, unlabelled smoothing/CI omission, rainbow color ramps, hover-only values, or missing fallback tables on Grade `C`/`D` charts.
  - Blank white error screen when stream disconnects instead of last-known-good retention with `stale`/`offline` status badge.

```bash
# Metric reconciliation, axe-core accessibility, and mobile/URL-state dashboard checks
npx playwright test --grep "dashboard-reconciliation|url-filters|mobile-chart-first"
npx @axe-core/cli http://127.0.0.1:3000/dashboard --exit
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **KPI Tile Wall & Symmetrical Padding** | 8+ identical cards dilute executive focus; invented 4th KPI creates noise | `> 4` top-strip KPI cards or filler metric added just to make a `2x2` grid | Cap at `1-3` primary KPIs, keep odd counts odd, show denominator + window |
| **Dual-Axis & Truncated-Bar Distortion** | Manipulates perceived correlation and exaggerates tiny `1%` deltas visually | Bar Y-axis starting at `90` instead of `0`, or dual left/right Y-axes | Always anchor bar/area at `0`; split unrelated units into aligned stacked panels |
| **Rainbow Ramps & Hue Overloading** | Destroys perceptual ordering and breaks comprehension for `~8%` CVD users | `hsl()` rainbow scales or using the same red/green for brand AND alerts | Use semantic Color-Role Ledger (`cobalt/slate/amber/crimson` CVD-safe) |
| **Hover-Only Values & Detached Legends** | Unusable on touchscreens and keyboard; forces constant eye scanning away from data | Values readable only on mouseover, or 6-item color legend below chart | Direct end labels, click/tap step-through inspection, `<table>` fallback |
| **3D Business Charts & Unbacked Complex Graphs** | Perspective distortion skews area comparisons; Sankey/Network lock out screen readers | 3D pie/bar tilts or Treemap/Network/Sankey lacking keyboard/table view | Flat 2D charts; ship sortable HTML `<table>` + CSV export beside every complex viz |
| **Mobile Settings-First & Blank Stream Failures** | Pushes the chart off-screen behind 6 filter dropdowns; drops critical ops data on blip | Filter form stacked above chart on `390px` or spinner wiping stale telemetry | Render main chart first on mobile; retain last-known-good + `stale` timestamp badge |
