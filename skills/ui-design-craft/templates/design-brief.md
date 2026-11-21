# Design Brief Template

> **Purpose:** Lock product research, JTBD, behavioral personas, Information Architecture (IA), critical user flows, and aesthetic + Radical Simplicity constraints **before** generating `design-master.md` or writing UI code.

---

## 1. Product & Conversion Context

| Field | Value |
|---|---|
| **Product / Project Name** | `<Project Name>` |
| **Site-Kind Taxonomy** | `<software \| gaming \| tech \| product \| service \| place>` |
| **Research Rigor Tier** | `<minimal \| standard \| full>` |
| **Primary Conversion Action** | `<Single primary verb + outcome, e.g., Start free 14-day trial>` |
| **Core Offer / Value Proposition** | `<Concrete, measurable outcome without AI hype words>` |
| **Ideal Customer Profile (ICP)** | `<Role, team size, context, technical baseline>` |
| **Top 3 User Objections** | `1. <Objection + proof> 2. <Objection + proof> 3. <Objection + proof>` |

---

## 2. UX Research & JTBD Synthesis

- **Evidence Base:** `<N interviews / usability sessions / telemetry funnel / competitor teardown>`
- **Functional Job:** `When <situation>, I want to <action>, so I can <measurable outcome>.`
- **Emotional Job:** `<How the user wants to feel — e.g., confident under production pressure>`
- **Social Job:** `<How the user wants to be perceived by peers/stakeholders>`
- **Forces of Progress:**
  - **Push (Current Pain):** `<Concrete friction in existing tool>`
  - **Pull (Desired State):** `<Target workflow improvement>`
  - **Anxiety (Switching Fear):** `<Migration, learning curve, lock-in risk>`
  - **Habit (Inertia):** `<Existing spreadsheet/CLI/manual habit>`

---

## 3. Behavioral Personas & Assistive Constraints

| Persona / Cohort | Primary Task Frequency | Tech & Viewport Context | Accessibility / Assistive Needs |
|---|---|---|---|
| `<Primary Operator>` | `<Daily>` | `<Desktop 1440px + Mobile 390px>` | `<Keyboard-first shortcuts, WCAG AA 4.5:1, reduced motion>` |
| `<Reviewer / Approver>` | `<Weekly>` | `<Tablet 768px + Desktop>` | `<High-contrast light/dark parity, clear error recovery>` |

---

## 4. Information Architecture (IA) & Sitemap

- **IA Topology:** `<Flat Hub (<=5 L1) \| Hierarchical L1/L2 \| Faceted Search \| Task-Wizard \| Command-First>`
- **L1 Navigation Budget:** `<List <= 7 top-level destinations; zero redundant routes>`
- **Tree-Test Target:** `>= 80%` direct-success rate, `< 20%` backtrack rate (`n >= 15` participants for `standard`/`full` tier).

```text
/ (Landing / Overview)
├── /<primary-workspace>
├── /<secondary-workflow>
└── /settings
```

---

## 5. Critical User Flows & Edge States

| Flow Name | Happy Path (Max Clicks) | Empty State | Error / Recovery State | Permission / Offline State |
|---|---|---|---|---|
| `<Core Creation Flow>` | `<3 steps>` | `<Actionable CTA + starter template>` | `<Inline aria-invalid + specific fix>` | `<Read-only explanation + queued retry>` |

---

## 6. Aesthetic Direction & Radical Simplicity Record

- **Focal Boldness Choice:** `<Spend visual boldness in ONE deliberate place>`
- **Native HTML/CSS Substitutions:** `<e.g., native <dialog>, <details>, CSS Grid/@container instead of JS layout libs>`
- **Approved Font & Icon Baseline:** `<e.g., Geist + Geist Mono; Phosphor icons>`
- **Brand / Brownfield Override ADR (if any):** `<None — strict anti-AI-slop defaults enforced>`
- **Simplicity Pruning Log:** `<Routes, wizard steps, or redundant chrome deleted before build>`
