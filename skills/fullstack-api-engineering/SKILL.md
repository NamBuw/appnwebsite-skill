---
name: fullstack-api-engineering
description: Full-stack backend, frontend, API, i18n/l10n, and code review engineering for Spiral 3A-3C. Use when designing APIs, building services, durable workflows, SSR/RSC frontends, localization pipelines, debugging regressions, or reviewing diffs.
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  milestone: M2
  spiral_stages: "3A,3B,3C"
---

# Full-Stack & API Engineering (`fullstack-api-engineering`)

Standalone child skill governing Spiral Stages `3A`, `3B`, and `3C` implementation across backend services, durable workflows, SSR/RSC frontends, REST/GraphQL/gRPC/Webhook/MCP/CLI contracts, internationalization (`i18n`/`l10n`), and defect-first code review.

**Negative Triggers (Do NOT Load This Skill For)**:
- Product discovery, PRDs, JTBD, or use cases (handled by `product-discovery-and-specs`).
- Greenfield C4 architecture, ADRs, ERD design, or GDPR/DPIA governance (handled by `system-data-architecture`).
- Visual design systems, typography/OKLCH palettes, Figma tokens, or landing-page copywriting (handled by `ui-design-craft` / `figma-design-to-code` / `frontend-surfaces-and-redesign`).
- Full threat modeling, SAST/DAST pentests, black-box QA suites, or SRE runbooks (handled by `security-engineering` / `multi-layer-qa-testing` / `observability-sre-release`).

---

## 1. Phase 3A Hard-Stop & Radical Simplicity Pre-Check

1. **Phase 3A System-First Gate**: Before writing production routes, services, or UI components, confirm Phase 3A foundation artifacts (`architecture.md`, `data-model.md`, `control-manifest.md`, core contracts, `system-foundation-gate.md` = `UNLOCKED`) are satisfied. Skip ONLY for localized Direct-mode hotfixes (`<= 1–2` files with zero schema/API/auth boundary impact).
2. **4 Mandatory Socratic Simplicity Checks ("Least Code, Highest Craft")**:
   - *Simpler Equal-or-Higher-Quality Option*: Start with **Option A** (Modular Monolith + Postgres `SKIP LOCKED`, Server Components + native HTML `<dialog>`/`<details>` + URL `searchParams`, flat REST + RFC 9457, native `Intl.*`).
   - *Native Primitives Over Dependencies*: Never install a library when language stdlib, SQL, HTTP semantics, or HTML/CSS solves it cleanly in `<= 150` lines.
   - *Verified Constraint vs. YAGNI*: Escalate to Option B (queues, GraphQL, gRPC, client state stores) ONLY with a measured Option A failure or cited `NFR-xx`. Document bounded choices inline with `// shortcut: <limit>, <upgrade trigger>`.
   - *Pre-Ship Deletion & Condensation Pass*: Before shipping any slice, delete dead code, collapse `< 20`-LOC 1:1 wrappers, trim redundant deps, and **re-run the full build + test suite after deletion**.

---

## 2. Token-Economy & Progressive Disclosure Rules

1. **Active Module Ceiling (`<= 1–2`)**: Read ONLY the single reference module and template matching your active Spiral task. **NEVER** bulk-load all 5 reference modules into context.
2. **Targeted Range Reads**: Inspect Top TOC anchors or run heading searches first, then read bounded line ranges (`StartLine..EndLine`) for large sections. When invoked inside the parent suite, query via `python3 scripts/query_skill.py --headings skills/fullstack-api-engineering/references/<module>.md` before opening files.
3. **Quiet Verification Output**: Run tests with concise flags (`pytest -q --tb=short`, `npm test -- --silent`, `dotnet test --verbosity minimal`) and zero `@path` eager imports.

---

## 3. Progressive Disclosure Routing Table

| Spiral Stage / Task Trigger | Load Reference Module (1–2 Max) | Reusable Template | Primary Exit Artifact & Gate |
|---|---|---|---|
| **3A/3B Backend**: clean/hexagonal layers, deep modules, Postgres `SKIP LOCKED` outbox, durable workflows, Workers/ASP.NET/Node | [Backend Engineering](references/fullstack-backend-engineering.md) | [API Contract Spec](templates/api-contract-spec.md) | Unidirectional seams, `shortcut:` bounds, green unit + real-DB integration tests |
| **3B Frontend**: App Router SSR/SSG/PPR/`'use cache'`, RSC serialization, waterfall removal, compound components, SWR, CWV | [Frontend Engineering](references/fullstack-frontend-engineering.md) | [API Contract Spec](templates/api-contract-spec.md) | Zero `async` client leaves, AuthZ inside Server Actions, `LCP<=2.5s`, `INP<=200ms`, `CLS<=0.1` |
| **3A/3B APIs & Tools**: REST/OpenAPI 3.1, RFC 9457 errors, cursor pagination, `Idempotency-Key`, webhooks, GraphQL/gRPC, MCP, CLIs | [API Design & Versioning](references/api-design-and-versioning.md) | [API Contract Spec](templates/api-contract-spec.md) | Locked OpenAPI/schema contracts, `Sunset` deprecation headers, `0` breaking diffs |
| **3A/3B/3C Global**: BCP 47 negotiation, ICU MessageFormat, `Intl.*` CLDR, IANA timezones, CSS Logical Properties, RTL/BiDi, pseudo-l10n | [Internationalization & L10n](references/internationalization-and-l10n.md) | [i18n/L10n Spec](templates/i18n-l10n-spec.md) | `0` hardcoded strings, `100%` placeholder/plural parity, `+35%` pseudo-l10n + RTL `PASS` |
| **3B/3C Quality**: `P0–P3` defect-first review, Five-Axis structural remedies, Stop-the-Line/`git bisect`, Rule of 500, `Lean` audit | [Engineering & Review Standards](references/engineering-and-review-standards.md) | [Code Review Report](templates/code-review-report.md) | `0` open `P0/P1` defects, ADR compliance, post-deletion build/tests green, `Lean` metrics |

---

## 4. Spiral `3A -> 3B -> 3C` Execution Cadence

1. **3A — Lock Contracts & Simplicity Baseline**: Verify Phase 3A Foundation unlock; populate [API Contract Spec](templates/api-contract-spec.md) and/or [i18n/L10n Spec](templates/i18n-l10n-spec.md) using Option A defaults first.
2. **3B — Build Thin Vertical Slice (`<= 300` LOC Diff)**: Implement one end-to-end slice (`SQL/Domain -> Boundary Handler/Action -> Leaf UI -> Boundary Tests`) respecting unidirectional imports and RSC serialization rules.
3. **3B — Globalize Early**: Externalize messages with ICU placeholders, native `Intl.*` formatting, and CSS Logical Properties (`inline-start`/`inline-end`) instead of retrofitting localization later.
4. **3C — Pre-Ship Deletion & Condensation Pass**: Run Chesterton's Fence check, delete dead branches/deps, inline shallow wrappers, and **re-run full build + tests after deletion**.
5. **3C — Defect-First Review & Root-Cause Verification**: Audit the merge-base diff with [Code Review Report](templates/code-review-report.md) (`P0–P3`, Five-Axis, `Lean: -N lines`); apply Stop-the-Line + `git bisect` and the 3-fix architectural escalation cap on any failure.
6. **Exit Gate**: Confirm `0` `P0/P1` findings, all active Pillar 5 quality gate commands exit `0`, and record fresh post-edit verification output.
