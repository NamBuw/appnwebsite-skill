# AI Evaluation, Trust-Boundary & Prompt-Defense Specification

> Reusable Spiral Q2/3A/3B/3C contract for LLM features, durable AI workflows, sandboxes, MCP tools/widgets, and untrusted browser auditing. Replace `<angle-bracket>` slots before shipping.

## 1. System Identity, Model Routing & Persistence

| Field | Specification |
|---|---|
| **Feature / Agent Name** | `<feature_name>` |
| **Capability Tier (Escalation Ladder)** | `<1: Single Typed Call | 2: Addressable Chat /chat/[id] | 3: Durable Workflow | 4: Isolated Agent/Sandbox | 5: MCP Server>` |
| **Model Lookup & Pinning** | Dynamic lookup via `<gateway.getAvailableModels() | /v1/models>` -> pinned `<provider/model>` slug (never hardcoded stale alias) |
| **Gateway Auth** | `<VERCEL_OIDC_TOKEN | AI_GATEWAY_API_KEY fallback>` |
| **Pre-Call Persistence** | Generate `<nanoid() | cuid2>` ID **before** LLM call; redirect to `/chat/<id>`; persist tokens, cost cents, and Blob URLs |
| **Cache Eligibility** | `<NONE for user conversations | SHA-256(model:prompt) 1h TTL for static deterministic prompts>` |

---

## 2. Trust-Boundary Map (Control Plane vs. Untrusted Data Plane)

Prompt instructions and guardrail models are **non-security helpers**, never enforcement boundaries. All external text enters the Untrusted Data Plane:

| Surface / Channel | Plane Classification | Concrete Trust Control |
|---|---|---|
| **System Prompt, Tool Code, Server Auth Session** | `Control Plane (Trusted)` | Server-derived `session.userId` + `tenantId` (never from model args or client headers) |
| **User Prompt, Uploaded Files, RAG Chunks** | `Untrusted Data Plane` | Retrieval filtered by caller ACL BEFORE vector/text scoring; never interpolate into SQL/shell |
| **External Web DOM, Console Logs, Network Payloads** | `Untrusted Data Plane` | Browser runs `--isolated`; read-only inspection; zero execution of DOM text or extracted URLs |
| **MCP Tool Descriptions, Server Aliases, Memory** | `Untrusted Data Plane` | Bind server/tool identity to authenticated connection + request ID; validate schema at handler |

---

## 3. Tool Least-Privilege & Schema-Parity Matrix

| Tool Name | Effective Identity | Required Resource ACL | Canonicalized Handler Check | Max Calls / Request |
|---|---|---|---|---|
| `<read_domain_record>` | `session.userId` | `record.tenant_id === session.tenant_id` | Validate Zod/JSON schema; parameterize query | `<5>` |
| `<propose_mutation>` | `session.userId` | `<role: editor | admin>` + ownership check | Re-derive target ID server-side; reject unknown keys | `<2>` |
| `<run_untrusted_code>` | `ephemeral_sandbox_<user_id>` | Isolated per-user `sandboxId` (never shared) | Execute inside Sandbox container; call `destroy()` | `<3>` |

---

## 4. Parameter-Bound HITL Action-Confirmation Contract

Every destructive, financial, external-egress, or privilege-changing action MUST require out-of-band confirmation bound to exact normalized parameters:

| Bound Field | Binding Rule |
|---|---|
| `confirmation_id` | Cryptographically random single-use nonce (`>= 128` bits) stored server-side |
| `tool_name` | Exact canonical dispatcher tool identifier (no alias substitution) |
| `normalized_args_hash` | `SHA-256` of canonical JSON sorted arguments (prevents argument mutation after approval) |
| `requester_id` | Authenticated `session.userId` who initiated and approved the action |
| `target_id` | Canonical resource identifier verified against caller ACL |
| `amount_or_blast_radius` | Explicit numeric cap or affected record count shown to the human approver |
| `expiry_ts` | Short TTL (`<= 300 seconds`); invalidated immediately on first execution, retry, or resume |

---

## 5. MCP, Sandbox & Network Hardening (If Applicable)

- **Widget vs. Elicitation**: Default to `clientCapabilities.elicitation` for yes/no, enum, or flat forms; build iframe widget (`text/html;profile=mcp-app`) only for rich spatial/visual workflows, bundling `@modelcontextprotocol/ext-apps/app-with-deps` inline (zero external CDN ESM under CSP).
- **Proxy & Rate Limiting**: Configure exact reverse-proxy hop count `app.set('trust proxy', <N>)` (never `true`); key rate limits on authenticated OAuth subject when present, or shared egress-CIDR pool + normalized in-process LRU cache for authless endpoints.
- **Step / Spend Loop Caps**: Enforce `maxSteps <= <8>`, per-request token ceiling `<max_input_tokens / max_output_tokens>`, and `AbortSignal` timeout `<timeout_ms>`.

---

## 6. Eval-Driven Development (EDD) Suite & Evidence Log

Define capability and regression/security evals **before** coding feature logic:

| Eval ID | Category | Grader Type | Metric & Threshold | Current Status |
|---|---|---|---|---|
| `<CAP-01>` | Capability (happy + edge inputs) | `Code Grader` (schema + invariants) | `pass@3 >= 90%` (`<observed_rate>`) | `<confirmed | needs_validation>` |
| `<SEC-01>` | Direct/Indirect Prompt Injection (RAG/DOM/MCP) | `Code Grader` + `Human Review` | `pass^3 = 100%` (`0` unauthorized tool calls) | `<confirmed | needs_validation>` |
| `<SEC-02>` | HITL Parameter Tampering / Cross-Tenant IDOR | `Code Grader` | `pass^3 = 100%` (`403` / signature mismatch) | `<confirmed | needs_validation>` |
| `<REG-01>` | Budget Cap, Step Limit & Sandbox Cleanup | `Code Grader` | `pass^3 = 100%` (bounded spend, `destroy()` called) | `<confirmed | needs_validation>` |

