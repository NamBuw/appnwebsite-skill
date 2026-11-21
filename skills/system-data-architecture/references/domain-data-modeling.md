# Domain & Data Modeling

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Data schemas outlive frameworks, API versions, and frontend rewrites. A sloppy data model multiplies bugs across every query, permissions check, and migration for years. During Spiral Q2 and Phase 3A, align Domain-Driven Design (`DDD`) ubiquitous language and bounded contexts directly with battle-tested PostgreSQL schema, indexing, concurrency, connection pooling, and Row-Level Security (`RLS`) primitives.

---

## 1. Decision Framework

### 1.1 Simplicity & Single-Database First Rule ("Least Code, Highest Craft")

Surface **Option A (One ACID PostgreSQL Database with Bounded Schemas/Tables)** first. Exhaust native PostgreSQL primitives before provisioning Redis, Elasticsearch, or document stores:

- **Full-Text Search**: Generated `tsvector` + `GIN` index (`< 10 ms`) before Elasticsearch.
- **Semi-Structured Data**: `JSONB` with `jsonb_path_ops` `GIN` (`2–3x` smaller) or expression B-tree index.
- **Job Queues**: `SELECT ... FOR UPDATE SKIP LOCKED` inside PostgreSQL before Kafka or RabbitMQ.
- **Idempotent Upserts**: Atomic `INSERT ... ON CONFLICT DO UPDATE / NOTHING`.

Split physical stores only when load testing proves single-DB throughput, retention, or compliance boundaries fail.

### 1.2 Bounded Context & Aggregate Sizing Rules

- **Exclusive Context Ownership**: One bounded context owns each table exclusively.
  - Cross-context reads pass through exposed interfaces or views; direct cross-context writes are banned.
  - Wrap external API models in an `Anti-Corruption Layer` at context boundaries.
- **Small Aggregates**: Limit each aggregate to one root entity plus tightly coupled value objects updated in `< 50 ms` transactions.
  - Reference foreign aggregates strictly by ID.
- **Pure Ubiquitous Language**: Keep `GLOSSARY.md` (`GLOSSARY-MAP.md` for multi-context repos) strictly free of SQL, ORM, or HTTP terms.

### 1.3 Multi-Tenancy Isolation Matrix

| Isolation Model | When to Choose | Operational & Migration Cost | Security & Noisy-Neighbor Profile |
|---|---|---|---|
| **Option A: Shared Schema + `tenant_id` + RLS** | Default for `95%` of B2B/B2C SaaS apps (`1–100k+` tenants) | Lowest — single migration target, shared connection pool | Strong when `FORCE ROW LEVEL SECURITY` + indexed `tenant_id` enforced |
| **Option B: Schema-per-Tenant** | Strict per-tenant backup/restore or custom schema extensions (`<= 500` tenants) | Medium-High — `N` schema migrations and `search_path` management | Strong logical separation; watch catalog bloat above `500` tenants |
| **Option C: Database-per-Tenant** | Enterprise HIPAA/FedRAMP, regional data residency, or dedicated hardware SLAs | Highest — automated provisioning, per-tenant pools, fleet migrations | Physical isolation; eliminates cross-tenant noisy-neighbor risk |

### 1.4 PostgreSQL Key, Type, Index & Partitioning Selection

Synthesizing MIT-licensed `supabase-postgres-best-practices` rules:

| Design Choice | Standard Choice | Avoid / Ban | Quantitative Threshold & Rationale |
|---|---|---|---|
| **Primary Keys** | `bigint generated always as identity` or `UUIDv7` / ULID | Random `UUIDv4` on high-write tables | Random `UUIDv4` fragments B-trees; `UUIDv7` stays time-ordered |
| **Data Types** | `text` + `CHECK`, `timestamptz`, `numeric(p,s)`, `boolean` | `varchar(n)`, `timestamp`, `float` money | Lowercase `snake_case` unquoted identifiers prevent case bugs |
| **Foreign Key Indexes** | Explicit B-tree index on **every** FK column | Relying on parent PK index | Postgres never auto-indexes FKs; unindexed FKs scan on delete |
| **Composite Indexes** | Equality `=` first, range (`>`, `<`) last; `INCLUDE (...)` | Leading with low-cardinality range/bool | Matches left-to-right B-tree traversal |
| **Index Families** | `B-tree`, `GIN` (`JSONB @>`, `tsvector`), `GiST`, `BRIN`, `Hash` | Indexing every column indiscriminately | `BRIN` is `10–100x` smaller on monotonic time columns |
| **Partial Indexes** | `WHERE deleted_at IS NULL` or `status = 'pending'` | Indexing `99%` historical closed rows | Shrinks hot working set to active rows only |
| **Partitioning** | Declarative `PARTITION BY RANGE (created_at)` | Partitioning `< 10M` row tables | Partition only above `~100M` rows or for `DROP TABLE` TTL |

---

## 2. Step-by-Step Workflow

Apply **Token Economy** by checking existing schema files via targeted section/DDL searches rather than dumping entire migration histories into context.

1. **Establish Ubiquitous Language (`GLOSSARY.md` / `GLOSSARY-MAP.md`)**
   - **Inputs**: `docs/product/prd.md`, domain stakeholder notes, `docs/architecture/architecture.md`.
   - **Owner**: Domain Lead / System Architect.
   - **Action**:
     - Interview specs to resolve overloaded nouns (`Account` vs. `Workspace` vs. `User`, `Cancel` vs. `Refund`) with explicit rejected aliases.
     - Keep canonical definitions 100% devoid of SQL types, framework classes, or transport terms.
   - **Output**: Domain glossary and bounded-context boundary map.

2. **Model Bounded Contexts, Aggregates & Table Ownership**
   - **Inputs**: Domain glossary and module ownership matrix.
   - **Owner**: System Architect / Data Lead.
   - **Action**:
     - Map `Upstream/Downstream` and `Anti-Corruption Layer` boundaries.
     - Define aggregate invariants (e.g., Invoice total matches line-item sum) and assign each physical table an exclusive owning context.
   - **Output**: Bounded context ownership table and aggregate invariant list.

3. **Design Logical & Physical ERD (3NF First, Controlled Denormalization)**
   - **Inputs**: Core user flows and read/write NFRs.
   - **Owner**: Data / Backend Engineer.
   - **Action**:
     - Normalize to **Third Normal Form (`3NF`)** first.
     - Use `bigint identity` or `UUIDv7` PKs, `timestamptz`, `numeric(p,s)` money, `text` + `CHECK`, and `snake_case` identifiers.
     - Denormalize only with a measured read NFR plus explicit stale-sync ownership.
     - Tag every column with its privacy tier (`Public` through `Regulated`).
   - **Output**: Logical ASCII ERD and physical table inventory.

4. **Enforce Constraints, Indexes, Keyset Pagination & Concurrency Primitives**
   - **Inputs**: Physical table inventory and top query paths.
   - **Owner**: Backend Engineer.
   - **Action**:
     - Add `NOT NULL`, `UNIQUE`, `CHECK`, and FK constraints using idempotent `DO $$` guards.
     - Index every FK column, hot `WHERE`/`JOIN` predicates, `(eq_col, range_col)` composites, and active partial queues.
     - Enforce **keyset/cursor pagination** `(created_at, id) > ($1, $2)` (ban deep `OFFSET`).
     - Kill N+1 queries via `JOIN` / `= any($1::bigint[])`, batch inserts (`~1k` rows or `COPY`), and lock via `ORDER BY id FOR UPDATE`.
   - **Output**: DDL + index spec and query-pattern budget.

5. **Configure Multi-Tenant RLS, Least-Privilege Roles & Connection Pooling**
   - **Inputs**: Multi-tenancy decision and security baseline.
   - **Owner**: Security / Database Engineer.
   - **Action**:
     - Revoke `PUBLIC` defaults; create `app_writer` and `app_readonly` roles (no `SUPERUSER`, `CREATEDB`, or DDL; enforce `TLS >= 1.2` and parameterized SQL).
     - Enable `ENABLE` + `FORCE ROW LEVEL SECURITY` on tenant tables.
     - Wrap `(select auth.uid())` or `(select current_setting('app.tenant_id', true))` in a scalar subquery and index all RLS columns.
     - Isolate `SECURITY DEFINER` helpers in `private` schema with `SET search_path = ''`, caller checks, and `REVOKE EXECUTE` from `PUBLIC`/`anon`/`authenticated`.
     - Size `PgBouncer` `(cores * 2) + spindle_count`, keep `work_mem * max_connections <= 25%` RAM, set `idle_in_transaction_session_timeout = '30s'`, and disable named prepared statements under transaction pooling.
   - **Output**: Hardened role/RLS SQL policy set and pooler configuration.

6. **Profile Query Plans, Tune Autovacuum & Run Condensation Pass**
   - **Inputs**: Seeded schema and top 10 queries.
   - **Owner**: Backend / DBA Lead.
   - **Action**:
     - Run `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` against realistic row volumes and enable `pg_stat_statements`.
     - Tune `autovacuum` (`0.05` vacuum / `0.02` analyze) on high-churn tables.
     - Delete speculative EAV tables, prefix-shadowed indexes, and unused columns.
   - **Output**: Verified query plans and condensed physical schema.

---

## 3. Reusable Artifact & Template

Instantiate Sections 1–4 of [templates/erd-migration-plan.md](../templates/erd-migration-plan.md) to output `docs/architecture/data-model.md` for every domain and schema foundation.

### 3.1 Field-by-Field Schema Contract

| Template Section | Required Content | Enforcement Rule |
|---|---|---|
| **1. Glossary & Bounded Contexts** | Domain-only `GLOSSARY` table + Context Ownership matrix | Zero SQL/framework terms in Glossary; zero shared-write tables |
| **2. Logical ERD & Physical Tables** | ASCII ERD + Table inventory (`PK`, `Data Tier`, `Partitioning`) | `timestamptz`, `numeric`, `text`, lowercase `snake_case`, no `UUIDv4` hot PKs |
| **3. Indexes, Query Plans & Pooling** | FK indexes, composite/partial/GIN/BRIN specs, keyset cursor, PgBouncer math | `100%` FK columns indexed; zero `OFFSET` on unbounded feeds |
| **4. Multi-Tenancy RLS & Roles** | Least-privilege roles, `FORCE RLS`, `(select auth.uid())`, `private` helper inventory | App role lacks superuser/DDL; every RLS filter column indexed |

### 3.2 Hardened Multi-Tenant RLS & Role Reference Pattern

```sql
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE ROLE app_writer NOINHERIT LOGIN PASSWORD '...';

ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces FORCE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_workspaces_owner ON workspaces (owner_id);

CREATE POLICY workspaces_owner_isolation ON workspaces
  FOR ALL TO app_writer
  USING (owner_id = (select auth.uid()))
  WITH CHECK (owner_id = (select auth.uid()));
```

- **Keyset Pagination Reference**: `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT 20;`
- **Deadlock Prevention**: Update multi-row sets in deterministic `ORDER BY id FOR UPDATE` order inside `< 50 ms` transactions.
- **Batch Sizing**: Stream bulk inserts in `~1,000`-row batches or `COPY` rather than single-row loops.
- **Pool Sizing**: Configure `PgBouncer` `(cores * 2) + spindle_count` and `work_mem * max_connections <= 25%` RAM.
- **Vacuum Hygiene**: Set `autovacuum_vacuum_scale_factor = 0.05` and `analyze = 0.02` on high-churn tables.

---

## 4. Verification Checklist

- [ ] `GLOSSARY.md` defines every domain noun without implementation leakage.
  - Zero SQL types, ORM classes, or HTTP fields appear in canonical terms.
- [ ] Each physical table belongs exclusively to one bounded context.
  - Cross-context writes occur via public ports or outbox events only.
- [ ] Every foreign-key column has an explicit supporting index in catalog checks.
  - Zero unindexed FKs exist on mutable application tables.
- [ ] High-write primary keys avoid random `UUIDv4` fragmentation.
  - Tables use `bigint identity` or time-ordered `UUIDv7` / ULID.
- [ ] Timestamps use `timestamptz` and monetary columns use `numeric(p,s)`.
  - Zero floating-point currency or timezone-naive timestamps exist.
- [ ] Multi-tenant tables enforce `FORCE ROW LEVEL SECURITY` and cached predicates.
  - Policies wrap `(select auth.uid())` and index every policy filter column.
- [ ] Runtime credentials use least-privilege `app_writer` / `app_readonly` roles.
  - `PUBLIC` defaults revoked and all SQL statements strictly parameterized.
- [ ] Core feeds use keyset pagination and pass `EXPLAIN (ANALYZE, BUFFERS)`.
  - Unbounded deep `OFFSET` queries are banned.
- [ ] `PgBouncer` pool size, `work_mem`, and idle transaction timeouts are bounded.
  - Named prepared statements are disabled under transaction pooling.

---

## 5. Hard Quality Gate

Database foundation passes Phase 3A only under explicit binary checks:

- **PASS**: `100%` of tables map to single owning contexts, `0` unindexed foreign keys exist, `100%` of tenant tables pass cross-tenant isolation tests under `app_writer` (non-owner role), `EXPLAIN (ANALYZE, BUFFERS)` confirms index usage on all primary access paths, and `0` string-interpolated SQL statements exist.
- **CONCERNS**: Minor non-blocking index tuning remains for post-MVP reporting queries while core OLTP tables, RLS isolation, and FK indexes pass cleanly.
- **NOT ASSESSED**: Seeded `EXPLAIN` plans or cross-tenant RLS integration tests have not yet run against a live PostgreSQL instance — never emit `PASS` without live catalog verification.
- **FAIL**: Any unindexed FK on mutable tables, any tenant table missing `FORCE ROW LEVEL SECURITY` (in shared-schema mode), any runtime role holding `SUPERUSER` or `BYPASSRLS`, any per-row uncached `auth.uid()` RLS scan on large tables, or any missing `EXPLAIN` check on core queries.
- **Evidence Rule**: Capture the exact FK catalog query output (`0` rows) and `EXPLAIN (ANALYZE, BUFFERS)` buffers/cost summary in the Phase 3A gate receipt.

Run automated PostgreSQL diagnostic verification against staging/local DB:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "SELECT conrelid::regclass AS table_name, a.attname AS fk_col FROM pg_constraint c JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey) WHERE c.contype = 'f' AND NOT EXISTS (SELECT 1 FROM pg_index i WHERE i.indrelid = c.conrelid AND i.indkey[0] = a.attnum);"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT id, created_at FROM workspaces ORDER BY created_at DESC, id DESC LIMIT 20;"
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **God-Table / Shared-Write Coupling** | Cross-context mutations cause hidden invariant breaks and schema lockups | `> 1` module writing to the same table | Exclusive table ownership + public ports or outbox events |
| **Unindexed Foreign Keys** | Parent deletes/updates force full sequential scans on child tables | FK column absent from leading column of any `pg_index` | Manually add `CREATE INDEX` on every FK column |
| **Random `UUIDv4` PK Fragmentation** | Random inserts scatter B-tree leaf pages, inflating WAL and cache misses | `gen_random_uuid()` on high-volume order or event tables | Use `bigint generated always as identity` or time-ordered `UUIDv7` |
| **Uncached Per-Row RLS (`auth.uid()`)** | Evaluates function per scanned row (`10–100x` slower) | `USING (user_id = auth.uid())` without scalar subquery | Wrap as `USING (user_id = (select auth.uid()))` + index column |
| **Deep `OFFSET` Pagination** | Scans and discards `N` rows on every page turn | Queries using `OFFSET $2 LIMIT $1` on large feeds | Keyset cursor `(created_at, id) < ($1, $2)` |
| **App-Only Tenant Filtering** | One omitted `WHERE tenant_id` filter leaks cross-tenant data | `relrowsecurity = false` on tenant tables in `pg_class` | Enforce `ENABLE` + `FORCE ROW LEVEL SECURITY` in Postgres |
| **Superuser Role & SQL Concat** | Exposes cluster takeover and raw SQL injection | `postgres` superuser DSN or string-interpolated queries | Scoped `app_writer` role + strictly parameterized queries |
| **Premature NoSQL / Sharding** | Adds cross-store sync drift before PG limits are tested | Adding Elasticsearch/MongoDB for `< 10M` rows without proof | Exhaust PG `tsvector` GIN, `JSONB`, `SKIP LOCKED`, and indexes |
