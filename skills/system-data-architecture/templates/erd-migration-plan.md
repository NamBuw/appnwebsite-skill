# Domain Model, ERD & Migration Plan: [System / Release Name]

> **Canonical Output Path**: `docs/architecture/data-model.md` (Sections 1–4) and `docs/architecture/migration-plan.md` (Section 5)

- **Schema Version**: `[1.0.0]`
- **Database Engine & Version**: `[PostgreSQL 16+]`
- **Multi-Tenancy Model**: `[Shared Schema + tenant_id + RLS | Schema-per-Tenant | DB-per-Tenant]`
- **Spiral ID**: `[S01 / Phase 3A]`
- **Linked ADRs**: `[ADR-0002, ADR-0003]`

---

## 1. Ubiquitous Language Glossary & Bounded Context Map

Keep canonical definitions strictly free of SQL, ORM, framework, or UI implementation details.

| Term | Bounded Context | Canonical Domain Definition | Rejected Aliases |
|---|---|---|---|
| `[Workspace]` | `[Tenancy]` | `[Isolated billing and permission boundary owning projects and members.]` | `[Org, Team, Account]` |
| `[Subscription]` | `[Billing]` | `[Time-bounded commercial entitlement tied to one Workspace and plan tier.]` | `[Plan, License]` |

| Bounded Context | Upstream / Downstream Relationship | Integration Mechanism | Exclusive Tables Owned |
|---|---|---|---|
| `[Tenancy]` | `[Upstream to Billing & Core]` | `[Public query port + domain events]` | `[workspaces, memberships]` |
| `[Billing]` | `[Downstream of Tenancy]` | `[ACL over Payment gateway + outbox]` | `[subscriptions, invoices, outbox_events]` |

---

## 2. Logical ERD & Physical Table Inventory

```text
+---------------+       1:N       +----------------+
|  workspaces   |---------------->|  memberships   |
+---------------+                 +----------------+
| id (PK)       |                 | id (PK)        |
| slug (UQ)     |                 | workspace_id   |
| created_at    |                 | user_id        |
+---------------+                 +----------------+
```

| Table (`snake_case`) | Context Owner | PK Strategy | Highest Data Tier | Partitioning Strategy | Notes |
|---|---|---|---|---|---|
| `[workspaces]` | `[Tenancy]` | `[bigint identity / UUIDv7]` | `[Internal]` | `[None (< 100M rows)]` | `[Soft/hard delete policy linked]` |
| `[outbox_events]` | `[Platform]` | `[bigint identity]` | `[Confidential]` | `[Monthly range if > 100M]` | `[Consumed via SKIP LOCKED]` |

- **Physical Type Standards**: `[text with CHECK length limits (no varchar(n)); timestamptz everywhere; numeric(p,s) for currency; zero random UUIDv4 PKs on high-write tables.]`

---

## 3. Indexes, Query Plans & Concurrency Policies

| Table | Index Name & Definition | Type | Query Pattern Served | `EXPLAIN` Target |
|---|---|---|---|---|
| `[memberships]` | `idx_memberships_workspace_user (workspace_id, user_id)` | `B-tree` | `[FK lookup + tenant membership check]` | `[Index Only Scan < 2 ms]` |
| `[invoices]` | `idx_invoices_pending (workspace_id, created_at) WHERE status = 'open'` | `Partial B-tree` | `[Open invoice queue]` | `[Index Scan < 5 ms]` |

- **Pagination Policy**: `[Keyset cursor pagination on (created_at, id) > ($1, $2) — zero deep OFFSET.]`
- **Pooling & Timeout Policy**: `[PgBouncer transaction mode sized (cores * 2) + spindle_count; work_mem * max_connections <= 25% RAM; idle_in_transaction_session_timeout = '30s'.]`
- **Lock Ordering & Upserts**: `[Update multi-row batches in deterministic ORDER BY id FOR UPDATE order; use INSERT ... ON CONFLICT for idempotent writes.]`

---

## 4. Multi-Tenancy RLS & Least-Privilege Grants

| DB Role | Privilege Scope | Transport & Auth | Prohibited Grants |
|---|---|---|---|
| `app_writer` | `SELECT, INSERT, UPDATE, DELETE on app tables` | `TLS >= 1.2 + rotated secret` | `SUPERUSER, CREATEDB, DDL, PUBLIC schema` |
| `app_readonly` | `SELECT on reporting views/tables` | `TLS >= 1.2 + read replica` | `INSERT, UPDATE, DELETE, DDL` |

- **RLS Policies**: `[ENABLE ROW LEVEL SECURITY and FORCE ROW LEVEL SECURITY on all tenant tables; wrap (select auth.uid()) / (select current_setting('app.tenant_id', true)) in scalar subqueries; index every policy filter column.]`
- **`SECURITY DEFINER` Helpers**: `[Isolated in private schema with SET search_path = '', explicit auth check, and EXECUTE revoked from PUBLIC/anon/authenticated.]`

---

## 5. Zero-Downtime Expand-and-Contract Migration Plan

- **Change Risk Tier**: `[Pre-Launch Direct Additive | Production Expand-and-Contract]`
- **Mandatory DDL Timeout Header**: `SET lock_timeout = '2s'; SET statement_timeout = '10s';`

| Phase | Target Deploy | Actions & Lock Level | Verification & Rollback Trigger |
|---|---|---|---|
| `1. Expand` | `[Deploy N-1 compatible]` | `[Add nullable column / CHECK NOT VALID / CREATE INDEX CONCURRENTLY]` | `[Zero lock waits > 2s; N-1 app passes smoke]` |
| `2. Dual-Write & Backfill` | `[Deploy N]` | `[App N writes old+new; cursor backfill 1k-5k rows/tx + sleep + ANALYZE]` | `[Replica lag < threshold; cursor idempotent]` |
| `3. Parity & Cutover` | `[Deploy N+1 / Flag]` | `[Shadow-read diff == 0; switch reads; VALIDATE CONSTRAINT]` | `[Zero parity mismatches over soak window]` |
| `4. Contract` | `[Separate cleanup PR]` | `[Remove dual-write; DROP INDEX CONCURRENTLY; drop old column]` | `[N-1 instances 100% drained before drop]` |

- **Staging Rollback Rehearsal Receipt**: `[Command executed against production-like snapshot, elapsed time, and verified zero lock escalation.]`

## References

- [Domain & Data Modeling Guide](../references/domain-data-modeling.md)
- [Zero-Downtime Migrations Guide](../references/zero-downtime-migrations.md)
- [System & Data Architecture Router](../SKILL.md)
