# Use Cases & Vertical Feature Breakdown Specification

> **Canonical Output Paths**: `docs/product/use-cases.md` (Part A) and `docs/product/feature-breakdown.md` (Parts B & C)

| Field | Value |
|---|---|
| **Feature / Epic Scope** | [e.g., Spiral 1 Core Invoice Reconciliation] |
| **Spiral ID** | `SP-01` |
| **Rigor Tier** | `minimal` / `standard` / `full` |
| **Story Granularity** | `coarse` (`minimal`: 5–10 ACs) / `balanced` (`standard`: 2–4 ACs) / `fine` (`full`: 1 AC) |
| **PR-EPIC Realism Verdict** | `REALISTIC` / `CONCERNS` / `UNREALISTIC` / `NOT ASSESSED` |
| **QL-STORY-READY Verdict** | `ADEQUATE` / `GAPS` / `INADEQUATE` / `NOT ASSESSED` |

---

## Part A — Structured Use Cases (`UC-NNN`)

### `UC-001`: [Verb-Noun Use Case Title]

- **Linked Requirements**: `FR-001`, `NFR-001`
- **Primary Actor**: [e.g., `P-01` Operations Manager]
- **Secondary Actors / Systems**: [e.g., Payment Webhook Gateway, Object Storage]
- **Preconditions**: [Observable system state required before trigger fires, e.g., Authenticated `Member` with active `Workspace`]
- **Trigger**: [Exact user action, schedule, or inbound event starting the flow]

#### Main Success Flow
1. [Actor submits/initiates exact input.]
2. [System validates contract, permissions, and boundaries.]
3. [System persists state change atomically and emits domain event if applicable.]
4. [System returns confirmation and updated state within `NFR` latency budget.]

#### Alternative Flows
- **`A1` (Step 2 — Valid Variant)**: [Alternate legitimate path, e.g., cached idempotency key returns prior result cleanly and jumps to Step 4.]

#### Exception / Failure Flows
- **`E1` (Step 2 — Invalid Input / Boundary Violation)**: [Exact rejection status, zero partial mutation, actionable user recovery message.]
- **`E2` (Step 3 — Downstream Timeout / Conflict)**: [Safe rollback/compensation state, retryable flag, operator telemetry emitted.]

- **Postconditions**: [Verifiable final state for both success and rolled-back failure paths.]

---

## Part B — Dependency-Ordered Vertical Epics (`EP-NNN`)

> Epics MUST slice vertically (`Schema -> Domain Logic -> API -> UI -> Automated Test`) and obey dependency layers (`Foundation -> Core -> Feature -> Presentation`). Cap Spiral 1 at `<= 3` thin epics.

| Epic ID | Layer | Vertical Slice Scope | Linked FR / UC | Governing ADR & Status | Target Capacity / Effort | PR-EPIC Verdict |
|---|---|---|---|---|---|---|
| `EP-001` | `Foundation` | [Auth/workspace boundary + walking skeleton] | `FR-001`, `UC-001` | `ADR-0001` (`Accepted`) | [e.g., `2d`] | `REALISTIC` |
| `EP-002` | `Core` | [Primary domain workflow end-to-end] | `FR-002`, `UC-002` | `ADR-0002` (`Accepted`) | [e.g., `3d`] | `REALISTIC` |

---

## Part C — Vertical Slice Stories (`ST-NNN`)

### `ST-001`: [Actionable Vertical Slice Title]

- **Epic**: `EP-001`
- **Story Type**: `Logic` / `Integration` / `Visual/Feel` / `UI` / `Config/Data`
- **Estimate**: `S` (`0.5–1d`) / `M` (`1–2d`) *(split any story exceeding `3d`; merge `< 2h` micro-tasks)*
- **Status**: `Ready` / `Blocked` *(if `Blocked`, cite exact unresolved ADR or upstream story ID)*
- **Dependencies**: `Blocked By: None` | `Unlocks: ST-002`
- **Interfaces**:
  - `Consumes`: [Exact upstream input schema, table, or endpoint]
  - `Produces`: [Exact persisted state, response payload, or UI state]
- **Out of Scope**: [Explicitly delegated to neighboring stories or `NG-NNN`, e.g., Bulk export handled in `ST-004`]
- **Required Test Evidence**: [e.g., `tests/unit/test_reconcile.py` + `tests/integration/test_import_api.py`]

#### Acceptance Criteria (`Given / When / Then / Edge Cases` or `Setup / Verify / Pass condition`)
- **AC-1**: `Given` [initial state], `When` [exact action/input], `Then` [observable, measurable outcome].
- **AC-2 (Edge / Error)**: `Given` [boundary/invalid input or duplicate trigger], `When` [action], `Then` [explicit error contract and clean state preserved].
- **AC-3 (Visual/UI if applicable)**: `Setup` [viewport/state], `Verify` [focus, keyboard, loading/error states], `Pass condition` [zero layout shift, clear feedback].
