# Privacy & Data Governance

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Every personal attribute a system collects becomes a permanent security, compliance, and deletion liability.
- Start privacy engineering at schema design time—not as a pre-launch legal checkbox.
- Minimize collected fields, offload regulated card/health scopes, mask PII across logs and UIs, and automate Data Subject Rights (`DSR`) erasure.

---

## 1. Decision Framework

### 1.1 Simplicity & Data Minimization Gate ("Least Data, Least Liability")

Apply **Radical Simplicity ("Least Code, Highest Craft")** before adding columns or trackers:

1. **Delete Before Encrypting**: The safest `PII` is data never collected.
   - Challenge every field (`DOB`, phone, address, raw IP) against a concrete product need and lawful basis.
2. **Tokenize & Offload Regulated Scopes**: Never store raw card numbers (`PAN`), CVVs, or PHI blobs locally when a certified vault (`Stripe`, external IdP) handles them.
3. **Prefer Opaque Identifiers**: Use internal `bigint` or `UUIDv7` keys in URLs, telemetry, and audit logs instead of emails or phone numbers.

### 1.2 Five-Tier Data Classification Matrix

| Tier | Representative Examples | Transport & Storage Control | Logging, Caching & Access Rule |
|---|---|---|---|
| **1. Public** | Marketing copy, catalog, docs | `TLS >= 1.2`; public CDN cache allowed | Standard access logs; zero user IDs attached |
| **2. Internal** | Feature flags, opaque tenant/job IDs | `TLS >= 1.2`; disk encryption at rest | Authenticated internal access only |
| **3. Confidential** | B2B contracts, billing tiers, ops metrics | `TLS >= 1.2`; RBAC/RLS + disk encryption | `Cache-Control: private`; auth required |
| **4. Restricted — PII** | Email, phone, name, address, DOB, IP | `TLS >= 1.2`; KMS encryption; tagged | **0 PII in logs**; masked UI; `no-store`; DSR scope |
| **5. Regulated — PCI / PHI** | Payment cards, SSN, medical records | **Offload to certified vault by default** | `no-store`; BAA/PCI scope; formal DPIA sign-off |

- **Default Rule**: Unclassified user fields default to **Tier 4 (Restricted — PII)** until explicitly downgraded.
- **Log Boundary**: Never log raw Tier 3–5 request payloads or user structs at `INFO` or `ERROR`.

### 1.3 GDPR / CCPA Erasure Strategy Selector

| Deletion Strategy | When to Choose | Mechanism | Legal & Integrity Trade-Off |
|---|---|---|---|
| **Option A: Cascading Hard Delete** | Profiles, preferences, sessions, drafts | Transactional `DELETE` + session revocation | Simplest choice; breaks FKs on tax ledgers |
| **Option B: Anonymization** | Invoices (`7-year` tax hold), aggregates | Replace PII columns with irreversible random/null | Keeps accounting totals intact without PII |
| **Option C: Crypto-Shredding** | Immutable event streams, backups | Per-subject KMS `DEK`; **destroy DEK** on erasure | Renders archives unreadable without rewrites |

- **Grace Window**: Keep deleted-account recovery windows `<= 30 days` before automated hard purge triggers.
- **Cross-Context Sync**: Emit a single `subject.erased` domain command across all owning bounded contexts.

### 1.4 Mandatory Security & Privacy Baselines

Apply these baseline engineering rules (`Google.securecoder` `securecoder_generation` synthesis) before writing schema or endpoint code:
- **Transport**: Enforce `TLS >= 1.2` across client edges, internal service hops, and PostgreSQL connections (`sslmode=verify-full`).
- **Encryption & Keys**: Use KMS-managed envelope encryption at rest; store zero plaintext secrets, API keys, or encryption keys in source code or `.env` commits.
- **Response Caching**: Emit `Cache-Control: no-store` on every endpoint returning Restricted PII, credentials, or Regulated data.
- **Session Revocation**: Atomically invalidate active sessions, refresh tokens, and API keys whenever an account is deleted or removed from a tenant.
- **Audit Purity**: Record `actor_id`, `action`, `target_type`, `target_id`, `occurred_at`, and `request_id`—never raw PII payloads.

---

## 2. Step-by-Step Workflow

Apply **Token Economy** by scanning schema definitions and logger configurations directly via targeted searches rather than reading entire codebases sequentially.

1. **Inventory Data Flows & Tag Every Column (`Input -> Owner -> Output`)**
   - **Inputs**: `docs/architecture/data-model.md`, API payload schemas, frontend forms, subprocessor list.
   - **Owner**: Privacy / Security Lead & Data Architect.
   - **Action**:
     - Map every inbound field, third-party subprocessor (`analytics`, `email`, `billing`, `AI`), log sink, and DB column to one of the 5 Classification Tiers.
     - Challenge and delete every optional PII field lacking a concrete product need and legal basis (`GDPR Art. 6` / `CCPA` purpose limitation).
   - **Output**: Column-level classification matrix and pruned data collection spec.

2. **Implement Versioned Consent Ledger & Opt-Out Controls**
   - **Inputs**: Jurisdiction matrix (`GDPR`, `CCPA/CPRA`, `ePrivacy`) and subprocessor list.
   - **Owner**: Backend / Compliance Engineer.
   - **Action**:
     - Replace boolean `accepted_terms` flags with an immutable, versioned consent ledger (`consent_id`, `subject_id`, `purpose`, `policy_version`, `status`, `granted_at`, `withdrawn_at`, `source_ip_hash`).
     - Enforce server-side Global Privacy Control (`GPC`) and opt-out checks before initializing non-essential telemetry or marketing SDKs.
   - **Output**: Versioned consent schema and server-side enforcement hook.

3. **Enforce PII Protection Across Transport, Storage, UI & Logs**
   - **Inputs**: Classified column inventory and API/UI boundaries (integrating `Google.securecoder` `securecoder_generation` safeguards).
   - **Owner**: Backend / Security Engineer.
   - **Action**:
     - Mandate `TLS >= 1.2` in transit (including DB connections) and KMS-managed encryption at rest with zero plaintext secrets in code or config.
     - Enforce structured logger allowlists so raw user objects, passwords, tokens, API keys, and Restricted PII never reach console logs or error trackers.
     - Mask sensitive displays in UI and exports (`***-***-1234`) and set `Cache-Control: no-store` on sensitive endpoints.
   - **Output**: Logger redaction rules, cache headers, and encrypted secret configuration.

4. **Build Verifiable DSR Pipelines (Export & Erasure + Session Revocation)**
   - **Inputs**: Context ownership map and erasure strategy selector.
   - **Owner**: Backend Engineer.
   - **Action**:
     - **Access / Portability Export (`GDPR Art. 15/20`)**: Build an authenticated, rate-limited async export job assembling subject records across bounded contexts into `JSON`/`CSV` via short-lived signed URLs (`<= 15 min` expiry).
     - **Erasure Cascade (`GDPR Art. 17` / `CCPA Delete`)**: Verify identity -> check legal holds (anonymize tax invoices instead of breaking FK totals) -> cascade hard deletes -> destroy per-subject KMS DEK for backups/event streams -> **immediately invalidate all active sessions, refresh tokens, and API keys** -> log a PII-free cryptographic erasure receipt.
   - **Output**: Tested DSR export and erasure handlers with immediate token invalidation.

5. **Automate Retention / TTL & Maintain Immutable Audit Trails**
   - **Inputs**: Retention schedule per table, object bucket, and log sink.
   - **Owner**: Platform / Data Engineer.
   - **Action**:
     - Set concrete numeric TTLs per store (`debug logs: 30d`, `sessions: 14–30d`, `deleted-account grace: <= 30d`, `financial invoices: 7y anonymized`).
     - Automate expiry via monthly PostgreSQL range-partition `DROP TABLE` or scheduled batched purges rather than leaving `deleted_at` rows forever.
     - Record privileged admin, role, and DSR events in an append-only `audit_events` table (`audit_id`, `actor_id`, `action`, `target_type`, `target_id`, `occurred_at`, `request_id`) with **zero raw PII payloads**.
   - **Output**: Automated purge jobs/partition policies and PII-free audit table.

6. **Author DPIA & Run Privacy Condensation Pass**
   - **Inputs**: Completed privacy controls and high-risk processing descriptions (large-scale PII, profiling/AI training, minors, or health/payment data).
   - **Owner**: Technical Lead / Data Protection Officer.
   - **Action**:
     - Complete `docs/architecture/dpia-privacy.md` and verify signed DPAs plus cross-border transfer safeguards (`SCCs`/regional pinning) for every subprocessor.
     - Run a **Condensation Pass**: remove unnecessary analytics SDKs, redundant PII duplicates across caches/services, and verbose debug request logging.
   - **Output**: Signed `docs/architecture/dpia-privacy.md` and minimal-footprint data plane.

---

## 3. Reusable Artifact & Template

Instantiate [templates/dpia-privacy.md](../templates/dpia-privacy.md) to output `docs/architecture/dpia-privacy.md` for every product storing personal or regulated user data.

### 3.1 Field-by-Field Template Contract

| Template Section | Required Content | Verification Rule |
|---|---|---|
| **1. Classification Inventory** | Every entity/field mapped to Tiers `1–5` + purpose + lawful basis + masking | Zero untagged user columns; zero raw PAN/CVV stored locally |
| **2. Consent & Subprocessors** | Versioned consent columns + subprocessor region, transfer mechanism, DPA date | Non-essential tracking gated on consent/GPC opt-out |
| **3. Retention & TTL Schedule** | Concrete numeric TTL + purge mechanism (`Partition Drop`, `TTL Job`, `Crypto-Shred`) | Every PII store and log sink has an automated expiry rule |
| **4. DSR Pipelines & Audit Trail** | Export SLA/format, erasure cascade, DEK destruction, session revocation, audit schema | Erasure immediately returns `401` on all prior tokens; audit log holds 0 PII |
| **5. DPIA Risk Register** | High-risk flows, mitigations, residual risk, executable verification test | Mandatory sign-off when processing Tier 4 large-scale or Tier 5 data |

### 3.2 Reference Consent & Audit SQL Pattern

```sql
CREATE TABLE consent_ledger (
  consent_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  subject_id     bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose        text NOT NULL CHECK (purpose IN ('analytics', 'marketing', 'ai_training')),
  policy_version text NOT NULL,
  status         text NOT NULL CHECK (status IN ('granted', 'withdrawn')),
  granted_at     timestamptz NOT NULL DEFAULT now(),
  withdrawn_at   timestamptz
);
CREATE INDEX idx_consent_subject_purpose ON consent_ledger (subject_id, purpose, granted_at DESC);
```

### 3.3 Mandatory Erasure Sequence Diagram

```text
[DSR Delete Request] -> [Verify Auth + Legal Hold] -> [Cascade DB Delete / Anonymize Invoices]
                                                            |
                                                            v
[PII-Free Audit Receipt] <-- [Revoke Sessions/JWTs (401)] <-- [Destroy Subject KMS DEK]
```

---

## 4. Verification Checklist

- [ ] Every user-related database column carries a 5-tier classification tag.
  - Non-essential PII fields were deleted during Data Minimization review.
- [ ] Zero raw payment card numbers (`PAN`) or plaintext secrets exist locally.
  - Regulated card/PHI payloads offload to certified external vaults.
- [ ] Loggers and error trackers redact Restricted PII, passwords, and tokens.
  - Static and integration checks confirm zero raw user object logging.
- [ ] Sensitive endpoints emit `Cache-Control: no-store` and masked UI values.
  - Prevents browser/proxy caching of confidential user attributes.
- [ ] Versioned consent records policy version, purpose, timestamps, and opt-out state.
  - Non-essential tracking blocks until server-side consent/GPC allows it.
- [ ] DSR erasure cascade removes PII and revokes active tokens immediately.
  - Integration tests confirm `401` rejection on prior JWTs and sessions.
- [ ] Every PII table, backup, and log bucket defines an automated TTL purge.
  - Partition drops or batched deletes prevent indefinite soft-delete retention.
- [ ] Immutable `audit_events` logs actor, action, target ID, and timestamp cleanly.
  - Audit payloads contain zero raw PII or credential strings.
- [ ] Subprocessor registry verifies signed DPAs and cross-border safeguards.
  - DPIA sign-off completed prior to production launch.

---

## 5. Hard Quality Gate

Privacy governance passes Phase 3A and pre-launch release gating only under explicit binary checks:

- **PASS**: `100%` of PII columns tagged in `docs/architecture/dpia-privacy.md`, `0` unmasked PII/token log hits in static and integration log checks, `Cache-Control: no-store` verified on sensitive routes, automated TTL rules configured, and end-to-end DSR erasure test proves `0` remaining subject PII rows plus immediate `401` invalidation of active JWTs/sessions.
- **CONCERNS**: Core PII classification, masking, and erasure pass, while secondary marketing consent copy or subprocessor regional addendum awaits final legal review.
- **NOT ASSESSED**: Log sanitization scan or end-to-end DSR erasure integration tests have not yet run — never declare privacy compliance without verified test runs.
- **FAIL**: Any raw payment card or unencrypted secret in DB/code, any PII object logged to stdout/Sentry, soft-delete flags without automated purge/TTL, DSR erasure leaving active sessions valid, or missing DPIA sign-off on Tier 4/5 processing.
- **Evidence Rule**: Record log-scan command output and DSR erasure `401` session-revocation test receipt before production launch.

Run static log-leak and schema privacy verification checks:

```bash
grep -rnE "console\.(log|debug|info)\(.*(user|password|token|email|secret)" src/ && echo "FAIL: potential PII log leak" || echo "PASS: no naive PII log calls"
pytest -q -k "dsr_erasure or privacy" --tb=short
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **"Collect Everything Just In Case"** | Expands breach blast radius and erasure cost for unused attributes | Unused DOB, phone, or raw IP columns | Delete unused PII fields during Q2/3A review |
| **Logging Raw User Objects / Tokens** | Leaks credentials and emails into third-party log aggregators | `console.log(user)` or full body dumps on `500` | Structured logger allowlists (`user_id`, `request_id`) |
| **Soft-Delete Forever (`deleted_at`)** | Violates erasure rights while keeping stale PII exposed indefinitely | `deleted_at` column lacking automated purge/TTL | Hard-delete/anonymize after `<= 30 d` grace window |
| **Orphaned PII in Backups & Logs** | Restored backups resurrect erased users unless encrypted per subject | Plaintext emails inside immutable logs or backups | Per-subject KMS crypto-shredding (`DEK` destruction) |
| **DIY Card or Health Vaulting** | Pulls entire app into PCI-DSS/HIPAA scope unnecessarily | Custom `credit_cards` or `card_number` DB columns | Offload to certified vaults (`Stripe`); store tokens only |
| **Erasure Leaving Sessions Valid** | Deleted users retain API access until JWT/session expiry | Deletion handler skips session/token revocation | Revoke sessions, refresh tokens, and API keys atomically |

- **Subprocessor Hygiene**: Never add telemetry or AI SDKs transmitting user attributes without consent gating and a signed DPA.
- **Backup Parity**: Verify backup restore procedures document how destroyed crypto-shredding DEKs prevent erased user reappearance.
