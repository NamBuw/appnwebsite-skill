---
name: appnwebsite-orchestrator
description: >-
  Use when discovering, architecting, designing, building, securing, testing,
  auditing, redesigning, or operating web apps, landing pages, SaaS dashboards,
  mobile apps, APIs, design systems, or Figma-to-code products end to end.
  Enforces iterative Spiral governance, system-first foundation gating before
  coding or UI authoring, radical simplicity ("least code, highest craft"),
  multi-layer black-box QA, security, SRE, and progressive-disclosure routing.
license: MIT
metadata:
  version: "1.0.0"
  author: nambuw
---

# App & Website Engineering Orchestrator (`appnwebsite-orchestrator`)

Lean Parent Router for the **Hierarchical Multi-Skill Suite** ([Registry](registry.json), [Orchestration Protocol](references/orchestration-protocol.md), [Source Inventory](references/source-coverage-inventory.md)). Governs full-lifecycle app and web engineering across 11 standalone Child Skills with **System-First Foundation**, **Least Code, Highest Craft ("ít nhất mà tốt nhất")**, and **Maximum Signal, Minimum Tokens**.

---

## 1. Progressive Disclosure & Context Hygiene Rules

1. **Active Child Ceiling (`<= 2`)**: Load ONLY this Parent + the exact `1–2` Child Skills active for the current Spiral stage/surface. NEVER bulk-load `references/` or all `skills/*`.
2. **CLI Query Before File Reads**: Query exact sections first via `python3 scripts/query_skill.py` (supports BM25+MMR, `--headings`, `--extract`, `--stage`, `--surface`, `--summary`).
3. **Zero `@` Eager Imports**: Never use `@path` syntax. Keep links 1 level deep (`references/...`, `templates/...`, `scripts/...`). Always invoke scripts via `python3 scripts/...`.
4. **40 KB Read Guard & Quiet Tools**: Never full-read docs `> 40 KB`; run `--headings` / `grep -n` / AST symbol lookup then `StartLine..EndLine` reads. Use quiet test flags (`pytest -q --tb=short`) and offload `> 2k`-char outputs to scratch.
5. **Disk Checkpoints**: Persist a `<= 25`-line overwrite-only `<!-- CHECKPOINT -->` in [Spiral Charter](templates/spiral-charter.md) before `/compact` or `/clear` (never rely on ephemeral todo lists).

---

## 2. Execution Mode Router (Simplicity-First)

| Mode | When to Use | Action & Target |
|---|---|---|
| **Direct Mode** | Simple localized fix (`<= 1–2` files; zero schema, API, auth, boundary, or UX-pattern impact) | Skip heavy orchestration; run Simplicity Q1/Q2 + TDD + fresh verification directly |
| **Plan-First (`/plan`)** | Standard multi-file feature, greenfield slice, or architectural change | Route to `skills/meta-plan-goal-teamwork` (`plan-first-execution`) + active 1–2 children |
| **Goal Loop (`/goal`)** | Ambiguous or iterative target requiring falsifiable receipts until exit criteria pass | Route to `skills/meta-plan-goal-teamwork` (`goal-completion-evidence-loop`) |
| **Teamwork (`/teamwork`)** | Complex cross-domain build (`>= 3` disjoint subsystems or `> 5k`-token exploration) | Route to `skills/meta-plan-goal-teamwork` (`multi-agent-teamwork-orchestration`) |

---

## 3. Spiral Model Master Workflow (`Q1 -> Q4`)

Rigor tiers: `minimal | standard | full` (aliases `micro -> minimal`, `enterprise -> full`). Verdict precedence: **`FAIL > CONCERNS > NOT ASSESSED > PASS`** (`NOT ASSESSED` outranks `PASS` on placeholders or missing telemetry).

| Quadrant | Core Objective & Action | Hard Gate & Canonical Artifact | Primary Governance Reference |
|---|---|---|---|
| **Q1** | Detect `greenfield` vs `brownfield` (`Adopt` 4-tier triage), set slice scope, Non-Goals, NFRs, Complexity Budget, `PRE-DESIGN` Simplicity check | [Spiral Charter](templates/spiral-charter.md) + [Simplicity Record](templates/simplicity-interrogation-record.md) | [Spiral Lifecycle](references/00-spiral-governance/spiral-lifecycle.md) |
| **Q2** | Score Likelihood/Severity separately, STRIDE threat model boundaries, run isolated `<= 4h` spikes / `<= 1d` prototypes (`3-PIVOT-to-KILL`) | [Risk & Spike Register](templates/risk-spike-register.md) (`0` `OPEN` High/Critical, `0` prod imports) | [Risk, Prototyping & Spikes](references/00-spiral-governance/risk-prototyping-and-spikes.md) |
| **3A** | **HARD SYSTEM-FIRST GATE**: Lock C4 Architecture, Domain/Data Model, Boundaries/`control-manifest.md`, Core Contracts + `tokens.json`, Accepted ADRs (acyclic), Runnable Walking Skeleton + smoke test | [System Foundation Gate](templates/system-foundation-gate.md) (`Downstream Lock = UNLOCKED`; **blocks all feature coding & UI authoring**) | [System-First Foundation Gate](references/00-spiral-governance/system-first-foundation-gate.md) |
| **3B** | Build thin end-to-end vertical slices (`Schema -> API -> UI -> tests`) via active Child Skills (`<= 2` loaded) | Disjoint file ownership, TDD red-green, `<= 25`-line checkpoints | [Orchestration Protocol](references/orchestration-protocol.md) |
| **3C** | **Pre-Ship Deletion/Condensation Pass** + Multi-Layer Black-Box/White-Box QA + Security SAST/DAST + re-run tests **after** deletion | `PRE-SHIP-CONDENSATION` `[x]` + fresh Iron-Law receipts | [Simplicity Gate](references/00-spiral-governance/anti-overengineering-simplicity-gate.md) |
| **Q4** | Scope Delta audit (`<= 10%` PASS, `> 25%` FAIL, `0` base -> `NOT ASSESSED`), Exit Telemetry, 5-Q Chain-of-Verification, `<= 5` carryover items | Updated [Spiral Charter](templates/spiral-charter.md) + SRE launch | [Token Economy](references/00-spiral-governance/token-economy-and-progressive-disclosure.md) |

---

## 4. Mandatory System-First & Radical Simplicity Gates

- **Phase 3A Hard Block (R3)**: Feature endpoints, business services, and production UI components/pages are **STRICTLY BLOCKED** until `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage foundation --strict` exits `0` (`UNLOCKED`). Any early feature/UI code triggers `SYSTEM_FIRST_VIOLATION`.
- **4 Mandatory Socratic Simplicity Questions ("Least Code, Highest Craft" / "ít nhất mà tốt nhất")**:
  1. *Is there a simpler approach delivering equal or HIGHER quality, UX, reliability, and maintainability?*
  2. *What layers, dependencies, wrappers, or state stores can be deleted or replaced with native platform/language/DB/HTML/CSS primitives?*
  3. *Are we solving a verified current constraint right now or inventing complexity for hypothetical scale (YAGNI)?*
  4. *How do we make code and architecture maximally concise, dense, readable, and minimal while maximizing craft?*
- **Enforcement**: Surface **Option A (Simplest High-Craft)** first; enforce a **Complexity Budget**; execute the **Pre-Ship Deletion/Condensation Pass** and re-run full tests before shipping.

---

## 5. Child Skill Orchestration & Surface Routing Table

All 11 Child Skills live under `skills/<name>/` (all 11 `status: "active"` in [Registry](registry.json)). Query first with `python3 scripts/query_skill.py --skill <name>` or `--surface <surface> --stage <stage>`.

| Surface / Lifecycle Domain | Spiral Stage(s) | Target Child Skill(s) (`skills/<name>/`) | Quick CLI Lookup |
|---|---|---|---|
| **Ideation, Brainstorming, Discovery, PRDs, Use Cases, NFRs** | `Q1`, `Q2`, `Q4` | `skills/product-discovery-and-specs/` | `python3 scripts/query_skill.py --skill product-discovery-and-specs` |
| **Greenfield Architecture, ADRs, Data/ERD, Privacy** | `Q2`, `3A` | `skills/system-data-architecture/` | `python3 scripts/query_skill.py --skill system-data-architecture` |
| **Backend / API / Full-Stack / i18n / Code Review** | `3A`, `3B`, `3C` | `skills/fullstack-api-engineering/` | `python3 scripts/query_skill.py --surface backend-api --stage 3b` |
| **UI Design Craft, Typography, OKLCH, Anti-AI-Slop** | `3A`, `3B`, `3C` | `skills/ui-design-craft/` | `python3 scripts/query_skill.py --surface design-system --stage 3a` |
| **Figma Architecture, MCP, DTCG Sync & Parity** | `3A`, `3B`, `3C` | `skills/figma-design-to-code/` | `python3 scripts/query_skill.py --skill figma-design-to-code` |
| **Landing Page, Web App/SaaS, Mobile, Dashboard, Redesign** | `3B`, `3C` | `skills/frontend-surfaces-and-redesign/` | `python3 scripts/query_skill.py --surface landing-page --stage 3b` |
| **Security, STRIDE, Auth/RBAC, SBOM, Pentest/PoC** | `Q2`, `3A`, `3C`, `Q4` | `skills/security-engineering/` | `python3 scripts/query_skill.py --skill security-engineering` |
| **Multi-Layer & Black-Box QA (EP/BVA/State/E2E/Load)** | `Q2`, `3B`, `3C`, `Q4` | `skills/multi-layer-qa-testing/` | `python3 scripts/query_skill.py --skill multi-layer-qa-testing` |
| **Observability (OTel/SLOs), CI/CD, Runbooks, Incidents** | `3A`, `3C`, `Q4` | `skills/observability-sre-release/` | `python3 scripts/query_skill.py --skill observability-sre-release` |
| **Payments, AI Guardrails, Realtime/PWA, SEO/CWV, MCP** | `Q2`, `3B`, `3C` | `skills/advanced-web-app-capabilities/` | `python3 scripts/query_skill.py --skill advanced-web-app-capabilities` |
| **Execution Modes (`/plan`, `/goal`, `/teamwork`)** | `Q1–Q4` | `skills/meta-plan-goal-teamwork/` | `python3 scripts/query_skill.py --skill meta-plan-goal-teamwork` |

*(Full-Stack E2E surfaces enter Q1 `product-discovery-and-specs` -> Q2 `system-data-architecture` + `security-engineering` -> Serial Phase 3A Unlock -> Parallel Phase 3B `fullstack-api-engineering` + `ui-design-craft` / `frontend-surfaces-and-redesign` -> Phase 3C Condensation + `multi-layer-qa-testing` + `security-engineering` -> Q4 `observability-sre-release`.)*

---

## 6. Core Suite CLI Tools

Run via `python3 scripts/...` (zero external dependencies; pass `--help` for full options):

- **Suite Validator**: `python3 scripts/validate_skill.py . --strict --json`
- **Minimal-Token Query & Budget Auditor**:
  - `python3 scripts/query_skill.py --list`
  - `python3 scripts/query_skill.py --module orchestration-protocol --pillar 5`
  - `python3 scripts/query_skill.py "system first foundation" --mmr 0.7 -n 3 --summary`
  - `python3 scripts/query_skill.py --headings references/00-spiral-governance/spiral-lifecycle.md`
  - `python3 scripts/query_skill.py --extract references/00-spiral-governance/spiral-lifecycle.md "5. Hard Quality Gate"`
  - `python3 scripts/query_skill.py --audit-budget`
- **Spiral, Phase 3A & Simplicity Gate Enforcer**: `python3 scripts/check_spiral_gates.py --project-dir <target_repo> --stage all --strict --json`
