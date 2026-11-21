"""Self-integrity tests verifying suite hygiene, oracles, and isolated fixtures.

Runs cleanly immediately (`pytest tests/ -m self_check -v`) without requiring M1-M5.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from conftest import (
    CHILD_SKILLS,
    FIXTURES_DIR,
    TESTS_DIR,
    assert_r2_module_compliant,
    check_english_prose_only,
    extract_markdown_links,
    get_registry_entries,
    markdown_heading_slugs,
    materialize_skill_fixture,
    parse_r2_pillars,
    validate_frontmatter_contract,
    validate_registry_dag,
    wcag_contrast_ratio,
)

pytestmark = pytest.mark.self_check


def test_no_skip_or_xfail_decorators_in_test_suite() -> None:
    """Enforce zero @pytest.mark.skip / skipif / xfail cheats across tests/."""
    test_files = sorted(TESTS_DIR.glob("test_*.py"))
    assert len(test_files) >= 5, f"Expected >= 5 test files, found {len(test_files)}"

    forbidden_marks = {"skip", "skipif", "xfail"}
    violations: list[str] = []

    for tf in test_files:
        tree = ast.parse(tf.read_text(encoding="utf-8"), filename=str(tf))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    dumped = ast.dump(dec)
                    for mark in forbidden_marks:
                        if f"attr='{mark}'" in dumped and "mark" in dumped:
                            violations.append(f"{tf.name}:{node.lineno}: forbidden @{mark}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in {"skip", "xfail"}:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest":
                        violations.append(
                            f"{tf.name}:{node.lineno}: forbidden pytest.{node.func.attr}()"
                        )

    assert not violations, f"Skip/xfail cheats detected: {violations}"


def test_fixture_hygiene_no_literal_skill_agents_gemini_or_symlinks() -> None:
    """Confirm tests/ contains zero literal SKILL.md, AGENTS.md, GEMINI.md, or symlinks."""
    forbidden_names = {"SKILL.md", "AGENTS.md", "GEMINI.md"}
    hits: list[str] = []
    symlinks: list[str] = []

    for p in TESTS_DIR.rglob("*"):
        if p.is_symlink():
            symlinks.append(str(p.relative_to(TESTS_DIR)))
        if p.name in forbidden_names:
            hits.append(str(p.relative_to(TESTS_DIR)))

    assert not hits, f"Forbidden literal files on disk under tests/: {hits}"
    assert not symlinks, f"Symlinks forbidden under tests/: {symlinks}"


def test_wcag_oracle_exact_boundary_math() -> None:
    """Verify independent WCAG 2.1 contrast oracle on exact AA/large/AAA boundaries."""
    assert wcag_contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert wcag_contrast_ratio("#000000", "#000000") == pytest.approx(1.0, abs=0.001)

    # Normal text AA (4.5:1)
    assert wcag_contrast_ratio("#767676", "#FFFFFF") >= 4.5
    assert wcag_contrast_ratio("#777777", "#FFFFFF") < 4.5

    # Large text / UI component AA (3.0:1)
    assert wcag_contrast_ratio("#949494", "#FFFFFF") >= 3.0
    assert wcag_contrast_ratio("#959595", "#FFFFFF") < 3.0

    # Normal text AAA (7.0:1)
    assert wcag_contrast_ratio("#595959", "#FFFFFF") >= 7.0
    assert wcag_contrast_ratio("#5A5A5A", "#FFFFFF") < 7.0

    with pytest.raises(ValueError):
        wcag_contrast_ratio("#GGGGGG", "#FFFFFF")


def test_r2_parser_accepts_valid_fixture_and_rejects_stubs(tmp_path: Path) -> None:
    """Verify R2 parser accepts materialized valid_minimal_skill and rejects synthetic stubs."""
    repo = materialize_skill_fixture(tmp_path, include_child=True)

    validate_frontmatter_contract(repo / "SKILL.md", expected_name="appnwebsite-orchestrator")
    validate_frontmatter_contract(
        repo / "skills" / "sample-child" / "SKILL.md",
        expected_name="sample-child",
        require_child_fields=True,
    )

    for mod in (
        repo / "references" / "00-spiral-governance" / "sample-module.md",
        repo / "references" / "orchestration-protocol.md",
        repo / "skills" / "sample-child" / "references" / "sample-child-module.md",
    ):
        stats = assert_r2_module_compliant(mod)
        assert stats["words"] >= 800
        assert stats["non_empty_lines"] >= 120
        assert not check_english_prose_only(mod.read_text(encoding="utf-8"))

    # Synthetic stub missing Pillar 5 & containing TODO must be rejected
    bad_mod = tmp_path / "stub_module.md"
    bad_mod.write_text(
        "# Stub\n\n## 1. Decision Framework\nTODO\n\n## 2. Step-by-Step Workflow\n1. Do x\n",
        encoding="utf-8",
    )
    with pytest.raises(AssertionError):
        assert_r2_module_compliant(bad_mod)


def test_registry_dag_validator_accepts_valid_and_rejects_cycles(tmp_path: Path) -> None:
    """Verify registry DAG validator supports both 'children' & 'skills' and rejects cycles."""
    repo = materialize_skill_fixture(tmp_path, include_child=True)
    reg = json.loads((repo / "registry.json").read_text(encoding="utf-8"))
    expected_fixture_children = ["sample-child"] + [name for name, _ in CHILD_SKILLS]
    validate_registry_dag(reg, expected_child_names=expected_fixture_children)

    # Legacy/alternative 'skills' key must also be accepted cleanly
    skills_reg = {
        "skills": [
            {
                "id": "sample-child",
                "path": "skills/sample-child",
                "spiral_stages": ["Q1"],
                "triggers": ["sample"],
                "depends_on": [],
                "inputs": ["in.md"],
                "outputs": ["out.md"],
                "estimated_tokens": 500,
            }
        ]
    }
    validate_registry_dag(skills_reg, expected_child_names=["sample-child"])

    # Missing both 'children' and 'skills' must raise AssertionError, never KeyError
    with pytest.raises(AssertionError):
        get_registry_entries({"suite_name": "broken"})

    cyclic_reg = {
        "children": [
            {
                "id": "a",
                "path": "skills/a",
                "spiral_stages": ["Q1"],
                "triggers": ["a"],
                "depends_on": ["b"],
                "inputs": ["x"],
                "outputs": ["y"],
                "estimated_tokens": 500,
            },
            {
                "id": "b",
                "path": "skills/b",
                "spiral_stages": ["Q2"],
                "triggers": ["b"],
                "depends_on": ["a"],
                "inputs": ["y"],
                "outputs": ["z"],
                "estimated_tokens": 500,
            },
        ]
    }
    with pytest.raises(AssertionError, match="cycle"):
        validate_registry_dag(cyclic_reg)


def test_domain_fixtures_present_and_parse_cleanly() -> None:
    """Verify spiral_gates, ui_samples, and api_security_samples fixtures are intact."""
    spiral = FIXTURES_DIR / "spiral_gates"
    for sub in ("complete_workspace", "missing_phase3a", "missing_simplicity"):
        assert (spiral / sub / "spiral-charter.md").is_file()
    assert (spiral / "complete_workspace" / "simplicity-interrogation-record.md").is_file()
    assert (spiral / "complete_workspace" / "risk-spike-register.md").is_file()
    assert not (spiral / "missing_simplicity" / "simplicity-interrogation-record.md").exists()

    ui = FIXTURES_DIR / "ui_samples"
    for fname in (
        "sloppy_ui.tsx",
        "sloppy_styles.css",
        "clean_ui.tsx",
        "clean_styles.css",
        "tokens_valid.json",
        "tokens_missing_value.json",
        "tokens_dangling_alias.json",
        "tokens_circular_alias.json",
        "tokens_invalid_syntax.json.txt",
    ):
        assert (ui / fname).is_file(), f"Missing UI fixture: {fname}"

    valid_tokens = json.loads((ui / "tokens_valid.json").read_text(encoding="utf-8"))
    assert "primitive" in valid_tokens and "semantic" in valid_tokens and "component" in valid_tokens
    with pytest.raises(json.JSONDecodeError):
        json.loads((ui / "tokens_invalid_syntax.json.txt").read_text(encoding="utf-8"))

    sec = FIXTURES_DIR / "api_security_samples"
    for fname in ("vulnerable_handler.py", "vulnerable_client.tsx", "clean_handler.py", "clean_client.tsx"):
        assert (sec / fname).is_file(), f"Missing security fixture: {fname}"


def test_r2_anti_bypass_boilerplate_and_password_failure_rejected(tmp_path: Path) -> None:
    """Verify R2 oracle rejects 125x boilerplate repetition, fenced P5 commands, and PASSWORD/FAILURE."""
    base_md = (FIXTURES_DIR / "valid_minimal_skill" / "references" / "00-spiral-governance" / "sample-module.md").read_text(
        encoding="utf-8"
    )

    # 1. 125x repeated boilerplate sentence must fail anti-boilerplate checks
    bp_line = "Evaluate simplest high-craft approach with explicit thresholds before adding abstractions in every spiral."
    bp_doc = tmp_path / "boilerplate.md"
    bp_doc.write_text(
        base_md.replace(
            "## 2. Step-by-Step Workflow",
            "\n".join([bp_line] * 125) + "\n\n## 2. Step-by-Step Workflow",
        ),
        encoding="utf-8",
    )
    with pytest.raises(AssertionError, match="(?i)boilerplate|repetition"):
        assert_r2_module_compliant(bp_doc)

    # 2. Fenced ## 5. Hard Quality Gate in Pillar 1 must NOT supply Pillar 5's command
    fenced_bypass = base_md.replace(
        "## 1. Decision Framework",
        "## 1. Decision Framework\n\n````markdown\n## 5. Hard Quality Gate\n- `fake_cmd --run`\n````\n",
    )
    # Strip the real command from Pillar 5
    fenced_bypass = fenced_bypass.replace("```bash\n     python3 scripts/sample_check.py --check\n     ```", "No cli command here.")
    fenced_bypass = fenced_bypass.replace("`python3 scripts/sample_check.py --check`", "missing command")
    fenced_doc = tmp_path / "fenced_p5_bypass.md"
    fenced_doc.write_text(fenced_bypass, encoding="utf-8")
    with pytest.raises(AssertionError, match="command"):
        assert_r2_module_compliant(fenced_doc)

    # 3. PASSWORD and FAILURE substrings must NOT satisfy Pillar 5 PASS/FAIL word-boundary check
    substr_bypass = base_md
    p5_idx = substr_bypass.index("## 5. Hard Quality Gate")
    p6_idx = substr_bypass.index("## 6. Anti-Patterns")
    bad_p5 = (
        "## 5. Hard Quality Gate\n\n"
        "- PASSWORD policy verified with numeric bound 12.\n"
        "- FAILURE modes logged before shipping.\n"
        "- Run `python3 scripts/sample_check.py --check`.\n"
        "- Extra gate line alpha checking artifact integrity.\n"
        "- Extra gate line beta checking latency budgets.\n"
        "- Extra gate line gamma checking schema validation.\n"
        "- Extra gate line delta checking dependency counts.\n"
        "- Extra gate line epsilon checking link targets.\n"
        "- Extra gate line zeta checking deletion notes.\n"
        "- Extra gate line eta checking ownership signoff.\n"
        "- Extra gate line theta checking audit logs.\n"
        "- Extra gate line iota checking token budgets.\n"
        "- Extra gate line kappa checking rollback readiness.\n\n"
    )
    substr_doc = tmp_path / "substr_p5.md"
    substr_doc.write_text(substr_bypass[:p5_idx] + bad_p5 + substr_bypass[p6_idx:], encoding="utf-8")
    with pytest.raises(AssertionError, match="PASS and FAIL"):
        assert_r2_module_compliant(substr_doc)

    # 4. Incidental prose ("delete stale rows") must NOT satisfy Pillar 2 deletion-pass requirement
    p2_idx = base_md.index("## 2. Step-by-Step Workflow")
    p3_idx = base_md.index("## 3. Reusable Artifact")
    incidental_p2 = (
        "## 2. Step-by-Step Workflow\n\n"
        "1. Gather domain inputs and confirm owner assignment across the repository workflow.\n"
        "   - Owner: technical lead reviews input schema boundaries before processing.\n"
        "   - Tool: run `python3 scripts/sample_check.py --check` on staged manifests.\n"
        "2. Run maintenance script to delete stale rows from the staging database table before indexing.\n"
        "   - Input: staging snapshot table exported from yesterday's nightly batch.\n"
        "   - Output: compacted staging index ready for deterministic integration checks.\n"
        "3. Execute schema validation and emit the required output contract artifacts cleanly.\n"
        "   - Owner: platform engineer verifies backward compatibility across active clients.\n"
        "   - Output: schema diff summary stored alongside release verification records.\n"
        "4. Review telemetry metrics and confirm alert thresholds across every active service endpoint.\n"
        "   - Owner: operations engineer confirms p95 latency stays below the service objective.\n"
        "   - Output: dashboard snapshot archived under operational evidence artifacts.\n"
        "5. Verify backup retention intervals and archive expired snapshots on the configured schedule.\n"
        "   - Owner: storage maintainer audits encrypted volume checksums after rotation.\n"
        "   - Output: rotation manifest signed with deterministic timestamp entries.\n"
        "6. Confirm release owners sign off on deployment readiness and rollback runbook locations.\n"
        "   - Owner: release captain validates canary rollout percentages before traffic shift.\n"
        "   - Output: deployment checklist stamped with rollout gate verification.\n"
        "7. Record audit timestamps and verify deterministic test suites across staging containers.\n"
        "   - Owner: quality engineer confirms end-to-end assertions execute without flakiness.\n"
        "   - Output: deterministic execution report uploaded to build artifacts.\n"
        "8. Validate endpoint health checks and monitor response latency distributions for stability.\n"
        "   - Owner: service maintainer inspects error budgets during staged soak windows.\n"
        "   - Output: soak stability summary confirmed by automated telemetry queries.\n"
        "9. Publish generated release manifests and notify downstream pipeline consumers of completion.\n"
        "   - Owner: pipeline coordinator posts release SHA digests to downstream subscribers.\n"
        "   - Output: immutable release notes committed to changelog records.\n"
        "10. Archive historical execution logs and verify deterministic metrics in the artifact store.\n"
        "    - Owner: compliance auditor confirms retention policy enforcement across buckets.\n"
        "    - Output: final stage signoff record prepared for quadrant review.\n\n"
    )
    incidental_doc = tmp_path / "incidental_p2.md"
    incidental_doc.write_text(base_md[:p2_idx] + incidental_p2 + base_md[p3_idx:], encoding="utf-8")
    with pytest.raises(AssertionError, match="Deletion/Condensation"):
        assert_r2_module_compliant(incidental_doc)


def test_markdown_fences_inline_links_slugs_and_english_motto_edge_cases() -> None:
    """Verify empty fences, 4-backtick outer fences, inline links, double-hyphen slugs, and motto rules."""
    # Empty fence + 4-backtick outer fence + CRLF must not swallow or leak pillars
    md_fences = (
        "## 1. Decision Framework\r\n"
        "```\r\n"
        "```\r\n"
        "## 2. Step-by-Step Workflow\r\n"
        "   ````markdown\r\n"
        "```python\r\n"
        "## 5. Hard Quality Gate\r\n"
        "```\r\n"
        "   ````\r\n"
        "## 3. Reusable Artifact & Template\r\n"
    )
    parsed = parse_r2_pillars(md_fences)
    assert parsed["order"] == [1, 2, 3], f"Unexpected parsed order: {parsed['order']}"

    # Inline code links must be ignored while real relative links are returned
    md_links = (
        "Ignore `[x](missing.md)` and `` `[y](missing2.md)` ``.\n"
        "Keep [Real](references/real.md).\n"
    )
    assert extract_markdown_links(md_links) == [("Real", "references/real.md")]

    # GitHub heading slug preserves double hyphen around stripped '&'
    slugs = markdown_heading_slugs("## 3. Reusable Artifact & Template\n## Risk Analysis & Spikes\n")
    assert "3-reusable-artifact--template" in slugs
    assert "risk-analysis--spikes" in slugs

    # English prose check: allowlist motto, English loanwords, and fenced/double-backticked non-English
    clean_prose = (
        'Follow "ít nhất mà tốt nhất" ("Least Code, Highest Craft").\n'
        "Visit the café for a résumé review; avoid cliché, vis-à-vis, à la carte, déjà vu, naïve.\n"
        "Inline code `` `tiếng Việt` `` and 4-backtick fenced ````\n```\n中文 tiếng Việt\n```\n```` are ignored.\n"
    )
    assert check_english_prose_only(clean_prose) == []

    # Actual Vietnamese and CJK prose outside fences/motto MUST be caught
    assert check_english_prose_only("Đây là mô tả bằng tiếng Việt.\n")
    assert check_english_prose_only("这是中文说明。\n")

    # Stray unclosed backticks across blank-line paragraph breaks must NOT mask prose
    cross_para = (
        "Paragraph one has a stray ` backtick.\n\n"
        "Đây là mô tả bằng tiếng Việt.\n\n"
        "Paragraph three also has a stray ` backtick.\n"
    )
    assert check_english_prose_only(cross_para)
