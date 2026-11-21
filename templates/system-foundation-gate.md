# System-First Foundation Gate (`SFG-<NNN>`)

- **Gate ID**: [SFG-001]
- **Spiral ID**: [SP-001]
- **Primary Surface**: [Landing Page | Web App / SaaS | Mobile App | Dashboard | Design System | UI Redesign | Backend / API | Full-Stack Product]
- **Lifecycle Mode**: [greenfield | brownfield]
- **Rigor Tier**: [minimal | standard | full] *(Aliases: micro -> minimal, enterprise -> full)*
- **Verdict**: [NOT ASSESSED | PASS | CONCERNS | FAIL] *(Precedence: `FAIL > CONCERNS > NOT ASSESSED > PASS`)*
- **Downstream Lock**: Feature Coding & UI Authoring = [LOCKED | UNLOCKED]
- **Evaluated (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]

> **HARD RULE (R3)**: Feature code, route handlers, business logic, and production UI authoring are **STRICTLY BLOCKED** while `Downstream Lock` is `LOCKED`. Unlock ONLY after all 6 Foundation Pillars meet their tier floor, all Section 2 checks are `[x]`, ADR dependency graph is acyclic with `Status: Accepted`, and `scripts/check_spiral_gates.py` passes.

---

## 1. Mandatory Phase 3A Foundation Pillars

| # | Foundation Pillar | Required Artifact(s) | Tier Floor (`minimal` / `standard` / `full`) | Status (`PASS \| CONCERNS \| FAIL \| NOT ASSESSED`) | Evidence Locator |
|---|---|---|---|---|---|
| 1 | **System Architecture & Boundaries** | C4 Context/Container or data-flow diagram, runtime/rendering boundary, trust zones | `minimal`: 1-page architecture + boundaries; `standard`/`full`: full C4 + failure/retry paths | [NOT ASSESSED] | [docs/architecture/architecture.md] |
| 2 | **Domain & Data Model** | Bounded contexts, ERD, PK/FK constraints, tenancy/RLS, PII tags, migration plan | `minimal`: core entity/content/form schema; `standard`/`full`: full ERD + expand-contract migration plan | [NOT ASSESSED] | [docs/architecture/data-model.md] |
| 3 | **Core Contracts & Interfaces** | OpenAPI/JSON Schema/GraphQL/RPC/Events, RFC 9457 error model, UI `design-master.md` + W3C DTCG tokens | `minimal`: typed I/O + token contract; `standard`/`full`: versioned contracts + fixtures + `tokens.json` | [NOT ASSESSED] | [docs/contracts/ or tokens.json] |
| 4 | **ADRs & Control Manifest** | Accepted Foundation ADRs (`Status: Accepted`, acyclic `Depends On`) + allowed/forbidden layer import rules | `minimal`: >=1 core ADR + layer rules; `standard`/`full`: full Foundation ADR suite + `control-manifest.md` | [NOT ASSESSED] | [docs/architecture/adr/ & control-manifest.md] |
| 5 | **Repo & Infrastructure Skeleton** | Directory layout, lockfile, `.env.example`, CI config, healthcheck, `>=1` passing smoke/unit test | `all tiers`: runnable build/lint/test skeleton mandatory | [NOT ASSESSED] | [Repo root + CI workflow + test cmd] |
| 6 | **Simplicity, Threat & Risk Pre-Checks** | Linked `SIR-<NNN>` (`PASS`/`CONCERNS`), `RSK-SP-<NNN>` (`0` unmitigated High/Critical), STRIDE entry points mapped | `all tiers`: mandatory before Phase 3B | [NOT ASSESSED] | [SIR path & RSK path] |

---

## 2. Phase 3A Pre-Code Verification Checklist

- [ ] Every foundation pillar in Section 1 meets its Rigor Tier floor with concrete file locators on disk (zero `[TBD]` or missing docs).
- [ ] Zero circular dependencies across ADR `Depends On` edges (`0` `CYCLE:` / `UNFILLED_DEPS`), and all Foundation ADRs carry `Status: Accepted` (never `Proposed`).
- [ ] Control Manifest defines allowed/forbidden dependency directions and zero feature/UI files exist outside the walking skeleton prior to gate unlock.
- [ ] Linked `RSK-SP-<NNN>` contains `0` `OPEN` risks of severity `High` or `Critical`, and zero `spikes/`/`prototypes/` imports exist in production paths.
- [ ] Linked `SIR-<NNN>` Simplicity Gate passed with Option A (Simplest High-Craft) selected or measured exception recorded.
- [ ] Walking skeleton compiles/starts cleanly and executes at least one real automated smoke/unit test (`FAIL` if test runner missing or failing).
- [ ] Independent Builder Check resolved all blocking ambiguities (`Theirs` decisions settled).

---

## 3. Conditional Risk Waivers (`CONCERNS` Verdict Only)

*(Note: `FAIL` and `NOT ASSESSED` items are non-waivable blockers and MUST prevent `UNLOCKED`.)*

| Item / Risk ID | Accepted By | Waiver Rationale | Remediation Deadline | Follow-Up Gate |
|---|---|---|---|---|
| [None or ID] | [Owner] | [Why safe to defer within current slice] | [Date or Q4] | [Q3C / Q4] |

---

## 4. Chain-of-Verification (5 Challenge Questions) & Sign-Off

1. **[TOOL ACTION]** Re-read `architecture.md` and `data-model.md` — do all S1 slice entities and boundaries match? -> [Verified evidence]
2. **[TOOL ACTION]** Execute walking-skeleton build + smoke test command freshly — what was the exact exit code? -> [Command + exit code]
3. Could any Foundation ADR still be `Proposed` or create a circular dependency? -> [Verified answer]
4. Does any production file already implement post-3A feature endpoints or UI pages? -> [Verified answer]
5. If an isolated builder receives ONLY these Foundation docs, where would they have to guess? -> [Zero guesses remaining / resolved]

- **Validator Command**: `python3 scripts/check_spiral_gates.py --stage foundation --file <this-file> --strict`
- **Unlock Invariant**: `Downstream Lock` may be set to `UNLOCKED` **only if** `Verdict` is `PASS` (or `CONCERNS` with signed waivers in Section 3), **zero** Section 1 rows are `FAIL` or `NOT ASSESSED`, and **all** Section 2 boxes are `[x]`.

---

## References
- Governance: [System-First Foundation Gate](../references/00-spiral-governance/system-first-foundation-gate.md) | [Orchestration Protocol](../references/orchestration-protocol.md)
- Sibling Templates: [Spiral Charter](spiral-charter.md) | [Simplicity Record](simplicity-interrogation-record.md) | [Risk & Spike Register](risk-spike-register.md)
- Parent Router: [SKILL.md](../SKILL.md)
