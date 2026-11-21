# appnwebsite-skill

**Production-ready, all-in-one App & Website Design and Engineering Hierarchical Multi-Skill Suite** organized around an iterative **Spiral Model** master workflow with enforced **System-First Engineering**, **Radical Simplicity ("Least Code, Highest Craft" / "ít nhất mà tốt nhất")**, and **Hyper Token-Efficient Progressive Disclosure ("Maximum Signal, Minimum Tokens")**.

---

## Architecture: Parent Orchestrator + 11 Standalone Child Skills

```text
appnwebsite-skill/
├── SKILL.md                  # Parent Orchestrator (`name: appnwebsite-orchestrator`)
├── registry.json             # Machine-readable routing, I/O bus & token-budget contract
├── references/
│   ├── orchestration-protocol.md
│   └── 00-spiral-governance/ # Q1–Q4 Spiral, Phase 3A Hard Gate, Simplicity, Token Economy, Risk/Spikes
├── templates/                # Spiral Charter, Foundation Gate, Simplicity Record, Risk/Spike Register
├── scripts/                  # Pure Python 3 stdlib: validate_skill.py, query_skill.py, check_spiral_gates.py
└── skills/                   # 11 standalone-valid, deep Child Skills (all 11 active)
```

### Suite Skill Catalog (`registry.json`)

| Skill ID | Role / Domain | Milestone | Status |
|---|---|---|---|
| `appnwebsite-orchestrator` ([SKILL.md](SKILL.md)) | Parent Spiral Router, Phase 3A & Simplicity Enforcer | M1 | `active` |
| `product-discovery-and-specs` (`skills/product-discovery-and-specs/`) | Ideation/brainstorming (Double Diamond, Crazy 8s, SCAMPER, RAT), discovery/JTBD, PRDs, use cases, quantitative NFRs/SLOs | M2 | `active` |
| `system-data-architecture` (`skills/system-data-architecture/`) | Greenfield C4 architecture, ADRs, Control Manifest, DDD/ERD, expand-contract migrations, GDPR/DPIA | M2 | `active` |
| `fullstack-api-engineering` (`skills/fullstack-api-engineering/`) | Clean backend & durable workflows, SSR/RSC frontend, OpenAPI/GraphQL/gRPC/Webhooks, i18n/l10n, code review | M2 | `active` |
| `ui-design-craft` (`skills/ui-design-craft/`) | UX/IA, typography & `clamp()`, grids & ergonomics, OKLCH/APCA & W3C tokens, motion, strict Anti-AI-Slop | M3 | `active` |
| `figma-design-to-code` (`skills/figma-design-to-code/`) | Figma Variables/Auto Layout/Code Connect/MCP, Style Dictionary sync, pixel-faithful Figma-to-code | M3 | `active` |
| `frontend-surfaces-and-redesign` (`skills/frontend-surfaces-and-redesign/`) | Landing pages, SaaS web apps, mobile apps, dashboards/data-viz, design systems, UI audit & redesign | M3 | `active` |
| `security-engineering` (`skills/security-engineering/`) | STRIDE & attack trees, OAuth 2.1/PKCE/WebAuthn/RBAC/RLS, SBOM/SLSA/secrets, SAST/DAST/PoC | M4 | `active` |
| `multi-layer-qa-testing` (`skills/multi-layer-qa-testing/`) | Master test strategy, systematic Black-Box QA (EP, BVA, State, Decision, Pairwise, E2E/UAT), Load/A11y/Chaos | M4 | `active` |
| `observability-sre-release` (`skills/observability-sre-release/`) | OpenTelemetry & SLO burn-rate alerts, signed CI/CD/canary/rollback, docs, runbooks, SEV postmortems | M5 | `active` |
| `advanced-web-app-capabilities` (`skills/advanced-web-app-capabilities/`) | Payments/webhooks idempotency, AI/LLM prompt-injection defense, realtime/PWA, SEO/CWV/analytics, MCP visual audit | EXP | `active` |
| `meta-plan-goal-teamwork` (`skills/meta-plan-goal-teamwork/`) | Execution mode wrappers: `/plan` (plan-first), `/goal` (evidence loop), `/teamwork` (multi-agent orchestration) | EXP | `active` |

---

## Core Lifecycle & Engineering Principles

1. **Spiral Model Master Workflow (`Q1 -> Q4`)**:
   - **Q1**: Entry mode audit (`greenfield` vs `brownfield` 4-tier Adopt), [Spiral Charter](templates/spiral-charter.md), Non-Goals, Complexity Budget, `PRE-DESIGN` Simplicity check.
   - **Q2**: Independent Likelihood/Severity scoring, STRIDE threat modeling, isolated throwaway spikes (`<= 4h`) / prototypes (`<= 1d`) with `3-PIVOT-to-KILL`.
   - **3A (HARD SYSTEM-FIRST GATE)**: Architecture, Data Model, Boundaries/`control-manifest.md`, Core Contracts + `tokens.json`, Accepted ADRs (acyclic), and runnable walking skeleton + smoke test MUST pass before writing any feature code or production UI.
   - **3B**: Thin end-to-end vertical slices (`Schema -> API -> UI -> tests`) loading `<= 2` active Child Skills concurrently.
   - **3C**: Mandatory **Pre-Ship Deletion/Condensation Pass** + Multi-Layer Black-Box/White-Box QA + Security verification + fresh Iron-Law receipts.
   - **Q4**: Scope Delta audit, Exit Telemetry (`NOT ASSESSED` > `PASS`), 5-question Chain-of-Verification, `<= 5` owned carryover actions.
2. **Anti-Overengineering ("Least Code, Highest Craft" / "ít nhất mà tốt nhất")**:
   - Enforces the 4 Socratic Simplicity Questions before design and a Deletion/Condensation Pass before shipping ([Anti-Overengineering Simplicity Gate](references/00-spiral-governance/anti-overengineering-simplicity-gate.md)).
3. **Hyper Token-Efficient Progressive Disclosure ("Maximum Signal, Minimum Tokens")**:
   - Lean `< 250`-line Parent router, deterministic BM25+MMR & section-extraction CLI (`scripts/query_skill.py`), `40 KB` Read Guard, quiet test flags, and disk-backed `<= 25`-line checkpoints ([Token Economy](references/00-spiral-governance/token-economy-and-progressive-disclosure.md)).

---

## Multi-Ecosystem Installation

Clone the repository once, then link or copy the Parent Orchestrator (and any active `skills/<child-name>` directories you want independently discoverable) into your agent platform's skills directory.

```bash
git clone https://github.com/NamBuw/appnwebsite-skill.git
cd appnwebsite-skill
python3 scripts/validate_skill.py . --strict
```

### Option A — Full Suite Install (Recommended)

Link or copy the repository root as `appnwebsite-orchestrator` and expose individual child skills cleanly when active:

| Agent Ecosystem | Parent Orchestrator Target | Standalone Child Skill Targets (Optional / Per-Skill) |
|---|---|---|
| **Antigravity** | `ln -s "$(pwd)" ~/.gemini/config/skills/appnwebsite-orchestrator` | `for d in skills/*/; do [ -f "$d/SKILL.md" ] && ln -s "$(pwd)/$d" ~/.gemini/config/skills/"$(basename "$d")"; done` |
| **Claude Code** | `ln -s "$(pwd)" ~/.claude/skills/appnwebsite-orchestrator` | `for d in skills/*/; do [ -f "$d/SKILL.md" ] && ln -s "$(pwd)/$d" ~/.claude/skills/"$(basename "$d")"; done` |
| **OpenAI Codex** | `ln -s "$(pwd)" ~/.codex/skills/appnwebsite-orchestrator` | `for d in skills/*/; do [ -f "$d/SKILL.md" ] && ln -s "$(pwd)/$d" ~/.codex/skills/"$(basename "$d")"; done` |
| **Cursor (Global or Project)** | `ln -s "$(pwd)" ~/.cursor/skills/appnwebsite-orchestrator` *(or `.cursor/skills/`)* | `for d in skills/*/; do [ -f "$d/SKILL.md" ] && ln -s "$(pwd)/$d" ~/.cursor/skills/"$(basename "$d")"; done` |
| **Shared Agent Skills (`~/.agents/skills/`)** | `ln -s "$(pwd)" ~/.agents/skills/appnwebsite-orchestrator` | `for d in skills/*/; do [ -f "$d/SKILL.md" ] && ln -s "$(pwd)/$d" ~/.agents/skills/"$(basename "$d")"; done` |

### Option B — Standalone Child Skill Copy (Zero Suite Dependency)

Every folder under `skills/<child-name>/` is self-contained (zero external relative Markdown links), so you can copy any individual child folder directly into `~/.claude/skills/`, `~/.codex/skills/`, `~/.cursor/skills/`, `~/.gemini/config/skills/`, or `~/.agents/skills/` and validate it standalone with `python3 scripts/validate_skill.py <copied_dir>`.

*(Note: Keep real files without symlinks inside the source repository itself; symlinks above are only for local ecosystem registration.)*

---

## CLI Tools (Python 3 Stdlib Only — Zero External Dependencies)

```bash
# 1. Validate Parent SKILL.md, registry.json parity, links, syntax & R2 6-pillar modules
python3 scripts/validate_skill.py . --strict --json

# 2. Progressive-disclosure query CLI (list, stage/surface routing, BM25+MMR search, extract, budget audit)
python3 scripts/query_skill.py --list
python3 scripts/query_skill.py --surface web-app --stage 3a
python3 scripts/query_skill.py --module orchestration-protocol --pillar 5
python3 scripts/query_skill.py "simplicity deletion" --mmr 0.7 --summary -n 3 --json
python3 scripts/query_skill.py --headings references/00-spiral-governance/spiral-lifecycle.md
python3 scripts/query_skill.py --extract references/00-spiral-governance/spiral-lifecycle.md "5. Hard Quality Gate"
python3 scripts/query_skill.py --audit-budget

# 3. Enforce Charter, Simplicity Record, Q2 Risk Register & Phase 3A Foundation Gate on any project
python3 scripts/check_spiral_gates.py --project-dir /path/to/target-project --stage all --strict --json
```

---

## Attribution & License

- **License**: [MIT License](LICENSE) (`Copyright (c) 2026 nambuw`).
- **Source Traceability**: Complete mapping of evaluated local skills and vetted open-source GitHub repositories is tracked in [Source-Coverage Inventory](references/source-coverage-inventory.md).
