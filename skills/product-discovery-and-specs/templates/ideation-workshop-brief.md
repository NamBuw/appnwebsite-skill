# Product Ideation & Brainstorming Brief

> **Canonical Output Path**: `docs/product/ideation-brief.md` (feeds `docs/product/prd.md`)

| Field | Value |
|---|---|
| **Domain / Problem Space** | [e.g., Independent Clinic Billing Reconciliation] |
| **Target Platform(s)** | `web-app` / `mobile-app` / `landing-page` / `fullstack` |
| **Rigor Tier** | `minimal` / `standard` / `full` |
| **Spiral Horizon** | `SP-01` (`<= 14 days` V1 Option A Wedge) |
| **Status** | `DIVERGING` / `CONVERGING` / `RAT-RUNNING` / `GO` / `KILL` |
| **Updated (UTC)** | `YYYY-MM-DDTHH:MM:SSZ` |

---

## 1. Constraint Box & How Might We (HMW) Prompts

- **ICP (1 specific role/context)**: [Who suffers the bottleneck and controls adoption.]
- **Hard Constraints**: [Build window, platform constraints, compliance boundary, `$0` ad budget.]
- **Observed Workarounds Today**: [Exact manual tools used right now: Excel, WhatsApp, copy-paste, legacy tool.]

1. `HMW-01`: How might we [outcome] for [ICP] without [major friction]?
2. `HMW-02`: How might we eliminate [manual step] in `< [time]`?
3. `HMW-03`: How might we turn the core workflow artifact into a built-in distribution loop?

---

## 2. Divergent Concept Log (`>= 8` Crazy 8s + SCAMPER Concepts)

| Idea ID | Technique / Lens | Concrete Product Concept & Wedge Mechanism | Target HMW | Eliminated Friction |
|---|---|---|---|---|
| `IDEA-01` | Crazy 8s (Baseline) | [First obvious workflow concept] | `HMW-01` | [Manual data entry] |
| `IDEA-02` | Crazy 8s (Speed) | [Zero-setup single-action utility] | `HMW-02` | [Account creation before value] |
| `IDEA-03` | Crazy 8s (Distribution) | [Shareable output artifact bringing next user] | `HMW-03` | [Cold outreach acquisition] |
| `IDEA-04` | Crazy 8s (Automation) | [Deterministic rule/parser replacing manual QA] | `HMW-01` | [Manual cross-checking] |
| `IDEA-05` | SCAMPER — Eliminate | [Strip dashboard/settings; single screen + export] | `HMW-02` | [Multi-step onboarding] |
| `IDEA-06` | SCAMPER — Reverse | [Value delivered first; save/account optional] | `HMW-01` | [Upfront paywall/login drop-off] |
| `IDEA-07` | SCAMPER — Combine | [Merge capture + structured resolution in one flow] | `HMW-01` | [Context switching across 2 apps] |
| `IDEA-08` | First-Principles Inversion | [Invert industry assumption on how input/price works] | `HMW-02` | [Legacy pricing/setup friction] |

---

## 3. Competitive White-Space & Convergent Scoring (`Max 25`)

| Idea ID | Pain Severity (`x2`, `2–10`) | Speed to Value (`1–5`) | Distribution Wedge (`1–5`) | Build Simplicity (`1–5`) | Total (`/25`) | Verdict (`KEEP` / `KILL`) |
|---|---|---|---|---|---|---|
| `IDEA-05` | `8` | `5` | `4` | `5` | `22` | `KEEP (Option A Wedge)` |
| `IDEA-03` | `8` | `4` | `5` | `4` | `21` | `KEEP (Runner-up)` |

- **Incumbent White-Space Proof**: [Why existing SaaS / spreadsheet workarounds fail on Speed vs. Simplicity.]
- **Simplicity Ablation Notes**: [Features explicitly stripped from the winner so V1 ships cleanly in `<= 2` weeks.]

---

## 4. Killed Ideas Log (`>= 5` Explicit Rejections)

| Kill ID | Rejected Concept (`IDEA-NN`) | Primary Kill Reason (`Me-Too` / `Weak Pain` / `No Distribution` / `Over-Engineered`) | Salvaged Insight |
|---|---|---|---|
| `KILL-01` | `IDEA-01` | [Generic parity clone of incumbent with zero switching incentive] | [Keep fast keyboard shortcut] |
| `KILL-02` | `IDEA-04` | [Requires brittle third-party integration before proving user demand] | [Defer to `SP-02` if RAT passes] |
| `KILL-03` | `IDEA-07` | [Scope exceeds 2-week Option A Wedge; forces multi-role permissions] | [Split capture flow out] |
| `KILL-04` | `IDEA-02` | [Vitamin utility; users tolerate existing 2-minute workaround] | [Use as free landing tool] |
| `KILL-05` | `IDEA-08` | [Violates buyer procurement or trust expectations in target market] | [Document boundary constraint] |

---

## 5. Locked Value Proposition & 48h Riskiest Assumption Test (RAT)

- **Value Proposition Thesis**: Our `[product]` helps `[ICP]` achieve `[quantified outcome]` in `[time window]` without `[major pain]`, unlike `[incumbent]` because `[defensible wedge]`.
- **Top Riskiest Assumption (`RA-01`)**: `[Exact falsifiable belief that kills the product if false.]`
- **48h Experiment Design**: `[Manual concierge test / static interactive prototype / 5 ICP commitment checks.]`
- **Binary Pass Threshold**: `[e.g., >= 4 of 5 target buyers upload a real file or commit to weekly pilot within 48h.]`
- **RAT Verdict**: `PENDING` / `GO -> Feed docs/product/prd.md` / `PIVOT` / `KILL`
