---
name: appnwebsite-orchestrator
description: Minimal hierarchical parent orchestrator fixture for validating packaging, progressive disclosure, registry DAG, and R2 six-pillar structure.
license: MIT
metadata:
  version: "1.0.0"
---

# Minimal Parent Orchestrator Fixture

Lean entry router for fixture verification. Read ONLY the reference module or child skill active for the current Spiral stage and NEVER bulk-load all references into context.

## Progressive Disclosure Routing

1. Active orchestration protocol: read [Orchestration Protocol](references/orchestration-protocol.md) and [Sample Spiral Module](references/00-spiral-governance/sample-module.md).
2. Registry index: inspect `registry.json` before dispatching child skills such as [Sample Child](skills/sample-child/SKILL.md).
3. Minimal-token lookup: run `python3 scripts/sample_check.py --help`.
4. Template instantiation: copy [Sample Template](templates/sample-template.md) into the working deliverable.
