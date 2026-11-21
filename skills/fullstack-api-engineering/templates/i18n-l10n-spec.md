# Internationalization (i18n) & Localization (l10n) Specification

> **Usage**: Lock locale scope, catalog schema, ICU plural/gender rules, formatting primitives, RTL/BiDi layout rules, String Freeze ledger, and pseudo-localization QA verdict. Replace `<angle-bracket>` fields with concrete project values.

## Metadata

| Field | Value |
|---|---|
| **Spec ID** | `<L10N-001>` |
| **Product / Surface** | `<Web App + Transactional Emails>` |
| **Source Locale (BCP 47)** | `<en-US>` |
| **Negotiation Precedence** | `<URL path -> user profile -> cookie -> Accept-Language -> source fallback>` |
| **String Freeze Status** | `<NOT CALLED | ACTIVE | LIFTED>` |
| **Updated (UTC)** | `<YYYY-MM-DDTHH:MM:SSZ>` |

---

## 1. Supported BCP 47 Locale Matrix

| BCP 47 Tag | Script & Direction (`LTR | RTL`) | Fallback Chain | CLDR Plural Categories | Font / Script Coverage | Status (`ACTIVE | PLANNED | VERIFIED`) |
|---|---|---|---|---|---|
| `<en-US>` | `<Latn / LTR>` | `<en -> source>` | `<one, other>` | `<Plus Jakarta Sans / Latin>` | `<ACTIVE>` |
| `<vi-VN>` | `<Latn / LTR>` | `<vi -> en>` | `<other>` | `<Be Vietnam Pro / Vietnamese diacritics>` | `<ACTIVE>` |
| `<ar-EG>` | `<Arab / RTL>` | `<ar -> en>` | `<zero, one, two, few, many, other>` | `<IBM Plex Sans Arabic / ligatures>` | `<PLANNED>` |

---

## 2. Catalog Structure & Translator Context Contract

- **Key Naming Convention**: `<domain>.<section>.<element>` (example: `checkout.summary.item_count`)
- **Catalog Storage & Bundle Split**: `<locales/<bcp47>/<namespace>.json — loaded per active locale only>`
- **Required Translator Context Fields**: `screen`, `max_chars` (or `max_px`), `placeholders` (name + type + example), `gender_plural_note`

```json
{
  "checkout.summary.item_count": {
    "message": "{count, plural, =0 {No items} one {# item} other {# items}}",
    "context": {
      "screen": "Checkout summary header",
      "max_chars": 24,
      "placeholders": {
        "count": { "type": "number", "example": 3 }
      },
      "gender_plural_note": "Refers to physical/digital cart line items; zero case rendered when cart is empty."
    }
  }
}
```

---

## 3. Native `Intl.*`, Currency & Timezone Policy

| Data Type | Storage Format (Backend / DB) | Display Formatting Primitive | Forbidden Pattern |
|---|---|---|---|
| **Dates & Instants** | `<UTC ISO-8601 timestamptz>` | `<Intl.DateTimeFormat(locale, { timeZone: userIanaTz, dateStyle: 'medium', timeStyle: 'short' })>` | `<Fixed +07:00 offsets for recurring rules; custom regex dates>` |
| **Currency & Numbers** | `<BIGINT minor units (cents) + ISO 4217 code>` | `<Intl.NumberFormat(locale, { style: 'currency', currency })>` | `<Floating-point dollars or hardcoded '$' prefix>` |
| **Relative Time & Lists** | `<UTC delta / string array>` | `<Intl.RelativeTimeFormat / Intl.ListFormat>` | `<Manual "2 days ago" or ", " concatenation>` |

---

## 4. RTL / BiDi & Layout Expansion Rules

- **CSS Logical Properties Enforced**: `margin-inline-start`, `margin-inline-end`, `padding-block`, `inset-inline-start`, `text-align: start`, `border-start-start-radius`. Physical `left`/`right` prohibited for layout geometry.
- **Mixed-Direction Isolation**: Wrap user-generated IDs, emails, URLs, and code spans in `<bdi>` inside translated sentences.
- **Icon Mirroring Policy**:
  - *Mirror in `[dir="rtl"]`* (`transform: scaleX(-1)`): `<back/forward arrows, chevrons, breadcrumbs, reading-order progress bars>`
  - *Do NOT mirror*: `<checkmarks, clocks, media play/pause, brand logos, lock/shield>`
- **Expansion Budget (Pseudo-Localization)**: `<+35% character length allowance and 2x line-height headroom tested at mobile 375px & desktop 1440px>`

---

## 5. Automated Validation, Freeze Ledger & Locale QA Gate

### 5.1 Catalog Coverage & Structural Audit
| Locale | Total Keys | Translated | Missing | Stale / Orphan | Placeholder / Plural Errors | Coverage % |
|---|---|---|---|---|---|---|
| `<en-US>` | `<240>` | `<240>` | `<0>` | `<0>` | `<0>` | `<100%>` |
| `<ar-EG>` | `<240>` | `<240>` | `<0>` | `<0>` | `<0>` | `<100%>` |

### 5.2 String Freeze & Post-Freeze Delta Log
| Freeze Event / Key | Reason | Approved By | Delta Applied |
|---|---|---|---|
| `<Freeze v1.2 — 2026-01-10>` | `<Release cut>` | `<Product + Engineering Lead>` | `<0 post-freeze keys added>` |

### 5.3 Pseudo-Localization & Visual QA Verdict
- **Validation Command**: `<project-i18n-check-cmd> && npx playwright test tests/i18n-rtl.spec.ts -q` *(e.g., ESLint literal-string check + project JSON placeholder/plural parity script)*
- **Locale QA Verdict**: `<PASS | PASS WITH CONDITIONS | NOT ASSESSED | FAIL>`
- **Notes / Truncation Checks**: `<Verified +35% pseudo-locale and RTL layout with zero overflow or clipped buttons>`
