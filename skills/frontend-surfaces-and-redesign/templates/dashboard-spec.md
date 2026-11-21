# Dashboard & Data Visualization Specification (`DSP-<NNN>`)

- **Spec ID**: `<DSP-001>`
- **Surface Name**: `<Operational Revenue & Reliability Console>`
- **Decision Mode**: `<Monitoring (real-time ops) | Operating Review (weekly KPIs) | Exploratory Analytics>`
- **Audience & Cadence**: `<persona, refresh SLA, e.g. 30s stream | hourly warehouse | daily batch>`
- **Primary Renderer Stack**: `<Vega-Lite / Observable Plot / Recharts (SVG) | Canvas2D | WebGL/deck.gl>`
- **Last Updated (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`

---

## 1. Metric Model & Reconciliation Contract

*Limits*: `1-3` primary KPIs, `1-2` diagnostic drivers per KPI, `1-2` protective guardrails. Odd-count KPI strips remain odd (do not pad to 4).

| Metric ID | Role (`Primary | Driver | Guardrail`) | Formula (`Numerator / Denominator`) | Time Window & Grain | Freshness SLA & Source Table | Reconciles With |
|---|---|---|---|---|---|
| `KPI-1` | `Primary` | `<Net Revenue Retention = (Start + Expansion - Churn) / Start>` | `<Rolling 30d, daily UTC>` | `<5m, fct_mrr_daily>` | `<Chart C-1 + Table T-1>` |
| `DRV-1` | `Driver` | `<Seat Expansion Rate>` | `<Rolling 30d, account>` | `<5m, fct_account_seats>` | `<Chart C-2>` |
| `GRD-1` | `Guardrail` | `<Support Ticket Spike / 1k Active Orgs>` | `<Rolling 7d, org>` | `<1m, fct_support_sla>` | `<KPI-1 Strip Alert>` |

---

## 2. Tri-Pane Layout, URL State & Mobile Flow

| Surface / Control | Layout Position | State Owner | URL Param & History Mode | Mobile (`390x844`) Behavior |
|---|---|---|---|---|
| **KPI Strip (`1-3` cards)** | `Row 1: Summary` | `Server query` | `None (derived from global range)` | `1-col stack; single headline + denominator + delta` |
| **Global Date & Segment Filter** | `Row 1 / Left Outline` | `URL searchParams` | `?range=30d&seg=ent` (`push` on commit, `replace` on search type) | `Collapsed behind "Filters" button AFTER main chart; bottom sheet restores focus/scroll on Apply` |
| **Primary Trend & Breakdown** | `Row 2: Dominant Viewport` | `URL + React Query` | `?focus=2026-10` (`pushState`) | `Chart rendered BEFORE filter controls; tap step-through tooltip` |
| **Entity Inspector / Detail Table** | `Row 3 / Right Inspector` | `URL entity ID` | `?org=org_123` (`pushState`) | `Slide-over Sheet with tabular-nums right-aligned numbers` |
| **Saved Views** | `Header Menu` | `IndexedDB / Remote API` | `view=<id>` (`localStorage` reserved for sidebar open pref only)` | `Compact selector menu` |

---

## 3. Chart Inventory, Statistical Rigor & Accessibility Matrix

| Chart ID | Analytical Job | Selected Chart Type | Point Volume & Renderer | Statistical & Uncertainty Encoding | Color-Role & `>= 3:1` Contrast | Non-Visual Fallback & A11y |
|---|---|---|---|---|---|---|
| `C-1` | `Trend + Forecast` | `Multi-series Line + Confidence Band` | `<= 365 pts -> SVG` | `Zero baseline check; 15% CI fill + solid actual vs dashed forecast; n disclosed` | `Neutral grid (0.5px), Cobalt actual, Slate forecast, Direct end labels` | `Sortable HTML <table> + CSV export + arrow-key point stepper` |
| `C-2` | `Compare Breakdown` | `Horizontal Bar (<= 8 categories)` | `<= 20 bars -> SVG` | `Zero baseline mandatory; error bars for sample variance; no dual axes` | `Single sequential ramp; >= 3:1 bar-to-bg` | `Data table toggle + screen-reader aria-label summary` |
| `C-3` | `Real-Time Stream` | `Rolling Ring-Buffer Line` | `>= 1,500 pts -> Canvas2D + LTTB` | `Window aggregation + missing-gap break (no false interpolation)` | `Live/Stale/Delayed/Offline status chip + Pause/Resume button` | `prefers-reduced-motion freezes live auto-scroll into manual refresh` |

---

## 4. Resilience, Simplest High-Craft & Sign-Off Checks

- **Simplest High-Craft Check**: `<Declarative chart spec / native HTML table fallback / URL searchParams before custom WebGL or Redux store>`
- **Metric Reconciliation Verified**: `<SQL/API totals match across KPI cards, charts, and detail table within rounding tolerance>`
- **Live/Stale/Offline Retention**: `<Last-known-good values remain visible with explicit timestamp badge when stream disconnects>`

## References
- Surface Guides: [Dashboards and Data Visualization](../references/dashboards-and-data-visualization.md) | [Web Apps and SaaS Workspaces](../references/web-apps-and-saas-workspaces.md)
- Surface Router: [SKILL.md](../SKILL.md)
