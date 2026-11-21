# API & Service Contract Specification

> **Usage**: Lock this contract during Spiral Phase 3A (or before Phase 3B vertical-slice implementation) for REST/OpenAPI, GraphQL, gRPC, Webhooks, Durable Workflows, MCP Servers, or Composable CLIs. Replace `<angle-bracket>` fields with concrete values.

## Metadata

| Field | Value |
|---|---|
| **Contract ID** | `<API-001>` |
| **Service / Slice Name** | `<orders-billing-slice>` |
| **Spiral ID** | `<Spiral-01>` |
| **Protocol Surface** | `<REST-OpenAPI | GraphQL | gRPC | Webhook | MCP | CLI>` |
| **API Version** | `<v1>` |
| **Contract Status** | `<DRAFT | LOCKED | DEPRECATED>` |
| **Owner** | `<Backend / API Engineer>` |
| **Updated (UTC)** | `<YYYY-MM-DDTHH:MM:SSZ>` |

---

## 1. Simplicity & Protocol Selection (Option A First)

| Decision Dimension | Selected Option | Rejected Complexity | Verified Constraint / NFR Justification |
|---|---|---|---|
| **Transport & Schema** | `<e.g., Flat REST JSON + OpenAPI 3.1 + RFC 9457>` | `<e.g., GraphQL federation / custom 12-field wrapper>` | `<e.g., Single web/mobile client; NFR-02 p95 < 120ms>` |
| **Backend Execution Model** | `<e.g., Modular Monolith + Postgres SKIP LOCKED>` | `<e.g., Separate Kafka cluster + microservice>` | `<e.g., < 2,000 req/min peak; single ACID transaction needed>` |
| **Frontend Boundary (if paired)** | `<e.g., RSC direct read + Server Actions + SWR>` | `<e.g., Client Redux store mirroring API>` | `<e.g., SSR TTFB < 200ms, INP <= 200ms, zero waterfalls>` |

---

## 2. Endpoint, RPC, or Tool Inventory

| Operation ID | Method & Path / Tool Name | AuthN & AuthZ Boundary Rule | Idempotency Mechanism | Rate Limit Tier | SLA p95 |
|---|---|---|---|---|---|
| `<listOrders>` | `<GET /api/v1/orders>` | `<Session/JWT + tenant_id == resource.tenant_id>` | `<Safe & idempotent (GET)>` | `<120 req/min/user>` | `<80ms>` |
| `<createOrder>` | `<POST /api/v1/orders>` | `<Session/JWT + role:member + ownership check>` | `<Idempotency-Key header + payload SHA-256>` | `<30 req/min/user>` | `<180ms>` |
| `<service_get_item>` | `<MCP tool or CLI noun-verb>` | `<Token scope: read + workspace ACL>` | `<readOnlyHint: true>` | `<60 req/min/token>` | `<150ms>` |

---

## 3. Request / Response Schemas, Pagination & Filter Whitelist

- **Schema Source of Truth**: `<docs/contracts/openapi.yaml | src/schemas/orders.ts>`
- **Input Validation Boundary**: `<Zod / Pydantic / .NET AddValidation() schema rejecting unknown fields>`
- **Public DTO Separation**: `<Explicit response fields; database internal columns excluded>`
- **Pagination Policy**: `<Cursor: ?cursor=<opaque>&limit=20 (max 100), LIMIT + 1 -> has_more, next_cursor>`
- **Allowed Filter Keys**: `<status[eq], created_at[gte|lte], amount_cents[gte|lte]>`
- **Allowed Sort Keys**: `<created_at, total_cents (prefix '-' for descending; unknown keys return 422)>`

```json
{
  "data": [
    {
      "id": "ord_01J9XYZ",
      "status": "confirmed",
      "total_cents": 4900,
      "currency": "USD",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "has_more": true,
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wMS0xNVQxMDozMDowMFoiLCJpZCI6Im9yZF8wMUo5WFlaIn0"
  }
}
```

---

## 4. RFC 9457 Problem Details Error Catalog (`application/problem+json`)

| HTTP Status | Machine `code` | `type` URI | Trigger Condition | Safe Client `detail` (No Stack/SQL) |
|---|---|---|---|---|
| `400` | `<MALFORMED_JSON>` | `<https://api.example.com/problems/malformed-json>` | `<Unparseable request body>` | `<Request body is not valid JSON.>` |
| `403` | `<FORBIDDEN_RESOURCE>` | `<https://api.example.com/problems/forbidden>` | `<Authenticated caller lacks resource ownership>` | `<You do not have permission to access this resource.>` |
| `409` | `<VERSION_CONFLICT>` | `<https://api.example.com/problems/version-conflict>` | `<Optimistic lock version mismatch or idempotency payload drift>` | `<Resource was modified concurrently; refresh and retry.>` |
| `422` | `<VALIDATION_FAILED>` | `<https://api.example.com/problems/validation-failed>` | `<Field constraint or unknown sort/filter key>` | `<One or more request parameters failed validation.>` |
| `429` | `<RATE_LIMITED>` | `<https://api.example.com/problems/rate-limited>` | `<Rate limit exceeded; emit Retry-After header>` | `<Rate limit exceeded. Retry after the indicated seconds.>` |

---

## 5. Async Webhooks, Durable Workflows & Service Seams

| Seam / Workflow / Webhook | Dependency Category | Locking / Delivery Mode | Deduplication & Replay Rule | Timeout / Retry Budget | `shortcut:` Limit & Upgrade Trigger |
|---|---|---|---|---|---|
| `<stripe.invoice.paid>` | `<External Webhook>` | `<Verify HMAC-SHA256 + ts <= 5m, fast 200 ack>` | `<INSERT processed_events(event_id) ON CONFLICT DO NOTHING>` | `<Ack < 1s; worker 5 retries exp backoff>` | `<Single Postgres outbox table; upgrade to queue at > 500 events/min>` |
| `<fulfillOrderWorkflow>` | `<Local-substitutable>` | `<Deterministic workflow + idempotent step>` | `<Step outputs persisted; FatalError on 4xx>` | `<Step timeout 15s, max 3 retries>` | `<DB state machine; upgrade to Temporal/Workflow SDK if > 1k concurrent>` |

---

## 6. Versioning, Deprecation & Verification Receipt

- **Breaking Change Policy**: `<Additive optional fields do not bump version; removals/renames/type changes create /api/v2/ with <= 2 active majors>`
- **Deprecation & Sunset Policy**: `<Emit Deprecation: true and Sunset: <HTTP-date> (>= 6 months notice); return 410 Gone after sunset>`
- **Contract Lint / Test Command**: `<npx @redocly/cli lint openapi.yaml && pytest tests/contract -q --tb=short>`
- **Latest Pass Receipt**: `<PASS | FAIL — YYYY-MM-DDTHH:MM:SSZ, exit code 0, N contract assertions passed>`

---

## 7. Frontend Route & Boundary Manifest

*(Populate when pairing this contract with SSR/RSC frontend routes per `references/fullstack-frontend-engineering.md`.)*

| `route_path` | `render_mode` | `cache_policy` | `client_leaves` | `server_actions` | `cwv_budget` |
|---|---|---|---|---|---|
| `</workspaces/[id]/orders>` | `<PPR-'use cache' + <Suspense>>` | `<cacheLife('minutes'), cacheTag('orders-' + id), updateTag>` | `<OrderFilterBar.tsx, CancelOrderDialog.tsx (14 KB gz)>` | `<cancelOrderAction (Zod + session + owner check)>` | `<LCP <= 1.8s, INP <= 120ms, CLS <= 0.02>` |
