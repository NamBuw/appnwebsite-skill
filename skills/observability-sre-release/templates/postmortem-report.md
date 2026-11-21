# Blameless Incident & Postmortem Report (`INC-YYYY-NNN`)

- **Incident ID**: [INC-2026-001]
- **Title**: [User-Visible Symptom Summary]
- **Severity**: [SEV1 | SEV2 | SEV3 | SEV4]
- **Status**: [Mitigated | Resolved | Postmortem Complete]
- **Detected (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Acknowledged (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Mitigated (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Resolved (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **TTD (Time to Detect)**: [N min] | **TTM (Time to Mitigate)**: [N min] | **TTR (Time to Resolve)**: [N min]
- **Error Budget Burn (%)**: [X.X% of 30d SLO budget]
- **Related Deploy / Commit / Hotfix Tag**: [sha-or-tag]

---

## 1. ICS Role Roster (Active & Collapsed Mapping)

| ICS Role | Assigned Engineer / Role | Small-Team Collapse / Handoff Note |
|---|---|---|
| **Incident Commander (IC)** | [Name] | [Declare explicit collapse if solo/small team, e.g., `IC+Comms`] |
| **Operations / Tech Lead (Ops)** | [Name] | [Executes diagnostics and rollback/mitigation] |
| **Communications Lead (Comms)** | [Name] | [Internal updates + external status page; never skipped] |
| **Scribe** | [Name] | [Captures live UTC timeline and telemetry screenshots] |

---

## 2. User-Visible Impact Summary

- **User Symptom**: [Plain-language description of what users experienced — no internal blame]
- **Affected Scope**: [X% of requests / N affected accounts / impacted regions & platforms]
- **Breached SLO(s)**: [SLO-01 / SLO-02] | **Data Integrity / Revenue Impact**: [None / quantified impact]

---

## 3. Chronological Timeline (UTC)

| Timestamp (UTC) | Event / Observation | Actor / Signal | Action Taken |
|---|---|---|---|
| `[HH:MM:SSZ]` | [Deploy / traffic shift / fault introduced] | [CI / Release / External] | [Baseline change recorded] |
| `[HH:MM:SSZ]` | [Burn-rate alert fired (`ALR-01`)] | [Monitor / Pager] | [Incident opened; ICS roles declared] |
| `[HH:MM:SSZ]` | [Checked recent deploys & feature flags] | [Ops Lead] | [Triggered rollback / kill-switch flag] |
| `[HH:MM:SSZ]` | [5xx dropped `< 0.1%`, p95 normal] | [Live Telemetry] | [Held 15m stability watch -> Resolved] |

---

## 4. Blameless Root Cause & 5-Whys Analysis

- **Proximate Trigger**: [Exact commit, migration, dependency outage, or traffic spike]
- **5-Whys Systemic Causal Chain** *(Focus on missing guardrails, tests, monitors, or defaults — never blame individuals)*:
  1. **Why 1**: [Immediate technical symptom]
  2. **Why 2**: [Mechanism that allowed trigger to impact production]
  3. **Why 3**: [Why automated tests or CI gates did not catch it]
  4. **Why 4**: [Why canary/monitoring/defaults did not limit blast radius]
  5. **Why 5 (Systemic Root)**: [Structural process, contract, or guardrail gap]
- **Contributing Factors**: [Monitoring blind spots, missing boundary tests, unsafe config defaults]

---

## 5. Mitigation, Hotfix & Backport Verification

- **Immediate Mitigation Taken**: [Rollback / kill-switch / load-shedding executed]
- **Permanent Fix PR / Hotfix Tag**: [PR # / tag `vX.Y.(Z+1)`]
- **Backport Verification** *(Mandatory if hotfix branched from release tag)*:
  - [ ] Hotfix commit merged and verified on `main`.
  - [ ] Hotfix commit merged and verified on active `release/*` branch.

---

## 6. Stakeholder & Status Page Communication Log

| Milestone | Timestamp (UTC) | Channel | Verbatim Message Summary & Cadence Note |
|---|---|---|---|
| **Initial Acknowledgment** | `[HH:MM:SSZ]` | [Status Page / Incident Channel] | [User symptom + affected scope + next update time; zero speculation] |
| **Periodic Update(s)** | `[HH:MM:SSZ]` | [Status Page / Stakeholders] | [Met `15–30m` SEV1 / `60m` SEV2 cadence] |
| **Resolution Notice** | `[HH:MM:SSZ]` | [Status Page / Incident Channel] | [Published after `>= 15–30m` stable recovery] |
| **Remediation / SLA Credits** | `[YYYY-MM-DD]` | [Customer Comms] | [N/A or compensation criteria executed] |

---

## 7. Lessons Learned (3-Bucket Synthesis)

- **What Went Well**: [Fast detection, effective runbook, clean rollback]
- **What Went Poorly**: [Alert noise, slow diagnostics, unclear flag ownership]
- **Where We Got Lucky**: [Hidden risks mitigated only by chance — e.g., low off-peak traffic, manual notice before cron ran — convert each into a preventive action item]

---

## 8. Prioritized Preventive Action Items (3–5 Max, Owned & Time-Bound)

| Action ID | Concrete Preventive Action | Category (`Guardrail \| Test \| Alert \| Runbook \| TechDebt`) | Priority (`Impact/Effort 1–4`) | Owner | Due Date | Tracking Ref (`PR / TD-NNN`) | Status (`Open \| In Progress \| Done`) |
|---|---|---|---|---|---|---|---|
| `AI-01` | [Add regression black-box/integration test for trigger] | `Test` | [4.0] | [Name] | `[YYYY-MM-DD]` | [PR / TD-001] | `Open` |
| `AI-02` | [Add canary halt threshold or burn-rate alert] | `Alert` | [3.0] | [Name] | `[YYYY-MM-DD]` | [PR / TD-002] | `Open` |
| `AI-03` | [Update runbook with exact recovery check] | `Runbook` | [2.0] | [Name] | `[YYYY-MM-DD]` | [RB-001] | `Open` |

- **Recurring Action Audit**: [Confirmed 0 unclosed recurring actions from prior postmortems on the same subsystem.]

---

## 9. Blameless Review Sign-Offs

- **Incident Commander / SRE Lead**: `[Name — Date]`
- **QA / Test Gap Sign-Off**: `[Name — Date]`
- **Product / Comms Sign-Off**: `[Name — Date]` *(Published within `<= 48h` SEV1 / `<= 72h` SEV2 SLA)*

---

## References
- Reference Module: [Incident Response & Blameless Postmortems](../references/incident-and-postmortems.md)
- Companion Templates: [Operational Runbook](operational-runbook.md) | [Release Checklist](release-checklist.md) | [SLO & Alerting Spec](slo-alerting-spec.md)
- Skill Router: [SKILL.md](../SKILL.md)
