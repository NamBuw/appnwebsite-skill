# UI Redesign Audit & Preservation Report (`URA-<NNN>`)

- **Audit ID**: `<URA-001>`
- **Target App / URL / Repo Path**: `<repo-path-or-staging-url>`
- **Detected Stack**: `<Next.js / React / Vue / HTML / SwiftUI / Expo + Tailwind v3|v4 | CSS Modules | Vanilla CSS>`
- **Migration Mode**: `<Direct In-Place 9-Step Fix (<= 5 screens) | Incremental Strangler-Fig (@layer / .ui-v2)>`
- **User Diagnosis Veto Status**: `<PENDING_USER_REVIEW | APPROVED | APPROVED_WITH_EXCLUSIONS>`
- **Audited (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`

---

## 1. Quantitative Baseline vs. Post-Fix Delta

| Metric / Check | Baseline (`--before`) | Post-Fix (`--after`) | Target / Gate |
|---|---|---|---|
| **Lighthouse Performance** | `<score>` | `<score>` | `>= 90` (no regression) |
| **Lighthouse Accessibility** | `<score>` | `<score>` | `>= 95` (`100` preferred) |
| **Lighthouse SEO** | `<score>` | `<score>` | `>= 90` (if public web) |
| **`axe-core` Critical/Serious** | `<count>` | `<count>` | `0` |
| **`pa11y` WCAG 2.2 AA Errors** | `<count>` | `<count>` | `0` |
| **`390x844` Horizontal Overflow** | `<px>` | `<px>` | `0 px` |
| **Normalized `@2x` Screenshots** | `<artifacts/before/*.png>` | `<artifacts/after/*.png>` | Side-by-side verified (`P0/P1 = 0`) |

---

## 2. Structural Preservation Ledger (`--before` vs. `--kept`)

| Interactive Surface | `--before` Count / Identifiers | `--kept` Count / Identifiers | Parity Status |
|---|---|---|---|
| **Navigation & Anchor Links (`<a href>`)** | `<count + route list>` | `<count + route list>` | `<100% KEPT | INTENTIONAL_REMOVAL_ADR>` |
| **Action Buttons & Handlers (`onClick`/`onSubmit`)** | `<count + handler list>` | `<count + handler list>` | `<100% KEPT | INTENTIONAL_REMOVAL_ADR>` |
| **Form Controls (`input[name]`, `select`, `textarea`)** | `<count + field names>` | `<count + field names>` | `<100% KEPT | INTENTIONAL_REMOVAL_ADR>` |
| **Test Suite / Smoke Assertions** | `<passing count>` | `<passing count>` | `<PASS>` |

---

## 3. Nine-Domain Diagnosis Table (`Floor | Reflex | Finish`)

| Finding ID | Domain (`1-9`) | Severity (`Floor | Reflex | Finish`) | File / Selector | Concrete Evidence | Targeted Fix (Priority Step `1-9`) |
|---|---|---|---|---|---|
| `F-01` | `1. Typography` | `Reflex` | `<src/app/layout.tsx>` | `<Uses banned Inter font and weight 900>` | `Step 1: Swap to Geist + 500/600 weights` |
| `F-02` | `2. Color & Surfaces` | `Reflex` | `<src/styles/globals.css>` | `<Unrequested purple hero gradient + mixed gray temps>` | `Step 2: Lock flat surface + single warm/cool gray scale` |
| `F-03` | `4. Interactivity` | `Floor` | `<src/components/Table.tsx>` | `<Missing focus-visible ring and error state; blocks paste>` | `Step 3/7: Add 2px focus ring, inline alert, remove onPaste block` |
| `F-04` | `3. Layout` | `Floor` | `<src/components/Hero.tsx>` | `<100vh clips iOS toolbar; 28px horizontal overflow at 390px>` | `Step 4: Switch to 100dvh + min-w-0 grid track` |
| `F-05` | `6. Components` | `Finish` | `<src/components/Features.tsx>` | `<3 identical border+shadow+white cards + accordion FAQ>` | `Step 6: Convert to open bento band + side-by-side Q&A` |

*Nine Domains Covered*: `1. Typography`, `2. Color & Surfaces`, `3. Layout`, `4. Interactivity & States`, `5. Content & Microcopy`, `6. Component Patterns`, `7. Iconography & Imagery`, `8. Code Quality & Tokens`, `9. Strategic Omissions`.

---

## 4. Nine-Step Fix Priority & Deletion Pass Log

1. **User-Excluded / Vetoed Fixes**: `<List any finding explicitly deferred by stakeholder>`
2. **Step Execution Check**:
   - [ ] `1. Font swap` -> `2. Color/surface` -> `3. Hover/active/focus` -> `4. Layout/100dvh/390px` -> `5. Motion` -> `6. Generic components` -> `7. Loading/empty/error` -> `8. Copy` -> `9. Type scale`
3. **Deletion & Condensation Receipts**:
   - **Dead CSS / Wrappers Deleted**: `<files/selectors removed and net LOC delta>`
   - **Deprecated Dependencies Removed**: `<packages removed, if any>`
4. **Final Verdict**: `<PASS | CONCERNS | FAIL>`

## References
- Surface Guides: [UI Audit and Redesign](../references/ui-audit-and-redesign.md) | [Design Systems Engineering](../references/design-systems-engineering.md) | [Mobile Apps Engineering UX](../references/mobile-apps-engineering-ux.md)
- Surface Router: [SKILL.md](../SKILL.md)
