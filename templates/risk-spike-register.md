# Risk & Spike Register (`RSK-SP-<NNN>`)

- **Register ID**: [RSK-SP-001]
- **Spiral ID**: [SP-001]
- **Updated (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Unmitigated High/Critical Risks**: [1] *(Invariant: MUST equal `0` before Phase 3A Foundation Gate can unlock)*
- **Verdict**: [NOT ASSESSED | PASS | CONCERNS | FAIL]

---

## 1. Risk & Threat Trigger Register

*(Keep Likelihood and Impact separate — never mask fatal Impact inside an averaged score.)*

| Risk ID | Domain (`Architecture \| Data \| UI/UX \| Perf \| Security \| Supply-Chain \| Scope`) | Failure Scenario & Trigger | Likelihood (`L \| M \| H`) | Severity (`Low \| Med \| High \| Critical`) | Mitigation Strategy or Spike ID | Status (`OPEN \| SPIKING \| MITIGATED \| ACCEPTED \| CLOSED`) |
|---|---|---|---|---|---|---|
| RSK-001 | [Architecture] | [Concrete failure scenario & observable trigger] | [M] | [High] | [SPK-001 or concrete mitigation] | [OPEN] |

> **Gate Invariant**: Any row with `Severity` in `{High, Critical}` and `Status == OPEN` causes Phase 3A readiness to **FAIL** (`check_spiral_gates.py`).

---

## 2. Throwaway Spike & Concept Prototype Cards

### Spike Card: `[SPK-001]`
- **Spike ID**: [SPK-001]
- **Linked Risk ID**: [RSK-001]
- **Vehicle Type**: [Throwaway Spike (<=4h) | Concept Prototype (<=1d) | Realistic Benchmark (<=4h)]
- **Riskiest Assumption**: [Single riskiest technical, security, or UX assumption]
- **Falsifiable Hypothesis**: *"If [actor/system performs X] under [realistic condition], [outcome Y] will occur — measured by [quantitative signal Z]."*
- **Falsifier / Kill Condition**: [Exact threshold that proves the approach unviable]
- **Timebox Hard Cap**: [<=4h spike | <=1d prototype — 2h stuck reframe trigger]
- **Isolation Path**: [spikes/SPK-001-slug/ or prototypes/SPK-001-slug/]
- **Observed Evidence / Benchmarks**: [Exact logs, latency numbers, usability observations — never localhost 0ms guesses]
- **Pivot Count**: [0] *(Circuit Breaker: `Pivot Count >= 3` MUST yield `Verdict: KILL` and archive in `GRAVEYARD.md`)*
- **Verdict**: [NOT ASSESSED | GO | PIVOT | KILL]
- **Next Action**: [If GO/PROCEED: rewrite cleanly from scratch through Phase 3A contracts; if PIVOT: write PIVOT-NOTE; if KILL: log GRAVEYARD]

---

## 3. Throwaway Artifact Isolation & Cleanup Verification

- [ ] Engineering-vs-gap triage ruled out local config/env/data errors before declaring any spike failure.
- [ ] Zero production source files (`src/`, `app/`, `pages/`, `components/`, `lib/`, `server/`, `api/`) import from `spikes/` or `prototypes/`.
- [ ] Zero `spikes/` or `prototypes/` modules import production domain code to mutate prod state.
- [ ] Completed throwaway spike directories deleted or archived cleanly after extracting findings into `SPIKE-NOTE.md` / ADRs.
- [ ] Any `GO`/`PROCEED` capability was re-authored cleanly from Phase 3A contracts (never refactored throwaway code into production).

---

## References
- Governance: [Risk, Prototyping & Spikes](../references/00-spiral-governance/risk-prototyping-and-spikes.md) | [System-First Foundation Gate](../references/00-spiral-governance/system-first-foundation-gate.md)
- Validator: `python3 scripts/check_spiral_gates.py --stage q2-risk --file <this-file> --strict`
- Sibling Templates: [Spiral Charter](spiral-charter.md) | [System Foundation Gate](system-foundation-gate.md)
- Parent Router: [SKILL.md](../SKILL.md)
