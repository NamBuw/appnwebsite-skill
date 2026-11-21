# Simplicity Interrogation Record (`SIR-<NNN>`) — "Least Code, Highest Craft"

- **Record ID**: [SIR-001]
- **Spiral ID**: [SP-001]
- **Target Scope**: [Architecture | Feature | UI Surface | API | Data Model | Infra / Tooling | Full Spiral]
- **Pass Stage**: [PRE-DESIGN | PRE-SHIP-CONDENSATION | BOTH]
- **Verdict**: [NOT ASSESSED | PASS | CONCERNS | FAIL] *(Precedence: `FAIL > CONCERNS > NOT ASSESSED > PASS`)*
- **Evaluated (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]

---

## 1. Mandatory 4 Socratic Self-Interrogation Questions

1. **Q1 — Simpler High-Craft Alternative**: *"For this feature/requirement, is there a simpler approach that delivers equal or HIGHER quality, UX, reliability, and maintainability?"*
   - **Response & Evidence**: [Explain the simplest alternative evaluated and why it delivers equal/higher craft, or provide measured proof if a richer mechanism is strictly required.]
2. **Q2 — Layer Deletion & Native Primitives**: *"What layers, dependencies, abstractions, or moving parts can be deleted or replaced with native platform/language/database/browser primitives?"*
   - **Response & Substitutions**: [List specific wrappers, libraries, caches, or JS widgets replaced by stdlib, SQL/Postgres primitives, HTTP semantics, `<dialog>`/`<details>`, CSS Grid/`:has()`/`clamp()`, etc.]
3. **Q3 — Verified Constraint vs. Hypothetical Scale (YAGNI)**: *"Are we solving a real, verified constraint right now or inventing complexity for hypothetical scale?"*
   - **Verified Constraint Locator & Speculative Scope Cut**: [Cite exact PRD/NFR/telemetry locator proving any non-minimal choice, and list speculative features/abstractions cut right now.]
4. **Q4 — Maximum Code & Architecture Density ("ít nhất mà tốt nhất")**: *"How do we make the code and technical architecture as concise, dense, readable, and minimal as possible while maximizing craft?"*
   - **Concrete Condensation Plan**: [Detail module consolidation, Rule-of-Three adherence, direct function calls, and deletion targets.]

---

## 2. Simplest High-Craft Option Analysis (Surfaced First)

- **Option A — Simplest High-Craft Baseline**: [Describe concrete design, moving-parts count, external dependencies added (`0` preferred), and estimated files/LOC.]
- **Option B — Added-Complexity Proposal (omit unless Option A fails a verified constraint)**: [Describe only if Option A cannot satisfy a measured constraint cited in Q3.]

| Dimension | Option A (Simplest High-Craft) | Complex Alternative | Verified Constraint Evidence | Decision |
|---|---|---|---|---|
| Moving Parts / Layers | [N layers] | [M layers] | [Citation or N/A] | [Option A / Exception] |
| External Dependencies | [N deps] | [M deps] | [Stdlib/native check] | [Option A / Exception] |
| Failure Modes & Ops Cost | [Low] | [High] | [SLO/reliability impact] | [Option A / Exception] |
| Craft / UX / Maintainability | [High] | [Same or lower] | [Criteria] | [SELECTED / REJECTED] |

---

## 3. Rejected Complexity & Native-Primitive Substitutions Ledger

| Rejected Item (Layer / Dep / Abstraction) | Anti-Overengineering Category (`Gratuitous-Wrapper \| Redundant-State-Layer \| Premature-Pattern \| Dependency-Bloat \| Over-Engineered-UI`) | Native Platform / Language / DB Replacement | Estimated Deps / LOC Saved |
|---|---|---|---|
| [e.g. Single-impl IFooService/FooServiceImpl] | [Gratuitous-Wrapper] | [Direct typed module function] | [0 deps / ~60 LOC] |
| [e.g. Custom modal JS state + portal lib] | [Over-Engineered-UI] | [Native HTML `<dialog>` + CSS] | [1 dep / ~120 LOC] |

---

## 4. Complexity Budget & Pre-Ship Deletion / Condensation Pass

- **Declared Complexity Budget**:
  - **Max New External Deps**: [N] | **Max New Architectural Layers**: [N] | **Target Max Files / Net LOC**: [N files / N LOC] | **Bundle / Latency Ceiling**: [e.g. <= 150KB gz / p95 < 200ms]
- **Pre-Ship Deletion / Condensation Checklist** *(Mandatory before `PRE-SHIP-CONDENSATION` / `BOTH` completion)*:
  - [ ] Dead code, unused exports, speculative feature flags, and single-use pass-through wrappers deleted.
  - [ ] Redundant client state/cache/CSS overrides collapsed into native HTML/CSS/SQL/HTTP primitives.
  - [ ] Every added external dependency justified against a `<= 50`–`150` LOC stdlib/native alternative and supply-chain checked.
  - [ ] Rule of Three enforced: zero speculative abstractions created for fewer than 3 real diverging call sites.
  - [ ] Full build and test suite re-run cleanly **after** deletion pass (`verification-before-completion` Iron Law).
- **Condensation Metrics**:
  - `Files Deleted: [N] | Deps Removed: [N] | Net LOC Reduced: [N] | Craft/Quality Regressions: [0]`

---

## References
- Governance: [Anti-Overengineering Simplicity Gate](../references/00-spiral-governance/anti-overengineering-simplicity-gate.md) | [Spiral Lifecycle](../references/00-spiral-governance/spiral-lifecycle.md)
- Validator: `python3 scripts/check_spiral_gates.py --stage simplicity --file <this-file> --strict`
- Sibling Templates: [Spiral Charter](spiral-charter.md) | [System Foundation Gate](system-foundation-gate.md)
- Parent Router: [SKILL.md](../SKILL.md)
