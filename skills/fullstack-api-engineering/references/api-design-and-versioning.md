# API Design & Versioning

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs contract-first API design across Spiral Stages `3A`, `3B`, and `3C`, spanning REST/OpenAPI 3.1, RFC 9457 Problem Details, GraphQL/gRPC/WebSocket/SSE selection, signed webhooks, MCP servers, and composable agent CLIs.
It enforces **Phase 3A contract locking** and **Radical Simplicity** so clients consume predictable, minimal, evolvable interfaces.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft API Baseline & Anti-Overengineering Gate

Before introducing GraphQL federation, gRPC proto toolchains, or deeply nested generic response envelopes, apply the four simplicity checks:
1. **Option A First**:
   - Default to **flat REST JSON over HTTPS + OpenAPI 3.1 + RFC 9457 `application/problem+json` + cursor pagination**.
   - Reject custom 12-field response wrappers (`{ meta, debug, trace, data, statusCode }`) when HTTP status codes and clean resource JSON already convey the exact semantics.
2. **Protocol Escalation Requires Evidence**:
   - Escalate to GraphQL only when diverse clients require arbitrary multi-entity graph projections in one round-trip.
   - Escalate to gRPC only when both client and server are internal AND binary streaming throughput is measurably required.
3. **Zero Premature Version Proliferation**:
   - Start at `/api/v1/`.
   - Never bump major versions for additive optional response fields or new optional query parameters.
   - Maintain at most `2` active major versions concurrently.
4. **Native HTTP Semantics First**:
   - Use standard HTTP status codes, `Location`, `ETag` / `If-Match`, `Retry-After`, `Deprecation`, and `Sunset` headers instead of proprietary JSON envelope fields.
   - Keep error payloads minimal and safe (`type`, `title`, `status`, `detail`, `instance`, `code`).

### 1.2 Protocol, Streaming & Agent-Surface Selection Matrix

| Consumer / Need | Default Simplest Option A | Escalation Option B (Evidence Required) | Mandatory Contract & Safety Rule |
|---|---|---|---|
| **Web, Mobile & Partner APIs** | **REST + OpenAPI 3.1 + RFC 9457** | **GraphQL** (arbitrary client-selected nested projections) | Plural kebab-case nouns (`/api/v1/team-members`), semantic HTTP codes, cursor pagination default |
| **Internal Service-to-Service** | **Typed REST/HTTP or RPC binding** | **gRPC (`.proto` + HTTP/2)** (high-throughput streaming, both ends owned) | Versioned schema, explicit call deadlines (`<= 10s`), auth token propagation |
| **Server -> Client Live Push** | **SSE (`text/event-stream`)** | **WebSockets / SignalR** (bidirectional low-latency frames) | Auth on initial handshake, exponential backoff reconnect, external pub/sub beyond 1 node |
| **External Event Webhooks** | **Signed Webhooks (HMAC-SHA256)** | Managed event bus / stream | Verify raw-body signature + `<= 5 min` timestamp, `event_id` dedup, fast `200`/`202` ack |
| **AI Agent / Terminal Tooling** | **Composable CLI (`--json`)** or **MCP Server** | Interactive MCP widget (only if rich canvas required) | Service-prefixed `snake_case` tools (`{service}_{action}_{resource}`), strict schemas, `stdout` JSON-only |

### 1.3 Quantitative Pagination, Rate-Limit & Versioning Thresholds

- **Cursor Pagination (Default)**:
  - Format: `?cursor=<opaque>&limit=20` with hard cap `max_limit <= 100`.
  - Execution: query `LIMIT + 1` rows to compute `has_more` and `next_cursor` without `COUNT(*)` scans.
  - Scope: mandatory for feeds, public APIs, and collections `>= 10,000` rows.
- **Offset Pagination (Bounded Exception)**:
  - Format: `?page=1&per_page=20` allowed only on `< 10,000`-row admin tables requiring arbitrary page jumps.
- **Rate Limits & Headers**:
  - Emit `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` on protected routes.
  - Return `429 Too Many Requests` with `Retry-After: <seconds>` on limit breach.
- **Deprecation & Sunset**:
  - Breaking changes (removing/renaming fields, narrowing types, changing auth) require `/api/v2/`.
  - Emit `Deprecation: true` and `Sunset: <HTTP-date>` (`>= 6` months notice for external consumers).
  - Return `410 Gone` after the sunset timestamp passes.
- **Token-Economy Contract Hygiene**:
  - Keep OpenAPI schemas modular by domain (`paths/orders.yaml`) so agents inspect only the active slice.

---

## 2. Step-by-Step Workflow

1. **Model Resources, Verbs & Idempotency Semantics** *(Owner: API Engineer | Inputs: `data-model.md`, `feature-breakdown.md` | Output: Resource map)*
   - Name resources as plural kebab-case nouns (`/api/v1/invoices`, `/api/v1/workspaces/{id}/members`).
   - Keep resource nesting `<= 2` levels deep and reserve verb sub-paths strictly for non-CRUD state transitions (`POST /api/v1/orders/{id}/cancel`).
   - Enforce HTTP method semantics:
     - `GET` / `HEAD`: safe and cacheable.
     - `PUT` / `DELETE`: idempotent.
     - `POST`: returns `201 Created` + `Location` header on resource creation or `202 Accepted` for async jobs.
   - Require `Idempotency-Key` on critical side-effect `POST` mutations:
     - Store `(idempotency_key, actor_id, request_sha256, status, response_body)` atomically.
     - Return `409`/`422` if the same key is reused with a mismatched payload hash.

2. **Lock OpenAPI 3.1 Schema & RFC 9457 Error Catalog (Phase 3A Gate)** *(Owner: API Engineer | Inputs: `api-contract-spec.md` | Output: Validated OpenAPI / typed schema)*
   - Author the OpenAPI 3.1 contract (or code-first typed Zod/Pydantic/`.NET OpenAPI` synchronized 1:1) before building UI consumers.
   - Standardize **all** `4xx`/`5xx` failures to **RFC 9457 `application/problem+json`**.
   - Never return `200 OK` with `{ success: false }`, and never leak stack traces or SQL strings inside `detail`:
     ```json
     {
       "type": "https://api.example.com/problems/validation-failed",
       "title": "Validation Failed",
       "status": 422,
       "detail": "One or more request parameters failed validation.",
       "instance": "/api/v1/orders",
       "code": "VALIDATION_FAILED",
       "errors": [{ "field": "limit", "code": "OUT_OF_RANGE", "message": "Must be between 1 and 100." }]
     }
     ```

3. **Implement Query Whitelists, Cursor Pagination & Rate Limits** *(Owner: Backend/API Engineer | Inputs: `api-contract-spec.md` | Output: Hardened collection endpoints)*
   - Whitelist allowed filter operators (`?status=active&amount_cents[gte]=500`), sort fields (`?sort=-created_at,id`), and sparse fieldsets (`?fields=id,status`).
   - Reject unknown filter/sort keys with `422` so user input never reaches dynamic SQL identifiers.
   - Order cursor queries deterministically (`ORDER BY created_at DESC, id DESC`) using `LIMIT + 1` to avoid expensive `COUNT(*)` scans.
   - Apply rate-limit policies per actor/IP/key tier and return `429` + `Retry-After`.
   - Cursor query reference pattern:
     ```sql
     SELECT id, status, total_cents, created_at
     FROM orders
     WHERE tenant_id = $1 AND (created_at, id) < ($2, $3)
     ORDER BY created_at DESC, id DESC
     LIMIT $4; -- fetch limit + 1 to set has_more
     ```

4. **Author Signed Webhooks, MCP Tools & Composable CLIs (When In Scope)** *(Owner: API Engineer | Inputs: Event/agent requirements | Output: Verified integrations)*
   - **Webhooks**:
     - Verify HMAC-SHA256 over the raw unparsed body + timestamp (`<= 5 min` replay window) with constant-time comparison (`crypto.timingSafeEqual` in Node.js `node:crypto`, `crypto.subtle.timingSafeEqual` in Cloudflare Workers, or `hmac.compare_digest` in Python).
     - Deduplicate via `INSERT INTO processed_events(event_id) ... ON CONFLICT DO NOTHING`.
     - Enqueue durable worker execution and return `200`/`202` in `< 1s`.
   - **MCP Servers**:
     - Use Streamable HTTP (stateless JSON) remotely and `stdio` locally (never write logs to `stdout` under `stdio`).
     - Enforce `Origin` + `127.0.0.1` host checks against DNS rebinding on local HTTP servers.
     - Name tools `{service}_{action}_{resource}`, declare strict `inputSchema` + `outputSchema` (`structuredContent`), and bound `limit` (`20–50`).
     - Support JSON + Markdown formats, set behavioral hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), and return actionable `isError: true` hints.
   - **Composable Agent CLIs**:
     - Provide noun-verb primitives (`doctor --json`, `discover`, `resolve` name/URL->ID, `read`, bounded `--dry-run` `write`, and raw `request` fallback).
     - Emit `--json` strictly on `stdout` and diagnostics on `stderr`.
     - Exit `0` on valid empty lists, nonzero on failures, and follow `env -> config -> flag` auth precedence without printing secrets.

5. **Run Contract Diff, Deletion/Condensation Pass & Smoke Verification** *(Owner: API Engineer | Tool: OpenAPI linter + contract tests | Output: Locked contract)*
   - Diff OpenAPI specs between commits to catch accidental breaking changes:
     - Removed or renamed properties
     - Tightened input enums or types
     - Altered HTTP status codes
   - Execute **Condensation Pass**:
     - Collapse redundant 12-field wrapper envelopes.
     - Merge duplicate DTO classes sharing identical validation shapes.
     - Remove unused query parameters and speculative version branches.
   - Re-run OpenAPI lint and contract tests **after** final simplification edits.

---

## 3. Reusable Artifact & Template

- **Canonical Template**: [API Contract Spec](../templates/api-contract-spec.md)
- **Contract Scope Enforced**:
  - Endpoint inventory with explicit AuthN/AuthZ predicates
  - Request/response schemas, cursor pagination, and query allowlists
  - RFC 9457 error catalog, webhook dedup, and deprecation/sunset schedule

### API Contract Field-by-Field Specification

| Contract Field | Mandatory Requirement | Validation Rule |
|---|---|---|
| `operation_id` & `path` | Unique verb+resource ID, plural kebab-case path (`/api/v1/...`) | Zero verbs in REST resource nouns except explicit action sub-endpoints |
| `auth_and_authz` | AuthN scheme + explicit resource/tenant ownership predicate | Every non-public endpoint declares actor + ownership check |
| `idempotency_policy` | `GET`/`PUT`/`DELETE` native or `Idempotency-Key` + SHA-256 hash | `409`/`422` when reused key has different body |
| `pagination_whitelist` | Cursor (`LIMIT + 1`) default; explicit filter/sort/fields allowlists | Unknown filter/sort key returns `422` |
| `problem_catalog` | RFC 9457 `application/problem+json` entries for all error codes | Zero `200` error envelopes; zero internal stack/SQL leaks |
| `version_and_sunset` | Active major versions (`<= 2`) + `Deprecation`/`Sunset` policy | Minimum `6`-month deprecation window for public breaking changes |

---

## 4. Verification Checklist

- [ ] Option A (flat REST JSON + OpenAPI 3.1 + RFC 9457) was selected unless GraphQL/gRPC/WebSockets had verified evidence.
- [ ] Resource paths use plural kebab-case nouns (`/api/v1/orders`) with semantic HTTP status codes (`201`+`Location`, `204`, `409`, `422`, `429`).
- [ ] All error responses conform to RFC 9457 `application/problem+json` without leaking internal stack traces, paths, or SQL fragments.
- [ ] Collection endpoints default to cursor pagination (`LIMIT + 1`, `has_more`, `next_cursor`) and reject unwhitelisted sort/filter keys with `422`.
- [ ] Critical mutating `POST` endpoints enforce `Idempotency-Key` with request payload hash verification.
- [ ] Webhooks verify constant-time HMAC signatures, enforce `<= 5`-minute timestamp windows, deduplicate `event_id`, and ack quickly.
- [ ] MCP tools and CLIs separate `stdout` JSON from `stderr` logs, validate strict schemas, bound result sizes (`limit` `20–50`), and include `--dry-run` on destructive writes.
- [ ] Breaking changes bump `/api/v2/` cleanly with `Deprecation` and `Sunset` headers, and contract tests pass **after** final simplification edits.

---

## 5. Hard Quality Gate

- **PASS Criteria**:
  - OpenAPI / schema linter exits `0` with zero unapproved breaking diffs on active major versions.
  - Contract integration suite verifies `2xx` happy paths and `401`/`403` auth boundaries.
  - Contract tests confirm `409` idempotency conflicts, `422` RFC 9457 validation payloads, and `429` rate-limit headers **after** final edits.
- **FAIL Criteria**:
  - Any endpoint returning `200 OK` for domain or validation failures (`P1`).
  - Missing RFC 9457 `application/problem+json` fields or internal stack/SQL leak (`P1`).
  - Unvalidated query sort/filter interpolation (`P0`).
  - Missing `Idempotency-Key` on payment/order `POST` or unverified webhook receiver (`P0`).
  - MCP `stdio` server writing logs to `stdout` or unauthenticated remote transport (`P0`).

```bash
# Lint OpenAPI contract and run contract black-box verification tests quietly
npx @redocly/cli lint docs/contracts/openapi.yaml && pytest tests/contract -q --tb=short
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **HTTP `200 OK` Error Envelopes** | Breaks HTTP caches, proxies, client error interceptors, and status-code alerting | `{ "success": false, "error": "Not found" }` with HTTP `200` | Semantic `4xx`/`5xx` status + `Content-Type: application/problem+json` (RFC 9457) |
| **Unbounded `OFFSET` Pagination & `SELECT *`** | `OFFSET 100000` forces full index/table scans; unbounded lists exhaust server and client memory | `?page=5000` without max cap or cursor; missing `limit` bound | Keyset cursor pagination (`LIMIT + 1`, `max_limit <= 100`) and sparse field selection |
| **In-Place Breaking Contract Mutation** | Renaming JSON keys or tightening enums under `/api/v1/` silently crashes deployed mobile clients | Removed/renamed fields in OpenAPI diff without new version path | Additive optional fields in `v1`; breaking changes on `/api/v2/` with `Deprecation` + `Sunset` + `410` |
| **Unverified or Non-Idempotent Webhooks** | Missing HMAC/timestamp checks invite forged events; synchronous work causes timeouts and duplicate billing | Route parsing JSON before HMAC check or lacking `processed_events` table | Raw-body constant-time HMAC + `<= 5m` timestamp + `ON CONFLICT DO NOTHING` + fast `200` ack |
| **Premature GraphQL Federation / gRPC Overkill** | Introduces N+1 resolver complexity, schema build pipelines, and debugging friction for simple 1-client CRUD | Subgraph gateway or `.proto` compiler for 5 endpoints serving 1 web app | Flat REST JSON + OpenAPI 3.1 + typed client SDK |
| **Raw-HTTP-Only CLIs & Unbounded MCP Tools** | Forcing agents to craft raw `curl` wastes tokens and risks typos; huge MCP payloads blow context windows | CLI lacking `discover`/`resolve`/`--dry-run`; MCP returning 5,000 rows uncapped | Composable noun-verb CLI (`--json` on `stdout`) and bounded (`20–50`) paginated MCP tools |
