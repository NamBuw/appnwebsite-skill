# Realtime Coordination, Durable Sync, Offline-First PWA & Passkeys

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

### 1.1 Transport, Coordination & Offline Escalation Ladder

Choose the simplest transport and state coordination primitive that preserves correctness under reconnects, retries, and concurrent actors:

| Tier | Primitive / Architecture | When to Choose | Hard Constraints & Scaling Limits |
|---|---|---|---|
| **1 (Default)** | **HTTP + Query Cache (`staleTime`)** | Standard CRUD, dashboards, infrequent polling (`>= 10s`) | Zero WebSocket socket overhead; rely on HTTP `ETag` / `Cache-Control` |
| **2 (One-Way)** | **Server-Sent Events (SSE)** | Live activity feeds, notifications, LLM token streaming | Automatic browser reconnect via `Last-Event-ID`; keep payloads idempotent |
| **3 (Stateful Atom)** | **WebSockets + Single-Atom Durable Object** | Multiplayer presence, room chat, seat locks, collaborative cursors | **1 DO per coordination atom** (`getByName(atomId)`), SQLite `new_sqlite_classes`; NEVER 1 global DO |
| **4 (Offline PWA)** | **IndexedDB Outbox + Background Sync + Server `UNIQUE`** | Field apps, flaky mobile networks, offline-queued mutations | Client generates `crypto.randomUUID()` `idempotency_key`; pair SW `sync` with `online` listener fallback |
| **5 (Multi-Day Saga)** | **Durable Workflows (`"use workflow"` / Temporal)** | Multi-day cross-service sagas, human timeouts, compensating rollbacks | Keep Workflow Definitions strictly deterministic; enforce **Task Queue Fairness** across tenants |
| **6 (CRDT)** | **Yjs / Automerge CRDT** | True simultaneous multi-user offline editing of rich text or vector canvas | Forbidden for normal forms/orders/inventory (use Optimistic Concurrency Control `version` or LWW) |

### 1.2 Auth, Mobile & Passkey Baselines

- **Phishing-Resistant Auth (WebAuthn Passkeys)**:
  - Issue a server-side CSPRNG `challenge` (`>= 32` random bytes) with short TTL (`<= 300s`, single-use in Redis/DB).
  - Support Conditional UI (`autocomplete="username webauthn"`, `mediation: "conditional"`).
  - Verify `origin`, `rpIdHash`, cryptographic signature, and `signCount`/backup flags on the server.
  - Provision **multi-device synced passkeys or an explicit recovery factor** so hardware loss never locks out an account.
- **Mobile Data & Delivery (Expo / React Native)**:
  - Use `expo/fetch` (avoid axios bundle/streaming overhead), store tokens exclusively in `expo-secure-store` (NEVER `AsyncStorage`), and wire `onlineManager.setEventListener` with `NetInfo`.
  - Enforce single-flight serialized token refresh (`refreshPromise` lock).
  - Treat `EXPO_PUBLIC_*` as public build-time constants (zero write secrets), and ship via EAS with `cli.appVersionSource: "remote"` and `autoIncrement: true`.

### 1.3 Sync Simplest High-Craft Check & Token Economy

- **Decision Tree (Pick Narrowest Sync & Coordination Tier)**:
  ```text
  Read-mostly or >=10s refresh tolerance?
  ├── YES -> Tier 1 (Standard HTTP + ETag / Query staleTime)
  └── NO -> Server-to-client push only?
      ├── YES -> Tier 2 (SSE with Last-Event-ID)
      └── NO -> Multi-client room / presence / lock?
          ├── YES -> Tier 3 (WebSockets + 1 SQLite Durable Object per atom)
          └── NO -> Offline mobile/field mutations?
              ├── Simultaneous rich-text editing? -> Tier 6 (CRDT)
              └── Standard records/forms -> Tier 4 (IndexedDB Outbox + UUID key + OCC)
  ```
- **Anti-Overengineering Gate**:
  - Ask: *"Do two users genuinely edit the exact same paragraph offline simultaneously, or do server-wins / optimistic version checks (`version = expected_version`) plus an IndexedDB idempotent retry outbox solve 99% of cases without CRDTs or a self-hosted Temporal cluster?"*
  - Reject CRDTs and distributed workflow engines for single-user or form-based workflows.
- **Token Economy Rule**:
  - Load only the active surface rules (Web DO/PWA vs. Expo Mobile vs. WebAuthn Passkeys).
  - Re-use the idempotency ledger contract from `webhook-state-machine.md` rather than inventing a second deduplication schema.

---

## 2. Step-by-Step Workflow

1. **Partition Coordination Atoms & Define Sync Conflict Strategy (Q2 / 3A)**
   - **Owner**: System Architect
   - **Input**: `architecture.md`, `data-model.md`, offline user stories.
   - **Output**: Atom partitioning spec + DB unique idempotency constraint.
   - **Tool**: SQL migration linter, `system-foundation-gate.md`.
     - Select the minimum viable transport tier from the Escalation Ladder.
     - Partition Cloudflare Durable Objects strictly by coordination atom (`room:<id>`, `doc:<id>`, `user:<id>` via `getByName()`)—never route global traffic through one singleton DO.
     - Define conflict resolution per mutation type (`append_only_event`, `occ_version_check`, or `server_timestamp_lww`).
     - Add a composite `UNIQUE (tenant_id, idempotency_key)` database constraint on every mutation endpoint.

2. **Implement Durable Object Storage & Client Network Resilience**
   - **Owner**: Full-Stack Engineer
   - **Input**: Atom partitioning spec, `wrangler.jsonc` (`new_sqlite_classes` migration).
   - **Output**: Race-free DO actors and resilient client fetch layer.
   - **Tool**: `@cloudflare/vitest-pool-workers`, React Query / TanStack Query, `expo/fetch`.
     - Inside Durable Objects, execute `blockConcurrencyWhile()` **exclusively inside the `constructor()`** to initialize SQLite tables (`this.ctx.storage.sql.exec`)—never per-request and never wrapping `fetch()` or external I/O.
     - Follow **persist-first, cache-second** with zero `await` points between coupled SQLite writes.
     - Keep at most one scheduled alarm per DO (`setAlarm` overwrites earlier alarms).
     - On web and Expo clients, attach `AbortController` cleanup on unmount, implement a single-flight `refreshPromise` lock preventing concurrent refresh token races, and connect `NetInfo` to `onlineManager` for automatic offline pause/resume.

3. **Wire Offline IndexedDB Outbox & WebAuthn Passkeys**
   - **Owner**: Frontend & Backend Engineer
   - **Input**: Mutation endpoints supporting `Idempotency-Key`, RP ID and origin configuration.
   - **Output**: Cross-browser offline mutation outbox + phishing-resistant passkey ceremony.
   - **Tool**: IndexedDB wrapper (`idb`), `@simplewebauthn/server` / `@simplewebauthn/browser`, Service Worker API.
     - **PWA Outbox**: Before attempting mutating requests while offline or flaky, persist `{ idempotency_key: crypto.randomUUID(), op, resource_version, payload, created_at, attempts, status: 'pending' }` in an IndexedDB `outbox` object store.
     - Register a Service Worker `sync` event tag (`Background Sync API`) **plus** an explicit `window.addEventListener('online', flushOutbox)` and manual retry button so Safari and Firefox (which lack Background Sync) flush reliably:

```ts
// Browser fallback guaranteeing outbox delivery on Safari, Firefox & Chromium
window.addEventListener("online", () => { void flushIndexedDbOutbox(); });
if ("serviceWorker" in navigator && "SyncManager" in window) {
  const reg = await navigator.serviceWorker.ready;
  await reg.sync.register("outbox-flush");
}
```

     - Server handlers record `(tenant_id, idempotency_key)` in the same transaction as the domain mutation, returning cached `200/201` on replay.
     - **WebAuthn Passkeys**: Expose `/auth/passkey/options` generating a single-use `>= 32`-byte CSPRNG challenge bound to session/challenge ID (`TTL <= 300s`).
     - Render inputs with `autocomplete="username webauthn"` and invoke `navigator.credentials.get({ mediation: "conditional", ... })` on mount.
     - Verify `clientDataJSON.origin`, `authenticatorData.rpIdHash`, `UP`/`UV` flags, signature, and `signCount` strictly on the server, and require at least one backup passkey or verified recovery code flow.

4. **Configure Expo Mobile Secure Storage & Store Release Pipeline (If Mobile)**
   - **Owner**: Mobile Engineer
   - **Input**: `app.json` / `eas.json`, backend API base URL.
   - **Output**: Hardened Expo auth client + reproducible store build config.
   - **Tool**: `eas-cli`, `expo-secure-store`, `rg`.
     - Store all refresh tokens, session keys, and PII encryption keys in `expo-secure-store` (forbid `AsyncStorage` for secrets).
     - Audit all `EXPO_PUBLIC_*` variables to confirm zero private keys or webhook secrets exist in the client bundle.
     - Configure `eas.json` with `cli.appVersionSource: "remote"`, `autoIncrement: true`, and an internal `developmentClient: true` profile.
     - Promote Android tracks (`internal -> closed -> open -> production`) and iOS TestFlight (`npx testflight`) via `.eas/workflows/release.yml`.

5. **Deletion / Condensation & Fault-Injection Verification Pass**
   - **Owner**: Engineer & QA Lead
   - **Input**: Synced client/server implementation.
   - **Output**: Lean, fault-tested realtime/offline implementation.
   - **Tool**: Vitest (`@cloudflare/vitest-pool-workers`), Playwright offline emulation (`context.setOffline(true)`).
     - Delete speculative CRDT libraries, unused WebSocket heartbeat loops, or redundant local Redux sync caches when server OCC + IndexedDB outbox covers the workflow.
     - Run fault-injection tests: toggle offline mid-mutation, replay the identical `idempotency_key` three times, simulate DO hibernation/eviction between alarms, and verify Safari/Firefox `online` event flush behavior.

---

## 3. Reusable Artifact & Template

Reuse the idempotent ledger and state-transition mechanics from [Webhook State Machine Template](../templates/webhook-state-machine.md) (`provider = 'pwa_outbox'`, `event_id = idempotency_key`) and pair it with this concrete **Offline Outbox, Sync & Passkey Contract**:

### 3.1 Offline Outbox, Sync & Passkey Contract Fields

| Contract Field | Type / Constraint | Runtime Invariant |
|---|---|---|
| `coordination_atom_key` | `<entity_type>:<uuid>` | Maps 1:1 to `DurableObjectNamespace.getByName(atomKey)` (never global singleton) |
| `outbox_record.idempotency_key` | Client-generated `UUIDv4` (`crypto.randomUUID()`) | Generated once at user action time; reused unchanged across all retries |
| `outbox_record.resource_version` | Integer `expected_version` | Server executes `WHERE version = expected_version` returning `409 Conflict` on mismatch |
| `outbox_record.flush_triggers` | `['sw_sync', 'window_online', 'visibility_focus']` | Guarantees flush parity across Chromium, Safari, and Firefox |
| `passkey_ceremony.challenge` | Base64URL CSPRNG (`>= 32` bytes, `TTL <= 300s`) | Bound to challenge ID and deleted atomically upon first verification attempt |
| `passkey_ceremony.rp_origin` | Exact `rpId` + `https://` origin allowlist | Server rejects any origin or `rpIdHash` mismatch before signature check |
| `mobile_secret_store` | `expo-secure-store` (`Keychain` / `Keystore`) | Zero auth/session secrets in `AsyncStorage` or `EXPO_PUBLIC_*` |

### 3.2 Canonical SQLite Durable Object Constructor & Single-Flight Refresh Pattern

```ts
// Durable Object: constructor-only blockConcurrencyWhile + persist-first writes
export class RoomCoordinator extends DurableObject<Env> {
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      ctx.storage.sql.exec(`CREATE TABLE IF NOT EXISTS participants (
        user_id TEXT PRIMARY KEY, joined_at INTEGER NOT NULL
      )`);
    });
  }
}

// Client: single-flight refresh lock preventing concurrent 401 token storms
let refreshPromise: Promise<string> | null = null;
async function getFreshAccessToken(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = performTokenRefresh().finally(() => { refreshPromise = null; });
  }
  return refreshPromise;
}
```

### 3.3 Passkey Ceremony & Recovery Invariants

- Always render login inputs with `autocomplete="username webauthn"` so Conditional UI surfaces saved passkeys automatically.
- Delete or mark the issued `challenge` consumed in an atomic transaction before verifying the WebAuthn assertion response.
- Require every account enrolling a hardware-only passkey to register at least one synced passkey or verified recovery code set.

---

## 4. Verification Checklist

- [ ] Durable Objects are partitioned per coordination atom (`getByName`) with zero single-global-DO bottlenecks.
- [ ] `blockConcurrencyWhile()` appears exclusively in Durable Object constructors for schema initialization and never wraps `fetch()`.
- [ ] Offline PWA mutations generate a stable `crypto.randomUUID()` `idempotency_key` in IndexedDB before network dispatch.
- [ ] Server mutation tables enforce a `UNIQUE (tenant_id, idempotency_key)` constraint guaranteeing at-most-once side effects on replay.
- [ ] Service Worker Background Sync (`sync`) includes `window.online` and manual retry fallbacks for Safari and Firefox.
- [ ] WebAuthn passkey verification validates single-use `>= 32`-byte challenges, `origin`, `rpIdHash`, signature, and recovery fallbacks.
- [ ] Mobile apps store auth tokens exclusively in `expo-secure-store`, serialize token refreshes via single-flight locks, and keep `EXPO_PUBLIC_*` free of secrets.
- [ ] Automated tests verify offline toggle, duplicate sync replay, and Durable Object hibernation/alarm recovery.

---

## 5. Hard Quality Gate

- **PASS**:
  - Zero `blockConcurrencyWhile` calls outside DO constructors; zero auth tokens in `AsyncStorage` or `localStorage`.
  - Every offline-capable mutation endpoint enforces `(tenant_id, idempotency_key)` uniqueness; Safari/Firefox fallback flush verified.
  - WebAuthn verifies server challenge + origin + RP-ID; replay and offline E2E tests pass `100%`.
- **FAIL**:
  - Global singleton DO handling all users, or `await fetch()` inside `blockConcurrencyWhile()`.
  - Offline queue mutating without client `idempotency_key`, or relying solely on Background Sync API without `online` fallback.
  - Tokens persisted in `AsyncStorage` or leaked in `EXPO_PUBLIC_*`, or WebAuthn skipping challenge expiration or origin checks.

```bash
# 1. Scan for dangerous AsyncStorage token patterns, per-request blockConcurrencyWhile, and public-env leaks
rg -n "AsyncStorage\.(setItem|getItem).*token|blockConcurrencyWhile|EXPO_PUBLIC_.*(SECRET|KEY|TOKEN)" src/

# 2. Run Durable Object hibernation & idempotent sync replay tests
npx vitest run tests/sync/ tests/durable-objects/

# 3. Validate EAS build/versioning config when mobile targets exist
npx eas-cli@latest config --platform all --profile production
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Single Global Durable Object** | Serializes every tenant/user through one thread, hitting CPU/throughput limits globally | `getByName("global")` or `idFromName("singleton")` | Partition 1 DO per coordination atom (`room:<id>`, `doc:<id>`, `user:<id>`) |
| **`blockConcurrencyWhile()` Per Request or Around `fetch()`** | Halts all incoming messages/WebSockets while waiting on external network latency | `blockConcurrencyWhile` inside `fetch()` or `webSocketMessage()` | Call `blockConcurrencyWhile` ONLY in `constructor()` for SQLite DDL |
| **Offline Queue Without Client `idempotency_key`** | Retries after flaky cellular drops create duplicate orders, posts, or charges | Outbox posts to `POST /items` without client UUID `Idempotency-Key` | Generate `crypto.randomUUID()` on capture and enforce server `UNIQUE (tenant_id, key)` |
| **Background Sync Only (No `online` Fallback)** | Safari and Firefox do not support `SyncManager`; queued user edits stay stuck forever | `registration.sync.register(...)` with no `online` listener or manual flush | Pair SW `sync` with `window.addEventListener('online', flushOutbox)` and retry CTA |
| **Tokens in `AsyncStorage` / Secrets in `EXPO_PUBLIC_`** | Unencrypted storage and plaintext JS bundle embedding expose credentials on rooted devices or APK inspection | `AsyncStorage` storing JWTs or `EXPO_PUBLIC_STRIPE_SECRET` | Use `expo-secure-store` for tokens and keep all write secrets on backend/edge proxies |
| **Speculative CRDT or Self-Hosted Temporal (Over-Engineering)** | Adds megabytes of sync state, tombstone GC bugs, and cluster ops for simple form CRUD | Installing Yjs/Automerge or multi-node Temporal for single-owner records | Use server `version` OCC or LWW + IndexedDB outbox; adopt Temporal/CRDT only when proven |
| **Single-Device Passkey Without Recovery Factor** | Lost or wiped device permanently locks users out of accounts | Passkey registration with zero backup passkey, synced provider, or recovery codes | Support synced multi-device passkeys plus verified recovery codes or secondary credential |
