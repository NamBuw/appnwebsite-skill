# DPIA & Privacy Governance Specification: [Product / Surface Name]

> **Canonical Output Path**: `docs/architecture/dpia-privacy.md`

- **Assessment ID**: `[DPIA-001]`
- **Product / Surface**: `[Web App / Mobile / API]`
- **Jurisdictions**: `[GDPR | CCPA/CPRA | Other Applicable Frameworks]`
- **Data Controller / Owner**: `[Product / Engineering Owner Role]`
- **Review Date**: `[YYYY-MM-DD]`

---

## 1. Data Minimization & 5-Tier Classification Inventory

Apply data minimization first: delete or tokenize any field not strictly required for the stated product purpose.

| Table / Field | Classification Tier | Purpose & Minimization Check | Lawful Basis | Encryption & Storage Rule | Masking & Cache Rule |
|---|---|---|---|---|---|
| `[users.email]` | `Restricted-PII` | `[Auth, transactional notices]` | `[Contract performance]` | `[TLS >= 1.2 + KMS disk encryption]` | `[Redacted in logs; masked in UI]` |
| `[payment_tokens]` | `Regulated-PCI/PHI` | `[Billing via Stripe token only]` | `[Contract performance]` | `[Offloaded to Stripe vault; 0 PAN stored]` | `[No-store cache; never logged]` |

---

## 2. Consent Ledger & Subprocessor Map

### 2.1 Versioned Consent Ledger Schema

- **Required Columns**: `consent_id`, `subject_id`, `purpose` (`analytics | marketing | ai_training`), `policy_version`, `status` (`granted | withdrawn`), `granted_at`, `withdrawn_at`, `source_ip_hash` (salted/truncated).
- **Opt-Out Propagation**: `[Server-side Global Privacy Control / Do-Not-Sell flag disables non-essential tracking before client SDK init.]`

### 2.2 Subprocessor & Cross-Border Transfer Map

| Subprocessor | Purpose | Data Shared | Storage Region & Transfer Safeguard | DPA Verified |
|---|---|---|---|---|
| `[Payment Processor]` | `[Billing & invoicing]` | `[Customer ID, invoice metadata]` | `[EU/US SCCs or regional vault]` | `[Yes — YYYY-MM-DD]` |
| `[Transactional Email]` | `[Auth & receipts]` | `[Recipient email, template ID]` | `[Zero body PII logged after send]` | `[Yes — YYYY-MM-DD]` |

---

## 3. Retention, TTL & Automated Purge Schedule

| Store / Table / Bucket | Data Tier | Retention TTL | Automated Purge Mechanism | Legal Hold Exception |
|---|---|---|---|---|
| `[application_logs]` | `Confidential` | `[30 days]` | `[Log sink lifecycle expiry]` | `[None]` |
| `[deleted_accounts]` | `Restricted-PII` | `[<= 30 days grace]` | `[Hard-delete cascade + crypto-shred DEK]` | `[Invoices retained 7y anonymized]` |
| `[audit_events]` | `Confidential` | `[1-7 years]` | `[Monthly range partition DROP TABLE]` | `[Zero raw PII in payload]` |

---

## 4. DSR Pipelines (Export & Erasure) & Audit Trail

### 4.1 Right of Access / Portability (Export)

- **Trigger & Auth**: `[Authenticated self-service or verified support ticket; rate-limited]`
- **SLA & Format**: `[<= 30 days (GDPR) / <= 45 days (CCPA); machine-readable JSON + CSV via short-lived signed URL]`

### 4.2 Right to Erasure / Deletion Cascade

1. `[Verify subject identity and check statutory retention locks (e.g., tax invoices anonymized, not deleted).]`
2. `[Execute transactional delete/anonymization across all owning bounded contexts.]`
3. `[Destroy per-subject crypto-shredding DEK in KMS so immutable backups and event streams become unreadable.]`
4. `[Immediately revoke all active sessions, refresh tokens, and API keys for the subject.]`
5. `[Emit PII-free cryptographic erasure receipt to immutable audit log.]`

### 4.3 Immutable Audit Trail Schema

- **Columns**: `audit_id`, `actor_id`, `actor_role`, `action` (`dsr.erase | role.grant | export.create`), `target_type`, `target_id`, `occurred_at`, `request_id`.
- **Prohibition**: `[Never store raw PII, passwords, bearer tokens, or full request bodies inside audit_events.]`

---

## 5. DPIA Risk Register & Sign-Off

| Risk Scenario | Likelihood / Impact | Technical Mitigation | Residual Risk | Verification Command / Test |
|---|---|---|---|---|
| `[PII leaked into debug logs]` | `[Medium / High]` | `[Structured logger redaction allowlist + lint rule]` | `[Low]` | `[Log sanitizer regex + unit test]` |
| `[Deleted user retains valid JWT]` | `[Low / Critical]` | `[Token version bump / session table purge on delete]` | `[Low]` | `[Integration test expecting HTTP 401]` |

- **DPIA Sign-Off**: `[Privacy / Security Lead, Engineering Lead, Date, Verification Status]`

## References

- [Privacy & Data Governance Guide](../references/privacy-and-data-governance.md)
- [Domain & Data Modeling Guide](../references/domain-data-modeling.md)
- [System & Data Architecture Router](../SKILL.md)
