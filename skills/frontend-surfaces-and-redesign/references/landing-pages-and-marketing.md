# Landing Pages and Marketing Sites

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs high-converting landing pages, marketing sites, comparison pages, and launch microsites from batched discovery through conversion copywriting, visual assembly, SEO/AEO engineering, and Core Web Vitals verification. It enforces the suite's Cross-Skill Conflict Contract (`Geist`, `Manrope`, `Poppins`, or curated non-banned pairings; `Phosphor`, `Solar`, or `Iconamoon` icons; flat intentional surfaces) and Radical Simplicity ("Least Code, Highest Craft").

---

## 1. Decision Framework

### 1.1 Layout Archetype Selection Matrix

Select the page archetype strictly from offer complexity, buyer skepticism, and traffic intent before writing copy or markup:

| Archetype | When to Choose | Above-the-Fold Structure | Target Section Count | Primary Conversion Pattern |
|---|---|---|---|---|
| **A. Classic Hero + Sections** | Product value is obvious from a screenshot or live interactive preview | Headline (`<= 680px`) + subheadline + 1 primary CTA + adjacent proof + crisp UI preview | `8-12` sections | Direct trial, demo, or interactive sandbox |
| **B. Long-Form Story** | High-ticket offer, novel category, or skepticism-heavy switching decision | Problem-first narrative hook + 1 primary CTA + anchored founder/outcome proof | `10-12` sections | Guided persuasion leading to identical bottom CTA |
| **C. Minimal Conversion** | Single high-intent action (waitlist, download, gated tool, ad landing) | Focused value line + 1 email/action control + 1 trust cue; zero nav distraction | `3-5` sections | Zero-navigation distraction-free capture |
| **D. X-vs-Y Comparison** | High-intent competitor/alternative search queries | Direct verdict headline + capability matrix + switching steps + 1 CTA | `6-8` sections | Side-by-side factual proof + migration offer |

### 1.2 Site-Kind Aesthetic Calibration

Calibrate visual temperature, hero media, and motion restraint by site kind:

| Site Kind | Hero Media Strategy | Surface & Ground Temperature | Motion Intensity Budget |
|---|---|---|---|
| **`software` / SaaS** | Crisp product UI frame or live interactive snippet (no fake abstract blobs) | Neutral obsidian `#09090B` or crisp paper `#FFFFFF` / `#FAFAFA` | Subtle `IntersectionObserver` reveals (`<= 300ms` ease-out); zero parallax loops |
| **`tech` / Developer Tool** | Real CLI/API code block, architecture diagram, or latency benchmark | Cool zinc/slate ground; `1px` crisp structural borders | Instant state transitions (`150-220ms`); zero decorative floaters |
| **`product` / Hardware** | High-resolution studio photography with clean negative space (zero unrequested color tint) | Warm neutral or dark gallery ground matching lighting direction | Smooth media crossfade on state switch; explicit `width`/`height` |
| **`service` / Agency** | Editorial case-study snapshot and real team outcomes | High-contrast editorial typography (`65ch` measure) | Minimal fade-up only; no scroll-jacking |
| **`gaming` / Interactive** | Full-bleed trailer frame or playable canvas inside safe-zone bounds | Deep dark `#050507` with strict legible HUD contrast | GPU-composited `transform`/`opacity` only; honor `prefers-reduced-motion` |
| **`place` / Venue** | Architectural photography + location/hours/booking action immediately accessible | Warm paper `#F9F8F6` or mineral stone; real map/directions fallback | Zero kinetic text gymnastics; fast LCP image preload |

### 1.3 Simplest High-Craft Option & Quantitative Thresholds

**Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft")**: Before installing animation frameworks, WebGL globes, or multi-step form libraries, test the simplest baseline:
- Semantic SSR/static HTML + CSS Grid/Flexbox (`0` layout JS overhead).
- Native `clamp()` fluid typography + `text-wrap: balance` / `pretty`.
- Native `<details>` or plain side-by-side 2-column Q&A grid (no JS accordion library).
- A `< 30`-line `IntersectionObserver` scroll reveal with `prefers-reduced-motion` instant fallback.

Static semantic markup achieves sub-second LCP, zero hydration blocking, and higher conversion reliability than client-rendered marketing SPAs.

| Constraint / Metric | Quantitative Threshold | Enforcement Rule |
|---|---|---|
| **Above-the-Fold Primary CTAs** | Exactly `1` primary CTA | Optional secondary link (`Watch 90s walkthrough`) is plain muted text, never a competing button |
| **Hero Copy Measure** | `max-width: 680px` (`~65ch` body) | Prevent ultra-wide headlines that break visual scanning across `1440px` monitors |
| **Outcome Benefits & Steps** | `3-5` benefits; `3` How-It-Works steps | Lead every item with buyer outcome, never raw implementation feature labels |
| **FAQ Density** | `6-12` plain Q&A pairs | Cover pricing, setup time, migration, security, cancellation, and support |
| **Responsive Breakpoints** | `320px`, `390x844`, `1440px` | `0 px` horizontal overflow; primary CTA visible above the fold on `390x844` |
| **Core Web Vitals** | `LCP <= 2.5s`, `INP <= 200ms`, `CLS < 0.1` | Preload hero LCP asset (`fetchpriority="high"`); reserve explicit aspect boxes |

---

## 2. Step-by-Step Workflow

### Token Economy Protocol
- Query `ui-design-craft` palettes and font pairings via `design_search.py` instead of bulk-reading entire CSV catalogs.
- Batch all intake questions into one turn and emit concrete code/markup once per section rather than regenerating boilerplate.
- Use deterministic Playwright, `axe-core`, and Lighthouse CLI checks to inspect overflow and CWV rather than pasting DOM trees into context.

1. **Batched Intake & Non-Stalling Assumptions (`Owner: Product / UI Lead`)**
   - **Inputs**: `spiral-charter.md` (or user prompt), target URL/traffic source, locked `tokens.json` / `design-master.md`.
   - **Action**: Ask missing facts (ICP, core pain/outcome, top 3 objections, proof assets, traffic source, legal/brand constraints) in a **single batched message**. Never stall on unanswered optional items: record explicit 1-line assumptions inside [Landing Page Brief Template](../templates/landing-page-brief.md) and mark unverified facts with braced tokens (`{{price}}`, `{{team_count}}`, `{{testimonial}}`).
   - **Outputs**: Completed `landing-page-brief.md` with locked Archetype (`A-D`) and Site-Kind.

2. **Twelve-Section Narrative & Conversion Copywriting (`Owner: Copy / UX Designer`)**
   - **Inputs**: `landing-page-brief.md`, traffic source promise (for exact message-to-source headline match).
   - **Action**: Draft all 12 sections in conversion order:
     - *Above the Fold (Sections 1-5)*: (1) Headline using proven formulas (`{Outcome} without {pain}`, `The {category} for {audience}`, `Ship {result} in {time}`), (2) 1-2 sentence Subheadline, (3) Verb+Outcome Primary CTA (e.g., `Start free trial`, `Book 15-min architecture review` — zero generic `Submit` or appended arrows), (4) Single adjacent proof line, (5) Hero visual/interactive preview. **Strict rule**: NO unrequested ALL-CAPS eyebrow pills or badges above the hero headline.
     - *Mid-Page Persuasion (Sections 6-9)*: (6) Problem-to-Solution contrast, (7) `3-5` outcome-led benefits breaking 3-equal-card symmetry (use asymmetric bento, zig-zag split, or open typographic bands), (8) `3`-step How It Works (numbered ONLY for true sequence), (9) Social proof (real quotes or `{{testimonial}}` tokens; synthetic UI demos use odd/decimal figures like `41.8%` or `37 ms` instead of round numbers) **plus the mandatory B11 word-by-word scroll-reveal tagline section** bridging proof into conversion.
     - *Bottom Closure (Sections 10-12)*: (10) Pricing or comparison matrix (weight/border/color emphasis on the recommended plan — never an inflated taller middle tower; bottom-align all card CTAs), (11) `6-12` plain Q&A FAQs (side-by-side 2-column grid or searchable FAQ preferred over accordion traps that hide text from `Ctrl+F` and crawlers), (12) Risk reversal + identical Final CTA matching Section 3 verbatim.
   - **Copy Hygiene**: Sentence case throughout, zero hyphens inside body copy where clean phrasing works, `text-wrap: balance` on headings, `text-wrap: pretty` on paragraphs, and zero AI buzzwords (`delve`, `unleash`, `seamless`, `game-changer`, `revolutionize`, `elevate`).
   - **Outputs**: Verified copy deck mapped to sections `1-12`.

3. **Incremental Visual & Surface Assembly (`Owner: Frontend Engineer`)**
   - **Inputs**: Locked copy deck, `tokens.json`, `ui-design-craft` typography/palette tokens.
   - **Action**: Build incrementally from top to bottom (`Hero -> Benefits -> How It Works -> Proof & B11 Tagline -> Pricing -> FAQ -> Final CTA & Footer`). Enforce Cross-Skill Conflict defaults:
     - *Typography*: Single non-banned typeface (`Geist`, `Manrope`, `Poppins`, or approved non-banned display/body pairing — **ban `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`**); zero italics in UI/marketing copy; zero weight `900`; snap type sizes to named scale steps (`clamp()` for fluid display hero).
     - *Iconography*: Standardize on `Phosphor`, `Solar`, or `Iconamoon` (`20-24px` feature icons, `16px` inline); **ban `Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols`** by default.
     - *Surfaces, Spacing & Radii*: Flat intentional grounds (`#09090B`, `#0A0A0C`, `#FFFFFF`, `#FAFAFA`); allow directional text-only gradient strictly on hero headline (`#FFFFFF -> #9B9B9B` on dark or `#000000 -> #666666` on light) without background gradient wash; forbid 1-sided decorative accent borders (`border-left: 4px`); enforce primary button padding `8px 12px` minimum (`44px` comfortable touch target); compute nested card/button corners via `inner = outer - gap` when `gap < 32px` and result `> 2px`.
     - *Motion*: Single translucent floating nav (`backdrop-filter: blur(12px)`), full-height mobile drawer (`60ms` item stagger capped at `400ms`), GPU-only `transform`/`opacity` reveals (`cubic-bezier(0.22, 1, 0.36, 1)`), and mandatory `@media (prefers-reduced-motion: reduce)` instant-visible fallback.
   - **Outputs**: Sectioned responsive page components with all 6 states (`default`, `hover`, `active`, `focus-visible`, `loading`, `error`).

4. **SEO, AEO & CWV Asset Pipeline (`Owner: Frontend / Growth Engineer`)**
   - **Inputs**: Page metadata, route structure, hero/media assets.
   - **Action**:
     - Apply indexing discipline: `noindex, nofollow` on paid-ad-only or expiring promo pages; full `index, follow` on evergreen pages with unique `<title>` (`50-60` chars), `<meta name="description">` (`140-155` chars), canonical link, OpenGraph `og:image`, and internal links.
     - Add Answer Engine Optimization (AEO): plain semantic `<h3>`/`<p>` FAQ markup paired with valid `FAQPage` JSON-LD, explicit `Allow` directives for search/AI crawlers (`Bingbot`, `OAI-SearchBot`) in `robots.txt`, dynamic `/llms.txt` generated from shared product constants, and `dynamicParams = false` (or explicit 404 handling) on dynamic routes to prevent catch-all soft-404s.
     - Optimize CWV: preload LCP hero image (`fetchpriority="high"`, modern AVIF/WebP `srcset`), set explicit `width`/`height` on every `<img>`/`<video>` (`CLS < 0.1`), lazy-load below-the-fold media, and include custom branded 404, privacy/terms links, and a keyboard skip-to-content link.
   - **Outputs**: Metadata, JSON-LD, `/llms.txt`, and CWV-optimized asset tags.

5. **Complexity Budget, Deletion Pass & Responsive Audit (`Owner: QA / Frontend Lead`)**
   - **Inputs**: Built landing page running in local dev/preview server.
   - **Action**:
     - Execute **Deletion / Condensation Pass**: remove unused animation libraries, unreferenced CSS rules, decorative floating blobs, redundant wrapper `<div>`s, and heavy hero embeds replaceable by crisp static/SVG media. Confirm net JS payload stays minimal.
     - Inspect rendered pages freshly in a real headless browser across `320x568`, `390x844`, and `1440x900`: verify `0 px` horizontal overflow, primary CTA visible without scrolling on `390x844`, contrast compliance, and reduced-motion behavior.
   - **Outputs**: Clean production bundle + verified screenshots and CWV/a11y receipts.

### 2.6 Minimal Reference Implementation (Motion, Nested Radius & Hero Cap)

```css
/* Approved flat surface, 680px hero cap, nested radius, and GPU-only reveal */
.hero-copy {
  max-width: 680px;
  text-wrap: balance;
}
.hero-headline-dark {
  background: linear-gradient(90deg, #ffffff 0%, #9b9b9b 100%);
  -webkit-background-clip: text;
  color: transparent;
}
.feature-frame {
  --outer-radius: 16px;
  --frame-gap: 12px;
  border-radius: var(--outer-radius);
  padding: var(--frame-gap);
}
.feature-frame-inner {
  /* inner = outer - gap when gap < 32px and result > 2px */
  border-radius: calc(var(--outer-radius) - var(--frame-gap));
}
.reveal-item {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 280ms cubic-bezier(0.22, 1, 0.36, 1),
              transform 280ms cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal-item[data-visible="true"] {
  opacity: 1;
  transform: translateY(0);
}
@media (prefers-reduced-motion: reduce) {
  .reveal-item { opacity: 1; transform: none; transition: none; }
}
```

---

## 3. Reusable Artifact & Template

All landing pages and marketing sites MUST instantiate [Landing Page Brief Template](../templates/landing-page-brief.md) before authoring HTML/JSX.

| Template Field Group | Required Contents | Validation Rule |
|---|---|---|
| **Brief Metadata** | `Page ID`, `Rigor Tier`, `Site-Kind`, `Archetype (A-D)`, `Primary CTA`, `Index Directive` | Zero ambiguous multi-CTA goals; index policy explicit |
| **Batched Intake & Assumptions** | `ICP`, `Core Pain`, `Top 3 Objections`, `Traffic Source`, `Proof Assets`, `1-Line Assumptions` | Missing facts marked with `{{...}}` tokens, never fabricated |
| **12-Section Narrative Map** | `Hero (1-5)`, `Bridge/Benefits/How-It-Works (6-8)`, `Proof + B11 Tagline (9)`, `Pricing/FAQ/Final CTA (10-12)` | Headline `<= 680px`, `3-5` benefits, `6-12` FAQs, identical CTA |
| **Visual & Anti-Slop Locks** | Approved `Font`, `Phosphor/Solar/Iconamoon` icon set, `Flat Ground`, `Nested Radius Formula` | Zero banned fonts (`Inter`/`Roboto`/`Arial`/`Open Sans`/`Helvetica`) or banned icons |
| **SEO/AEO & CWV Budget** | `<title>`, `<meta description>`, `FAQPage` JSON-LD, `/llms.txt`, `LCP <= 2.5s`, `CLS < 0.1` | `dynamicParams = false` for catch-all safety; `fetchpriority="high"` on LCP |

---

## 4. Verification Checklist

- [ ] Batched intake completed once with explicit 1-line assumptions and `{{...}}` tokens for any unverified metrics, prices, or testimonials.
- [ ] Hero contains headline (`max-width: 680px`), subheadline, exactly 1 primary verb+outcome CTA, 1 adjacent proof signal, and zero unrequested eyebrow pills or appended arrows.
- [ ] All 12 narrative sections (or Archetype C minimal equivalent) are present, including the B11 word-by-word scroll-reveal tagline section and identical final CTA.
- [ ] Typography excludes `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica`, uses zero italics and zero `900` weight, and applies `text-wrap: balance` and `pretty`.
- [ ] Iconography uses `Phosphor`, `Solar`, or `Iconamoon` exclusively with zero `Lucide`, `Feather`, `Heroicons`, `Material Icons`, or `Material Symbols`.
- [ ] Surfaces remain flat and intentional without unrequested hero gradients, 1-sided accent borders, 3-equal-card feature stereotypes, or taller-tower middle pricing tiers.
- [ ] Nested border radii satisfy `inner = outer - gap` when `gap < 32px` and result `> 2px`, and card CTAs align along the bottom edge.
- [ ] Motion uses GPU-composited `transform` and `opacity` via `IntersectionObserver` (`cubic-bezier(0.22, 1, 0.36, 1)`) with a working `prefers-reduced-motion` fallback.
- [ ] Evergreen SEO/AEO metadata (`FAQPage` JSON-LD, `/llms.txt`, `robots.txt`, `dynamicParams = false`) or ad-page `noindex` is configured alongside custom 404, privacy/terms, and skip-link.
- [ ] Live browser check confirms `0 px` horizontal overflow at `320px`, `390x844`, and `1440px`, primary CTA visible above the fold on mobile, and `LCP <= 2.5s` / `CLS < 0.1`.

---

## 5. Hard Quality Gate

- **`PASS`**:
  - `landing-page-brief.md` is complete with zero unbraced placeholder copy or invented customer claims.
  - Zero banned fonts, zero banned icon libraries, zero horizontal overflow across `320px / 390px / 1440px`, and `0` critical/serious `axe-core` accessibility errors.
  - Lighthouse Performance `>= 90`, Accessibility `>= 95`, `LCP <= 2.5s`, `CLS < 0.1`, and deletion pass verified with fresh post-edit test/build receipts.
- **`FAIL`**:
  - Any competing dual primary CTA above the fold, unrequested hero eyebrow badge, banned font/icon import, or fabricated testimonial/metric.
  - Any horizontal scroll at `320px` or `390px`, missing `prefers-reduced-motion` fallback, soft-404 dynamic route leak, or missing live browser verification receipt.

```bash
# Structural, anti-slop, accessibility, and responsive verification commands
npx playwright test --grep "landing-responsive-and-cta"
npx @axe-core/cli http://127.0.0.1:3000 --exit
npx lighthouse http://127.0.0.1:3000 --only-categories=performance,accessibility,seo --output=json --quiet
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Dual Hero CTAs & Unrequested Eyebrow Pills** | Splits buyer attention above the fold and signals generic AI-generated SaaS templates | Two equally styled hero buttons or an ALL-CAPS pill badge above `<h1>` | Keep 1 primary verb+outcome CTA, plain text secondary link if needed, and clean `<h1>` |
| **Three-Equal-Card SaaS Stereotype** | Identical white cards with `border + shadow` and centered icons look templated and hide hierarchy | Uniform 3-column grid of `rounded-xl border shadow-sm` boxes | Use asymmetric bento splits, zig-zag product bands, or open typographic grids |
| **Invented Metrics & Round Demo Numbers** | Fabricated logos/quotes destroy trust; round placeholder numbers (`50%`, `100ms`) look synthetic | Unverified `%` claims without source or `Lorem ipsum` / round demo KPIs | Use `{{metric}}` / `{{testimonial}}` tokens for missing facts; use odd/decimal figures (`41.8%`) in demos |
| **Scroll-Jacking & WebGL Globe Bloat** | Burns main-thread CPU, spikes INP/LCP, and breaks keyboard/trackpad scroll physics | `window.addEventListener('scroll', ...)` animations or 500 KB 3D canvas heroes | Use CSS + `< 30`-line `IntersectionObserver` (`transform`/`opacity`) + crisp UI screenshot |
| **Soft-404 Catch-All & Ad-Page Indexing** | Wastes crawl budget, leaks paid-campaign variants into organic search, and confuses AI crawlers | Ad pages missing `noindex`, or `/[slug]` returning HTTP 200 for unknown slugs | Enforce `noindex` on campaign routes, `dynamicParams = false`, and explicit 404 responses |
| **Accordion-Only FAQ & Taller-Tower Pricing** | Accordions hide answers from `Ctrl+F`/skimmers; inflated middle pricing cards look templated | Chevron-only hidden FAQ rows or `scale-105` elevated middle tier | Render plain 2-column/searchable FAQ + `FAQPage` JSON-LD; highlight tier via border/weight |
