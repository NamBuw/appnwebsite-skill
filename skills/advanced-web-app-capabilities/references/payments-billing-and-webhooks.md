# Payments, Billing, Connect v2 & Webhook Idempotency

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

### 1.1 Payment & Billing Surface Escalation Ladder

Select the simplest surface that satisfies product UX and compliance scope without building custom card-handling plumbing:

| Tier | Surface / Architecture | When to Choose | Hard Constraints |
|---|---|---|---|
| **1 (Default)** | **Payment Links** | Single-product purchase, donation, or fixed checkout without custom cart state | Zero backend checkout code; configure tax and portal in dashboard |
| **2 (Standard)** | **Hosted Checkout Sessions + Customer Portal** | SaaS subscriptions, multi-item carts, trial-to-paid, B2B `tax_id_collection` | Pass `integration_identifier` (`<slug>_<8chars>`) on API `2026-03-25.dahlia+`; omit `payment_method_types` |
| **3 (Embedded)** | **Checkout Sessions (`ui_mode: 'custom'`) + Payment Element** | Brand-locked inline checkout requiring custom DOM layout | Use Confirmation Tokens for pre-payment review; never mount legacy Card Element or Charges API |
| **4 (Off-Session)** | **PaymentIntents + SetupIntents** | Delayed capture, merchant-initiated off-session billing, saved mandate | Never build manual cron renewal loops for subscriptions (use Billing APIs + `Prices`) |
| **5 (Usage Billing)** | **Metronome vs. Billing Meters** | New complex usage-based billing (credits, enterprise commits, high-volume bursts) -> **Metronome**; existing simple pay-as-you-go -> stay on **Billing Meters** | Enforce **1 Product per pricing tier**; attach multiple `Prices` only for cadence or currency |

### 1.2 Stripe Connect Accounts v2 Responsibility Matrix

Every multi-party payment integration MUST specify the exact Accounts v2 tuple `(dashboard, fees_collector, losses_collector)` paired with `charge_pattern` (`direct | destination | separate`):

| Pattern | `dashboard` | `fees_collector` | `losses_collector` | `charge_pattern` | Gate Status | Mandatory Platform Guardrail |
|---|---|---|---|---|---|---|
| **Standard SaaS** | `full` | `stripe` | `stripe` | `direct` | `ALLOWED` | Connected account owns disputes; use hosted onboarding + CSRF `state` on OAuth |
| **Marketplace** | `express` | `application` | `application` | `destination` | `CAUTION` | Disputes debit platform first; `charge.dispute.created` MUST reverse transfer explicitly |
| **White-Label** | `none` | `application` | `application` | `destination` or `direct` | `ALLOWED` | Platform handles support, pricing, and negative-balance recovery |
| **Invalid Combos** | `express` / `none` | `stripe` | `stripe` | Any | `BLOCKED` | Never pair `express` or `none` with `losses_collector: "stripe"`; never pair `destination`/`separate` with `losses_collector: "stripe"` (`full` + `application` is `SALES-GATED`) |

### 1.3 Payments Simplest High-Craft Check & Token Economy

- **Decision Tree (Pick Narrowest Viable Payment Surface)**:
  ```text
  Single fixed item / no custom cart?
  ├── YES -> Payment Links (Tier 1, 0 checkout code)
  └── NO -> Multi-party marketplace split?
      ├── NO -> Subscriptions or cart?
      │   ├── Standard UI OK -> Hosted Checkout + Customer Portal (Tier 2)
      │   └── Custom inline DOM -> Checkout ui_mode='custom' + Confirmation Tokens (Tier 3)
      └── YES -> Select Connect v2 Tuple
          ├── SaaS platforms -> full / stripe / stripe / direct (ALLOWED)
          ├── Marketplaces -> express / application / application / destination (CAUTION)
          └── White-label -> none / application / application / destination|direct (ALLOWED)
  ```
- **Anti-Overengineering Gate**:
  - Ask: *"Can Payment Links or Hosted Checkout Sessions + Customer Portal + a single `subscriptions` projection table eliminate custom card forms, custom invoice PDFs, and Express Connect liability?"*
  - Reject `stripe-apps` React-17 iframe UIs, custom PCI card inputs, and manual `PaymentIntent` subscription-renewal schedulers.
  - Native Hosted Checkout + Billing `Prices` + Customer Portal handle upgrades, proration, and dunning with zero custom UI maintenance.
- **Token Economy Rule**:
  - During Spiral Q2 and 3B, read ONLY the active surface row (single-merchant Checkout vs. Connect v2 vs. Webhook State Machine).
  - Never bulk-load Connect dispute rules or Metronome specs when implementing a simple single-merchant SaaS subscription.
- **Quantitative Thresholds**:
  - Webhook HTTP acknowledgment latency: `< 500 ms` (hard ceiling `<= 2,000 ms` before offloading to async queue).
  - Outbound `Idempotency-Key` retention window: `24 hours` across retryable mutations.
  - DLQ retry ceiling: `<= 5` attempts with exponential backoff (`10s -> 30s -> 2m -> 10m -> 30m`).

---

## 2. Step-by-Step Workflow

1. **Pin API Version, Client Instantiation & Vault Keys**
   - **Owner**: Backend Engineer
   - **Input**: Approved `system-foundation-gate.md` and secrets-vault configuration.
   - **Output**: Typed `StripeClient` factory, CSP middleware, and least-privilege `rk_` vault bindings.
   - **Tool**: `stripe logs tail`, platform secret store CLI.
     - Pin Stripe API version `2026-07-29.dahlia` and instantiate `new StripeClient(secretKey)` per service.
     - Forbid global `stripe.api_key`, `Stripe.setApiKey`, `stripe.Key`, or `StripeConfiguration.ApiKey`.
     - Provision least-privilege Restricted API Keys (`rk_`) from Workbench request logs rather than broad `sk_` keys.
     - Store keys exclusively in the platform vault (AWS Secrets Manager/SSM, GCP Secret Manager, Azure Key Vault, or Vercel sensitive env vars).
     - Enforce strict CSP (`script-src`, `frame-src`, `connect-src` allowing `https://*.stripe.com`, plus `https://*.link.com` if enabled; forbid `default-src *`).

2. **Configure Catalog Invariants & Tax Pre-Flight**
   - **Owner**: Backend / Ops Lead
   - **Input**: Pricing tiers from `prd.md`, merchant Head Office address, active jurisdiction registrations.
   - **Output**: Verified catalog IDs, canonical `txcd_` mapping, and active Tax Registration proof.
   - **Tool**: Stripe Tax Codes API, Dashboard/CLI Tax Registrations check.
     - Create exactly **1 Product per tier** with multiple `Prices` strictly for cadence (`month`/`year`) or currency.
     - Verify active Head Office address and confirm `TaxRegistration` (`status === 'active'`) in every target customer jurisdiction **before** setting `automatic_tax: { enabled: true }`.
     - Account for silent failure: `automatic_tax` calculates `$0.00` without active registrations, and Stripe cannot recover retroactive tax.
     - Clear manual `tax_rates` (`automatic_tax` cannot coexist with `tax_rates`).
     - Select canonical `txcd_` codes from the Tax Codes API (avoid generic `txcd_10000000` in US jurisdictions).
     - Validate address resolution order (`shipping -> Customer.billing -> default_pm -> IP`, handling `customer_tax_location_invalid`) and enable `tax_id_collection` for B2B invoices.

3. **Implement Checkout, Outbound Idempotency & Connect Transfers**
   - **Owner**: Backend Engineer
   - **Input**: Catalog Price IDs, Connect tuple (if marketplace), `webhook-state-machine.md`.
   - **Output**: Idempotent checkout, refund, and Connect transfer endpoints.
   - **Tool**: Official Stripe SDK (`StripeClient`), local unit tests.
     - Create Checkout Sessions (`mode: 'payment' | 'subscription'`), passing `integration_identifier` with an 8-character random suffix on API `2026-03-25.dahlia+`.
     - **Omit `payment_method_types` everywhere** (only Terminal `card_present` / `interac_present` may pass it); use `payment_method_configurations` or `excluded_payment_method_types` when restricting methods.
     - Attach deterministic outbound `Idempotency-Key` headers on all `create`, `refund`, and `transfer` mutations (`24h` window).
     - For Connect `destination` or `separate` charges, set `reverse_transfer: true` on refunds and implement a `charge.dispute.created` handler calling `transfers.createReversal` (since `reverse_transfer` defaults to `false`).
     - Require a cryptographic CSRF `state` parameter on Connect OAuth flows and default to Standard accounts + hosted onboarding.

4. **Build Fast-Ack Webhook Receiver & Monotonic Async State Machine**
   - **Owner**: Backend Engineer
   - **Input**: Webhook signing secret (`whsec_`), PostgreSQL/SQL ledger table.
   - **Output**: Verified idempotent webhook ingestion + conditional state-transition worker.
   - **Tool**: `stripe listen --forward-to`, `stripe trigger`, PostgreSQL transaction tests.
     - Read the **raw unparsed request buffer** (`req.arrayBuffer()` / raw body middleware) before any JSON parser alters whitespace.
     - Verify `Stripe-Signature` via `stripe.webhooks.constructEvent`, then execute `INSERT INTO webhook_event_ledger (event_id, ...) ON CONFLICT (event_id) DO NOTHING`.
     - Enqueue a durable async job and return `HTTP 200` within `< 500 ms` (never run external API calls inside the HTTP handler).
     - Inside the async worker, execute conditional SQL transitions checking allowed prior states and monotonic timestamps:

```sql
UPDATE subscriptions
SET status = $1, last_event_ts = $2, updated_at = now()
WHERE stripe_sub_id = $3
  AND status = ANY($4::text[])
  AND last_event_ts <= $2;
```

     - Hold events whose parent record has not arrived in `held_out_of_order` status for exponential backoff retry or `stripe.<resource>.retrieve()` reconciliation.

5. **Deletion / Condensation & Replay Verification Pass**
   - **Owner**: Backend + QA Engineer
   - **Input**: Implemented payment code and webhook logs.
   - **Output**: Condensed payment module with passing replay proof.
   - **Tool**: `rg` static scan, `pytest` / `vitest` replay suite, `stripe trigger`.
     - Delete redundant client-side card form wrappers if Hosted Checkout covers the flow.
     - Remove unused `sk_` fallback env reads and collapse per-event boilerplate into a single declarative transition table.
     - Execute duplicate-event and out-of-order replay tests (`invoice.paid` before `checkout.session.completed`, and `subscription.deleted` before stale `invoice.paid`).

---

## 3. Reusable Artifact & Template

Instantiate [Webhook State Machine Template](../templates/webhook-state-machine.md) before writing billing handlers. Every implementation MUST lock these fields:

### 3.1 Required Webhook & Billing Contract Fields

| Field | Type / Constraint | Purpose |
|---|---|---|
| `event_id` | `TEXT PRIMARY KEY` (`evt_...`) | Guarantees at-most-once webhook ingestion via `ON CONFLICT DO NOTHING` |
| `object_id` | `TEXT NOT NULL` (`sub_...`, `pi_...`) | Correlates out-of-order events and supports `retrieve()` reconciliation |
| `event_ts` | `TIMESTAMPTZ NOT NULL` | Enforces monotonic `last_event_ts <= event_ts` transition guard |
| `allowed_from_states` | `TEXT[]` per event type | Prevents invalid transitions (e.g., `canceled -> active` from stale invoice) |
| `outbound_idempotency_key` | Deterministic `<op>:<tenant>:<ref>:<epoch>` | Prevents duplicate charges, refunds, or Connect transfer reversals on network retry |
| `connect_v2_tuple` | `(dashboard, fees, losses, charge_pattern)` | Documents dispute liability and verifies non-`BLOCKED` Connect configuration |
| `tax_registration_proof` | Active jurisdictions + `txcd_` list | Confirms `automatic_tax` actually collects tax instead of silently returning `0` |
| `dlq_policy` | Backoff schedule + max attempts (`<= 5`) | Routes unrecoverable or orphan-parent events to operator replay queue |

### 3.2 Canonical Fast-Ack Webhook Ingestion Pattern

```ts
// 1. Read raw bytes BEFORE JSON middleware parses body
const rawBody = await req.arrayBuffer();
const sig = req.headers.get("stripe-signature") ?? "";
const event = stripe.webhooks.constructEvent(Buffer.from(rawBody), sig, env.STRIPE_WEBHOOK_SECRET);

// 2. Idempotent ledger insert + async enqueue (< 500ms ACK)
const inserted = await db.query(
  `INSERT INTO webhook_event_ledger (event_id, tenant_id, provider, event_type, object_id, event_ts, payload_sha256, status)
   VALUES ($1, $2, 'stripe', $3, $4, to_timestamp($5), $6, 'queued')
   ON CONFLICT (event_id) DO NOTHING RETURNING event_id`,
  [event.id, resolveTenant(event), event.type, event.data.object.id, event.created, sha256(rawBody)]
);
if (inserted.rowCount === 1) await queue.enqueue("stripe.process", { eventId: event.id });
return Response.json({ received: true }, { status: 200 });
```

### 3.3 Connect Dispute Reversal Handler Contract

- Listen for `charge.dispute.created` on every `destination` or `separate` Connect charge flow.
- Compute `Idempotency-Key: rev:<dispute.id>:<transfer.id>` before invoking `stripe.transfers.createReversal(...)`.
- Persist the reversal ledger entry in the same transaction that flags the connected account balance for reconciliation.
- Escalate unrecovered negative balances older than `7 days` via automated payout hold or operator alert.

---

## 4. Verification Checklist

- [ ] Every Stripe SDK call uses an explicit `StripeClient` instance with zero global `api_key` assignment.
- [ ] Live and test services use least-privilege `rk_` keys in a platform vault with zero secrets in source or client bundles.
- [ ] Zero API calls pass `payment_method_types` except Terminal `card_present` or `interac_present` flows.
- [ ] Product catalog maintains one Product per pricing tier with `Prices` separated only by cadence or currency.
- [ ] Head Office address and active `TaxRegistration` records are verified before enabling `automatic_tax: { enabled: true }`.
- [ ] Webhook handler verifies `Stripe-Signature` on the raw request body, deduplicates on `event_id`, and returns `2xx` within 500ms.
- [ ] Async worker runs conditional `UPDATE` transitions guarded by `allowed_from_states` and monotonic `last_event_ts <= event_ts`.
- [ ] Out-of-order and duplicate webhook delivery tests pass deterministically against a real database constraint.
- [ ] Connect v2 tuple avoids all `BLOCKED` combinations and explicitly reverses transfers on `charge.dispute.created` for `destination` and `separate` charges.

---

## 5. Hard Quality Gate

- **PASS**:
  - Zero occurrences of global `stripe.api_key`, hardcoded `[sr]k_(live|test)_`, or non-Terminal `payment_method_types` in source.
  - Raw-body signature verification, `event_id` primary-key deduplication, and monotonic conditional SQL transitions pass duplicate and out-of-order replay tests.
  - Active Tax Registration verified when `automatic_tax` is enabled; Connect tuple verified non-`BLOCKED`.
- **FAIL**:
  - Any secret key literal in repo or client bundle, or any `payment_method_types` hardcode blocking dynamic payment methods.
  - Webhook endpoint performing synchronous external API work before returning `2xx`, or unconditional `UPDATE` susceptible to out-of-order regression.
  - `automatic_tax` enabled without active jurisdiction registrations, or any `BLOCKED` Connect tuple.

```bash
# 1. Scan for banned Stripe patterns, raw secret literals, and hardcoded payment_method_types
rg -n "stripe\.api_key|Stripe\.setApiKey|[sr]k_(live|test)_[A-Za-z0-9]+|payment_method_types" src/

# 2. Local end-to-end webhook signature & replay smoke test
stripe listen --forward-to http://127.0.0.1:3000/api/webhooks/stripe &
stripe trigger checkout.session.completed
stripe trigger charge.dispute.created

# 3. Run deterministic idempotency & out-of-order state-transition test suite
pytest -q --tb=short tests/payments/ -k "idempotency or out_of_order"
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Global `stripe.api_key` & `sk_` in Code** | Breaks multi-tenant/key-rotation isolation and exposes full account privileges if leaked | `stripe.api_key =` or `sk_live_` in app config or client env | Instantiate `new StripeClient(vaultRkSecret)` with least-privilege `rk_` keys |
| **Hardcoding `payment_method_types: ['card']`** | Disables Apple Pay, Link, SEPA, Klarna, and dynamic dashboard payment methods | `payment_method_types` array outside Terminal integrations | Omit `payment_method_types`; configure via Dashboard or `payment_method_configurations` |
| **Enabling `automatic_tax` Without Registration** | Silently calculates `$0.00` tax with zero error until audit; Stripe cannot recover tax retroactively | `automatic_tax: { enabled: true }` while `TaxRegistration.status !== 'active'` | Verify Head Office + active `TaxRegistration` per jurisdiction and valid `txcd_` before launch |
| **Multiple Tiers on One Product** | Breaks Customer Portal plan switching, entitlement mapping, and revenue reporting | Pro/Team/Enterprise `Prices` attached to a single `Product` | Enforce strict `1 Product = 1 Tier` with cadence/currency `Prices` only |
| **Synchronous Heavy Work Inside Webhook HTTP Handler** | Causes `> 5s` timeouts, Stripe retry storms, and partial state corruption | DB migrations, emails, or outbound API calls before `res.status(200)` | Verify raw signature -> `INSERT ... ON CONFLICT DO NOTHING` -> enqueue job -> return `200` `< 500ms` |
| **Unconditional `UPDATE subscriptions SET status = ...`** | Out-of-order `invoice.paid` overwrites a newer `customer.subscription.deleted` event | `UPDATE` lacking `status = ANY(...)` and `last_event_ts <= event_ts` | Conditional SQL state-machine `UPDATE` guarded by allowed prior states and monotonic timestamp |
| **`express` Connect + `losses_collector: "stripe"`** | Explicitly `BLOCKED` by Stripe Connect v2; disputes still fail settlement or break onboarding | `dashboard: 'express'` paired with `losses_collector: 'stripe'` or `destination` | Use `full/stripe/stripe/direct` for SaaS or `express/application/application/destination` with dispute reversal |
| **Custom Card Forms / Renewal Crons (Over-Engineering)** | Adds PCI scope, 3DS edge-case bugs, and fragile proration math for standard SaaS | Custom card inputs or cron jobs charging `PaymentIntents` monthly | Use Hosted Checkout Sessions + Billing `Prices` (1 Product/tier) + Customer Portal |
