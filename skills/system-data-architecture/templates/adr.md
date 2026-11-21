# ADR-<NNNN>: <Concise Decision Title>

> **Canonical Output Path**: `docs/architecture/adr/adr-NNNN-<slug>.md`

- **Status**: `[Proposed | Accepted | Deprecated | Superseded by ADR-NNNN]`
- **Date**: `[YYYY-MM-DD]`
- **Last Verified**: `[YYYY-MM-DD]`
- **Layer**: `[Foundation | Core | Feature | Presentation]`
- **Depends On**: `[None | ADR-NNNN | UNKNOWN]`
- **Enables / Blocks**: `[ADR-NNNN / Slice-NN | None]`
- **Requirements Addressed**: `[NFR-01, FR-01]`

---

## Summary

[Write exactly two crisp sentences: sentence 1 states the architectural decision and chosen mechanism; sentence 2 states the primary trade-off accepted and measurable constraint satisfied.]

---

## 3-Criteria Sparse ADR Check

Author an ADR only when all three criteria hold true (skip ADRs for reversible local choices):

1. **Hard to Reverse**: `[Yes — explain migration/refactor cost exceeding 1-2 engineering days.]`
2. **Surprising Without Context**: `[Yes — explain what a future engineer would question when reading the codebase.]`
3. **Result of a Real Trade-Off**: `[Yes — list the competing constraints balanced by this choice.]`

---

## Context & Constraints

- **Problem Statement**: `[Describe the verified technical problem and scope boundaries.]`
- **Verified Constraints & Budgets**: `[Cite exact NFRs, SLOs, compliance rules, or data volumes.]`
- **Runtime & Platform Compatibility**:

| Runtime / Platform | Minimum Version | Constraint / Pinning Note |
|---|---|---|
| `[PostgreSQL]` | `[16+]` | `[Requires native gen_random_uuid / partitioning / RLS]` |
| `[App Runtime]` | `[Node 20 LTS / Python 3.12]` | `[Pinned lockfile runtime target]` |

---

## Decision & Simplicity Analysis

- **Chosen Option**: `[Option A (Simplest High-Craft) | Option B (Justified Escalation)]` — `[State concrete choice.]`
- **Simplicity Interrogation Result**: `[Explain why native platform/database primitives suffice or cite the failed ablation/NFR evidence forcing Option B.]`

```text
[Caller / Module] --(Contract / Port)--> [Chosen Mechanism] --(Invariant)--> [Persistence / Output]
```

### Implementation Guidelines

Express enforceable rules for extraction into `control-manifest.md` using explicit `"must"` and `"must never"` statements:

1. `[Modules MUST interact with <resource> exclusively through <interface/boundary>.]`
2. `[Engineers MUST NEVER bypass <invariant/timeout/parameterization rule>.]`
3. `[All <operations> MUST satisfy <latency/memory/retry ceiling>.]`

---

## Alternatives Considered

| Option | Summary | Pros | Cons / Failure Mode | Disposition |
|---|---|---|---|---|
| `Option A (Simplest Baseline)` | `[Native monolith / Postgres primitive]` | `[Zero extra ops, single tx]` | `[Specific measured limit if rejected]` | `[Selected | Rejected with NFR evidence]` |
| `Option B` | `[Alternative technology or pattern]` | `[Specific advantage]` | `[Operational complexity, cost, latency]` | `[Rejected — reason]` |

---

## Consequences, Performance Implications & Validation Criteria

- **Positive Consequences**: `[List concrete maintainability, reliability, or security gains.]`
- **Negative Consequences & Mitigations**: `[List accepted trade-offs and compensating controls.]`
- **Performance & Resource Budgets**: `[Target p95 latency, connection count, memory footprint, or payload limit.]`
- **Migration / Rollback Path**: `[How existing state or code transitions if this ADR supersedes an earlier one.]`
- **Validation Criteria**: `[Observable command, test, or benchmark proving compliance once implemented.]`

## References

- [ADRs & Control Manifest Guide](../references/adrs-and-control-manifest.md)
- [Control Manifest Template](control-manifest.md)
- [System & Data Architecture Router](../SKILL.md)
