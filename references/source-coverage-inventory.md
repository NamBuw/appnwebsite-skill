# Source-Coverage Inventory (R1 Complete Provenance & Curation Audit)

Deterministic R1 provenance, curation verdict, license audit, and target mapping for `1,839` local `SKILL.md` paths (`841` unique names / `844` pairs), `5` extra assets, and `47` GitHub/web entries (`896` records). Full per-skill paths, `duplicate_paths`, `target_module`, and rationales live in `data/classified-skills-inventory.json` (`schema_version: 1.0.0`).

## Table of Contents

- [Summary Metrics & JSON Pointers](#summary-metrics--json-pointers)
- [1. Local Relevant Skills (306)](#1-local-relevant-skills-306)
- [2. Local Partially Relevant Skills (175)](#2-local-partially-relevant-skills-175)
- [3. Local Out-of-Scope & Promotions (363)](#3-local-out-of-scope--promotions-363)
- [4. Extra Local Assets & IDE Reconciliation (5)](#4-extra-local-assets--ide-reconciliation-5)
- [5. Star-Ranked GitHub & Web Skills (47)](#5-star-ranked-github--web-skills-47)
- [6. License Compliance & Conflict Resolution](#6-license-compliance--conflict-resolution)

## Summary Metrics & JSON Pointers

- **Local `SKILL.md` paths**: `1,839` (`590` Relevant + `377` Partial + `872` Out-of-Scope)
- **Unique local names / `(name, class)` pairs**: `841` unique / `844` pairs (`306` Relevant + `175` Partial + `363` Out-of-Scope)
- **Cross-classified (`844 - 841 = 3`)**: `index` (Rel/Part), `start` (Part/OOS), `user-context` (Rel/OOS)
- **Extra local assets / GitHub-web / Total**: `5` extra + `47` GitHub/web = `896` records (`844+5+47`)
- **JSON query (`data/classified-skills-inventory.json`)**: `summary` + `skills[]` (`id, name, source_type, classification, curation_verdict, disposition, target_skill, target_module, license, stars, url, safety_status, canonical_path, duplicate_paths, file_count, rationale`).
- **CLI lookup**: `python3 -c "import json; print([r for r in json.load(open('data/classified-skills-inventory.json'))['skills'] if r['name']=='<name>'])"`

## 1. Local Relevant Skills (306)

Verdicts: `5 ADOPT + 286 MERGE-INTO-EXISTING + 10 CONCEPTS-ONLY + 5 REJECT = 306`.

- **advanced-web-app-capabilities** (MERGE/ADAPT, 37): agent-browser, agent-browser-verify, agents-sdk, ai-elements, ai-gateway, ai-generation-persistence, ai-sdk, analyze-data-quality, audit, building-ai-agent-on-cloudflare, cdn-caching, connect-recommend, design-kpis, design-qa, durable-objects, expo-deployment, metric-diagnostics, mixpanel-auth, mixpanel-headless-setup, mixpanelyst, native-data-fetching, next-cache-components, payments, runtime-cache, sandbox-sdk, stripe-best-practices, stripe-directory, stripe-docs, stripe-projects, upgrade-stripe, validate-data, vercel-agent, vercel-flags, vercel-sandbox, verification, web-perf, workflow
- **appnwebsite-orchestrator** (ADOPT/ADAPT, 2): prototype, research-scientist
- **appnwebsite-orchestrator** (MERGE/ADAPT, 5): estimate, gate-check, milestone-review, project-stage-detect, scope-check
- **excluded** (REJECT/EXCL, 5): artifact-emulator, chat-sdk, cms, stripe-apps, temporal-serverless
- **figma-design-to-code** (MERGE/ADAPT, 16): figma, figma-code-connect, figma-code-connect-components, figma-create-design-system-rules, figma-create-new-file, figma-design-to-code, figma-generate-design, figma-generate-diagram, figma-generate-library, figma-implement-design, figma-implement-motion, figma-swiftui, figma-use, figma-use-figjam, figma-use-motion, figma-use-slides
- **frontend-surfaces-and-redesign** (ADOPT/REUSE, 2): landing-page-design, redesign-existing-projects
- **frontend-surfaces-and-redesign** (CONCEPTS/SYNTH, 1): generative_ui
- **frontend-surfaces-and-redesign** (MERGE/ADAPT, 47): accessibility-and-inclusive-visualization, artifact-template-analytics-dashboard, banner-design, build-dashboard, building-native-ui, canvas2d-data-visualization, codex-expo-run-actions, d3-data-visualization, dashboard-expert, dashboards-and-real-time-visualization, data-visualization, design, expo-api-routes, expo-cicd-workflows, expo-dev-client, expo-module, expo-tailwind-setup, expo-ui-jetpack-compose, expo-ui-swift-ui, frontend-design, gantt-chart-visualization, geist, geospatial-and-cartographic-visualization, grammar-of-graphics-and-declarative-visualization, image-to-code, node-link-and-diagram-layout, react-and-nextjs-data-visualization, reports-pdfs-and-slide-automation, scrollytelling-and-parallax-data-visualization, share, sites, sites-remix, statistical-and-uncertainty-visualization, team-polish, team-ui, testing-data-visualizations, threejs-data-visualization, typescript-data-visualization-engineering, ui-styling, upgrading-expo, url-to-code, use-dom, v0-dev, visualization-strategy-and-critique, visualize, visualize-data, web-artifacts-builder
- **fullstack-api-engineering** (MERGE/ADAPT, 48): aspnet-core, build-mcp-app, build-mcp-server, build-mcpb, building-mcp-server-on-cloudflare, cli-creator, cloudflare, code-review, dev-story, email, eve, finishing-a-development-branch, frontend-app-builder, gh-address-comments, investigation-mode, json-render, knowledge-update, localize, marketplace, mcp-builder, micro, microfrontends, ncc, next-forge, next-upgrade, nextjs, react-best-practices, receiving-code-review, requesting-code-review, review-agent, routing-middleware, satori, shadcn, swr, tech-debt, temporal-cloud-setup, temporal-developer, temporal-ops, turbopack, turborepo, using-git-worktrees, vercel-api, vercel-connect, vercel-functions, vercel-queues, vercel-services, vercel-storage, workers-best-practices
- **meta-plan-goal-teamwork** (MERGE/ADAPT, 8): define-goal, dispatching-parallel-agents, executing-plans, story-done, story-readiness, subagent-driven-development, verification-before-completion, writing-plans
- **multi-layer-qa-testing** (MERGE/ADAPT, 30): android-emulator-qa, android-performance, bug-report, bug-triage, debug-failing-test, experimental-design, frontend-testing-debugging, generate-snapshot, perf-profile, playwright, playwright-interactive, qa-plan, record-video, regression-suite, run-e2e-tests, run-integration-tests, run-pre-commit-checks, run-smoke-tests, screenshot, smoke-check, soak-test, statistical-analysis, statistical-power, systematic-debugging, team-qa, test-driven-development, test-evidence-review, test-flakiness, test-helpers, test-setup
- **observability-sre-release** (MERGE/ADAPT, 28): bootstrap, changelog, chunk, circleci-builds, circleci-cli, circleci-config, cloudflare-deploy, cron-jobs, day-one-patch, deployments-cicd, doc-coauthoring, env-vars, geistdocs, gh-fix-ci, hotfix, launch-checklist, netlify-deploy, observability, onboard, posthog, release-checklist, render-deploy, retrospective, sentry, team-release, vercel-cli, vercel-deploy, wrangler
- **product-discovery-and-specs** (MERGE/ADAPT, 21): brainstorming, citation-management, create-epics, create-stories, deep-research, get-context, hypothesis-generation, ideate, index, literature-review, notion-research-documentation, notion-spec-to-implementation, paper-lookup, peer-review, research, research-lookup, scholar-evaluation, scientific-brainstorming, scientific-critical-thinking, scientific-writing, user-context
- **security-engineering** (CONCEPTS/SYNTH, 8): create-security-implementation-plan, determine-threat-model, generate-security-audit-report, mandatory-secure-web-skills, run-poc, run-security-scanner, scan_dependencies, securecoder-persona
- **security-engineering** (MERGE/ADAPT, 28): assess-patch-risk, attack-path-analysis, auth, check-skills, claude-security, cloud-findings, deep-security-scan, define-security-policy, finding-discovery, fix-finding, propose-security-hardening, publish-findings, resolve-dependency-alert, security-audit, security-best-practices, security-diff-scan, security-ownership-map, security-scan, security-threat-model, sign-in-with-vercel, threat-model, threat-model-visualize, track-findings, triage-finding, validation, vercel-firewall, verify-fix, vulnerability-writeup
- **system-data-architecture** (MERGE/ADAPT, 12): adopt, architecture-decision, architecture-review, artifact-template-system-design, consistency-check, create-architecture, create-control-manifest, propagate-design-change, reverse-document, supabase, supabase-postgres-best-practices, uml-and-software-architecture-visualization
- **ui-design-craft** (ADOPT/REUSE, 1): ui-ux-pro-max
- **ui-design-craft** (CONCEPTS/SYNTH, 1): canvas-design
- **ui-design-craft** (MERGE/ADAPT, 6): artifact-template-design-report, brand, design-review, design-system, ux-design, ux-review

**Rejected Relevant (5)**: `artifact-emulator` (`Proprietary` Cowork; superseded by `playwright-interactive`/`agent-browser-verify`/`design-qa`), `chat-sdk` (bot wrapper), `cms` (vendor setup), `stripe-apps` (React-17 iframe niche), `temporal-serverless` (Lambda YAML bloat).

## 2. Local Partially Relevant Skills (175)

Verdicts: `45 MERGE-INTO-EXISTING + 46 CONCEPTS-ONLY + 84 REJECT = 175`.

- **advanced-web-app-capabilities** (MERGE/ADAPT, 14): KPI/data-quality reports & notebooks (e.g. `build-report`, `create-data-context`, `index`, `kpi-reporting`)
- **appnwebsite-orchestrator** (CONCEPTS/SYNTH, 23): Plugin/hook/command ergonomics (`agent-development`, `claude-automation-recommender`, `claude-md-improver`)
- **appnwebsite-orchestrator** (MERGE/ADAPT, 11): Progressive disclosure & skill lint (`evaluate-plugin`, `evaluate-skill`, `improve-skill`, `writing-skills`)
- **excluded** (REJECT/EXCL, 84): Xcode (`build-macos-apps`, `build-ios-apps`), `game-studio`, `hyperframes`, `shopify`, ChatGPT apps, `PokeWorld` game/art, `winui-app`
- **frontend-surfaces-and-redesign** (CONCEPTS/SYNTH, 1): MCP app embedding (`mcp-app-development`, `NONE (Builtin-IDE)`)
- **frontend-surfaces-and-redesign** (MERGE/ADAPT, 4): SwiftUI UI/perf (`swiftui-liquid-glass`, `swiftui-performance-audit`, `swiftui-ui-patterns`, `swiftui-view-refactor`)
- **fullstack-api-engineering** (CONCEPTS/SYNTH, 1): GitHub permission guardrails (`permissioned-github`, `NONE (Builtin-IDE)`)
- **fullstack-api-engineering** (MERGE/ADAPT, 8): PR automation, TS setup, Python rules (`address-pr-comments`, `create-pull-request`, `suggest-fix-issue`, `yeet`)
- **meta-plan-goal-teamwork** (CONCEPTS/SYNTH, 2): Workflow/swarm orchestration (`run-workflow`, `swarm`, `NONE (Builtin-IDE)`)
- **meta-plan-goal-teamwork** (MERGE/ADAPT, 6): Swarm scheduling & slices (`diagnosing-superpowers`, `sprint-plan`, `sprint-status`, `start`, `vertical-slice`)
- **multi-layer-qa-testing** (MERGE/ADAPT, 1): Python profiling (`pylance-python-profiling`)
- **observability-sre-release** (CONCEPTS/SYNTH, 1): Scheduled changelog hygiene (`automation`, `NONE (Builtin-IDE)`)
- **observability-sre-release** (MERGE/ADAPT, 1): Changelog updates (`rea-changelog-update`)
- **product-discovery-and-specs** (CONCEPTS/SYNTH, 18): Discovery/review concepts (`brainstorm` + 17 `artifact-template-*`; verbose office templates excluded)

## 3. Local Out-of-Scope & Promotions (363)

Totals: `358 EXCLUDED-OUT-OF-SCOPE + 1 MERGE-INTO-EXISTING + 4 CONCEPTS-ONLY = 363`.

### 3.1 Promoted Out-of-Scope Skills (5)

- `agy-customizations` -> `appnwebsite-orchestrator` (CONCEPTS, `NONE (Builtin-IDE)`): 24 KB cap, 20k `defaultRulesBudget`, path pointers.
- `chronicle` -> `appnwebsite-orchestrator` (MERGE, `MIT`): token-cost analytics (turn growth, tool thrash) in `audit_token_budget.py`.
- `swarm_monitor` -> `meta-plan-goal-teamwork` (CONCEPTS, `NONE (Builtin-IDE)`): stall detection & swarm health monitoring.
- `swarm_narrator` -> `meta-plan-goal-teamwork` (CONCEPTS, `NONE (Builtin-IDE)`): event-driven milestone narration.
- `swarm_pane` -> `meta-plan-goal-teamwork` (CONCEPTS, `NONE (Builtin-IDE)`): operator visibility & pane isolation.

### 3.2 Excluded Origin Buckets (358 Excluded + 5 Promoted = 363)

- **Telecom & Conferencing (108)**: `twilio-developer-kit` (55), `zoom` (53)
- **Biotech & Life Sciences (76)**: `life-science-research` (50), `ngs-analysis` (18), `boltz-api-cli` (8)
- **IDE / Extension / Builtins (36)**: `vscode-server-extensions` (28: 27 excl, 1 prom `chronicle`), `antigravity-builtin` (8: 4 excl, 4 prom)
- **Finance, Mfg & GPU Infra (52)**: `public-equity-investing` (23), `claude-for-manufacturing` (17), `nvidia` (12)
- **Media, Cloud Docs & Office (31)**: `canva` (8), `adobe` (6), `dropbox` (6), `google-drive` (5), `airtable` (3), `higgsfield` (3)
- **Local Non-Web, Game & Misc (60)**: `claude-local-non-web` (13), `other-local-out-of-scope` (12), `pokeworld-game-domain` (8), `champion-kit` (7), `plugin-eval` (4), `codex-curated-non-web` (3), `cwc-makers`/`example-plugin`/`math-proof` (2x3), `hookify`/`math-olympiad`/`receipts`/`session-report`/`chatcut`/`openai-ads-conversions`/`zotero` (7x1)

## 4. Extra Local Assets & IDE Reconciliation (5)

Reconciles `.vscode-server` (`254` paths/`42` unique) and `.antigravity-ide-server` (`9` paths/`9` unique) in Survey 1, plus `5` non-`SKILL.md` assets (`2 ADOPT + 3 MERGE-INTO-EXISTING`):

- `chronicle-cost-tips.prompt.md` (MERGE, `MIT`) -> `appnwebsite-orchestrator`: token heuristics vs context bloat.
- `add-telemetry.prompt.md` (MERGE) -> `observability-sre-release`: privacy-safe Python telemetry hooks.
- `claude-statusline-compact-reserve` (MERGE) -> `appnwebsite-orchestrator`: `COMPACT_RESERVE = 33_000` formula.
- `pokeworld-read-guard-and-md-section` (ADOPT) -> `scripts/query_skill.py`: 40 KB guard, heading index, AWK slicer.
- `research-scientist-release-extras` (ADOPT) -> `scripts/query_skill.py`: `local_evidence.py` BM25 + entropy + MMR.

## 5. Star-Ranked GitHub & Web Skills (47)

Totals: `2 ADOPT + 19 MERGE-INTO-EXISTING + 21 CONCEPTS-ONLY + 5 REJECT = 47` (`2026-11-21` stars). Targets: `orch`=`appnwebsite-orchestrator`, `ui`=`ui-design-craft`, `team`=`meta-plan-goal-teamwork`, `adv`=`advanced-web-app-capabilities`, `sec`=`security-engineering`, `surf`=`frontend-surfaces-and-redesign`, `arch`=`system-data-architecture`, `prod`=`product-discovery-and-specs`, `fs`=`fullstack-api-engineering`. Safety defaults `SAFE` unless noted (`CONCEPTS_LIC`/`REJECT_*`):

1. https://github.com/mattpocock/skills (329,377*, MIT, MERGE->orch): Smart-zone (~150k), fresh subagents, deletion test, sparse ADRs
2. https://github.com/obra/superpowers (323,325*, MIT, MERGE->team): Trigger-only desc, no @ imports, TDD, debugging, verification Iron Law
3. https://github.com/affaan-m/ECC (308,091*, MIT, MERGE->orch): Strategic-compact, prefix stability, parallel lanes, eval harness
4. https://github.com/multica-ai/andrej-karpathy-skills (234,834*, NONE, CONCEPTS_LIC, CONCEPTS->orch): 4 pillars (Think First, Simplicity, Surgical Changes, Goal-Driven)
5. https://github.com/anthropics/skills (198,257*, NONE, CONCEPTS_LIC, CONCEPTS->orch): 3-tier Progressive Disclosure budgets & discernment nudge
6. https://github.com/DietrichGebert/ponytail (195,993*, MIT, MERGE->orch): Lazy dev mode, stdlib-first, upgrade triggers, lean diff audit
7. https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (152,333*, MIT, ADOPT->ui): Stdlib BM25 CSV design search CLI & Master+Overrides reused
8. https://github.com/Graphify-Labs/graphify (151,408*, Apache-2.0, CONCEPTS->orch): Tree-sitter AST graph & symbol-path read reduction
9. https://github.com/garrytan/gstack (142,247*, MIT, MERGE->prod): Narrowest-wedge discovery, ASCII flow diagrams, race/N+1 audits
10. https://github.com/VoltAgent/awesome-design-md (128,483*, MIT, MERGE->ui): Portable DESIGN.md brand token contract
11. https://github.com/JuliusBrussee/caveman (121,878*, Apache-2.0, MERGE->orch): Answer-first updates, path:START-END, MCP schema shrinkage
12. https://github.com/Leonxlnx/taste-skill (119,544*, MIT, MERGE->ui): Site-kind taxonomy & 320/390/1440px gates (WebGL rejected)
13. https://github.com/addyosmani/agent-skills (119,486*, MIT, MERGE->orch): Restartable sessions, Rule of 500, fence lint, axe+pa11y gate
14. https://github.com/thedotmack/claude-mem (118,753*, Apache-2.0, CONCEPTS->orch): Compressed cross-session notes (no daemon)
15. https://github.com/pbakaus/impeccable (114,278*, Apache-2.0, MERGE->ui): Visual critique vocabulary & micro-polish diagnostics
16. https://github.com/rtk-ai/rtk (87,354*, Apache-2.0 / BUSL-1.1 (proxy), CONCEPTS_LIC, CONCEPTS->orch): CLI Apache-2.0, rtk-proxy BUSL-1.1: quiet flags, never compress Read
17. https://github.com/ruvnet/ruflo (82,195*, MIT, CONCEPTS->team): Swarm topology & task-routing concepts (no external runtime)
18. https://github.com/headroomlabs-ai/headroom (80,238*, Apache-2.0, CONCEPTS->orch): AST/statistical log & JSON compression for CLI output
19. https://github.com/cloudflare/security-audit-skill (76,477*, MIT, MERGE->sec): 6-phase audit, evidence bar, OWASP LLM parameter-binding
20. https://github.com/blader/humanizer (71,831*, MIT, MERGE->ui): 24 AI-writing slop patterns & anti-puffery UX copy
21. https://github.com/Nutlope/hallmark (58,843*, MIT, MERGE->surf): 3-tier Floor/Reflex/Finish gates & handler lint
22. https://github.com/emilkowalski/skills (58,553*, MIT, MERGE->ui): Ease-out motion, interruptibility, break-ui stress tests
23. https://github.com/wshobson/agents (42,763*, MIT, CONCEPTS->team): Role-specialized agent delegation & handoff boundaries
24. https://github.com/vercel-labs/skills (40,293*, MIT, MERGE->orch): Skills CLI discovery index & install manifest conventions
25. https://github.com/VoltAgent/awesome-agent-skills (37,406*, MIT, CONCEPTS->orch): 1,000+ skill taxonomy cross-checked for R1 completeness
26. https://github.com/vercel-labs/agent-skills (34,637*, NONE, CONCEPTS_LIC, CONCEPTS->surf): Web guidelines (tabular-nums, overscroll, translate='no', paste)
27. https://github.com/oraios/serena (31,567*, MIT, CONCEPTS->orch): LSP/AST symbol retrieval (get_symbols_overview, find_symbol)
28. https://github.com/yamadashy/repomix (29,362*, MIT, CONCEPTS->orch): Repo packing with token accounting & secret checks
29. https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering (18,388*, MIT, MERGE->orch): KV-cache prefix, >3-turn masking, 4-Probe compaction, >2k offload
30. https://github.com/ast-grep/ast-grep (16,650*, MIT, CONCEPTS->orch): Structural AST search & codemods
31. https://github.com/coderamp-labs/gitingest (16,166*, MIT, CONCEPTS->orch): Compact directory-tree & prompt-digest extraction
32. https://github.com/trailofbits/skills (8,324*, CC-BY-SA-4.0, CONCEPTS_LIC, CONCEPTS->orch): CC-BY-SA-4.0: --self-test & convergence ledgers in MIT code
33. https://github.com/mufeedvh/code2prompt (7,771*, MIT, CONCEPTS->orch): Glob-filtered tree packing & deterministic token counting
34. https://github.com/tw93/Waza (7,628*, MIT, CONCEPTS->fs): High-density engineering habits for coding reviews
35. https://github.com/bergside/awesome-design-skills (3,758*, MIT, MERGE->ui): Dual SKILL.md + DESIGN.md companion architecture
36. https://github.com/ciembor/agent-rules-books (3,325*, MIT, MERGE->arch): Clean Code, DDD, DDIA distributed-data rules
37. https://github.com/Illyism/seo-skills (1,659*, NONE, CONCEPTS_LIC, CONCEPTS->adv): Fatal-First SEO/GEO (Bingbot, soft-404, /llms.txt, no demo-wall)
38. https://github.com/ojuschugh1/sqz (681*, Apache-2.0, CONCEPTS->orch): Zero-LLM repeat-line deduplication for CLI output
39. https://github.com/ooples/token-optimizer-mcp (590*, MIT, CONCEPTS->orch): Output compression & quota pacing (no MCP daemon)
40. https://github.com/activeing123/mcptoon (441*, Apache-2.0, CONCEPTS->orch): Single-gateway lazy MCP tool discovery
41. https://github.com/Ronifue/skill-authoring (57*, MIT, MERGE->orch): Delta Principle, 1-level depth, Defaults Over Menus
42. https://github.com/newzwalker/claude-skill-studio (0*, MIT, ADOPT->orch): 3-level token profiler (_estimate_tokens, L1/L2/L3, XML check)
43. https://github.com/NeoLabHQ/context-engineering-kit (1,845*, GPL-3.0, REJECT_LIC, REJECT->excl): GPL-3.0 copyleft incompatible with MIT suite
44. https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools (144,795*, GPL-3.0, REJECT_LIC, REJECT->excl): GPL-3.0 & unverified third-party leaked prompts
45. https://github.com/SnailSploit/Claude-Red (11,331*, MIT, REJECT_SAF, REJECT->excl): offensive-security-cluster (SnailSploit/Claude-Red, elementalsouls/Claude-OSINT): offensive/OSINT
46. https://github.com/farion1231/cc-switch (156,138*, MIT, REJECT_SCOPE, REJECT->excl): llm-proxy-routing-cluster (farion1231/cc-switch, cheaper-inference/OmniRoute, decolua/9router): OOS proxy
47. https://github.com/career-ops-hq/career-ops (84,008*, Mixed (incl. AGPL-3.0), REJECT_SCOPE, REJECT->excl): off-topic-utility-cluster (qiye45/wechatDownload, OpenMontageInc/OpenMontage AGPL-3.0, career-ops-hq/career-ops): OOS

## 6. License Compliance & Conflict Resolution

### 6.1 License Policy

- `MIT` / `Apache-2.0`: Direct adaptation & original MIT implementation with attribution.
- `CC-BY-SA-4.0` (`trailofbits/skills`), `BUSL-1.1` (`rtk-proxy`; CLI `Apache-2.0`): **Concepts only**, zero verbatim copy.
- `NONE` (Karpathy, `anthropics/skills`, `vercel-labs/agent-skills`, `Illyism/seo-skills`) & `NONE (Builtin-IDE)` (`Google.securecoder` x8, Antigravity): **Concepts only** in original MIT prose.
- `GPL-3.0` / `AGPL-3.0` (`NeoLabHQ/context-engineering-kit`, `x1xhlol/system-prompts-and-models-of-ai-tools`, `OpenMontage`) & `Proprietary` (`artifact-emulator`): **Strictly excluded (`REJECT`)**.

### 6.2 Cross-Skill Conflict Resolution

- **Typography & Icons (`ui-design-craft`)**: Ban `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`; default `Phosphor`, `Solar`, `Iconamoon` (ban `Material Icons/Symbols`, `Lucide`, `Feather`, `Heroicons` unless brownfield ADR overrides).
- **Surfaces (`ui-design-craft`)**: Flat intentional surfaces; hero text gradients `#FFFFFF->#9B9B9B` / `#000000->#666666`; zero AI-slop blobs.
- **Security (`security-engineering`)**: Vendor-neutral CLI (`semgrep`, `bandit`, `codeql`, `osv-scanner`, `trivy`, `gitleaks`, `zap`); IDE hooks optional.
- **Hygiene**: Zero symlinks, zero `AGENTS.md`/`GEMINI.md`, zero broken links across Parent and all 11 Child Skills.
