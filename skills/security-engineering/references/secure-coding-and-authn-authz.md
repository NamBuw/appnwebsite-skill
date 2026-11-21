# Secure Coding, AuthN/AuthZ, Sessions & API/LLM Boundaries

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Production secure coding invariants for Spiral `3A`, `3B`, and `3C`. Enforce controls at the **last trusted decision point** (central router dependency, DAL, or Postgres RLS) using native primitives over brittle regexes or dispersed checks.

---

## 1. Decision Framework

### 1.1 Authentication, Session & Token Architecture Matrix

| Client Surface | Recommended Primary Mechanism | Required Cookie / Token Contract | Forbidden Pattern |
|---|---|---|---|
| **Browser Web / SaaS App** | **Backend-for-Frontend (BFF)** server-managed opaque CSPRNG session (`>= 128-bit` entropy) | `__Host-session` cookie (`HttpOnly`, `Secure` conditional on TLS/prod via `SESSION_COOKIE_SECURE`, `SameSite=Lax` or `Strict`, `Path=/`) + CSRF token / `Origin` check | Storing session IDs, access tokens, or refresh JWTs in `localStorage` or `sessionStorage` |
| **Passwordless / MFA** | **WebAuthn / Passkeys** (Conditional UI + server challenge) | Verify RP ID, exact origin, fresh single-use challenge, `userHandle`, and User Verification (`UV`) flag; bind step-up to initiating session | Client-trusted assertion flags or unverified `origin` / `rpId` |
| **SSO / Federated Login** | **OAuth 2.1 + PKCE (`S256`) + OIDC** | Exact `redirect_uri` allowlist, cryptographic `state` + `nonce`, validate `iss`, `aud`, `exp`, pinned JWKS `alg` (`alg != none`) | Implicit flow, wildcard `redirect_uri`, or skipping `state`/`nonce` validation |
| **Non-Browser API / Mobile** | Short-lived **JWT (`<= 15 min`)** + rotating opaque refresh token, OR scoped API keys | Asymmetric pinned algorithm (`RS256`/`EdDSA`), `exp`/`nbf`/`iss`/`aud` checked; API keys hashed (`SHA-256`/`HMAC`) with non-secret prefix (`rk_...`) | Long-lived non-revocable JWTs or trusting unverified JWT headers (`kid`/`jku`) |

### 1.2 Authorization & Multi-Tenant Isolation Model Selector

Choose the simplest authorization model whose enforcement cannot drift across endpoints:

| Scale & Sharing Complexity | Selected AuthZ Model | Enforcement Boundary | Escalation Trigger |
|---|---|---|---|
| **Coarse Roles (`<= 5` roles)** | **RBAC** | Central router dependency (`Depends()`, middleware) + explicit handler permission check | Object ownership or plan-tier predicates needed -> upgrade to ABAC |
| **Owner / Org / Plan Predicates** | **ABAC** | Shared policy helper at DAL + object-level `owner_id`/`org_id` predicate on every query | Multi-tenant SaaS sharing one Postgres database -> enforce RLS |
| **Multi-Tenant Shared DB** | **ABAC + Postgres Row-Level Security (RLS)** | `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY` + session-scoped `app.tenant_id`; audit every service-role bypass | Arbitrary deep folder/doc sharing graphs (`A -> B -> C`) |
| **Hierarchical Graph ACLs** | **ReBAC** (Zanzibar-style tuples) | Dedicated tuple store + central check API + search/cache ACL sync | Only when flat tenant/org/owner predicates genuinely fail |

### 1.3 Simplest High-Craft Security Controls (Anti-Overengineering)

Before writing custom middleware, sanitizers, or crypto, ask:
1. *"Does our framework, ORM, or DB already provide this guarantee (parameterized SQL, JSX escaping, CSRF, Postgres RLS, Argon2id/scrypt) with zero custom parsing risk?"*
2. *"Are we duplicating validation across 10 controllers instead of enforcing one fail-closed invariant at the last trusted decision point?"*
3. *"Are we building a custom ReBAC engine or JWT parser when 3 roles + Postgres RLS + a standard OIDC/WebAuthn library suffices?"*
4. **Simplest High-Craft Option**: Use BFF `__Host-` cookies, native schema validation (`Zod` / Pydantic `extra='forbid'`), parameterized SQL + RLS, Argon2id, and `DOMPurify` only for rich HTML.

---

## 2. Step-by-Step Workflow

1. **Boundary Schema Validation, DTO Separation & Proxy Trust (`3A / 3B`)**
   - **Inputs**: OpenAPI/API routes, Next.js Route Handlers & Server Actions (`"use server"`), FastAPI/Express/Go controllers.
   - **Owner**: Backend / Full-Stack Engineer.
   - **Tool / Script**: `Zod` / `Valibot` (TS), `Pydantic` (`ConfigDict(extra='forbid')`, Python), `check_security_baseline.py`.
   - **Action**:
     - Validate every untrusted body, query/path param, header, cookie, and webhook at runtime (TypeScript types erase at compile time).
     - Separate **Input DTOs**, **DB Models**, and **Public Response DTOs** to prevent mass assignment (`is_admin`) and over-exposure; use opaque UUIDv4/UUIDv7 IDs against enumeration.
     - Verify `Host` and proxy headers: enable `TrustedHostMiddleware` (FastAPI/Django) and restrict `--forwarded-allow-ips` / trusted hops to block `X-Forwarded-For` rate-limit bypass and `X-Forwarded-Host` reset poisoning.
   - **Output**: Strictly typed, mass-assignment-safe API boundary handlers.

2. **Authentication, Password Hashing, Session Lifecycle & Framework Traps (`3B`)**
   - **Inputs**: Login, signup, password reset, MFA, OAuth callback, Server Actions.
   - **Owner**: Auth / Backend Engineer.
   - **Tool / Script**: `argon2-cffi` / Node `crypto.scrypt`, framework session libs, `semgrep`.
   - **Action**:
     - Hash passwords with `Argon2id` (or `scrypt` / `bcrypt` cost `>= 12`), require `>= 12` chars, screen breached passwords, and rate-limit login/reset/OTP routes.
     - Regenerate session IDs on login, MFA elevation, and privilege change (session fixation). Invalidate **all** active sessions and refresh tokens on logout, password change/reset, deactivation, or org removal.
     - Bind account linking, OAuth `state`, and MFA recovery to the authenticated initiating session and verified email/credential ownership against pre-hijacking.
     - **Next.js / RSC Rules**: Treat every `"use server"` Server Action as a public `POST` endpoint needing explicit authn/authz and `serverActions.allowedOrigins`; never treat `.bind()` args as secret (sent unencrypted unlike closures); keep user data out of `"use cache"` / `force-static`; keep secrets out of `NEXT_PUBLIC_*` / `"use client"`; patch Next.js RSC/middleware CVEs (`15.0.5+` / `16.0.7+` for React2Shell CVE-2025-66478); verify webhook HMACs over raw unparsed bodies.
     - **FastAPI / Python Rules**: Enforce fail-closed auth via router/app `Depends()`/`Security()`; disable `/docs`, `/redoc`, and `debug=True` in prod; use Jinja `Environment(autoescape=True)` and never pass user strings to `Template(...)` (SSTI).
   - **Output**: Hardened auth/session lifecycle across browser and API paths.

3. **Authorization, Multi-Tenant Isolation & Data Lifecycle Guards (`3B`)**
   - **Inputs**: DAL queries, Postgres RLS policies, search/cache keys, export/batch endpoints.
   - **Owner**: Backend / Database Engineer.
   - **Tool / Script**: `psql` RLS policy checks + cross-tenant integration tests (`TenantA` vs `TenantB`).
   - **Action**:
     - Enforce object-level (`BOLA`/`IDOR`) and property-level (`BOPLA`) authorization on **every** single-item, nested-resource, bulk/batch, and async export endpoint.
     - Isolate multi-tenant Postgres tables with `RLS` policies; audit every `service_role` / `SECURITY DEFINER` function to ensure it explicitly filters by verified caller `tenant_id`.
     - Prefix cache keys and object-storage paths with server-derived `tenant_id` (canonical composite keys without separator ambiguity), mirror ACL filters into search/analytics indexes, enforce soft-delete/tombstone checks uniformly, and re-verify permissions before executing queued exports or restores.
   - **Output**: Tenant-isolated DAL, cache, search, and export paths.

4. **Injection, XSS, CSRF, CORS, SSRF, File Uploads, XXE & Deserialization (`3B`)**
   - **Inputs**: SQL/ORM calls, DOM/JSX rendering, CORS/CSRF config, outbound HTTP clients, upload/XML/YAML/exec handlers.
   - **Owner**: Full-Stack Engineer.
   - **Tool / Script**: `python3 skills/security-engineering/scripts/check_security_baseline.py --path . --json`, `semgrep`, `bandit`.
   - **Action**:
     - **SQLi**: Parameterized queries (`%s` / `$1` / `?`) or safe ORM builders only; zero f-strings, `%`, `.format()`, or `+` in `.execute()`; run app DB user with least privilege over TLS/mTLS; return generic error payloads (`RFC 9457`) without SQL traces.
     - **XSS & Browser**: Rely on React/Vue/Svelte text auto-escaping (`{val}`); ban `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, and `javascript:` URLs; wrap unavoidable rich HTML in `DOMPurify.sanitize()` paired with strict HTTP header CSP (`script-src 'self' 'nonce-...'`, `frame-ancestors 'none'`, `require-trusted-types-for 'script'` — remember `<meta>` CSP ignores `frame-ancestors`/`sandbox`); validate `postMessage` against an exact `event.origin` allowlist and pass an explicit `targetOrigin`; avoid global `window.x ||` DOM-clobbering gadgets; set `Cache-Control: no-store` on sensitive authenticated responses.
     - **CSRF & CORS**: Enforce Synchronizer/Double-Submit CSRF tokens + `Origin` validation on all cookie-authenticated state changes (`@csrf_exempt` banned); omit CORS headers unless cross-origin access is strictly required, use an exact origin allowlist, and **never** emit `Access-Control-Allow-Origin: *` alongside `Access-Control-Allow-Credentials: true`.
     - **SSRF & Open Redirects**: Allowlist `https:` schemes and explicit hostnames; resolve DNS and block loopback, RFC1918 private ranges, link-local (`169.254.169.254` metadata IP), and IPv6 ULA/mapped addresses; disable automatic HTTP redirects (or re-validate every hop); enforce connect/read timeouts. Restrict post-login redirects to relative paths starting with a single `/` (rejecting `//evil.com`, `/\evil.com`, and `https:`).
     - **File Uploads, Path Traversal, XXE, Deserialization & OS Exec**: Validate file extension AND magic-byte signature (`python-magic` / header bytes), cap upload size (`1–10 MB`), rename to server-generated UUID, store outside webroot/`public/` in non-executable storage, and serve downloads with `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff`. Canonicalize file paths and check `resolved.startsWith(baseDir + sep)`; inspect archive entries (`zip`/`tar`) against zip-slip `..` traversal before extraction. Disable XML DTDs and external entities (`defusedxml`). Ban `pickle`, `cPickle`, `marshal`, `yaml.load` (use `SafeLoader`), and `torch.load` without `weights_only=True`. Use `subprocess.run([...], shell=False)` / `execFile` argument arrays — never `shell=True` or `os.system`.
   - **Output**: Injection-free, sandboxed I/O and rendering code.

5. **OWASP API Rate Limits, Webhooks, Business Logic & AI/LLM Isolation (`3B`)**
   - **Inputs**: Public/auth endpoints, billing/checkout state machines, LLM/RAG tool dispatchers.
   - **Owner**: Backend / AI Engineer.
   - **Tool / Script**: `check_security_baseline.py` + concurrency/state-machine unit tests.
   - **Action**:
     - Apply per-IP and per-principal rate limits, pagination caps, and GraphQL depth/complexity limits. Protect financial/state transitions with atomic DB transactions (`SELECT ... FOR UPDATE` or optimistic version columns), idempotency keys, and positive-quantity/sign validation to prevent race/double-spend and step-skipping.
     - For AI/LLM features, enforce strict **Control-Plane vs Data-Plane separation**: treat retrieved RAG chunks, emails, web pages, and MCP tool responses as untrusted data. Never rely on system-prompt guardrails as an authorization boundary; validate tool arguments via code-side schemas and caller-scoped permissions at the dispatcher, bind human-in-the-loop (HITL) confirmations to exact immutable parameters, isolate RAG vectors by `tenant_id`, and enforce hard iteration/token budgets on delegated agent loops.
   - **Output**: Atomic business logic and code-enforced LLM tool boundaries.

6. **Complexity Budget & Security Code Condensation Pass (`3C`)**
   - **Inputs**: Implemented modules + test suite (`127.0.0.1` loopback test harness).
   - **Owner**: Tech Lead / Peer Reviewer.
   - **Tool / Script**: `python3 skills/security-engineering/scripts/check_security_baseline.py --path . --json`, `pytest` / `vitest`.
   - **Action**: Delete redundant ad-hoc regex checks or duplicate controller wrappers that shadow a single clean router dependency or DB RLS policy, confirm test servers bind strictly to `127.0.0.1` (never `0.0.0.0`), verify all logs mask PII/tokens, and re-run automated baseline + unit/integration tests after cleanup.
   - **Output**: Lean, verified security controls with zero redundant wrappers.

---

## 3. Reusable Artifact & Template

Document every implemented control invariant and waiver inside [Security Verification Plan Template](../templates/security-verification-plan.md) (`docs/security/security-verification-plan.md`):

| Schema Section | Field Contract | Required Evidence |
|---|---|---|
| **Scope & Simplicity** | `Risk Elevation Triggers`, `Simplest High-Craft Control Choice`, `Deleted Redundant Controls` | Explicit native primitive choice over custom crypto/sanitizers |
| **Control Matrix (`CTL-01..N`)** | `Control ID | Domain | Target File & Symbol | Enforced Invariant | Verification Test | Status` | Maps each control to last trusted decision point and test symbol |
| **Automated CLI Commands** | `check_security_baseline.py`, `semgrep`, `bandit`, `osv-scanner`, `gitleaks` | Fresh post-edit exit codes recorded |
| **Security Waivers (`SW-NNN`)** | `Waiver ID | Control/Rule | File:Line | Compensating Control | Approver & Owner | Expiry (UTC)` | Replaces any temporary deferrals with time-bound accountability |

---

## 4. Verification Checklist

- [ ] Browser sessions use opaque CSPRNG tokens in `__Host-` `HttpOnly` `SameSite=Lax` cookies.
- [ ] Zero access tokens, refresh tokens, or session IDs reside in `localStorage` or `sessionStorage`.
- [ ] Passwords use Argon2id or scrypt (`>= 12` chars) and all sessions invalidate on logout/reset/removal.
- [ ] Every protected route, Server Action, and DAL query verifies principal auth and tenant/object ownership.
- [ ] Multi-tenant database tables enforce Postgres RLS and audit every service-role bypass path.
- [ ] All SQL queries use parameterized placeholders (`%s`/`$1`) with zero string interpolation or concatenation.
- [ ] Rich HTML rendering uses `DOMPurify.sanitize()` paired with nonce CSP and `Trusted Types`.
- [ ] CORS forbids `*` with credentials; cookie state changes enforce CSRF tokens and `Origin` checks.
- [ ] Outbound URL fetchers block private/loopback/`169.254.169.254` IPs and disable unvalidated redirects.
- [ ] File uploads validate magic bytes, cap size, randomize UUID filenames outside webroot, and prevent zip-slip.
- [ ] XML parsers disable DTDs/XXE; `pickle`/`yaml.load`/`shell=True`/`eval` sinks are eliminated.
- [ ] LLM tool dispatchers enforce server-side schema and caller authorization rather than prompt guardrails.

---

## 5. Hard Quality Gate

Run deterministic static baseline and SAST checks offline after the final implementation edit (`3B -> 3C -> Q4`):

```bash
python3 skills/security-engineering/scripts/check_security_baseline.py --path . --json
semgrep scan --config auto --error .
bandit -r src/ -ll
```

- **Entry Condition**: Linked `threat-model.md` (`TM-NNN`) and runtime DTO/RLS schema contracts exist before implementing protected endpoints.
- **Primary Offline Check**: `check_security_baseline.py`, `semgrep`, and `bandit` execute cleanly with `$SECURECODER_API_PORT` unset; any optional IDE hook skips silently.
- **Freshness Requirement**: All baseline, SAST, and `127.0.0.1` AuthN/AuthZ/IDOR regression tests MUST run *after* the final code edit.
- **PASS**: `0` `High/Critical` baseline or SAST findings; `check_security_baseline.py` exits `0`; all AuthN, AuthZ, cross-tenant IDOR, and injection regression tests pass against `127.0.0.1` loopback fixtures; and any deliberate temporary exception is documented via an approved, expiring `Security Waiver (SW-NNN)`.
- **FAIL**: Any SQLi, XSS, SSRF, command execution, unsafe deserialization, `localStorage` auth token, wildcard CORS + credentials, missing Server Action / router auth, or `0.0.0.0` binding in test harnesses.
- **Waiver Guard**: Never leave bare unresolved debt markers in source or docs; unapproved or expired `SW-NNN` waivers fail the gate immediately.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Tokens in `localStorage` / `sessionStorage`** | Any XSS payload or malicious third-party script trivially reads and exfiltrates the bearer token | `localStorage.setItem("access_token", ...)` in client code | Store opaque session IDs in `__Host-` `HttpOnly` cookies via a thin BFF |
| **Wildcard CORS + Credentials** | Enables cross-origin authenticated reads depending on browser/proxy reflection quirks | `Access-Control-Allow-Origin: *` paired with `Credentials: true` | Omit CORS unless required, or match against an exact server allowlist |
| **`SameSite=Lax` Only CSRF Complacency** | Sibling-subdomain compromise, top-level GET state mutations, or older clients still bypass `SameSite` | Cookie-auth `POST`/`DELETE` endpoints lacking CSRF token or `Origin` verification | Pair `SameSite=Lax` with Synchronizer/Double-Submit CSRF token + `Origin` check |
| **Prompt Guardrail as AuthZ Boundary** | Indirect RAG or user prompt injection overrides text instructions and invokes privileged tools | System prompt says "never delete user data" while tool handler lacks caller authz | Enforce caller-scoped RBAC/ABAC and parameter schemas inside the tool dispatcher |
| **Bespoke Crypto / Custom JWT Parsers** *(Anti-Overengineering)* | Hand-rolled signing, encryption, or HTML regex sanitizers introduce subtle padding/bypass CVEs | Custom `hmac` token encoder or regex `<script>` stripper instead of stdlib/vetted libs | Use vetted OIDC/JWT/Argon2id/DOMPurify libraries and native framework escaping |
| **Premature ReBAC Graph Engine for 3-Role CRUD** *(Anti-Overengineering)* | Adds operational latency, sync drift, and complex ACL bugs where simple tenant predicates suffice | Deploying distributed tuple graph service for a 3-role single-org SaaS | Start with central RBAC/ABAC + Postgres RLS (`Simplest High-Craft Option`) |
