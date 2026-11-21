# Technical SEO, GEO, Core Web Vitals, Analytics & Feature Flags

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

### 1.1 Fatal-First SEO & Generative Engine Optimization (GEO) Triage

Fix blockers strictly from **Tier 1 to Tier 4**. Optimizing Tier 4 meta-tag formatting while Tier 1 crawl or soft-404 bugs exist is forbidden:

| Priority Tier | Scope & Defect Class | Quantitative Threshold / Rule | Action Rule |
|---|---|---|---|
| **Tier 1: FATAL** | Crawlability, Soft-404s, JS-Hidden Content, Demo Walls | `0` blocks on Googlebot, Bingbot, `OAI-SearchBot`, `PerplexityBot`, `ClaudeBot`, `GPTBot` on public routes; `/_next/` & `/static/` unblocked; unknown URLs return HTTP `404` (`dynamicParams = false`); plain-text pricing/specs visible with JS off; interactive value in `< 30s` | Block all other SEO tweaks until Tier 1 count = `0` |
| **Tier 2: REVENUE** | Thin Programmatic Pages, Conflicting Facts, Locale Bloat, Faceted Crawl Traps | Programmatic pages hold `>= 3` items (`< 3` -> `noindex`); zero contradictory counts across H1, FAQ, JSON-LD, and `/llms.txt`; `>= 3` contextual internal links into commercial pages; `<= 3` fully translated locales with reciprocal `hreflang` + `x-default`; `noindex` applied **before** `Disallow` | Prune thin pages (`301` in 2-rule chunks) and unify facts to 1 shared constant |
| **Tier 3: COMPOUNDING** | Earned Authority & Linkable Utility | Real interactive tools, calculators, or embeddable badges earning organic editorial backlinks | Build only after Tier 1 & Tier 2 pass; ignore inflated DR link-farm metrics |
| **Tier 4: FLUFF** | Meta-Description Length, Minor Alt/Heading Polish | Touch only when Tiers 1–3 are clean | Never spend sprint budget here if pages fail indexation or pricing visibility |

### 1.2 Core Web Vitals (CWV), INP & Next.js Caching Budgets

| Metric | Target (`p75`) | Primary Root Causes & Deterministic Remediation |
|---|---|---|
| **LCP** | `< 2.5 s` | Inline critical shell; set `priority` on hero `next/image`; load fonts via `next/font`; avoid client-fetched hero data |
| **INP** | `< 200 ms` | Break `> 50 ms` JS tasks with `scheduler.yield()`; batch DOM reads before writes (eliminate layout thrashing); keep DOM `< 1,400` nodes; animate `transform`/`opacity` only |
| **CLS** | `< 0.10` | Reserve explicit `width`/`height` or `aspect-ratio` on media/embeds; reserve dynamic banner slots |
| **TTFB / FCP / TBT** | `TTFB < 800ms`, `FCP < 1.8s`, `TBT < 200ms`, `SI < 3.4s` | Enable Next `cacheComponents: true` (3-tier: Static shell -> `'use cache'` + `cacheLife`/`cacheTag` -> `<Suspense>`); never read `cookies()`/`headers()`/`searchParams` inside `'use cache'` |

### 1.3 SEO & Flag Simplest High-Craft Check & Token Economy

- **Decision Tree (Feature Flag & Experimentation Selection)**:
  ```text
  Per-user bucketing or A/B readout required?
  ├── NO -> Global instant kill-switch needed?
  │   ├── NO -> Static process.env.<FLAG> (0 SDK, 0 runtime overhead)
  │   └── YES -> Single Edge Config read at middleware/server
  └── YES -> Server-only Flags SDK (flags v4+)
      ├── Define dedupe(identify) once per request
      ├── Set FLAGS_SECRET (32-byte base64) + .well-known/vercel/flags
      └── Public/ISR route? -> precompute() + generatePermutations()
  ```
- **KPI Ceiling**:
  - Define **`1–3` primary KPIs**, `1–2` diagnostic drivers, and `1–2` guardrails (including `INP <= 200ms` and `5xx` error rate).
  - Never ship dashboards bloated with 15 competing metrics, and always separate metric selection from target-setting.
- **Feature Flag Escalation**:
  - Static release toggle -> `process.env` variable (zero SDK).
  - Global instant kill-switch -> Edge Config.
  - User/tenant targeting or A/B test -> **Server-only** Flags SDK (`flags` v4+) with `dedupe(identify)` once per request, `FLAGS_SECRET` (`32`-byte base64), `.well-known/vercel/flags` discovery, and `precompute()` / `generatePermutations()` on static routes (zero client loading spinners).
- **Anti-Overengineering Gate**:
  - Ask: *"Can a plain environment variable or Edge Config replace a third-party experimentation SDK? Can fixing Tier 1 `robots.txt`/SSR HTML solve discovery without buying an enterprise SEO suite?"*
- **Token Economy Rule**:
  - Read only the active domain concern (SEO triage vs. CWV trace vs. Flags/Experiments) and confirm unused preconnects via DevTools network trace before touching head tags.

---

## 2. Step-by-Step Workflow

1. **Execute Fatal-First Crawl, Soft-404 & AI-Visibility Audit**
   - **Owner**: Full-Stack / Growth Engineer
   - **Input**: Live staging URL, `robots.txt`, dynamic route handlers, pricing/landing pages.
   - **Output**: Zero Tier 1 blockers + unified single-constant `/llms.txt` & JSON-LD.
   - **Tool**: `curl -A`, Chrome DevTools, schema validator.
     - Inspect `robots.txt` so Bingbot and AI search crawlers (`OAI-SearchBot`, `PerplexityBot`, `ClaudeBot`, `GPTBot`) can read public marketing/docs pages and `/_next/`/`/static/` assets while private `/api/`, `/app/`, and `/admin/` routes remain disallowed (`X-Robots-Tag: noindex` on `/api/`).
     - Probe nonexistent slugs (`/nonexistent-probe-404`) and enforce `dynamicParams = false` or `notFound()` so missing routes never return HTTP `200` soft-404s.
     - Verify pricing, feature tables, and structured JSON-LD render in initial server HTML (`JS disabled`).
     - Expose a dynamic `/llms.txt` route sharing a single source-of-truth constant for product counts/prices, and prune half-translated locales above `3` languages (`noindex` + consolidated `301` redirects).
     - Apply `noindex` **before** adding `Disallow` on faceted parameters so crawlers can drop stale URLs from the index.

2. **Profile Core Web Vitals & Refactor Long Tasks / Cache Boundaries**
   - **Owner**: Frontend Engineer
   - **Input**: Production build (`next build && next start`), Chrome DevTools MCP trace.
   - **Output**: Measured trace clearing `LCP < 2.5s`, `INP < 200ms`, `CLS < 0.10`.
   - **Tool**: Chrome DevTools MCP, Lighthouse CLI, `next build` bundle analyzer.
     - Run Chrome DevTools MCP (`navigate_page`, `performance_start_trace`, `performance_analyze_insight` targeting `LCPBreakdown`, `CLSCulprits`, `RenderBlocking`, `DocumentLatency`, `NetworkRequestsDepGraph`; verify unused `<link rel="preconnect">` tags via `list_network_requests` before removing).
     - Minimize `'use client'` leaf boundaries, replace barrel re-exports, inspect `browserslist` to eliminate legacy polyfills, and yield main-thread event handlers (`> 50ms`) via `scheduler.yield()`.
     - In Next.js 16+, replace legacy `experimental.ppr` with `cacheComponents: true`: keep `cookies()`/`headers()` outside `'use cache'` and pass extracted values as serializable arguments (using `updateTag()` for immediate read-your-own-writes vs. `revalidateTag()` for SWR; calling `await connection()` before per-request randomness):

```ts
export async function Page() {
  const region = (await cookies()).get("region")?.value ?? "us"; // outside 'use cache'
  return <CachedCatalog region={region} />;
}
```

3. **Instrument Server Feature Flags, KPIs & Verified Telemetry Drains**
   - **Owner**: Product & Backend Engineer
   - **Input**: `experiment-flag-spec.md`, `FLAGS_SECRET` (`32`-byte base64), analytics workspace.
   - **Output**: Flicker-free server flags + HMAC-verified telemetry pipeline.
   - **Tool**: `flags` SDK v4+, structured JSON logger (`requestId`, `duration_ms`).
     - Lock `1–3` primary KPIs + guardrails before writing tracking events.
     - Evaluate feature flags strictly on the server via `flag()` + `dedupe(identify)` (zero call-site boolean args; use `precompute()` + `getPrecomputed()` on cached public pages).
     - Wrap non-blocking analytics emissions in `waitUntil()` and verify incoming Speed Insights / log-drain webhooks via HMAC-SHA1 raw-body digest comparison (`crypto.timingSafeEqual`).

4. **Audit Experiment Data Quality & Person-Property Semantics**
   - **Owner**: Data / QA Engineer
   - **Input**: Assignment logs, exposure events, outcome events (e.g., PostHog HogQL / warehouse SQL).
   - **Output**: Signed-off data-quality readout in `experiment-flag-spec.md`.
   - **Tool**: PostHog MCP / SQL warehouse check, chi-square script.
     - Confirm matching **entity grain** (`user_id` vs. `tenant_id`) between numerator and denominator before computing rates.
     - Check all four experiment integrity failures: (a) **Sample Ratio Mismatch (SRM)** via chi-square (`p >= 0.001`), (b) **duplicate assignments** (`> 1` variant per entity), (c) **exposures without assignment**, and (d) **outcome events timestamped before first assignment**.
     - In PostHog HogQL, account for **person-on-events** (`person.properties.*` reflects ingestion-time traits, not current profile state) and align bucketing timezones.

5. **Deletion / Condensation & Post-Deploy 60s Smoke Pass**
   - **Owner**: Engineer & SRE
   - **Input**: Flag specs, preconnect headers, analytics client bundles.
   - **Output**: Minimal bundle, zero stale flags, verified production CWV & crawlability.
   - **Tool**: `rg`, Chrome DevTools MCP, `curl`.
     - Delete retired feature flags past their `retirement_date` (along with dead variant branches).
     - Remove unused preconnect links and strip redundant third-party client analytics tags inflating INP/TBT.
     - Run preflight + `60s` post-deploy error scan alongside `curl` crawl checks.

---

## 3. Reusable Artifact & Template

Complete [Experiment and Feature Flag Spec](../templates/experiment-flag-spec.md) for every flag, experiment, or growth optimization. Required fields:

### 3.1 Experiment & Feature Flag Schema Fields

| Field | Contract Requirement | Purpose |
|---|---|---|
| `flag_key` & `retirement_date` | Unique key + explicit removal date (`<= 30d` post-decision) | Prevents permanent dead-branch accumulation |
| `evaluation_mode` | `static_env_var` \| `edge_config` \| `vercel_flags_server` | Forces simplest server mechanism with zero client layout shift |
| `identify_entities` | `dedupe(identify)` entity shape + `precompute` flag list | Eliminates duplicate DB/auth lookups and preserves static/ISR caching |
| `primary_kpis_1_to_3` | Strictly `1–3` decision metrics with explicit formula & grain | Blocks vanity-metric sprawl and mismatched denominators |
| `guardrails` | CWV (`p75 INP <= 200ms`, `CLS <= 0.10`) + `5xx` error ceiling | Catches regressions before shipping losing variants |
| `data_quality_checks` | `SRM p >= 0.001`, `0` dupes, `0` pre-assignment events, PoE note | Prevents false wins caused by telemetry or timezone bugs |

### 3.2 Canonical Single-Constant `/llms.txt` & Server Flag Pattern

```ts
// Single shared source of truth across Pricing HTML, JSON-LD, and /llms.txt
export const PRODUCT_FACTS = {
  starterMonthlyUsd: 29,
  proMonthlyUsd: 79,
  supportedIntegrations: 42,
} as const;

// Server-only flag evaluation with deduped entity lookup (zero client flicker)
const identify = dedupe(async () => ({ userId: (await getSession())?.userId ?? null }));
export const newCheckoutFlag = flag<boolean>({
  key: "new-checkout-flow",
  identify,
  decide: ({ entities }) => Boolean(entities?.userId && isInRollout(entities.userId, 25)),
});
```

### 3.3 Experiment Integrity SQL Guardrails

- Always verify grain alignment (`user_id` vs. `tenant_id`) before computing any conversion ratio.
- Reject any readout exhibiting Sample Ratio Mismatch (`chi-square p < 0.001`), duplicate variant assignments per entity, exposure events lacking an assignment row, or conversion timestamps preceding first assignment.
- Document whether user traits come from ingestion-time event properties (`person.properties.*` in PostHog) or current warehouse profile tables.

---

## 4. Verification Checklist

- [ ] `robots.txt` permits Googlebot, Bingbot, and AI search bots on public pages and `/_next/` while protecting private `/api/` routes.
- [ ] Requesting random nonexistent slugs returns HTTP `404` (`dynamicParams = false` or `notFound()`) with zero soft-404 HTTP `200` responses.
- [ ] Core pricing, feature specs, JSON-LD, and dynamic `/llms.txt` render in initial server HTML with counts sourced from one shared constant.
- [ ] Production trace verifies `LCP < 2.5s`, `INP < 200ms`, `CLS < 0.10`, and `TTFB < 800ms` with `'use cache'` isolated from `cookies()` and `headers()`.
- [ ] Feature flags evaluate strictly server-side (or via `env` / Edge Config for static toggles) with zero client flicker and an explicit `retirement_date`.
- [ ] Analytics specification enforces `1–3` primary KPIs, HMAC-verified webhook drains, and `waitUntil()` non-blocking flush.
- [ ] Experiment readout checks confirm zero SRM, zero duplicate assignments, zero exposures without assignment, and zero pre-assignment conversions.

---

## 5. Hard Quality Gate

- **PASS**:
  - Zero Tier 1 FATAL SEO blockers; HTTP `404` verified on unknown slugs; plain-text pricing + `/llms.txt` consistency verified via `curl`.
  - `p75` CWV trace clears `LCP < 2.5s`, `INP < 200ms`, `CLS < 0.10`.
  - Flags evaluated server-side with `<= 3` KPIs and clean SRM/assignment data-quality check.
- **FAIL**:
  - `robots.txt` blocking Bingbot/AI search or `/_next/`, HTTP `200` soft-404 on invalid routes, or pricing hidden behind client JS.
  - `cookies()` called inside `'use cache'`, client-side flag flickering, or experimentation SDK installed for static booleans.
  - `> 3` primary KPIs or uninvestigated SRM/pre-assignment anomaly.

```bash
# 1. Verify crawlability for Bingbot/AI search and strict 404 on unknown slugs
curl -sI -A "Bingbot" https://example.com/robots.txt | head -n 5
curl -s -o /dev/null -w "soft404_probe=%{http_code}\n" https://example.com/nonexistent-route-probe-404
curl -s -A "OAI-SearchBot" https://example.com/pricing | rg -i "pricing|plan|month"

# 2. Static check for cookies()/headers() inside 'use cache' or legacy experimental.ppr
rg -n "experimental\.ppr|cookies\(\)|headers\(\)" src/

# 3. Lighthouse / CWV trace verification
npx lighthouse http://127.0.0.1:3000 --only-categories=performance,seo --output=json --quiet
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Blanket `robots.txt` Disallow Blocking AI/Bing Crawlers** | Erases site from ChatGPT/Perplexity/Bing answers and strips CSS/JS rendering access | `User-agent: * Disallow: /` or blocking `/_next/` | Allow public routes + `/_next/` + AI search bots; restrict only `/api/`, `/app/`, `/admin/` |
| **Catch-All Dynamic Routes Serving HTTP `200` Soft-404s** | Wastes crawl budget, dilutes domain authority, and indexes error pages | Unknown `/slug-xyz` returns `200` with fallback template | Set `dynamicParams = false` or call `notFound()` returning HTTP `404` |
| **JS-Only Pricing & Drifting Static `public/llms.txt`** | Non-JS crawlers see blank pricing (`$0`/empty) while static `llms.txt` advertises stale counts | Pricing requires client hydration; `llms.txt` hardcoded manually | Render pricing/specs in server HTML + serve dynamic `/llms.txt` from shared constants |
| **Polishing Meta Fluff Before Tier 1 Blockers** | Optimizes character counts on unindexed or soft-404 pages | Editing `meta description` while `robots.txt` or `404` status fails | Enforce strict Tier 1 -> 2 -> 3 -> 4 triage; block Tier 4 until Tier 1 & 2 are empty |
| **`Disallow` Added Before `noindex`** | Search engines cannot recrawl to see `noindex`, trapping faceted URLs in the index | Both `Disallow` and `noindex` added simultaneously on bloated query URLs | Serve `noindex` first until de-indexed, then add `Disallow` |
| **Client-Side Flag Flicker or SDK for Static Env Toggles (Over-Engineering)** | Delays LCP/CLS with hydration jumps and bloats bundle for simple booleans | Client `<FlagProvider>` spinner or LaunchDarkly/Statsig for an on/off toggle | Use `process.env` / Edge Config for static toggles; `flags` v4 server `dedupe(identify)` + `precompute()` |
| **KPI Sprawl (`> 3` Primary KPIs) & Ignoring SRM** | Guarantees p-hacking false positives and ships broken variants from telemetry skew | 8+ "primary" metrics or experiment analyzed without SRM/pre-assignment check | Enforce `1–3` primary KPIs + `INP/5xx` guardrails + mandatory SRM/grain/timestamp gate |
