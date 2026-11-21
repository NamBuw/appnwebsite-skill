# Full-Stack Frontend Engineering

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs production web frontend engineering across Spiral Stages `3A`, `3B`, and `3C`, covering React, Next.js App Router (Server Components, Server Actions, `'use cache'`, Partial Prerendering), client caching (`SWR`), composable components, and Core Web Vitals.
It pairs **Radical Simplicity** (native HTML/CSS and URL state first) with strict RSC boundary safety.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Frontend Baseline & Anti-Overengineering Gate

Before installing a client state store, modal portal library, or form framework, run the four simplicity checks:
1. **Option A First**:
   - Default to **Server Components + native HTML (`<form>`, `<dialog>`, `<details>`, `popover`) + URL `searchParams` + Server Actions**.
   - Add a client query cache (`SWR`/TanStack Query) only for live polling, optimistic mutations, or high-frequency client filtering; avoid Redux/Zustand stores that merely mirror server JSON.
2. **Native HTML/CSS Before JS Libraries**:
   - Replace JS modal/focus-trap/accordion/dropdown packages with `<dialog>.showModal()`, `<details>`, CSS `:has()`, `clamp()`, and Grid/Subgrid wherever platform primitives meet accessibility rules (`0` extra KB).
3. **Rule of Three for Component Abstractions**:
   - Never extract generic `BaseCardWrapper` or 12-boolean-prop megacomponents (`isCompact`, `hasFooter`, `isBorderless`).
   - Compose small primitives with `children` slots or explicit named variants.
4. **Verified Performance Budget**:
   - Every heavy client widget, chart, or polyfill must justify its gzipped bundle cost against `LCP <= 2.5s`, `INP <= 200ms`, and `CLS <= 0.1`.

### 1.2 Rendering, Caching & Boundary Selection Matrix

| Route / UI Shape | Simplest Rendering Mode | Caching & Revalidation Mechanism | Forbidden Misuse |
|---|---|---|---|
| **Marketing, Docs, Public Catalog** | **SSG (Static Shell)** | Immutable CDN / `cacheLife('max')` | Reading session cookies or headers inside a cached shell |
| **Shared Data + Personal Shell** | **PPR (`'use cache'` + `<Suspense>`)** | `cacheTag()` + `cacheLife()`, `updateTag()` (read-your-own-writes) or `revalidateTag(tag, profile)` | Accessing `cookies()`/`headers()`/`searchParams` inside `'use cache'` (pass primitives or use `'use cache: private'`) |
| **Authenticated / Live View** | **Dynamic SSR + `<Suspense>` Streaming** | `await connection()`, per-request `React.cache()` deduplication | Sequential `await` waterfalls blocking above-the-fold shell |
| **High-Frequency Interactive / Live UI** | **CSR Leaf + `useSWR` / `useSWRSubscription`** | `useSWRMutation` (`optimisticData` + `rollbackOnError: true`), conditional `null` keys | Fetching initial page data in `useEffect` when a Server Component can stream it |

### 1.3 React & Next.js 8-Tier Priority Optimization Hierarchy

Apply optimizations strictly in ROI order rather than micro-optimizing hot JS loops while leaving 800ms network waterfalls intact:
1. **CRITICAL — Eliminate Async Waterfalls**:
   - Parallelize independent fetches via `Promise.all()`.
   - Hoist `preload()` triggers and stream slower panels behind `<Suspense>`.
2. **CRITICAL — Shrink Client Bundles**:
   - Ban barrel imports (`import { Icon } from '@lib'`).
   - Lazy-load heavy client widgets via `next/dynamic` and defer analytics until post-hydration.
3. **HIGH — Server Boundary Security & Serialization**:
   - Treat every `'use server'` action as a public HTTP `POST` endpoint (validate schema + verify session + check resource ownership inside the action).
   - Pass only JSON-serializable primitives/plain objects/ISO strings across the Server-to-Client boundary (never `Date`, `Map`, `Set`, class instances, or non-action closures).
4. **MEDIUM-HIGH — Client Deduplication & Passive Listeners**:
   - Use `SWR` for client request deduplication.
   - Attach `{ passive: true }` on scroll and touch listeners.
5. **MEDIUM — Render Hygiene**:
   - Derive computed values inline during render (zero `useEffect` state syncing).
   - Use functional `setState(prev => ...)` and wrap non-urgent updates in `startTransition` or `useDeferredValue`.
6. **MEDIUM — DOM Discipline**:
   - Keep DOM nodes `< 1,400` and apply `content-visibility: auto` on long lists.
   - Prefer `cond ? <A /> : null` over `count && <A />` to avoid rendering literal `0`.
7. **LOW-MEDIUM — Hot-Path Structures**:
   - Use `Set`/`Map` for `O(1)` membership lookups in render loops (`> 500` items).
8. **LOW — Stable Refs & Once-Per-App Init**:
   - Keep mutable non-visual handles in refs and initialize client SDKs once outside render bodies.

### 1.4 Quantitative Core Web Vitals & Token-Economy Targets

- **LCP `<= 2.5s`**:
  - Set explicit dimensions, `sizes`, and `fetchPriority="high"` on hero media.
  - Self-host/preload fonts and eliminate render-blocking third-party scripts.
- **INP `<= 200ms`**:
  - Yield main-thread tasks `> 50ms` via `scheduler.yield()` or `startTransition`.
  - Keep `'use client'` boundaries strictly at interactive leaves.
- **CLS `<= 0.1`**:
  - Reserve exact aspect ratios on media and `<Suspense>` skeletons.
  - Apply theme/locale attributes pre-hydration to prevent layout shifts.
- **Client JS Ceiling**:
  - Target `<= 100 KB` gzipped initial JS for marketing/content routes.
  - Target `<= 180 KB` gzipped initial JS for stateful application shells.

---

## 2. Step-by-Step Workflow

1. **Map Routes, Rendering Modes & File Collisions** *(Owner: Frontend Engineer | Inputs: `architecture.md`, `feature-breakdown.md` | Output: Route boundary manifest)*
   - Assign every route segment to Static, `'use cache'` PPR, or Dynamic SSR + `<Suspense>`.
   - Ensure no folder defines both `page.tsx` and `route.ts` simultaneously.
   - Reserve `route.ts` for webhooks, external/mobile REST APIs, or HTTP-cacheable GETs—Server Components read domain services directly.
   - Keep `proxy.ts` / `middleware.ts` strictly for rewrites, headers, or locale routing—never as the sole auth gate.

2. **Enforce RSC Serialization & Leaf Client Boundaries** *(Owner: Frontend Engineer | Inputs: Domain services & DTOs | Output: Server + leaf Client Components)*
   - Keep layout shells, headings, and formatting as zero-JS Server Components.
   - Isolate `'use client'` strictly to interactive leaves (buttons, forms, charts).
   - Confirm zero `'use client'` components are marked `async`.
   - Convert `Date` instances to `.toISOString()` strings before crossing Server-to-Client boundaries.
   - Deduplicate per-request server reads with `React.cache()`.

3. **Eliminate Waterfalls & Compose Native-First UI** *(Owner: Frontend Engineer | Inputs: Design tokens & UI slice | Output: Streaming routes)*
   - Replace sequential `await` chains with `Promise.all()` and separate `<Suspense>` slots so primary content paints immediately.
   - Build multi-part UI using **Compound Components** (`<Dialog>`, `<Tabs>`) sharing typed `{ state, actions, meta }` context instead of boolean-prop explosion.
   - In React 19+, read context with `use()` and accept `ref` directly as a prop without `forwardRef`.
   - Store shareable filters, sort order, and pagination in URL `searchParams` instead of global client stores.

4. **Wire Server Actions, Optimistic SWR & Navigation Error Boundaries** *(Owner: Frontend Engineer | Inputs: Auth & DTO schemas | Output: Resilient mutations)*
   - Inside every `'use server'` action:
     - Parse and validate input schema (Zod/Valibot).
     - Verify active session AND resource ownership (`resource.ownerId === session.userId`).
     - Mutate domain state and call `updateTag()` (immediate caller read) or `revalidateTag(tag, profile)` (SWR).
   - Use `useSWRMutation` with `optimisticData` + `rollbackOnError: true` for optimistic client updates.
   - Pass `null` as the SWR key whenever required fetch prerequisites are unset.
   - Co-locate `error.tsx` (`'use client'`), `not-found.tsx`, `unauthorized.tsx`, and `forbidden.tsx`:
     ```ts
     try {
       await mutateOrder(id);
     } catch (err) {
       unstable_rethrow(err); // Never swallow redirect() / notFound() / forbidden()
       return { error: "Unable to update order" };
     }
     ```

5. **Bundle Audit, Pre-Ship Deletion Pass & Fresh Verification** *(Owner: Frontend Engineer | Tool: Bundle analyzer + typecheck + tests | Output: Condensed bundle)*
   - Inspect client chunks (`npx next experimental-analyze` or `vite-bundle-visualizer`) to catch barrel imports or server SDK leaks.
   - Execute **Pre-Ship Deletion/Condensation Pass**:
     - Delete `useEffect` chains mirroring derived state (`const fullName = ...`).
     - Replace custom JS modal/accordion wrappers with `<dialog>`/`<details>` and flatten wrapper `<div>` soup.
     - Remove unused hooks, CSS rules, and unreferenced icons.
   - **Re-run typecheck, production build, and tests AFTER final deletions.**

---

## 3. Reusable Artifact & Template

Connect frontend route contracts and locale readiness to:
- [API Contract Spec](../templates/api-contract-spec.md)
  - Section 3 (Client-Server DTOs & Validation), Section 4 (RFC 9457 Error Shapes), and Section 7 (Frontend Route & Boundary Manifest)
- [i18n/L10n Spec](../templates/i18n-l10n-spec.md)
  - Section 4 (RTL Logical Properties & `+35%` Expansion Headroom)
- **Boundary Rules Enforced**:
  - Zero `async` client leaves and zero non-serializable RSC props
  - AuthN + AuthZ verified inside every `'use server'` action
  - Target CWV budgets (`LCP <= 2.5s`, `INP <= 200ms`, `CLS <= 0.1`)

### Frontend Route & Boundary Manifest Schema

| Field | Required Specification | Example Value |
|---|---|---|
| `route_path` | App route segment & dynamic params | `/workspaces/[id]/orders` |
| `render_mode` | `SSG` \| `PPR-'use cache'` \| `SSR-Suspense` \| `CSR-SWR` | `PPR-'use cache' + <Suspense> table` |
| `cache_policy` | `cacheLife` profile, `cacheTag`, invalidation call | `cacheLife('minutes'), cacheTag('orders-' + id), updateTag` |
| `client_leaves` | Exact `'use client'` leaf components & gz size | `OrderFilterBar.tsx, CancelOrderDialog.tsx (14 KB gz)` |
| `server_actions` | `'use server'` endpoints + schema/AuthZ proof | `cancelOrderAction (Zod + session + owner check)` |
| `cwv_budget` | Target `LCP`, `INP`, `CLS` thresholds | `LCP <= 1.8s, INP <= 120ms, CLS <= 0.02` |

---

## 4. Verification Checklist

- [ ] Every route selects Static, `'use cache'` PPR, or Dynamic SSR deliberately, with zero `route.ts` and `page.tsx` collisions.
- [ ] Zero `'use client'` components are declared `async`, and zero non-serializable values (`Date`, `Map`, `Set`, functions) cross RSC boundaries.
- [ ] Independent data queries execute in parallel (`Promise.all` / `<Suspense>` streaming) without critical-path waterfalls.
- [ ] Every `'use server'` action validates its input schema, authenticates the caller, and checks resource ownership internally.
- [ ] Navigation throws (`redirect`, `notFound`, `forbidden`, `unauthorized`) are never swallowed inside `try/catch` without `unstable_rethrow`.
- [ ] Derived values compute inline during render without `useEffect` sync chains, and URL `searchParams` own shareable filters.
- [ ] Native HTML primitives (`<dialog>`, `<details>`, `<form>`) and compound components replace boolean-prop explosions and custom portals.
- [ ] Production build, bundle check, and CWV budgets (`LCP <= 2.5s`, `INP <= 200ms`, `CLS <= 0.1`) pass **after** the Deletion/Condensation Pass.

---

## 5. Hard Quality Gate

- **PASS Criteria**:
  - `tsc --noEmit`, production build (`next build` / `vite build`), and component/E2E smoke tests exit `0` **after** final simplification edits.
  - Zero hydration mismatches on server-rendered markup.
  - Zero unauthenticated Server Actions (`'use server'` enforces schema + session + ownership).
  - Zero sequential fetch waterfalls on primary routes.
  - Core Web Vitals within `LCP <= 2.5s`, `INP <= 200ms`, `CLS <= 0.1`.
- **FAIL Criteria**:
  - Client component marked `async` or passing non-serializable props (`P0`).
  - Missing AuthZ ownership check inside a Server Action (`P0`).
  - Relying solely on `middleware.ts`/`proxy.ts` for access control (`P0`).
  - `try/catch` swallowing `redirect()`/`notFound()`, barrel-import bundle bloat, or `CLS > 0.1` / `INP > 200ms` regression (`FAIL`).

```bash
# Verify TypeScript, production build, and quiet frontend tests after final edits
npx tsc --noEmit && npm run build && npm test -- --silent
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Boolean Prop Explosion & Div Soup** | `isCompact`/`hasHeader`/`noPadding` flags yield `2^N` untested states and brittle CSS | `> 4` boolean layout flags or 6 nested `<div>` wrappers | Compound components (`<Card><Card.Header /></Card>`) + `children` slots |
| **Global Client Store for Server JSON** | Mirroring fetched entities in Redux/Zustand adds stale-cache bugs and hydration bloat | `useEffect` dispatching `fetch()` results into global store | Server Components + URL `searchParams` + `SWR` for live queries |
| **`useEffect` Derived State & Waterfalls** | Computing derived values in `useEffect` causes double renders; stacked `await`s stall TTFB | `useEffect(() => setDerived(...))`; sequential `await`s | Compute `const derived = ...` inline; use `Promise.all()` + `<Suspense>` |
| **Unauthenticated Actions & Proxy-Only Auth** | `'use server'` compiles to public `POST`; middleware matchers miss subrequest quirks | Action trusting `userId` arg without session+ownership check | Validate schema + verify session + check `ownerId === userId` inside action |
| **Swallowing `redirect()` in `try/catch`** | Next.js navigation throws internal control errors; catching them breaks redirects | `try { redirect('/x'); } catch (e) { return { err }; }` | Call `redirect()`/`notFound()` outside `try/catch` or `unstable_rethrow(err)` |
| **Barrel Imports & Custom Modal JS** | Barrel `index.ts` drags entire icon/chart trees into client bundles; custom modals break a11y | `import { X } from '@/components'` or 3P `react-modal` deps | Direct subpath imports + `next/dynamic`; native `<dialog>` and `<details>` |
