---
name: system-data-architecture
description: Design C4 system architecture, deep modules, sparse ADRs, programmer control manifests, DDD and PostgreSQL/RLS data models, zero-downtime expand-and-contract migrations, and GDPR/CCPA governance. Use during Spiral Q2 and Phase 3A before coding or UI authoring, or when evolving schemas, locking ADRs, or auditing privacy compliance.
license: MIT
metadata:
  author: appnwebsite-skill
  version: "1.0.0"
  parent_suite: appnwebsite-orchestrator
  spiral_stages: "Q2, 3A"
---

# System & Data Architecture

Build the system topology, module boundaries, decision records, PostgreSQL data model, migration safety protocol, and privacy foundation during **Spiral Q2 and Phase 3A** before writing feature endpoints or production UI.

> **Progressive Disclosure Rule**: Never bulk-load all five reference modules into context. Load **only the 1–2 module(s) and template(s)** matching your active architectural or data task.

---

## Non-Negotiable Foundation Gates

1. **Phase 3A System-First Gate**: Do not author production feature endpoints or UI screens until `docs/architecture/architecture.md`, `docs/architecture/data-model.md`, `docs/architecture/migration-plan.md`, `Accepted` ADRs (`docs/architecture/adr/adr-*.md`), `docs/architecture/control-manifest.md`, `docs/spiral/system-foundation-gate.md`, and a compiling walking skeleton pass verification.
2. **Anti-Overengineering & Radical Simplicity ("Least Code, Highest Craft")**: Always evaluate **Option A (Modular Monolith + single ACID PostgreSQL + native DB/platform primitives)** first. Reject microservices, external message brokers, or separate caches unless a measured `NFR` bottleneck or compliance boundary proves Option A fails.
3. **Token Economy**: When running inside the parent `appnwebsite-skill` suite, project headings or extract single sections via CLI before reading full reference files:

```bash
python3 scripts/query_skill.py --headings skills/system-data-architecture/references/greenfield-system-architecture.md
python3 scripts/query_skill.py --extract skills/system-data-architecture/references/domain-data-modeling.md "5. Hard Quality Gate"
```

---

## Standalone Pre-Flight Fallback

When invoked standalone without the Parent Orchestrator:
1. **Inspect Repo State**: Classify the workspace as `greenfield` (empty/skeleton) or `brownfield` (live schema and existing callers).
2. **Run Simplicity Gate**: Answer whether a Modular Monolith + single PostgreSQL instance + native SQL/HTTP primitives meets all verified requirements with equal or higher quality.
3. **Lock Minimal Phase 3A Contract**: Author only the required architectural/schema/privacy artifacts before modifying feature code.
4. **Verify With Fresh Receipts**: Never emit `PASS` or `GO` without running real build, SQL, or gate commands in the current session (`NOT ASSESSED` whenever unrun).

---

## Task -> Reference -> Template Routing Table

| Active Task / Trigger | Load Reference Module (1–2 Max) | Instantiate Template | Hard Precondition / Simplicity Rule |
|---|---|---|---|
| C4 L1–L4 layers, monolith vs. microservices, deep modules/seams, `DESIGN-IT-TWICE`, ASCII data-flow/state diagrams, repo skeleton, caching/outbox/rate-limits | [Greenfield System Architecture](references/greenfield-system-architecture.md) | [System Architecture](templates/system-architecture.md) -> `docs/architecture/architecture.md` | Surface Option A Modular Monolith first; apply `DESIGN-IT-TWICE` only to 1–2 core seams |
| 3-criteria sparse ADRs, dependency DAG, traceability review (`FAIL > CONCERNS > NOT ASSESSED > PASS`), programmer control manifest | [ADRs & Control Manifest](references/adrs-and-control-manifest.md) | [ADR](templates/adr.md) -> `docs/architecture/adr/adr-NNNN-<slug>.md`, [Control Manifest](templates/control-manifest.md) -> `docs/architecture/control-manifest.md` | Author ADRs only when all 3 sparse criteria hold; explicit `Proposed -> Accepted` gate |
| DDD bounded contexts, `GLOSSARY.md`, ERD, PostgreSQL PK/types/indexes/`EXPLAIN ANALYZE`/partitioning, multi-tenant RLS, DB least privilege | [Domain & Data Modeling](references/domain-data-modeling.md) | [ERD & Migration Plan](templates/erd-migration-plan.md) -> `docs/architecture/data-model.md` | Single PostgreSQL + indexed FKs + `(select auth.uid())` RLS before any store split |
| Lock-free Postgres/MySQL DDL, 4-phase expand-and-contract, batched cursor backfills, dual-write/shadow-read, rollback rehearsal | [Zero-Downtime Migrations](references/zero-downtime-migrations.md) | [ERD & Migration Plan](templates/erd-migration-plan.md) -> `docs/architecture/migration-plan.md` | Expand-and-contract mandatory for breaking live changes; `lock_timeout = '2s'` set |
| 5-tier data classification, GDPR/CCPA consent/export/erasure/crypto-shredding, TTL purges, immutable audit trails, PII masking, DPIA | [Privacy & Data Governance](references/privacy-and-data-governance.md) | [DPIA & Privacy Spec](templates/dpia-privacy.md) -> `docs/architecture/dpia-privacy.md` | Minimize PII first; enforce log redaction + immediate session revocation on erasure |

---

## Out-of-Scope & Negative Triggers (System & Data Architecture)

- Do **NOT** load for visual tokens, typography, color palettes, Figma redlines, or landing-page copywriting (route to UI/design skills).
- Do **NOT** trigger `zero-downtime-migrations.md` on empty pre-launch development schemas with zero live production rows (use simple rebuildable additive DDL until real traffic exists).
- Do **NOT** spin up full Phase 3A ceremony for a localized single-file bugfix that changes zero boundaries, schemas, or contracts (`Direct Mode`).

---

## Phase 3A Exit Criteria & Verification Commands

Phase 3A unlocks downstream coding and UI work only when:
- All Foundation ADRs (`docs/architecture/adr/adr-*.md`) hold `Status: Accepted` with an acyclic `Depends On` graph and a current `docs/architecture/control-manifest.md`.
- `docs/architecture/architecture.md`, `docs/architecture/data-model.md`, `docs/contracts/openapi.yaml` (where APIs apply), and `docs/spiral/system-foundation-gate.md` (`UNLOCKED`) are verified, walking-skeleton smoke tests pass, all FK and RLS columns are indexed, and PII/DSR safeguards are verified.

Verify Foundation artifacts standalone or inside the full `appnwebsite-skill` suite:

```bash
# Standalone project check:
python3 -c "import pathlib, sys; req=['docs/architecture/architecture.md','docs/architecture/data-model.md','docs/architecture/control-manifest.md','docs/spiral/system-foundation-gate.md']; miss=[p for p in req if not pathlib.Path(p).is_file()]; adrs=list(pathlib.Path('docs/architecture/adr').glob('adr-*.md')); print('Missing:', miss, 'ADRs:', len(adrs)); sys.exit(1 if miss or not adrs else 0)"
# When inside the full appnwebsite-skill suite:
python3 scripts/validate_skill.py . --strict --json
python3 scripts/check_spiral_gates.py --stage foundation --strict --json
```
