# Webhook Idempotency & Payment State-Machine Specification

> Reusable Spiral Q2/3A/3B contract for payment, billing, Connect v2, and offline/async replay state machines. Fill every `<angle-bracket>` slot before Phase 3B implementation.

## 1. Provider, API & Secret Posture

| Field | Specification |
|---|---|
| **Provider / Transport** | `<Stripe | Billing Provider | Offline Sync Endpoint>` |
| **Pinned API Version** | `<2026-07-29.dahlia>` |
| **Client Instantiation** | `new StripeClient(<vault_rk_secret>)` (never global `api_key`) |
| **Secret Key Scope** | `<rk_live_...>` restricted key in `<AWS Secrets Manager | GCP Secret Manager | Vercel Sensitive Env>` |
| **Webhook Signature Header** | `<Stripe-Signature>` verified against **raw** unparsed request bytes |
| **CSP Allowlist** | `script-src`, `frame-src`, `connect-src` pinned to `https://*.stripe.com` (and `https://*.link.com` if enabled) |

---

## 2. Durable Event Ledger Schema (SQL)

Enforce idempotent ingestion with a database primary key or unique constraint on `<event_id>` (or `(tenant_id, idempotency_key)` for offline client mutations):

```sql
CREATE TABLE webhook_event_ledger (
  event_id        TEXT PRIMARY KEY,          -- Provider event.id or client UUIDv4 idempotency_key
  tenant_id       TEXT NOT NULL,
  provider        TEXT NOT NULL,             -- e.g. 'stripe' | 'pwa_outbox'
  event_type      TEXT NOT NULL,             -- e.g. 'invoice.paid' | 'charge.dispute.created'
  object_id       TEXT NOT NULL,             -- e.g. 'sub_...' | 'pi_...' | 'order_...'
  event_ts        TIMESTAMPTZ NOT NULL,      -- Monotonic source creation timestamp
  payload_sha256  TEXT NOT NULL,
  status          TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'applied', 'held_out_of_order', 'dead_letter')),
  attempts        INTEGER NOT NULL DEFAULT 0,
  last_error      TEXT,
  received_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  processed_at    TIMESTAMPTZ
);

CREATE INDEX idx_webhook_ledger_object_ts ON webhook_event_ledger (object_id, event_ts);
```

---

## 3. Conditional State-Transition Matrix

Every async worker transition MUST execute as an atomic conditional `UPDATE` verifying both allowed prior states and monotonic event timestamp (`last_event_ts <= <event_ts>`):

| Resource | Allowed `from_states` | Incoming Event | `to_state` | Monotonic Guard | Side Effect / Recovery |
|---|---|---|---|---|---|
| `<subscription>` | `incomplete`, `trialing`, `past_due` | `invoice.paid` | `active` | `last_event_ts <= event_ts` | Grant entitlement; reset dunning counter |
| `<subscription>` | `trialing`, `active` | `invoice.payment_failed` | `past_due` | `last_event_ts <= event_ts` | Trigger grace-period notice; retain access until `<grace_hours>` |
| `<subscription>` | `trialing`, `active`, `past_due` | `customer.subscription.deleted` | `canceled` | `last_event_ts <= event_ts` | Revoke entitlement at `current_period_end` |
| `<payment_intent>` | `requires_payment_method`, `processing` | `payment_intent.succeeded` | `succeeded` | `last_event_ts <= event_ts` | Fulfill order atomically in same DB transaction |
| `<connect_transfer>` | `settled` | `charge.dispute.created` | `dispute_reversed` | `dispute_id NOT IN reversed_disputes` | Call `transfers.createReversal` with outbound key `rev:<dispute_id>` |
| `<offline_mutation>` | `pending` | `<client_op>` | `applied` | `expected_version = current_version` | Apply mutation; return canonical server state |

---

## 4. Out-of-Order Delivery, Retries & Dead-Letter Policy

- **Fast-Ack Receiver**: Verify raw-body signature -> `INSERT ... ON CONFLICT (event_id) DO NOTHING` -> enqueue durable job -> return `HTTP 200` within `<500 ms>` (never run downstream API calls inside the HTTP handler).
- **Unknown Parent / Out-of-Order Hold**: If `<object_id>` is not yet created locally (e.g., `invoice.paid` arrives before `checkout.session.completed`), mark ledger row `held_out_of_order` and re-drive with exponential backoff (`<10s, 30s, 2m, 10m>`, max `<5>` attempts) or reconcile via `stripe.<resource>.retrieve(<object_id>)`.
- **Dead-Letter Queue (DLQ)**: After `<max_attempts>` failures, transition to `dead_letter`, page `<oncall_channel>`, and expose an idempotent replay command.

---

## 5. Outbound Idempotency-Key & Catalog/Tax Invariants

| Outbound Mutation | Deterministic `Idempotency-Key` Formula | Expiry / Window | Guardrail |
|---|---|---|---|
| `<checkout_session_create>` | `chk:<tenant_id>:<cart_or_order_id>:<attempt_epoch>` | `24 hours` | Omit `payment_method_types`; pass `integration_identifier` (`<slug>_<8chars>`) on API `2026-03-25.dahlia+` |
| `<refund_create>` | `ref:<payment_intent_id>:<refund_reason_seq>` | `24 hours` | Set `reverse_transfer: true` on Connect `destination` / `separate` charges |
| `<transfer_reversal>` | `rev:<dispute_id>:<transfer_id>` | `24 hours` | Triggered automatically on `charge.dispute.created` |

- **Catalog Invariant**: `1 Product = 1 Pricing Tier`; attach multiple `Prices` to that Product solely for cadence (`monthly`/`annual`) or currency variants.
- **Tax Invariant**: Active Head Office address + jurisdiction `TaxRegistration` (`status === 'active'`) verified before enabling `automatic_tax: { enabled: true }` (zero coexistence with manual `tax_rates`; canonical `txcd_` selected via Tax Codes API).
- **Connect v2 Tuple**: `dashboard: <full | express | none>`, `fees_collector: <stripe | application>`, `losses_collector: <stripe | application>`, `charge_pattern: <direct | destination | separate>` (verify tuple is NOT `BLOCKED`: never pair `express` + `losses_collector: "stripe"`, nor `destination`/`separate` + `losses_collector: "stripe"`).

