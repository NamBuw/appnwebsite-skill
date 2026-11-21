# Landing Page Brief (`LPB-<NNN>`)

- **Page ID**: `<LPB-001>`
- **Product / Offer Name**: `<product-or-offer-name>`
- **Spiral / Rigor Tier**: `<minimal | standard | full>`
- **Site-Kind Calibration**: `<software | tech | product | service | gaming | place>`
- **Layout Archetype**: `<A: Classic Hero + Sections | B: Long-Form Story | C: Minimal Conversion | D: X-vs-Y Comparison>`
- **Primary Conversion Action**: `<Single verb+outcome CTA, e.g. "Start free 14-day trial">`
- **Index Directive**: `<index, follow | noindex, nofollow (paid-ad/time-bound campaign)>`
- **Last Updated (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`

---

## 1. Batched Intake & Non-Stalling Assumptions

| Intake Dimension | Confirmed Input | 1-Line Default Assumption (If Unanswered) |
|---|---|---|
| **Ideal Customer Profile (ICP)** | `<role, team size, trigger event>` | `<Default assumption stated before drafting>` |
| **Core Pain & Quantified Outcome** | `<measurable problem and target delta>` | `<Default assumption stated before drafting>` |
| **Top 3 Purchase Objections** | `<1) price/ROI, 2) setup time, 3) migration/lock-in>` | `<Address setup time, switching cost, and support SLA>` |
| **Traffic Source & Message Match** | `<organic search | paid search | product hunt | referral>` | `<Headline mirrors exact referrer promise>` |
| **Available Proof Assets** | `<metrics, customer quotes, live sandbox, logos>` | `<Mark missing facts with {{metric}} or {{testimonial}} tokens>` |

---

## 2. Simplicity & Complexity Budget Check

- **Simplest High-Craft Stack**: `<Static SSR HTML + CSS Grid + IntersectionObserver + native details/side-by-side FAQ>`
- **JS Budget**: `<0 KB custom scroll-jacking / 3D hero libraries; <= 50 KB gz total client JS>`
- **Hero Visual Mode**: `<Annotated product screenshot | Interactive sandbox | Crisp diagram | Editorial photo>`

---

## 3. Copy & 12-Section Narrative Map

| # | Section | Copy / Content Spec | Word / Structural Constraint |
|---|---|---|---|
| 1 | **Hero Headline** | `<Formula: {Outcome} without {pain} | The {category} for {audience} | Ship {result} in {time}>` | `max-width: 680px`; sentence case; no hyphens in copy; no unrequested eyebrow pill |
| 2 | **Hero Subheadline** | `<1-2 sentences clarifying who it is for and concrete mechanism>` | `<= 28` words; `text-wrap: pretty` |
| 3 | **Primary CTA** | `<Verb + outcome label + destination>` | Single primary CTA above the fold; zero appended arrows; `8px 12px` minimum padding |
| 4 | **Adjacent Proof Signal** | `<Single short trust cue: e.g. "Used by {{team_count}} engineering teams">` | 1 line adjacent to CTA; real or braced `{{...}}` token only |
| 5 | **Hero Visual** | `<Media path, dimensions, alt text, fetchpriority="high">` | Explicit `width`/`height`; dark/light ground matched; zero unrequested tint overlay |
| 6 | **Problem -> Solution Bridge** | `<Contrast status-quo friction with new workflow>` | Max 2 concise paragraphs (`<= 65ch` measure) |
| 7 | **Outcome Benefits (`3-5`)** | `<3-5 outcome-led blocks (not raw feature names)>` | Break 3-equal-card symmetry (asymmetric bento, zig-zag, or open band) |
| 8 | **How It Works (`3` Steps)** | `<Step 1 -> Step 2 -> Step 3>` | Numbered only for true sequence; active-voice verb alignment |
| 9 | **Social Proof & B11 Tagline Reveal** | `<Customer proof + mandatory word-by-word scroll-reveal tagline section>` | Odd/decimal demo numbers if synthetic demo UI; `IntersectionObserver` + reduced-motion fallback |
| 10 | **Pricing / Comparison** | `<Tier table or X-vs-Y breakdown with {{price}} tokens>` | Weight/color emphasis on recommended tier (never taller middle tower); bottom-aligned CTAs |
| 11 | **FAQ & Risk Reversal** | `<6-12 plain Q&A pairs + guarantee/trial terms>` | Side-by-side or searchable plain Q&A (avoid chevron accordion trap); `FAQPage` JSON-LD |
| 12 | **Final CTA & Legal/404** | `<Identical primary CTA + privacy, terms, custom 404, skip-link>` | Matches Section 3 CTA label and destination verbatim |

---

## 4. Visual, Anti-Slop & CWV/SEO Locks

- **Typography**: `<Single non-banned family: e.g. Geist | Manrope | Poppins>` (`Inter`/`Roboto`/`Arial`/`Open Sans`/`Helvetica` excluded; zero italics; zero weight `900`).
- **Iconography**: `<Phosphor | Solar | Iconamoon>` (`Lucide`/`Feather`/`Heroicons`/`Material Icons`/`Material Symbols` excluded).
- **Surface & Radius Math**: `<Flat intentional ground; nested inner = outer - gap when gap < 32px and result > 2; hero text-only gradient if dark/light high-contrast>`.
- **SEO / AEO Meta**: `<title (50-60 chars)>`, `<meta description (140-155 chars)>`, `<canonical URL>`, `</llms.txt entry>`, `<dynamicParams = false for catch-all routes>`.
- **CWV Targets**: `LCP <= 2.5s`, `INP <= 200ms`, `CLS < 0.1`, `0 px` horizontal overflow at `320px`, `390px`, and `1440px`.

## References
- Surface Guide: [Landing Pages and Marketing](../references/landing-pages-and-marketing.md)
- Surface Router: [SKILL.md](../SKILL.md)
