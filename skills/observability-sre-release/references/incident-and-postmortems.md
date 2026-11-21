# Incident Response & Blameless Postmortems

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

During an active production outage, the highest-leverage priorities are:
1. **Stopping customer bleeding fast** (`mitigate first, debug second`).
2. **Transparent stakeholder communication** on a predictable SLA cadence.
3. **A blameless systemic postmortem** eliminating the missing guardrail without blame.

This module integrates Incident Command System (ICS) role discipline (with explicit small-team collapse rules), deployment-correlated triage, `Where We Got Lucky` near-miss mining, and `3–5` `TD-NNN`-scored preventive action items across **Q4** and live operations.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Incident Option & Anti-Overengineering Gate

Apply **Least Code, Highest Craft** before adopting heavy incident-management ceremony:

- **Option A (Default Simplest High-Craft)**:
  - One dedicated incident channel + structured Markdown timeline/postmortem (`templates/postmortem-report.md`) committed in `docs/postmortems/`.
  - Lightweight status page or webhook notifications.
  - Prioritized `TD-NNN` technical-debt/test-backlog tracking.
  - Zero custom Slack incident bots, zero bi-directional Jira-PagerDuty sync daemons.
- **Earned Evidence Required for Option B (Automated War-Room Provisioning & Escalation Trees)**:
  - Only adopt multi-tier PagerDuty/Opsgenie orchestration bots and automated incident-ticket synchronization when a measured organizational constraint disproves Option A:
    - Team exceeds `>= 10` rotating on-call engineers across `>= 4` concurrent production services requiring cross-team paging trees.

### 1.2 SEV1–SEV4 Severity, SLA & Communication Matrix

| Severity | User & Business Impact (`S1–S4` Aligned) | Error Budget Burn Trigger | Ack SLA | Stakeholder / Status Cadence | Mandatory Postmortem SLA |
|---|---|---|---|---|---|
| **`SEV1` (Critical)** | Total outage, checkout/auth down, active data loss, or security breach (`S1`) | `> 10%` of 30d budget in `<= 1h` (`14.4x+` burn) | **`<= 5 min`** | Initial ack `<= 15m`; updates **every `15–30 min`** | **Mandatory `<= 48h`** post-resolution |
| **`SEV2` (High)** | Major feature broken, severe latency (`p95 > 2x`), no workaround (`S2`) | `2%–10%` of 30d budget (`6.0x` over `6h`) | **`<= 15 min`** | Initial ack `<= 30m`; updates **every `60 min`** | **Mandatory `<= 72h`** post-resolution |
| **`SEV3` (Medium)** | Partial degradation or minor feature failure with viable workaround (`S3`) | Slow chronic burn (`1.0x` over `3d`) | **`<= 4 hours`** | Update at mitigation and resolution | Grouped in sprint/cycle retrospective |
| **`SEV4` (Low)** | Cosmetic UI issue, internal non-prod blip, zero customer impact (`S4`) | `< 0.5%` budget impact | Next business day | Async ticket update only | None (`TD-NNN` backlog item if systemic) |

### 1.3 ICS Role Matrix & Small-Team Collapse Protocol

Never allow implicit role ambiguity to drop status updates or timeline timestamps:

| ICS Role | Core Responsibility | Explicit Small-Team Collapse (`1–3` Responders) |
|---|---|---|
| **Incident Commander (IC)** | Owns severity calls, mitigation go/no-go, escalation, and unblocking — **does NOT edit code** | `2-person`: **IC + Comms** paired on Lead; `1-person`: alternate `Stabilize -> Timestamp -> Update every 30m` |
| **Operations / Tech Lead (Ops)** | Executes diagnostics, rollback, kill switches, load shedding, and recovery commands | `2-person`: **Ops + Scribe** paired on Primary On-Call |
| **Communications Lead (Comms)** | Drafts and posts Initial Ack, periodic status-page updates, and Resolution Notice | Explicitly announced at open; **never silently omitted** under time pressure |
| **Scribe** | Records live UTC timestamps, hypotheses tested, telemetry snapshots, and `TD-NNN` leads | Log each action in `templates/postmortem-report.md` chronological table in real time |

### 1.4 Action-Item Priority Scoring (`TD-NNN` / `retrospective` Discipline)

- Cap every postmortem at **`3–5` highest-leverage preventive action items** — more dilutes execution into an unmaintained wish list.
- Score every candidate using `Priority = Impact (1–4) / Effort (1–4)` (`Impact`: `4=Critical`, `3=High`, `2=Med`, `1=Low`; `Effort`: `1=S`, `2=M`, `3=L`, `4=XL`).
- Require a **single named Owner**, explicit **Due Date** (`<= 14d` for primary prevention, `<= 30d` for systemic work), and a concrete **Verification Artifact** (regression test, burn-rate alert, CI gate, runbook update, or `TD-NNN` register entry).
- Flag any `TD-NNN` item carried across `> 3` cycles.

---

## 2. Step-by-Step Workflow

- **Inputs**: Burn-rate/infra page, customer report, `telemetry-slo-config.md`, recent deploy SHA, feature-flag audit.
- **Outputs**: Active status updates, mitigated production state, blameless `docs/postmortems/INC-YYYY-NNN.md`, `3–5` `TD-NNN` / test / alert follow-ups.
- **Owners**: Incident Commander (`IC`), Operations Lead (`Ops`), Communications Lead (`Comms`), Scribe.
- **Primary Tools**: `vercel` CLI (`logs`, `metrics`, `rollback`, `bisect`), `sentry` CLI, `posthog` live queries, `git log`, `curl`.

1. **Detect, Declare Severity & Assign Explicit ICS Roles (`<= 5m` for SEV1) (Owner: IC)**:
   - Open an incident log immediately from `templates/postmortem-report.md` (`INC-YYYY-NNN`).
   - Declare `SEV1–SEV4` using Section 1.2 impact criteria.
   - Announce exact ICS assignments (`IC`, `Ops`, `Comms`, `Scribe`) — or declare the explicit **small-team collapse mapping** (`IC+Comms` / `Ops+Scribe`) so zero duties vanish silently.

2. **Execute Mitigation-First Triage Loop (`Stabilize Before Root-Causing`) (Owner: Ops)**:
   - Restore user service first; perform deep root-cause forensics second.
   - Correlate immediately with recent changes (`vercel-agent` deployment correlation + `posthog` read-first audit):
     - Inspect `git log --since="6 hours ago"`, recent deployment SHAs, DB migrations, and feature-flag edits before reading deep stack traces.
   - Execute the fastest reversible stabilization:
     - `vercel rollback`, feature-flag kill switch, load-shedding flag, or replica/pool scaling.
   - Confirm recovery on live telemetry (`vercel logs`, `sentry issue list`, `curl /healthz`) and log the exact UTC mitigation timestamp.

3. **Run Disciplined Stakeholder & Status-Page Communications (Owner: Comms)**:
   - Publish the **Initial Acknowledgment** within SLA (`<= 15m` SEV1 / `<= 30m` SEV2) stating only verified user-visible symptoms, affected scope, and the exact next update time — zero speculation or blame.
   - Post updates strictly on cadence (`15–30m` SEV1, `60m` SEV2) even when status remains *"mitigation in progress"*.
   - Publish the **Resolution Notice** only after recovery telemetry holds steady for **`>= 15–30 min`**.
   - Trigger customer remediation or SLA credit review if data or contractual SLA impact occurred.

4. **Facilitate Blameless Postmortem Within SLA (`<= 48h` SEV1 / `<= 72h` SEV2) (Owner: IC + Scribe)**:
   - Reconstruct the objective **UTC Timeline** computing exact **TTD** (Time to Detect), **TTM** (Time to Mitigate), **TTR** (Time to Resolve), and **Error Budget Burn %**.
   - Conduct a **5-Whys Causal Analysis** starting from the proximate trigger and walking downward until uncovering the *missing systemic safeguard*:
     - Missing black-box boundary test, unsafe default, absent canary halt threshold, or missing expand-only migration check.
     - Never stop a causal chain at *"engineer forgot"*.
   - Capture three **Lessons Learned** buckets:
     - `What Went Well` (fast detection, clean rollback).
     - `What Went Poorly` (diagnostic friction, noisy alerts).
     - **`Where We Got Lucky`** (near-misses avoided only by chance, e.g., off-peak traffic).

5. **Action-Item Prioritization, `TD-NNN` Linkage & Condensation Pass (Owner: IC + Tech Lead)**:
   - Execute the **Postmortem Condensation Pass**: review all brainstormed fixes, delete vague wishes (*"be more careful"*, *"double-check PRs"*) and duplicates, and distill strictly **`3–5` high-leverage preventive actions** scored by `Impact / Effort`.
   - Bind every action to one owner, a concrete due date, and a falsifiable verification artifact (new test in `tests/`, burn-rate alert, CI check, or `TD-NNN` entry).
   - Audit prior postmortems on the same subsystem to verify previous preventive actions were actually closed — escalating any recurring unaddressed process smell immediately.

---

## 3. Reusable Artifact & Template

Instantiate [Postmortem Report Template](../templates/postmortem-report.md) at incident open so live timestamps populate directly into the final review without rework.

| Template Section | Required Fields | Validation & Completeness Rule |
|---|---|---|
| **Header & SLO Metrics** | `incident_id`, `title`, `sev`, `status`, `detected/ack/mitigated/resolved_utc`, `ttd`, `ttm`, `ttr`, `error_budget_burn_pct`, `related_sha` | Exact UTC timestamps; `TTM` and `TTR` calculated cleanly; `error_budget_burn_pct` quantified |
| **1. ICS Role Roster** | `ic`, `ops`, `comms`, `scribe`, `collapse_note` | Every role explicitly assigned or collapse mapping declared at incident open |
| **2–3. Impact & Timeline** | `user_symptom`, `affected_pct`, `breached_slos`, `chronological_utc_table` | Zero blameful language; timeline tracks detection, deploy check, mitigation, and `15–30m` bake |
| **4–5. 5-Whys & Backport** | `proximate_trigger`, `five_whys_chain`, `contributing_factors`, `hotfix_backport_checks` | Reaches systemic guardrail/test gap; confirms hotfix backport to `main` + `release/*` if used |
| **6–7. Comms & 3-Bucket Lessons** | `initial_ack`, `cadence_log`, `resolution_notice`, `well/poorly/where_we_got_lucky` | Status cadence met SLA; `Where We Got Lucky` risks converted into action items |
| **8–9. Action Items & Sign-Off** | `3–5` rows (`ID`, `Action`, `Category`, `Priority`, `Owner`, `Due Date`, `Tracking Ref`, `Status`), `signoffs` | Strictly `3–5` owned, time-bound actions; published `<= 48h` SEV1 / `<= 72h` SEV2 |

---

## 4. Verification Checklist

- [ ] Incident severity (`SEV1–4`) and ICS roles (`IC`, `Ops`, `Comms`, `Scribe`, or explicit small-team collapse) declared at open.
- [ ] Mitigation-first triage checked recent deployments and feature flags and stabilized users before deep root-cause debugging.
- [ ] Status page and stakeholder updates met initial SLA and recurring cadence without speculation or internal blame.
- [ ] Chronological UTC timeline accurately records detection, mitigation, resolution, TTD, TTM, TTR, and error-budget burn percentage.
- [ ] Blameless 5-Whys analysis identifies systemic safeguard gaps rather than human error and captures `Where We Got Lucky` risks.
- [ ] Preventive follow-ups are condensed to 3 to 5 high-leverage actions, each with a single owner, due date, and verification artifact.
- [ ] Prior postmortems on the affected component were audited so recurring unclosed action items are flagged and resolved.

---

## 5. Hard Quality Gate

Audit postmortem completeness, deploy-correlation evidence, and action-item hygiene automatically before closing `INC-YYYY-NNN`:

```bash
# 1. Rapid deploy/config correlation during triage (last 6h changes)
git log --since="6 hours ago" --oneline -n 20
sentry issue list --query "is:unresolved environment:production" --period 24h --limit 10 --json --fields shortId,title,priority,status

# 2. Validate completed postmortem artifact contains required SRE fields & 3-5 owned actions
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding='utf-8')
required = ('TTD', 'TTM', 'TTR', 'Why 5', 'Where We Got Lucky', 'Owner', 'Due Date')
missing = [k for k in required if k not in text]
actions = [l for l in text.splitlines() if l.strip().startswith('| \`AI-')]
assert not missing, f'Missing required postmortem fields: {missing}'
assert 3 <= len(actions) <= 5, f'Expected 3-5 condensed action items, found {len(actions)}'
print(f'Postmortem PASS: {p} ({len(actions)} owned action items)')
" docs/postmortems/latest.md
```

- **PASS**: Blameless postmortem published within `<= 48h` (SEV1) / `<= 72h` (SEV2) with complete UTC timeline (`TTD`/`TTM`/`TTR`/budget burn), explicit ICS roster, systemic 5-Whys, `Where We Got Lucky`, `3–5` owned/time-bound preventive actions (`TD-NNN`/tests/alerts), and verified closure of any recurring prior actions.
- **CONCERNS**: Minor timeline timestamp precision gap (`+/- 2m`) or `SEV3` grouped retrospective published `24h` past target while mitigation, comms, and `3–5` owned preventive actions pass cleanly.
- **NOT ASSESSED**: Postmortem file missing on disk, timeline metrics unpopulated, or telemetry logs unavailable for correlation — MUST emit `NOT ASSESSED — NO DATA`.
- **FAIL**: Blameful root cause naming individuals instead of missing guardrails, debug-first delay ignoring safe rollback, `> 5` diluted unowned wish-list items or unowned deadlines, dropped status communications, or recurring incident caused by an unclosed prior postmortem action.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Debug-First During Active Outage** | Burns 45 minutes reading stack traces while customers fail instead of rolling back the deploy | `TTM > 30m` after a recent deploy without attempting rollback/flag-off | **Mitigate first**: check last `6h` deploys/flags, roll back or kill-switch immediately, debug later |
| **Blameful "Human Error" Root Cause** | Stopping 5-Whys at *"developer ran wrong script"* leaves the exact trap intact for the next engineer | Postmortem ends with *"remind team to be careful"* | Walk 5-Whys to **systemic safeguards** (missing CI lock, missing confirmation, missing test) |
| **Action-Item Graveyard (`> 10` Unowned Todos)** | Creating 15 vague wishes guarantees zero completion and repeats the same outage next quarter | `> 5` actions, missing owners, or missing due dates | Execute **Condensation Pass**: keep `3–5` `Impact/Effort`-scored actions with owner, date, and test/`TD-NNN` |
| **Silent Role Collision & Missing Scribe** | Solo or uncoordinated responders skip status updates and lose exact outage timestamps | Zero status updates during outage; reconstructed timeline full of guesses | Declare **ICS roster or explicit collapse mapping** (`IC+Comms`, `Ops+Scribe`) at minute zero |
| **Ignoring `Where We Got Lucky` Near-Misses** | Treats lucky timing (off-peak traffic, manual notice) as resilience until peak load triggers catastrophe | Lessons section lists only what broke, ignoring close calls | Capture `Where We Got Lucky` explicitly and convert hidden near-misses into concrete alerts/tests |
| **Enterprise Incident-Bot Overengineering (Anti-Overengineering)** | Spends sprints wiring Slack/Jira/PagerDuty bots before having basic rollback flags and a postmortem template | Complex incident automation maintained by `< 5` engineers | Dedicated incident channel + `postmortem-report.md` + `TD-NNN` backlog (`Option A`) |
