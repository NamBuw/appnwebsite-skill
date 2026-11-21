# AI Features, Durable Agents, MCP Apps & Prompt-Injection Defense

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

### 1.1 AI Architecture Escalation Ladder

Default to the lowest tier on the ladder that solves the user problem reliably; move up only when an explicit requirement demands it:

| Tier | Architecture | When to Choose | Mandatory Runtime Controls |
|---|---|---|---|
| **0 (No AI)** | Deterministic SQL / Regex / Rules | Classification, routing, or calculations with fixed logic | Zero LLM latency, zero token spend, 100% reproducible |
| **1 (Single Call)** | Gateway `generateText` / Structured Output | One-shot extraction, summary, or classification | Dynamic `provider/model` lookup; Zod schema validation; `AbortSignal` |
| **2 (Chat UI)** | Addressable Streaming Chat (`/chat/[id]`) | Interactive assistant needing persistent shareable history | `nanoid()`/`cuid2` generated **before** LLM call; `ToolLoopAgent` + `InferAgentUIMessage` |
| **3 (Durable)** | `"use workflow"` + `"use step"` | Multi-step pipelines (`> 30s`), webhooks, human sleep/hooks | Determinism inside `"use workflow"`; Node I/O only in `"use step"`; `FatalError` vs `RetryableError` |
| **4 (Isolated)** | Per-Entity SQLite `Agent` or `Sandbox` | Stateful WebSocket RPC agents or untrusted LLM code execution | `validateStateChange` sync guard; per-user `sandboxId` with `destroy()` cleanup |
| **5 (MCP)** | Remote Streamable-HTTP MCP Server | Cross-client tool exposure; prefer Elicitation before iframe widgets | `< 15` actions = 1 tool/action; `50+` = `search_actions` + `execute_action`; inline `ext-apps` bundle if widget |

### 1.2 Gateway, Persistence & Eval Thresholds

- **Model Lookup & Gateway Routing**:
  - Never hardcode stale model strings in prompts or code; resolve active `provider/model` dot-version slugs dynamically (`https://ai-gateway.vercel.sh/v1/models` or `gateway.getAvailableModels()`).
  - Authenticate with `VERCEL_OIDC_TOKEN` (`AI_GATEWAY_API_KEY` fallback) and use Gateway failover (`order`/`models`/`tags`) when uptime or cost routing matters.
  - Use direct provider SDKs only for exclusive provider features or self-hosted `vLLM`/`Ollama`.
- **Cache & Media Rules**:
  - Enable prompt caching (`cacheControl`) ONLY on static system prompts/FAQs/extraction schemas—**never** on user conversation history.
  - Persist generated images/files to Blob object storage URLs (never ephemeral base64 strings in React state or Postgres text columns).
  - Deduplicate identical `(model, prompt)` requests with a SHA-256 cache key (`1 hour` TTL).
- **Security & EDD Bar (OWASP LLM01/LLM06)**:
  - Prompt guardrails are **0% security boundaries**; every prompt injection exploits a **code-level boundary failure**.
  - Enforce Eval-Driven Development (EDD) with **`pass@3 >= 90%`** on capability evals (at least 1 success in 3) and **`pass^3 = 100%`** on regression and security evals (all 3 consecutive runs pass).
  - Bound agent loops with `maxSteps <= 8`, explicit token/spend ceilings, and `AbortSignal` timeouts (`<= 30s` interactive / workflow-scoped durable).

### 1.3 AI Simplest High-Craft Check & Token Economy

- **Decision Tree (Pick Lowest Viable AI Tier)**:
  ```text
  Deterministic rules / SQL solve it?
  ├── YES -> Tier 0 (No LLM; zero latency & token cost)
  └── NO -> Single request/response extraction or summary?
      ├── YES -> Tier 1 (Gateway generateText / typed schema)
      └── NO -> Multi-turn chat or >30s background steps?
          ├── Chat UI -> Tier 2 (/chat/[id] + nanoid pre-LLM + ToolLoopAgent)
          ├── Multi-step / webhooks -> Tier 3 ("use workflow" + "use step")
          ├── Stateful RPC / untrusted code -> Tier 4 (SQLite Agent / Sandbox)
          └── External client integration -> Tier 5 (Streamable-HTTP MCP; Elicitation first)
  ```
- **Anti-Overengineering Gate**:
  - Ask: *"Can deterministic validation, a single typed structured-output call, or MCP `clientCapabilities.elicitation` replace a multi-agent loop, custom RAG pipeline, or custom iframe MCP widget?"*
  - Reject multi-agent orchestration when a single typed server call + Zod validation solves the task.
- **Token Economy Rule**:
  - Inspect installed SDK docs (`node_modules/ai/docs/`, `node_modules/workflow/docs/`) with targeted `rg`/`grep` before reading source files.
  - Use `getWritable({ namespace })` in durable workflows to separate primary output from verbose step logs so long replays remain compact.

---

## 2. Step-by-Step Workflow

1. **Map Trust Boundaries & Persistence Schema (Q2 / 3A)**
   - **Owner**: Backend & Security Engineer
   - **Input**: `prd.md`, `control-manifest.md`, data classification rules.
   - **Output**: Completed Trust-Boundary Map + DB migration.
   - **Tool**: `ai-eval-and-prompt-defense.md` template, schema linter.
     - Separate the **Trusted Control Plane** (server auth session, tool code, policy checks) from the **Untrusted Data Plane** (user prompts, RAG documents, web DOM, persistent memory, MCP tool descriptions/responses).
     - Design the `generations` DB table (`id`, `user_id`, `model`, `prompt`, `result`, `blob_urls`, `token_usage`, `estimated_cost_cents`, `status`).
     - Wire a pre-flight token estimator handling HTTP `429` / `402` quota errors cleanly.

2. **Define Eval-Driven Development (EDD) Suite Before Feature Code**
   - **Owner**: Engineer & QA Lead
   - **Input**: Feature acceptance criteria and abuse cases.
   - **Output**: Baseline failing eval suite ready for red-green implementation.
   - **Tool**: Eval runner (`vitest` / `pytest`), deterministic assertion suite.
     - Author Capability Evals (`pass@k`) and Security/Regression Evals (`pass^k`) before implementing tool handlers.
     - Assign deterministic **Code Graders** (schema, SQL/ACL assertions, spend caps) as primary checks.
     - Use Model Graders only for open-ended prose quality, and require **Human Review** for any side-effecting or security-sensitive tool.

3. **Implement Generate-Then-Redirect & Durable Step Isolation**
   - **Owner**: Backend Engineer
   - **Input**: Gateway auth (`VERCEL_OIDC_TOKEN`), `generations` table.
   - **Output**: Resilient streaming or durable AI execution endpoints.
   - **Tool**: `ai` SDK (`ToolLoopAgent`, `InferAgentUIMessage`), `workflow` SDK.
     - Generate `nanoid()` or `cuid2` **before** invoking the LLM, insert the initial `pending` record, and redirect immediately to `/chat/[id]` so page reloads or stream drops never lose state.
     - Keep `"use workflow"` strictly deterministic (use workflow `sleep()`, `createHook()`/`resumeHook()`, `createWebhook()`—never Node `fs`, `crypto`, or `fetch` directly inside workflow body).
     - Place all LLM/HTTP/DB side effects inside `"use step"` functions throwing `FatalError` on permanent 4xx errors vs. `RetryableError` with `retryAfter` on transient failures.

4. **Harden Tools, HITL Binding, Sandboxes & MCP Endpoints**
   - **Owner**: Backend & Security Engineer
   - **Input**: Tool schemas, MCP server config, Sandbox binding.
   - **Output**: Hardened tool dispatchers, HITL verifier, and MCP/Sandbox isolation.
   - **Tool**: `semgrep`, TypeScript/Python schema validators, integration tests.
     - **Handler-Side AuthZ & Schema Parity**: Validate arguments at the dispatcher AND inside the concrete tool handler; re-derive `userId`/`tenantId` strictly from the authenticated server session (never trust model-supplied IDs or alias metadata).
     - **ACL-Scoped Retrieval**: Filter RAG retrieval and cache keys by caller ACL **before** semantic ranking.
     - **Parameter-Bound HITL**: For destructive/financial/external actions, issue a single-use cryptographic confirmation bound server-side to `(tool_name, normalized_args_hash, requester_id, target_id, amount, expiry_ts, batch_membership)` and invalidate immediately on retry or resume:

```ts
const argsHash = sha256(canonicalJson(validatedArgs));
const hitlToken = await issueSingleUseConfirmation({
  tool: "transferFunds", argsHash, requesterId: session.userId,
  targetId, amountCents, expiresAt: Date.now() + 300_000,
});
```

     - **Bounded Loops & Sandboxes**: Cap `maxSteps`, per-request spend/token budget, and delegate untrusted code execution exclusively to `getSandbox(env.Sandbox, userOrSessionId)` (`runCode()` + explicit `destroy()` cleanup; never share `sandboxId` across tenants).
     - **MCP & Proxy Hardening**: Bind MCP server/tool identity to the authenticated transport + request ID; check `clientCapabilities.elicitation` before building widgets.
     - **Widget CSP & Rate Limits**: If building an MCP App (`text/html;profile=mcp-app`), inline `@modelcontextprotocol/ext-apps/app-with-deps` (`/*__EXT_APPS_BUNDLE__*/`) because iframe CSP blocks CDN ESM, and use `app.openLink` instead of `window.open`. On authless Streamable-HTTP endpoints, set **exact** proxy hop count `app.set('trust proxy', N)` (never `true`), normalize + LRU-cache before rate-limiting, and account for shared egress CIDRs (`160.79.104.0/21`, `2607:6bc0::/48`) or require OAuth.

5. **Deletion / Condensation & Adversarial Boundary Pass**
   - **Owner**: Engineer & Security Reviewer
   - **Input**: Full AI implementation and EDD suite.
   - **Output**: Minimal, verified AI feature passing all EDD gates.
   - **Tool**: `tsc --noEmit`, eval suite, `rg` static scan.
     - Delete speculative multi-agent hops that can be deterministic function calls, and collapse custom retry wrappers into native SDK `RetryableError` / `maxRetries`.
     - Remove hardcoded model strings or unreferenced MCP widget HTML.
     - Run the adversarial `pass^3 = 100%` prompt-injection, cross-tenant RAG leak, and HITL-tampering suite recording `confirmed` vs. `needs_validation` evidence.

---

## 3. Reusable Artifact & Template

Complete [AI Eval and Prompt Defense Spec](../templates/ai-eval-and-prompt-defense.md) for every LLM, agent, or MCP feature. Mandatory schema fields:

### 3.1 Required AI Eval & Trust-Boundary Schema Fields

| Field | Contract Requirement | Failure Mode Prevented |
|---|---|---|
| `capability_tier` | Integer `0..5` from Escalation Ladder | Prevents building multi-agent loops where a single call or SQL query suffices |
| `model_lookup_source` | Dynamic Gateway `/v1/models` or `getAvailableModels()` | Eliminates hardcoded deprecated slugs and silent provider outages |
| `pre_call_id_strategy` | `nanoid()` / `cuid2` persisted before stream start | Prevents lost chats/costs on mid-stream disconnect or refresh |
| `trust_boundary_map` | Explicit Control Plane vs. Untrusted Data Plane table | Stops indirect prompt injections via RAG, DOM, memory, or MCP metadata |
| `tool_least_privilege_matrix` | Tool -> Session Identity -> Resource ACL -> Max Calls | Prevents confused-deputy privilege escalation and tool-argument tampering |
| `hitl_binding_contract` | 7 bound fields (`tool`, `args_hash`, `requester`, `target`, `amount`, `expiry`, `nonce`) | Blocks approval reuse, argument swapping, and cross-user confirmation replay |
| `budget_and_loop_caps` | `maxSteps`, token limit, `AbortSignal` timeout, `sandboxId` TTL | Caps denial-of-wallet loops and prevents cross-tenant container leakage |
| `edd_eval_suite` | `pass@3 >= 90%` capability + `pass^3 = 100%` security/regression | Enforces objective, repeatable proof instead of one-off anecdotal vibes |

### 3.2 Canonical Pre-Call Persistence & Sandbox Isolation Pattern

```ts
// 1. Pre-create persistent chat/generation ID BEFORE calling Gateway
const generationId = nanoid();
await db.insert(generations).values({
  id: generationId, userId: session.userId, model: selectedSlug, status: "running",
});

// 2. Execute untrusted model-generated code ONLY inside per-user isolated Sandbox
const sandbox = getSandbox(env.Sandbox, `usr_${session.userId}_${generationId}`);
try {
  const execResult = await sandbox.runCode(codeSnippet, { language: "python" });
  return execResult;
} finally {
  await sandbox.destroy();
}
```

### 3.3 Evidence Classification (`confirmed` vs. `needs_validation`)

- Record `confirmed` ONLY when an automated code grader or reproducible adversarial PoC proves the boundary held across `3` consecutive runs (`pass^3 = 100%`).
- Mark `needs_validation` whenever an indirect injection vector, MCP client capability fallback, or HITL replay test has not yet been executed against the live handler.
- Never promote a feature past Spiral Phase 3C while any mutating tool remains in `needs_validation` state.

---

## 4. Verification Checklist

- [ ] Model identifiers are resolved dynamically or pinned to valid `provider/model` slugs without stale hardcoded aliases.
- [ ] Every persisted AI generation creates its `nanoid()` or `cuid2` database row before invoking the model and stores Blob URLs instead of base64.
- [ ] Prompt caching (`cacheControl`) is restricted strictly to static system or FAQ content and disabled for user conversations.
- [ ] Durable workflows isolate deterministic orchestration in `"use workflow"` from Node I/O and retries in `"use step"`.
- [ ] Every mutating tool handler verifies caller identity and resource ACLs from server session state after schema validation.
- [ ] High-risk HITL confirmations bind canonical tool name, normalized arguments hash, requester, target, amount, expiry, and single-use nonce.
- [ ] Untrusted LLM-generated code runs exclusively inside a per-user isolated Sandbox container cleaned up via `destroy()`.
- [ ] Authless MCP servers configure an exact numeric `trust proxy` hop count (never `true`) and inline `@modelcontextprotocol/ext-apps` when rendering widgets.
- [ ] Security and regression evals achieve `pass^3 = 100%` with zero `needs_validation` gaps on shipped mutating tools.

---

## 5. Hard Quality Gate

- **PASS**:
  - Trust-boundary map complete; all mutating tools enforce handler-side ACLs and parameter-bound HITL.
  - Zero `trust proxy: true`, zero external CDN ESM in MCP widgets, zero shared `sandboxId` across tenants, zero unpersisted streaming generations.
  - Capability evals `>= 90%` (`pass@3`) and security/regression evals `100%` (`pass^3`).
- **FAIL**:
  - Any tool handler trusting model-supplied `userId`/`tenantId` or unvalidated file/SQL paths, or reusable/unbound HITL confirmations.
  - `app.set('trust proxy', true)` in production, or guardrail prompts relied upon as the sole injection defense.
  - Any security eval `< 100%` on `pass^3`.

```bash
# 1. Static scan for trust-proxy wildcard, external CDN ESM in widgets, stale model literals, and raw base64 storage
rg -n "trust proxy.*true|esm\.sh|cdn\.jsdelivr|gpt-4o-2024|data:image/.*base64" src/

# 2. Type-check tool schemas and InferAgentUIMessage contracts
npx tsc --noEmit

# 3. Execute EDD capability & adversarial prompt-injection test suite (3 consecutive trials)
pytest -q --tb=short tests/ai/ --count=3
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Guardrail Prompt as Security Boundary** | System prompt rules like "never reveal secrets" are routinely bypassed by indirect injection | AuthZ or injection defense exists only in system prompt prose | Enforce Control vs. Data Plane isolation, handler ACLs, and parameter-bound HITL in code |
| **Streaming First, Persisting Later (or Ephemeral Base64)** | Browser refresh or stream abort loses output/cost; base64 bloats DB rows and context | `generateText`/`streamText` called before DB `INSERT` or `data:image/` stored in DB | Generate `nanoid()` before LLM call, redirect to `/chat/[id]`, store Blob URLs |
| **Unbound / Reusable HITL Approvals** | Attacker modifies arguments after prompt or replays confirmation token across retries | Confirmation boolean stored without `args_hash`, `target_id`, `expiry`, or single-use nonce | Bind all 7 confirmation fields server-side and consume nonce atomically on execution |
| **Schema vs. Dispatcher Disagreement** | LLM schema exposes safe subset while dispatcher forwards extra unvalidated properties | `...args` spread into SQL/fetch/subprocess after partial Zod parse | Strip unknown keys (`.strict()`) and re-validate canonicalized parameters inside handler |
| **`app.set('trust proxy', true)` in Production** | Allows trivial `X-Forwarded-For` header spoofing to bypass IP rate limits | Boolean `true` passed to Express `trust proxy` | Set exact numeric proxy hop count (`1` or `2`) matching verified load-balancer topology |
| **Shared `sandboxId` or Cross-Tenant Cache Key** | Leaks files, env vars, or cached answers between tenants | Global/static `sandboxId` or cache key missing `tenant_id` / ACL scope | Scope Sandbox IDs per user/session with `destroy()` and prefix RAG/cache keys by ACL |
| **Unbounded `maxSteps` or Delegated Spend Loops** | Prompt injection or tool error spins infinite paid LLM calls and external mutations | Agent loop lacks `maxSteps`, token ceiling, or `AbortSignal` timeout | Enforce `maxSteps`, per-request spend ceiling, and `AbortSignal` deadline |
| **Custom MCP Widget for Simple Form / Yes-No (Over-Engineering)** | Adds iframe CSP complexity, inline bundle size, and mobile layout bugs unnecessarily | Custom HTML widget built for 1–3 inputs or simple confirmation | Check `clientCapabilities.elicitation` first; build `ext-apps` widget only for spatial/rich UI |
