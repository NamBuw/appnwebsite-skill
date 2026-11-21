# Web Apps and SaaS Workspaces

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module defines engineering and interaction standards for stateful SaaS applications, operational consoles, keyboard-driven workspaces, CRUD workflows, virtualized data grids, and embedded agent/MCP UI artifacts (`generative_ui` and SEP-1865 MCP Apps). It enforces Radical Simplicity ("Least Code, Highest Craft"), URL-backed shareable state, and worst-case `break-ui` stress resilience.

---

## 1. Decision Framework

### 1.1 Workspace Shell Selection Matrix

Match application navigation topology strictly to route count and workflow density:

| Shell Archetype | Route / Pane Budget | Best-Fit Product Class | Core Structural Rule |
|---|---|---|---|
| **Top Nav Shell** | `1-5` top-level sections | Focused single-purpose SaaS, billing portal, lightweight CRM | Keep header `<= 64px`; zero nested flyout menus on desktop |
| **Collapsible Left Rail** | `6-15` primary routes | Multi-module B2B SaaS, project workspaces, admin consoles | Persist rail collapse state cleanly; highlight active route with `aria-current="page"` |
| **Tri-Pane Operational Shell** | Outline rail + Dominant viewport (`>= 55%` width) + Inspector | Log/trace explorers, IDE-like editors, triage consoles, data workbenches | Use `min-w-0` on center grid track; inspector collapses into slide-over `<Sheet>` `< 1024px` |
| **Command-First Power Workspace** | Grouped `Cmd+K` palette + dense list/detail view | Issue trackers, developer consoles, keyboard-heavy operations | Every primary action reachable via keyboard without touching the pointer |

### 1.2 Overlay & Edit Surface Ladder

Select the least disruptive surface capable of completing the edit without losing user context:

1. **Inline Edit (`1-2` fields)**: Rename title, toggle status, or edit single cell directly in place with `Enter` to commit and `Escape` to cancel.
2. **Slide-Over `<Sheet>` / Drawer (`3-8` fields or record inspection)**: Open from the right edge (`380-540px` desktop, full-height mobile) while preserving background list scroll and selection context.
3. **Focused `<Dialog>` (`>= 4` interdependent fields)**: Reserve centered modals for focused multi-field creation or irreversible confirmations (`<AlertDialog>`). Never stack modal-on-modal.

### 1.3 Embedded Agent & Inline Artifact Surface Matrix

When building inline tool outputs or MCP App surfaces inside a host chat/IDE:

| Surface Mode | Viewport & Height Rule | Styling & Theme Contract | Persistence & Capability Rule |
|---|---|---|---|
| **Plain JSON / Markdown** | Default for static summaries or `< 3` simple metrics | Host typography | Zero custom UI code |
| **MCP Elicitation** | Structured flat form/confirmations | Host-rendered native inputs | Server declares schema; no custom HTML bundle |
| **Inline Widget (`generative_ui`)** | `<= 450px` target (`800px` max height); **never** `h-screen` / `100vh` / `height: 100%` | Transparent flush `<body>`; use `--background`, `--card`, `--foreground`, `--card-border` (`0` `:root` fallbacks or `--vscode-*`) | Redraw `<canvas>` on `themechange` listener; min text `12px` |
| **Standalone Side-Pane (`> 450px`)** | Persistent multi-panel workspace or wide table/canvas | Host `--color-background-*` / `--color-text-*` variables | Call `applyDocumentTheme` + `applyHostStyleVariables` in `connect()` & `onhostcontextchanged` |
| **MCP App (`ui://` SEP-1865)** | Single-file HTML bundle (`< 10 MiB`, tool result `< 1 MiB`) | `default-src 'none'` CSP + explicit bare origin fields | Register handlers BEFORE `app.connect()`; persist eagerly via `app-only` tools (never `localStorage`) |

### 1.4 Simplest High-Craft Option

**Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft")**: Before introducing Redux/Zustand client stores, custom modal portals, or heavyweight UI grid frameworks, test the simplest high-craft baseline:
- URL `searchParams` for filters, sorting, pagination, and active inspector tabs.
- Server-fetched initial state (RSC / route loader) instead of client cache duplication.
- Native HTML `<dialog>` / `<form>` or thin Radix/shadcn compound primitives.
- CSS Grid `minmax(0, 1fr)` with `min-w-0` flex/grid truncation guards.

Deleting duplicated client-side state mirrors eliminates whole classes of stale-cache bugs and shrinks client bundles by `30-70%`.

---

## 2. Step-by-Step Workflow

### Token Economy Protocol
- Read only the active route tree and OpenAPI/Zod schema rather than scanning unrelated app slices.
- Run Playwright `break-ui` and `axe-core` scripts to verify DOM constraints and keyboard traps deterministically.
- Keep component props minimal and rely on host/CSS variables instead of verbose inline style overrides.

1. **Lock Workspace Shell & URL-State Contract (`Owner: Frontend Architect`)**
   - **Inputs**: `architecture.md`, `openapi.yaml` (or route contracts), `tokens.json`.
   - **Action**: Map every route to one shell archetype (`Top Nav`, `Left Rail`, `Tri-Pane`, `Command-First`). Partition state strictly into:
     - *URL `searchParams`*: filters, sort order, pagination cursor, active tab, selected inspector entity (`history.replaceState` for rapid filter typing; `history.pushState` for committed entity/tab navigation so browser Back works cleanly).
     - *Server Cache / Query Layer*: canonical entities fetched with typed schemas.
     - *Ephemeral Local UI State*: hover preview, uncommitted form input, drag offset (`useState` only).
   - **Outputs**: Route shell map and URL parameter schema.

2. **Build Keyboard-First Navigation & Command Palette (`Owner: Frontend Engineer`)**
   - **Inputs**: Route shell map, action inventory.
   - **Action**:
     - Implement a grouped `Cmd+K` / `Ctrl+K` palette (`CommandInput`, `CommandGroup`, `CommandList`) indexing navigation, quick filters, and top commands with visible shortcut hints.
     - Guard global single-key shortcuts (`j`/`k`, `/`, `c`) so they NEVER fire when focus is inside `<input>`, `<textarea>`, `<select>`, or `[contenteditable]`.
     - Add `overscroll-behavior: contain` on scrollable sidebars, drawers, and inspectors to stop scroll chaining; restore keyboard focus to the exact trigger element when any `<Dialog>` or `<Sheet>` closes.
   - **Outputs**: Accessible landmark shell (`<header>`, `<nav>`, `<main>`, `<aside>`) + keyboard shortcut registry.

3. **Implement Forms, Optimistic Mutations & Multi-Step Wizards (`Owner: Frontend Engineer`)**
   - **Inputs**: OpenAPI/Zod payload schemas, error catalog (`RFC 9457` Problem Details).
   - **Action**:
     - Bind forms with React Hook Form (or native `<form action>`) + Zod schema validation running `onBlur` and `onSubmit` (never shouting red errors on the very first keystroke).
     - **Never block paste** (`onPaste` preventDefault is strictly forbidden on passwords, OTP codes, API keys, or IDs).
     - Add `translate="no"` on IDs, API keys, code snippets, currency codes, and status badges so browser auto-translate never corrupts identifiers.
     - Pair mutations with idempotency protection (disable/debounce double-submit with `aria-busy="true"`), optimistic updates with deterministic rollback on failure, and calm specific notifications (`"Invoice sent to Dana"` rather than generic `"Success!"`).
     - Persist multi-step wizard drafts across reloads (URL step param + safe draft storage) with clickable back-step summary review.
   - **Outputs**: Validated CRUD flows with composed `loading`, `empty`, and inline `error` states.

4. **Engineer Virtualized High-Density Data Grids (`Owner: Frontend Engineer`)**
   - **Inputs**: Dataset cardinality (`<= 100` vs `> 100` rows), column types, bulk actions.
   - **Action**:
     - Pair TanStack Table with row virtualization whenever rows can exceed `100` (render only visible viewport rows + overscan buffer).
     - Enforce strict typographic alignment: **Text left**, **Numbers right with `font-variant-numeric: tabular-nums`**, **Status center**, **Actions right**.
     - Support explicit density rows (`compact: 40px`, `default: 48px`, `comfortable: 56px`), sticky headers, pinned primary identifier column, contextual bulk-selection action bar, CSV export honoring active filters, skeleton rows matching final column widths, and helpful empty states (`"No invoices match 'overdue' — Reset filters"`).
   - **Outputs**: High-density accessible table component.

5. **Wire RBAC Gates, Real-Time Presence & Embedded Artifact Constraints (`Owner: Full-Stack / UI Engineer`)**
   - **Inputs**: Role/permission matrix, WebSocket/SSE stream contract, or MCP/inline host spec.
   - **Action**:
     - Enforce role permissions server-side and mirror cleanly in UI: hide admin-only routes or render unavailable actions as `aria-disabled="true"` with a clear tooltip/inline explanation (never silent dead clicks).
     - Show explicit `live | reconnecting | stale` connection indicators on collaborative/streaming views; retain last-known-good view on transient disconnect.
     - If building an inline `generative_ui` or SEP-1865 MCP App: remove all `100vh`/`h-screen`/`height: 100%` rules, bind host CSS variables exclusively, gate `sendMessage`/`updateModelContext` via `getHostCapabilities()`, register tool/context handlers before `connect()`, and store persistent state via `app-only` MCP tools rather than `localStorage`.
   - **Outputs**: Permission-safe, connection-aware workspace or compliant embedded artifact.

6. **Execute Deletion Pass & `break-ui` Worst-Case Stress Test (`Owner: QA / Frontend Engineer`)**
   - **Inputs**: Working workspace views.
   - **Action**:
     - **Deletion / Condensation Pass**: Delete redundant `useEffect` chains syncing props/server data into local state, delete client Redux/Zustand slices duplicating URL/query state, and collapse single-use wrapper components into direct semantic markup.
     - **Run `break-ui` 7-Case Stress Matrix** across every primary screen: (1) `0` items (empty state + clear CTA), (2) `10,000` items (virtualized scroll `>= 60 fps`), (3) `200`-character unbroken string (`min-w-0` + `truncate` / `overflow-wrap: anywhere` inside flex/grid tracks), (4) missing optional avatar/subtitle/dates, (5) long translated/German/RTL labels (`1.4x` width expansion), (6) rapid double-click on submit/delete, (7) throttled `3G` + `500` API error recovery.
   - **Outputs**: Verified stress-tested workspace ready for E2E QA.

### 2.7 Minimal Workspace CSS & MCP Host-Sync Snippet

```css
/* Tri-pane overflow guard, tabular metrics, and contained drawer scroll */
.tri-pane-shell {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr) 360px;
}
.pane-scroll {
  overscroll-behavior: contain;
}
.metric-cell {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
```

```ts
// SEP-1865 MCP App / generative_ui safe registration order
app.ontoolresult = (res) => renderSafeState(res);
app.onhostcontextchanged = (ctx) => {
  applyDocumentTheme(ctx.theme);
  applyHostStyleVariables(ctx);
  redrawCanvasForTheme();
};
await app.connect(); // Register all handlers BEFORE connect()
```

---

## 3. Reusable Artifact & Template

Web apps reuse the workspace pane/state section of [Dashboard Specification Template](../templates/dashboard-spec.md) for filter/URL state and record component contracts in the **Workspace Interaction & State Contract Table**:

| Contract Field | Description | Example Entry |
|---|---|---|
| `route_or_pane` | Target route path or shell region | `/workspaces/:id/logs` (Tri-Pane: Outline + Viewport + Inspector) |
| `state_owner` | Canonical source (`URL searchParams`, `Server Query`, `Local UI`) | `URL searchParams` (`?q=&level=error&span=sp_92`), `pushState` on span select |
| `keyboard_shortcuts` | Scoped shortcuts + focus restoration target | `Cmd+K` palette, `j/k` row step (disabled in inputs), `Esc` closes Sheet to row |
| `six_state_spec` | Behavior for `default/hover/active/focus-visible/loading/empty/error` | Skeleton matches 5 columns; empty shows `"Clear filters"`; error shows retry |
| `break_ui_matrix` | Verified stress cases (`0`, `10k`, `200-char`, missing, RTL, double-click, slow net) | `min-w-0` on flex cells; `tabular-nums` on latency; idempotent mutation lock |
| `embedded_constraints` | Applicable only for `generative_ui` / MCP Apps | `<= 450px` height; zero `100vh`; `onhostcontextchanged` theme redraw |

---

## 4. Verification Checklist

- [ ] Shell topology matches route count (`Top Nav`, `Left Rail`, `Tri-Pane`, or `Command-First`) with `min-w-0` on flexible main tracks.
- [ ] Filters, sort, pagination, and selected entity ID survive browser reload and Back/Forward via URL `searchParams`.
- [ ] `Cmd+K` palette and single-key shortcuts operate cleanly via keyboard, never hijack active text inputs, and restore focus on overlay close.
- [ ] Forms validate with Zod `onBlur`/`onSubmit`, never block paste on any field, and mark IDs/tokens/codes with `translate="no"`.
- [ ] Data grids exceeding `100` rows virtualize smoothly and enforce `tabular-nums`, right-aligned numbers, left-aligned text, and `40/48/56px` density rows.
- [ ] Destructive actions require `<AlertDialog>` confirmation, mutations guard against double-submit, and errors render inline with recovery actions.
- [ ] `overscroll-behavior: contain` is applied to scrollable drawers/panes so nested scrolling never chains to the document body.
- [ ] Embedded `generative_ui` / MCP artifacts avoid `100vh`/`h-screen`, use host CSS variables, redraw `<canvas>` on `themechange`, and persist via `app-only` tools.
- [ ] All 7 `break-ui` stress cases (`0` items, `10k` items, `200`-char string, missing optional fields, long/RTL copy, double-click, slow/error network) pass without layout breakage.

---

## 5. Hard Quality Gate

- **`PASS`**:
  - Zero console errors or uncaught promise rejections during interactive CRUD, `Cmd+K`, and filter/reload Playwright journeys.
  - All 7 `break-ui` stress scenarios pass at `390x844` and `1440x900` with `0` critical/serious `axe-core` violations and zero banned fonts/icons.
  - Deletion pass executed with zero redundant `useEffect` state-mirroring or unvirtualized `> 100`-row tables remaining.
- **`FAIL`**:
  - Any input blocking paste, missing `focus-visible` indicator, URL losing selected workspace filter/entity on reload, or `200`-char string blowing out grid width.
  - Any inline `generative_ui`/MCP widget collapsing via `100vh`/`height: 100%` or failing to update on `themechange`.

```bash
# Run workspace E2E, break-ui stress suite, and accessibility checks
npx playwright test --grep "workspace-url-state|break-ui|keyboard-nav"
npx @axe-core/cli http://127.0.0.1:3000/app --exit
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Client Store Mirroring Server State** | Causes stale-data flashes, duplicated loading flags, and pointless Redux boilerplate | `useEffect(() => setStore(serverData), [serverData])` or global slices mirroring API responses | Keep filters/selection in URL `searchParams` and server state in query/RSC layer |
| **Modal-for-Everything Interruptions** | Destroys list context and forces extra clicks for simple inspect or 1-field edits | Opening centered `<Dialog>` for quick status toggles or read-only detail inspection | Follow ladder: Inline edit (`1-2` fields) -> Slide-over `<Sheet>` -> `<Dialog>` only when needed |
| **Unvirtualized `1,000+` Row Tables** | Freezes main thread (`INP > 500ms`) and bloats DOM node count past `5,000` nodes | Rendering `rows.map(...)` directly on unbounded log/transaction tables | Add TanStack Virtual (`<= 50` DOM rows rendered) + sticky header + `tabular-nums` |
| **Blocking Paste & Mangled IDs** | Breaks password managers, OTP autofill, and corrupts hashes/UUIDs under browser translation | `onPaste={(e) => e.preventDefault()}` or missing `translate="no"` on token/ID cells | Allow paste unconditionally; add `translate="no"` on IDs, keys, and code tags |
| **`100vh` Inside Embedded Widgets** | Collapses iframe height or triggers infinite resize loops inside host chat/IDE containers | `className="h-screen"` or `height: 100%` inside `generative_ui` / MCP HTML | Use natural content flow (`<= 450px` inline or host container flex) + host tokens |
| **Unhandled `break-ui` Overflow & Double-Submit** | Long unbroken URLs/emails shatter flex layouts; rapid clicks trigger duplicate charges/records | Missing `min-w-0` on flex children or unlocked submit buttons during pending mutation | Add `min-w-0`/`truncate`, idempotency lock + `aria-busy`, and test 7 stress cases |
