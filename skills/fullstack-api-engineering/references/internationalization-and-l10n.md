# Internationalization & Localization

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs end-to-end internationalization (`i18n`) and localization (`l10n`) across web apps, mobile apps, backend error/email catalogs, and RTL scripts during Spiral Stages `3A`, `3B`, and `3C`.
It adapts rigorous `scan -> extract -> freeze -> validate -> rtl-check -> qa` pipeline discipline to modern platform primitives.
It prevents client bundle bloat and layout breakage across diverse scripts.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Localization Baseline & Anti-Overengineering Gate

Before adding heavyweight client i18n runtimes or scaffolding 20 empty locale files on day one, apply the four simplicity checks:
1. **Option A First**:
   - Use runtime/browser native **`Intl.*`** (`Intl.DateTimeFormat`, `Intl.NumberFormat`, `Intl.PluralRules`, `Intl.RelativeTimeFormat`, `Intl.ListFormat`).
   - Pair `Intl.*` with JSON ICU MessageFormat catalogs and **CSS Logical Properties** (`margin-inline-start`, `padding-block`, `inset-inline-end`).
   - Reject Moment.js, custom regex currency formatters, and separate `rtl.css` override sheets.
2. **Scope Locales to Verified Charter Targets**:
   - Even single-locale (`en-US`) apps MUST externalize dates, currencies, timezones, and UI strings cleanly from day one.
   - Defer multi-language vendor pipelines until target locales are scoped in the project charter.
3. **Zero Runtime ICU AST Compiler in Client Bundles**:
   - Pre-compile or load flat pre-resolved message catalogs per active locale instead of shipping a 40 KB parser to every browser.
4. **Native HTML BiDi & Direction Primitives**:
   - Use HTML `lang="..."`, `dir="rtl" | "ltr" | "auto"`, and `<bdi>` rather than JavaScript string reversal or regex direction hacks.

### 1.2 Locale, Formatting & BiDi Standards Matrix

| Localization Concern | Canonical Standard / Primitive | Mandatory Engineering Rule | Simplicity & Performance Guard |
|---|---|---|---|
| **Locale Tag & Negotiation** | **BCP 47** (`en-US`, `vi-VN`, `pt-BR`, `zh-Hans`, `ar-EG`) | Precedence: `URL path/domain -> user profile -> cookie -> Accept-Language -> fallback` | Never infer language solely from IP geolocation; preserve user override |
| **Message Strings & Plurals** | **Externalized Catalogs + ICU MessageFormat** | Named placeholders `{count, plural, =0 {None} one {# item} other {# items}}`, `select` for gender/role | Ban string concatenation (`"Hello " + name`) and positional `%s`/`%d` tokens |
| **Dates, Numbers & Currency** | **CLDR via native `Intl.*`** | Store UTC ISO-8601 + integer minor currency units (`cents`); format at display edge | Zero custom regex date/currency formatters; zero Moment.js bloat |
| **Timezones** | **IANA TZ Database** (`Asia/Ho_Chi_Minh`, `America/New_York`) | Store UTC instant + user/venue IANA TZ ID | Never store fixed `+07:00` offsets for recurring schedules (DST breaks them) |
| **RTL & BiDi Layout** | **HTML `dir` + CSS Logical Properties + `<bdi>`** | Use `inline-start`/`inline-end`, wrap embedded LTR tokens (emails, IDs, URLs) in `<bdi>` | Never maintain a duplicate `rtl.css` stylesheet when logical properties suffice |

### 1.3 Quantitative Expansion, Plural & Token-Economy Thresholds

- **Pseudo-Localization Expansion Budget**:
  - Test UI containers with **`+35%` to `+50%` character expansion** (German, French, Russian, Finnish expand 30–50% over English).
  - Reserve `2x` vertical line-height headroom for stacked scripts (Arabic, Thai, Devanagari).
- **CLDR Plural Coverage**:
  - `other` (Japanese, Vietnamese)
  - `one`, `other` (English, German)
  - `one`, `few`, `many`, `other` (Polish, Russian)
  - `zero`, `one`, `two`, `few`, `many`, `other` (Arabic)
- **Per-Locale Bundle Split**:
  - Download ONLY the active locale's namespace JSON (`<= 1` locale per session).
  - Keep inactive translation files out of the main client JS chunk.
- **Token-Economy Catalog Discipline**:
  - Split large catalogs by route namespace (`common.json`, `checkout.json`) so agents inspect only active domains.
  - Query missing keys via deterministic scripts rather than reading full locale JSON blobs into context.

---

## 2. Step-by-Step Workflow

1. **Lock Target Locales, Negotiation & Formatting Rules (Phase 3A)** *(Owner: Fullstack Engineer | Inputs: Product spec, `i18n-l10n-spec.md` | Output: Locale matrix)*
   - Declare source locale (`en-US`), active target BCP 47 locales, and fallback chains (`fr-CA -> fr -> en`).
   - Verify font subsets cover required scripts:
     - Latin extended diacritics (Vietnamese, Polish, Turkish)
     - CJK unified glyphs (`zh-Hans`, `ja`, `ko`)
     - Arabic/Hebrew ligatures and BiDi shaping
   - Lock UTC instant storage, IANA timezone identifiers, and integer minor currency units.
   - Ensure backend API responses and transactional emails resolve the user's locale (`Accept-Language` or profile).
   - Return localized validation error details without breaking machine-readable RFC 9457 `code` keys.

2. **Scan, Extract & Annotate Catalogs with Translator Context** *(Owner: Fullstack Engineer | Inputs: UI & API error files | Output: Keyed JSON catalogs)*
   - **Scan** source code for localization anti-patterns:
     - Hardcoded UI labels and API error strings
     - String concatenation (`"Welcome, " + user`) and positional tokens (`%s`)
     - Raw `toLocaleDateString()` calls lacking explicit locale/timezone
     - Text baked into SVG/PNG assets and physical CSS (`margin-left`, `right: 0`)
   - **Extract** strings into hierarchical keys (`<domain>.<section>.<element>`, e.g., `billing.invoice.due_date_label`).
   - Use named ICU placeholders (`{date}`, `{count}`) exclusively.
   - Attach mandatory **translator context** alongside every key:
     - `screen`: UI surface or email template name
     - `max_chars`: character or pixel width budget
     - `placeholders`: variable name, type, and example value
     - `gender_plural_note`: disambiguation (e.g., button verb vs noun)

3. **Implement CSS Logical Properties, BiDi Isolation & Selective Mirroring** *(Owner: Frontend Engineer | Inputs: Design tokens & CSS | Output: Direction-agnostic layouts)*
   - Replace physical CSS properties with logical equivalents (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `border-start-end-radius`, `text-align: start`).
   - **RTL & BiDi Hygiene**:
     - Set `<html lang={locale} dir={dir}>` before first paint to prevent RTL flash.
     - Wrap embedded LTR tokens (usernames, emails, order IDs, URLs, code snippets) in `<bdi>` so Unicode BiDi reordering never scrambles punctuation.
     - Mirror directional icons (arrows, chevrons, breadcrumbs, reading-order progress bars) via `[dir="rtl"]` `transform: scaleX(-1)`.
     - Keep **non-mirrored** icons (checkmarks, clocks, media play/pause, brand logos, locks) unflipped.
   - Logical CSS reference rule:
     ```css
     .banner {
       margin-inline-start: 1rem;
       padding-inline: 1.25rem;
       border-inline-start: 3px solid var(--accent);
       text-align: start;
     }
     ```

4. **Call String Freeze, Run Deterministic Validation & Pseudo-Localize** *(Owner: Fullstack Engineer / QA | Tool: Catalog validator + Playwright | Output: Verified catalogs)*
   - Enforce **String Freeze** before sending source catalogs for translation.
   - Record any urgent post-freeze edits in the delta ledger.
   - Run automated structural catalog validation verifying:
     - `0` missing keys against source locale (`100%` completeness or explicit fallback).
     - `100%` placeholder parity (every `{variable}` in source appears identically in translation).
     - Required CLDR plural forms present per locale.
     - Valid UTF-8 encoding and translated length within `max_chars`.
   - Run **Pseudo-Localization** in CI (`[!! Ŧḗşŧ ƀŭŧŧǿƞ !!]` with `+35%` padding and simulated `[dir="rtl"]`) across `375px` mobile and `1440px` desktop viewports:
     ```json
     {
       "checkout.action.submit": "[!! Ƥŀȧƈḗ ǿřđḗř ƞǿẇ — ḗẋƥȧƞşīǿƞ !!]"
     }
     ```

5. **Condense Catalogs & Audit Per-Locale Bundle Hygiene** *(Owner: Fullstack Engineer | Tool: Key/bundle scanner | Output: Pruned catalogs)*
   - Execute **Deletion/Condensation Pass**:
     - Prune stale/orphaned keys no longer referenced in source code.
     - Deduplicate identical shared action labels (`common.actions.save`) where translator context matches.
     - Confirm dynamic `import()` splits catalogs so each browser downloads only its active locale.
   - Record final per-locale QA verdict:
     - `PASS | PASS WITH CONDITIONS | NOT ASSESSED | FAIL`

---

## 3. Reusable Artifact & Template

- **Canonical Template**: [i18n/L10n Spec](../templates/i18n-l10n-spec.md)
- **Primary Sections Enforced**:
  - Supported BCP 47 Locale Matrix and fallback chains
  - Catalog Structure, ICU MessageFormat, and Translator Context
  - Native `Intl.*`, Minor-Unit Currency, and IANA Timezone Policy
  - CSS Logical Properties, `<bdi>` Isolation, and Icon Mirroring
  - Automated Validation, String Freeze Ledger, and Locale QA Verdict

### i18n/L10n Spec Field-by-Field Contract

| Contract Section | Required Fields | Acceptance Rule |
|---|---|---|
| **Locale Matrix** | `bcp47_tag`, `script_dir`, `fallback_chain`, `cldr_plurals`, `font_coverage` | Valid BCP 47 tags; explicit fallback chain terminating at source |
| **Catalog & Context Schema** | `key` (`domain.section.element`), ICU `message`, `screen`, `max_chars`, `placeholders`, `gender_plural_note` | Zero concatenated strings; zero positional `%s`; named ICU placeholders only |
| **Formatting & Timezones** | UTC storage, IANA TZ ID, minor currency units, `Intl.*` calls | Zero fixed UTC offsets for schedules; zero float math on money |
| **RTL & BiDi Policy** | Logical CSS properties, `<bdi>` rules, mirrored vs static icon table | Zero physical `left`/`right` layout couplings; accurate icon mirroring |
| **Freeze & QA Gate** | Coverage (`total`, `translated`, `missing`, `stale`, `placeholder_errors`), freeze log, QA verdict | `0` placeholder/plural errors; pseudo-locale `+35%` overflow check `PASS` |

---

## 4. Verification Checklist

- [ ] Target BCP 47 locales and fallback chains are locked cleanly.
- [ ] Negotiation precedence (`URL -> profile -> cookie -> Accept-Language -> default`) avoids IP-only guessing.
- [ ] Zero hardcoded user-facing strings or string concatenations remain in UI components or API error payloads.
- [ ] All pluralized and gender-sensitive messages use ICU MessageFormat (`plural` / `select`) with named placeholders instead of `count === 1` ternaries.
- [ ] Every catalog entry includes translator context (`screen`, `max_chars`, placeholder types/examples, plural/gender notes).
- [ ] Dates store UTC instants + IANA timezone IDs and currencies store integer minor units.
- [ ] Display formatting delegates exclusively to native `Intl.*` primitives.
- [ ] Layouts use CSS Logical Properties (`inline-start`/`inline-end`/`block`) and wrap mixed-direction tokens in `<bdi>`.
- [ ] Directional icons mirror cleanly in `[dir="rtl"]` while status/media/brand icons stay unflipped.
- [ ] Automated catalog validation confirms `0` missing placeholders, valid CLDR plural categories, and `0` stale keys after pruning.
- [ ] Pseudo-localization (`+35%` string expansion + `dir="rtl"`) passes across `375px` and `1440px` viewports with per-locale bundle splitting verified.

---

## 5. Hard Quality Gate

- **PASS Criteria**:
  - Automated i18n linter/validator reports `0` hardcoded literal strings.
  - Zero placeholder mismatches (`{var}` parity = `100%`) and `0` broken ICU plural forms.
  - Zero orphan or stale catalog keys remain **after** pruning.
  - Pseudo-locale `+35%` and RTL visual/DOM overflow checks pass at mobile (`375px`) and desktop (`1440px`) viewports.
- **FAIL Criteria**:
  - Missing or renamed `{placeholder}` in any target catalog (`P0`).
  - Hardcoded `count === 1 ? "item" : "items"` plural logic or string concatenation (`P1`).
  - Physical `margin-left`/`right` breaking RTL layout or fixed `+07:00` offset stored for recurring events (`FAIL`).
  - Bundling all locale JSON files into the main client JS chunk (`FAIL`).

```bash
# Audit hardcoded strings, validate ICU placeholders/plurals, and run RTL + pseudo-locale tests
npx eslint --rule 'i18next/no-literal-string: error' src/ && npx playwright test tests/i18n-rtl.spec.ts -q
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **String Concatenation & Positional `%s` Tokens** | Word order shifts across languages, forcing broken grammar when fragments are glued together | `"Deleted " + count + " files"` or `"%s by %s"` | Single ICU string with named placeholders: `"{count, plural, one {Deleted # file} other {Deleted # files}}"` |
| **English `count === 1` Plural Ternaries** | Breaks Slavic (`few`/`many`), Arabic (6 forms), and East Asian (`other` only) plural grammar | `n === 1 ? t('one') : t('many')` in UI/backend code | ICU `plural` syntax evaluated via `Intl.PluralRules` / compiled catalog |
| **Fixed UTC Offset Storage (`+07:00`)** | Daylight Saving Time shifts invalidate fixed offsets for future or recurring events | Numeric offset stored instead of `America/New_York` | Store UTC instant (`timestamptz`) + canonical IANA timezone identifier |
| **Physical CSS `left`/`right` & Separate `rtl.css`** | Duplicating overrides in `rtl.css` drifts on every edit and misses padding/radius asymmetries | `margin-left`, `padding-right`, `text-align: left` in CSS | CSS Logical Properties (`margin-inline-start`, `padding-inline-end`, `text-align: start`) |
| **Bundling All Locales Client-Side** | Shipping 15–30 translation JSONs in the main bundle inflates JS parse time and wastes bandwidth | Static `import allLocales from './locales'` in client entry | Dynamic per-locale/per-namespace loading (`locales/[lang]/[ns].json`) |
| **Translating Unfrozen Source Strings** | Mid-sprint key edits invalidate translator work and trigger placeholder mismatches at release | Unlogged English key edits after vendor handoff | Enforce String Freeze before handoff and log urgent edits in the delta ledger |
