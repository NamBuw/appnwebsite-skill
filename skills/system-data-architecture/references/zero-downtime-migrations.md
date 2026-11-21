# Zero-Downtime Schema Migrations

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

In production, application instances version `N-1` and version `N` run concurrently during every rolling deployment. Any schema change that drops, renames, or locks a live table breaks `N-1` pods or stalls the entire connection pool behind a lock queue. Zero-downtime migrations eliminate outages by separating additive schema expansion from destructive cleanup through the 4-phase **Expand-and-Contract** protocol while avoiding unnecessary ceremony on empty pre-launch databases.

---

## 1. Decision Framework

### 1.1 Simplicity Gate: Pre-Launch Additive DDL vs. Production Expand-and-Contract

Apply **Radical Simplicity ("Least Code, Highest Craft")** to migration strategy selection:

| Environment & Data State | Migration Strategy | Ceremony Required | Rationale |
|---|---|---|---|
| **Pre-Launch / Zero Production Traffic** (`0` live users, rebuildable DB) | **Direct Additive / Baseline DDL** | Single forward SQL migration + clean rebuild check | Dual-write shims and 4-deploy cycles on empty tables add pure waste |
| **Live Production Traffic — Additive Non-Breaking** (new table, nullable col, `PG 11+` constant `DEFAULT`) | **Single-Phase Lock-Safe DDL** | `lock_timeout` + `CONCURRENTLY` index + backward-compatible `N-1` check | Safe without dual-write because existing `N-1` queries ignore new nullable columns |
| **Live Production Traffic — Breaking Change** (rename, split, type change, `NOT NULL` on existing rows, column/table drop) | **4-Phase Expand-and-Contract** | Expand -> Dual-Write + Batched Backfill -> Parity + Cutover -> Contract | Guarantees `N-1` and `N` coexist cleanly with safe instant rollback |

### 1.2 PostgreSQL & MySQL Lock-Safety Classification Matrix

Every DDL statement acquires a table lock. On busy tables, an `AccessExclusiveLock` waits behind any long-running `SELECT` and **blocks all subsequent reads and writes** until timeout—turning a 50 ms `ALTER TABLE` into a total outage.

| DDL Operation | PostgreSQL Lock Level | MySQL 8+ Lock Strategy | Production-Safe Pattern |
|---|---|---|---|
| **Create Index** | `ShareLock` (blocks ALL writes!) | `COPY` if misconfigured | PG: `CREATE INDEX CONCURRENTLY` (`ShareUpdateExclusiveLock`, non-tx); MySQL: `ALGORITHM=INPLACE, LOCK=NONE` |
| **Drop Index** | `AccessExclusiveLock` | Metadata lock | PG: `DROP INDEX CONCURRENTLY IF EXISTS`; MySQL: `ALGORITHM=INPLACE, LOCK=NONE` |
| **Add Nullable Column** | Brief `AccessExclusive` (metadata only) | `ALGORITHM=INSTANT` | Safe with `SET lock_timeout = '2s'`; in PG `11+`, constant `DEFAULT` rewrites zero rows (volatile `DEFAULT` like `clock_timestamp()` still rewrites!) |
| **Add `NOT NULL` to Existing Column** | Full table scan under `AccessExclusive` | Table copy unless validated | **2-Step PG Pattern**: `ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT VALID`, then `VALIDATE CONSTRAINT` (`ShareUpdateExclusive`) |
| **Add Foreign Key** | `ShareRowExclusive` on both tables | Table lock during check | **2-Step PG Pattern**: `ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID`, then separate `VALIDATE CONSTRAINT` |
| **Rename / Change Column Type** | `AccessExclusive` (+ full rewrite on type change) | Full table copy | Never rename or alter type in place; run **4-Phase Expand-and-Contract** |
| **Drop Column / Table** | `AccessExclusive` | Table metadata lock | Run **only in Phase 4 Contract** after `N-1` instances are 100% drained and code references deleted |

### 1.3 Backfill Batching & Timeout Thresholds

- **Mandatory DDL Timeouts**: Prepend `SET lock_timeout = '2s'; SET statement_timeout = '10s';` to every production DDL statement.
  - Aborts blocked DDL safely instead of queuing application requests behind it.
- **Batched Backfill Sizing**: Process `1,000–5,000` rows per `< 500 ms` transaction using primary-key cursors (`WHERE id > $cursor ORDER BY id LIMIT 2500`).
  - Pause `50–200 ms` between batches and throttle if replica lag exceeds `2 s` or IOPS exceeds `70%`.
- **Rule of 500 (`addyosmani/agent-skills`)**: Automate call-site codemods spanning `> 500` lines or `> 10` files instead of manual edits.

---

## 2. Step-by-Step Workflow

Apply **Token Economy**: inspect only the target table DDL, active indexes, and direct module callers rather than loading unrelated historical migration files.

1. **Classify Change Risk & Check `N-1` Compatibility Window**
   - **Inputs**: `docs/architecture/data-model.md`, `docs/architecture/migration-plan.md`, target table size/QPS, active deployment topology.
   - **Owner**: Backend / Data Engineer.
   - **Action**:
     - Determine whether the environment is pre-launch or live production; commit to 4-phase Expand-and-Contract for any breaking live change.
     - Verify zero long-running reporting queries hold conflicting locks before scheduling.
     - Prepend `SET lock_timeout = '2s'; SET statement_timeout = '10s';` to every DDL file (outside transaction blocks for `CONCURRENTLY` indexes).
   - **Output**: Classified migration ticket with lock-safety verdict and timeout header.

2. **Phase 1 — Expand (Backward-Compatible Additive Schema)**
   - **Inputs**: Classified breaking change design.
   - **Owner**: Backend / Data Engineer.
   - **Action**:
     - Add the new column (`NULL` allowed) or new table using lowercase `snake_case`.
     - Create supporting indexes with `CREATE INDEX CONCURRENTLY`.
     - Add constraints as `NOT VALID` (`CHECK (...) NOT VALID` or `FOREIGN KEY ... NOT VALID`) via idempotent `DO $$` guards.
     - Expose a temporary compatibility view only when legacy read callers require the old shape.
   - **Output**: Expanded schema live in production with zero `N-1` breakage.

3. **Phase 2 — Dual-Write & Idempotent Batched Backfill**
   - **Inputs**: Expanded schema from Phase 1.
   - **Owner**: Backend Engineer.
   - **Action**:
     - Deploy release `N` writing **both** old and new columns/tables in the same transaction while reading from the authoritative old shape (or coalescing `COALESCE(new_col, old_col)`).
     - Use a lightweight DB trigger only when multiple independent writers cannot deploy together.
     - Run a resumable cursor backfill (`WHERE id > $cursor AND new_col IS DISTINCT FROM transformed(old_col) ORDER BY id LIMIT 2500`) across short transactions with inter-batch sleep and replica-lag checks.
     - Execute `ANALYZE <table_name>;` immediately after backfill completes to update planner statistics.
   - **Output**: `100%` of historical and live rows populated with fresh planner statistics.

4. **Phase 3 — Shadow-Read Parity Verification & Cutover**
   - **Inputs**: Backfilled new column/table and live dual-writes.
   - **Owner**: Backend / SRE Lead.
   - **Action**:
     - Enable shadow reads comparing old vs. new values in metrics/logs (without failing requests) until mismatch count stays at `0` across a full soak window (`>= 24 h` for critical tables).
     - Run `ALTER TABLE ... VALIDATE CONSTRAINT ...` (takes `ShareUpdateExclusiveLock`, allowing concurrent reads and writes).
     - Flip primary read path to the new schema via config/feature flag or release `N+1` while briefly keeping old-column dual-write as an instant rollback net.
   - **Output**: Authoritative reads served from new shape with validated constraints.

5. **Phase 4 — Contract (Cleanup After Soak & `N-1` Drain)**
   - **Inputs**: Verified Phase 3 cutover after rollback window expires and all `N-1` pods are drained.
   - **Owner**: Backend Engineer.
   - **Action**:
     - In a **separate PR and deployment**, stop writing to the legacy column/table and remove dual-write code.
     - Drop obsolete triggers or compatibility views and run `DROP INDEX CONCURRENTLY IF EXISTS` on superseded indexes.
     - Drop the legacy column/table under `SET lock_timeout = '2s'`.
   - **Output**: Clean schema with zero legacy columns or transitional shims.

6. **Staging Rehearsal, Rollback Verification & Condensation Pass**
   - **Inputs**: Full migration scripts (`Expand`, `Backfill`, `Contract`) and production-like schema snapshot.
   - **Owner**: Independent Reviewer / Data Lead.
   - **Action**:
     - Rehearse the full forward sequence AND rollback path on a seeded staging clone (`pg_dump --schema-only` + synthetic volume) under concurrent simulated traffic to verify `0` lock timeouts.
     - Delete temporary dual-write feature flags, transitional views, and dead backfill scripts once Contract finishes.
   - **Output**: Staging rehearsal receipt and clean codebase free of migration scaffolding.

---

## 3. Reusable Artifact & Template

Instantiate Section 5 of [templates/erd-migration-plan.md](../templates/erd-migration-plan.md) to output `docs/architecture/migration-plan.md` for every production schema evolution.

### 3.1 Migration Contract Fields

| Template Field | Required Content | Verification Rule |
|---|---|---|
| **Change Risk Tier** | `Pre-Launch Direct` vs. `Production Expand-Contract` | Breaking live changes without Expand-Contract fail gate |
| **DDL Timeout Header** | Exact `lock_timeout` (`<= 2s`) and `statement_timeout` (`<= 10s`) | Must appear in every live DDL script |
| **Phase 1 Expand Spec** | Additive DDL, `CONCURRENTLY` indexes, `NOT VALID` constraints | Zero `DROP`, `RENAME`, or blocking table scans |
| **Phase 2 Dual-Write & Backfill** | Dual-write owner, cursor SQL, batch size (`1k–5k`), sleep/lag guard, `ANALYZE` | Backfill script must be idempotent and resumable |
| **Phase 3 Parity & Validation** | Shadow-read metric target (`0` mismatch), `VALIDATE CONSTRAINT` command, cutover flag | Rollback requires flipping flag back without data loss |
| **Phase 4 Contract & Rehearsal** | `N-1` drain confirmation, `DROP INDEX CONCURRENTLY`, staging rehearsal output | Contract lives in a separate deploy from Cutover |

### 3.2 Lock-Safe PostgreSQL Expand-and-Validate Template

```sql
-- Step A: Safe additive column + NOT VALID constraint (short metadata lock)
SET lock_timeout = '2s';
SET statement_timeout = '10s';

ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS billing_status text;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_subscriptions_billing_status_nn'
  ) THEN
    ALTER TABLE subscriptions
      ADD CONSTRAINT chk_subscriptions_billing_status_nn
      CHECK (billing_status IS NOT NULL) NOT VALID;
  END IF;
END $$;

-- Step B (outside tx block): concurrent index build
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subscriptions_billing_status
  ON subscriptions (billing_status) WHERE billing_status = 'past_due';

-- Step C (post-backfill): non-blocking validation
ALTER TABLE subscriptions VALIDATE CONSTRAINT chk_subscriptions_billing_status_nn;
```

### 3.3 Idempotent Keyset Backfill Loop Pattern

```text
cursor = 0
loop:
  UPDATE target_table SET new_col = compute(old_col)
  WHERE id IN (SELECT id FROM target_table WHERE id > cursor ORDER BY id LIMIT 2500)
    AND new_col IS DISTINCT FROM compute(old_col);
  exit if 0 rows scanned; advance cursor = max(id); sleep 100ms (pause if replica_lag > 2s)
```

---

## 4. Verification Checklist

- [ ] Every live production DDL script sets `lock_timeout` and `statement_timeout`.
  - Timeout guards prevent blocked DDL from stalling the connection pool.
- [ ] PostgreSQL index builds and drops on live tables use `CONCURRENTLY`.
  - Statements execute outside multi-statement transaction blocks.
- [ ] New `NOT NULL` and FK constraints use 2-step `NOT VALID` validation.
  - Avoids `AccessExclusiveLock` full-table scans on live rows.
- [ ] Breaking changes keep `N-1` and `N` app releases compatible concurrently.
  - Additive expansion ships before dual-write or read cutover.
- [ ] Backfill scripts iterate by keyset cursor in `1k–5k` row batches.
  - Includes inter-batch sleep, replica-lag throttling, and post-backfill `ANALYZE`.
- [ ] Shadow-read parity checks confirm zero mismatches before read cutover.
  - Instant flag/release rollback remains viable throughout soak window.
- [ ] Phase 4 Contract cleanup ships in a separate deploy post-drain.
  - Runs only after `N-1` instances drain and rollback window closes.
- [ ] Forward and rollback paths passed on a seeded staging snapshot.
  - Concurrent traffic test observed zero lock escalations.

---

## 5. Hard Quality Gate

Production schema changes pass pre-deploy gating only when these binary criteria hold:

- **PASS**: `0` blocking `CREATE/DROP INDEX` statements, `0` single-step `ALTER TABLE ... RENAME/DROP/ALTER TYPE` statements on live tables, `lock_timeout` and `statement_timeout` enforced, idempotent batched backfill tested on staging snapshot, rollback path verified, and `0` lock escalations observed during rehearsal.
- **CONCERNS**: Staging dry-run succeeded, yet soak duration or replica-lag alert thresholds still need sign-off prior to Contract deployment.
- **NOT ASSESSED**: Staging rehearsal against realistic volume or concurrent lock checks have not run — never approve a live migration without execution evidence.
- **FAIL**: Any unguarded DDL lacking `lock_timeout`, any non-concurrent index build on a populated table, any unbounded single-transaction `UPDATE` across an entire table, or mixing Schema Cutover and Contract cleanup into the same deployment.
- **Evidence Rule**: Attach exact `psql` staging dry-run stdout and `pg_locks` check before merging any production migration PR.

Run deterministic migration lint and staging rehearsal verification:

```bash
python3 -c "import pathlib, re, sys; d=pathlib.Path('migrations'); d.is_dir() or sys.exit('FAIL: migrations/ directory missing'); hits=[(str(p),i,l.strip()) for p in sorted(d.rglob('*')) if p.is_file() for i,l in enumerate(p.read_text(encoding='utf-8',errors='replace').splitlines(),1) if not l.lstrip().startswith('--') and re.search(r'\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?!CONCURRENTLY\b)', l, re.I)]; print('FAIL: non-concurrent index:', hits) if hits else print('PASS: indexes concurrent'); sys.exit(1 if hits else 0)"
psql "$STAGING_DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/expand_and_validate.sql
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Single-Deploy `RENAME` / `DROP`** | Rolling `N-1` pods crash immediately with missing-column errors | Migration renames or drops live columns in app PR | 4-Phase Expand-and-Contract across separate deploys |
| **Blocking `CREATE INDEX`** | Acquires `ShareLock`, halting all table writes for minutes or hours | `CREATE INDEX` missing `CONCURRENTLY` on prod table | Run `CREATE INDEX CONCURRENTLY` outside transactions |
| **Missing `lock_timeout` on DDL** | Waiting behind slow `SELECT`s queues every new app query behind DDL | Migration SQL lacks `SET lock_timeout = '2s'` | Set `lock_timeout = '2s'` and retry on conflict |
| **Unbounded Full-Table Backfill** | Locks rows, inflates dead tuples, and spikes replication lag | Single `UPDATE` lacking `WHERE id > $cursor LIMIT` | Cursor batches (`1k–5k` rows/tx) + sleep + `ANALYZE` |
| **Mixing Cutover & Contract** | Prevents safe rollback once legacy columns are already dropped | Same deploy flips reads and drops legacy column | Keep dual-write through soak; Contract in later PR |
| **Expand-Contract on Empty DBs** | 4-step dual-write ceremony on `0`-row tables wastes days | Dual-write shims before launch on empty tables | Use clean additive DDL until live users exist |

- **Index Hygiene**: Always verify `pg_indexes` after a failed `CREATE INDEX CONCURRENTLY` to drop any `INVALID` index before retrying.
- **Schema Parity**: Keep staging schema snapshots refreshed before rehearsing production Expand-and-Contract scripts.
