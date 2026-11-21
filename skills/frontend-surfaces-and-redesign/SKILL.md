---
name: frontend-surfaces-and-redesign
description: >-
  Surface-specific frontend architecture, engineering, and in-place UI redesign across landing pages,
  stateful SaaS web apps, mobile apps (iOS/Android/Expo/Flutter), dashboards and statistical data
  visualization, design systems, and 9-domain UI audits. Use during Spiral Phase 3B/3C or standalone
  UI engineering after design tokens and system contracts are locked.
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  author: nambuw
  milestone: M3
  spiral_stages: "3B,3C"
---

# Frontend Surfaces and Redesign

Surface engineering router for Spiral Phases `3B` (Slice Build) and `3C` (Condensation & QA), plus standalone UI construction and in-place modernization.

> **Progressive Disclosure Rule**: Read ONLY the single reference module (and paired template, if applicable) matching the active surface task. **NEVER bulk-load all 6 reference modules into context.** When running inside the full suite, query targeted sections first via `python3 scripts/query_skill.py frontend-surfaces-and-redesign`.

---

## 1. Standalone Pre-Flight & Cross-Skill Defaults

When invoked standalone without the Parent Orchestrator, execute these three checks before authoring UI code:

1. **Confirm Upstream Inputs**: Verify locked design tokens (`tokens.json` / `design-master.md`) and API/data contracts (`openapi.yaml` / typed route schemas). If missing, lock a 1-page minimal brief or token sheet first rather than inventing arbitrary colors or payloads mid-component.
2. **Enforce Radical Simplicity ("Least Code, Highest Craft")**:
   - Prefer semantic HTML (`<button>`, `<dialog>`, `<details>`, `<table>`), CSS Grid `minmax(0, 1fr)`, `clamp()`, `@media (hover: hover)`, and URL `searchParams` before installing JS state stores, modal portals, or animation wrappers.
   - Surface the simplest high-craft baseline first and execute a Deletion/Condensation Pass before final verification.
3. **Honor Cross-Skill Conflict Contract**:
   - **Web Typography**: Ban `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` by default; pair `Geist`, `Manrope`, `Poppins`, or approved non-banned families.
   - **Web Iconography**: Standardize on `Phosphor`, `Solar`, or `Iconamoon`; ban `Lucide`, `Feather`, `Heroicons`, `Material Icons`, and `Material Symbols` on web unless a brownfield ADR grants an explicit waiver.
   - **Native Mobile Preservation**: Preserve platform-native **SF Symbols** on iOS (`SwiftUI` / `Expo`) and native Android **Vector Drawables** on native Android (`Jetpack Compose` / `Flutter`) — enforce the web font/icon ban strictly on web and mobile-web surfaces.
   - **Surfaces & Gradients**: Use flat intentional grounds by default; allow directional text-only gradients solely on hero display headlines (`#FFFFFF -> #9B9B9B` or `#000000 -> #666666`), and omit unrequested hero eyebrow pills or decorative `->` button arrows.

---

## 2. Six-Surface Routing Table (Load 1 Module Per Task)

| Active Surface / User Task | Load Exactly One Reference (`references/`) | Paired Template (`templates/`) | Primary Exit Deliverable |
|---|---|---|---|
| **Landing pages, marketing sites, conversion copy, pricing, FAQ, SEO/AEO** | [Landing Pages and Marketing](references/landing-pages-and-marketing.md) | [Landing Page Brief](templates/landing-page-brief.md) | Sectioned conversion page + CWV/SEO pass |
| **Stateful SaaS workspaces, `Cmd+K`, virtualized grids, forms, MCP/inline UI** | [Web Apps and SaaS Workspaces](references/web-apps-and-saas-workspaces.md) | [Dashboard Spec (pane/URL schema)](templates/dashboard-spec.md) | Interactive workspace + 7-case `break-ui` pass |
| **Native iOS/Android/Expo/Flutter apps & responsive mobile-web UX** | [Mobile Apps Engineering and UX](references/mobile-apps-engineering-ux.md) | [UI Redesign Audit (parity/a11y)](templates/ui-redesign-audit.md) | Platform-idiomatic views + thumb/safe-area pass |
| **BI/ops dashboards, KPI strips, 25-type charts, live streams, stats viz** | [Dashboards and Data Visualization](references/dashboards-and-data-visualization.md) | [Dashboard Spec](templates/dashboard-spec.md) | Reconciled dashboard + accessible table fallbacks |
| **3-tier W3C DTCG tokens, compound component APIs, Storybook, WCAG docs** | [Design Systems Engineering](references/design-systems-engineering.md) | [UI Redesign Audit (token audit)](templates/ui-redesign-audit.md) | `design-system-kit` + zero-hex token lint |
| **Existing UI critique, AI-slop cleanup, Strangler-Fig modernization** | [UI Audit and Redesign](references/ui-audit-and-redesign.md) | [UI Redesign Audit](templates/ui-redesign-audit.md) | `redesign-audit-report.md` + `--before/--kept` diff |

---

## 3. Cross-Skill Boundary Index (Reference by ID Only)

Do not duplicate sibling skill internals here; invoke or consult these suite siblings by identifier when boundaries cross:

- `ui-design-craft`: Foundational OKLCH/APCA color math, typography `clamp()` theory, Gestalt/Fitts/Hick rules, CSV datasets, and deterministic `design_search.py` / `check_contrast.py` / `check_anti_slop.py` / `validate_tokens.py` CLIs.
- `figma-design-to-code`: Figma Variables/Modes, Auto Layout, Code Connect, Figma MCP extraction, Style Dictionary DTCG sync, and pixel-parity QA.
- `system-data-architecture`: Phase 3A C4 boundaries, domain models, ADRs, and multi-tenant RLS before building workspaces.
- `fullstack-api-engineering`: Backend services, OpenAPI/GraphQL/Webhooks contracts, React Server Components, and ICU/RTL localization.
- `advanced-web-app-capabilities`: Billing/webhook state machines, LLM prompt-injection defense, offline PWA outbox/store readiness, and browser visual/MCP inspection.
- `multi-layer-qa-testing`: Black-box EP/BVA/state-transition test matrices, dual-engine accessibility gates, k6 load testing, and release sign-off.
- `observability-sre-release`: OpenTelemetry RUM/CWV telemetry, canary feature flags, changelogs, and production runbooks.

---

## 4. Universal Surface Ship Floor (8 Binary Checks)

Every surface shipped by this skill MUST satisfy all eight baseline checks before handoff:

1. **Responsive Integrity**: Zero horizontal overflow across `320px`, `390x844`, and `1440px` viewports; safe-area insets and `min-height: 100dvh` applied on mobile.
2. **Complete 6-State Coverage**: Explicit `default`, `hover` (scoped under `@media (hover: hover)`), `active` (`scale(0.98)`), `focus-visible` (`2px` ring + `2px` offset), dimension-matched `loading` skeleton, composed `empty`, and inline `error` states.
3. **Motion & Reduced-Motion Parity**: GPU-composited `transform`/`opacity` transitions (`cubic-bezier(0.22, 1, 0.36, 1)`) with instant static fallbacks under `prefers-reduced-motion`.
4. **Semantic Landmarks & Keyboard Traversal**: Proper `<header>`, `<nav>`, `<main>`, skip-link, reachable controls (`>= 44px` comfortable touch target), and zero `onPaste` blocking.
5. **Visual & Anti-Slop Discipline**: Non-banned fonts/icons, unified gray temperature, nested corner math (`inner = outer - gap`), and zero fabricated copy or metrics.
6. **Data & Preservation Integrity**: Reconciled metrics across dashboard cards/charts/tables, or `100%` `--before == --kept` route/handler/input preservation on redesigns.
7. **Post-Deletion Hygiene**: Dead CSS, unused icon packages, and redundant client state mirrors deleted and build/tests re-run cleanly.
8. **Fresh Runtime Inspection**: Verified in a real browser, simulator, or Playwright/axe run during the current session (`0` console errors, `0` critical/serious `axe-core` failures).
