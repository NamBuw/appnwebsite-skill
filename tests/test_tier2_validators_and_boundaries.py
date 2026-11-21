"""Tier 2: Validator, Script Syntax/Stdlib-Only, Boundary & Negative Behavioral Tests."""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import (
    CONTRACTED_SCRIPTS,
    FIXTURES_DIR,
    REPO_ROOT,
    assert_cli_rejected_cleanly,
    invoke_with_target,
    materialize_skill_fixture,
    pick_flag,
    probe_cli_contract,
    run_script,
)

pytestmark = pytest.mark.tier2

VALIDATE_SKILL = REPO_ROOT / "scripts" / "validate_skill.py"
QUERY_SKILL = REPO_ROOT / "scripts" / "query_skill.py"
CHECK_SPIRAL_GATES = REPO_ROOT / "scripts" / "check_spiral_gates.py"
AUDIT_TOKEN_BUDGET = REPO_ROOT / "scripts" / "audit_token_budget.py"

UI_SCRIPTS_DIR = REPO_ROOT / "skills" / "ui-design-craft" / "scripts"
DESIGN_SEARCH = UI_SCRIPTS_DIR / "design_search.py"
CORE_SEARCH = UI_SCRIPTS_DIR / "core_search.py"
CHECK_CONTRAST = UI_SCRIPTS_DIR / "check_contrast.py"
CHECK_ANTI_SLOP = UI_SCRIPTS_DIR / "check_anti_slop.py"
VALIDATE_TOKENS = UI_SCRIPTS_DIR / "validate_tokens.py"

CHECK_SECURITY_BASELINE = (
    REPO_ROOT / "skills" / "security-engineering" / "scripts" / "check_security_baseline.py"
)


def _all_repo_scripts() -> list[Path]:
    """Collect scripts in root scripts/ and skills/*/scripts/."""
    found: list[Path] = []
    for base in [REPO_ROOT / "scripts", *sorted((REPO_ROOT / "skills").glob("*/scripts"))]:
        if base.is_dir():
            for p in sorted(base.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts:
                    found.append(p)
    return found


@pytest.mark.parametrize(
    ("rel_script", "milestone"),
    [
        pytest.param(rel, ms, marks=getattr(pytest.mark, ms), id=rel)
        for rel, ms in CONTRACTED_SCRIPTS
    ],
)
def test_contracted_script_exists_help_syntax_and_stdlib_only(
    rel_script: str, milestone: str
) -> None:
    """Every contracted script must exist, pass --help, py_compile, and use Python 3 stdlib only."""
    script = REPO_ROOT / rel_script
    probe_cli_contract(script)

    comp = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert comp.returncode == 0, f"py_compile failed for {rel_script}:\n{comp.stderr}"

    sibling_modules = {p.stem for p in script.parent.glob("*.py")}
    tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    third_party: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in sys.stdlib_module_names and top not in sibling_modules:
                    third_party.append(top)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            top = node.module.split(".")[0]
            if top not in sys.stdlib_module_names and top not in sibling_modules:
                third_party.append(top)

    assert not third_party, (
        f"{rel_script}: Forbidden third-party imports (must be Python 3 stdlib only): {third_party}"
    )


@pytest.mark.m1
def test_all_present_scripts_pass_syntax_checks() -> None:
    """All .py, .sh, and .js/.cjs/.mjs scripts in repo must pass syntax checks."""
    scripts = _all_repo_scripts()
    assert len(scripts) >= 3, f"Expected >= 3 scripts at M1+, found {len(scripts)}"
    for s in scripts:
        if s.suffix == ".py":
            res = subprocess.run([sys.executable, "-m", "py_compile", str(s)], capture_output=True, text=True)
            assert res.returncode == 0, f"py_compile failed for {s}: {res.stderr}"
        elif s.suffix == ".sh":
            res = subprocess.run(["bash", "-n", str(s)], capture_output=True, text=True)
            assert res.returncode == 0, f"bash -n failed for {s}: {res.stderr}"
        elif s.suffix in {".js", ".cjs", ".mjs"}:
            res = subprocess.run(["node", "--check", str(s)], capture_output=True, text=True)
            assert res.returncode == 0, f"node --check failed for {s}: {res.stderr}"


@pytest.mark.m1
def test_validate_skill_passes_on_minimal_hierarchical_fixture(tmp_path: Path) -> None:
    """validate_skill.py must exit 0 on a valid materialized hierarchical skill fixture."""
    info = probe_cli_contract(VALIDATE_SKILL)
    assert "--require-all-active" in info["flags"], (
        "validate_skill.py --help must document --require-all-active"
    )
    repo = materialize_skill_fixture(tmp_path, include_child=True)
    res = invoke_with_target(VALIDATE_SKILL, repo)
    assert res.returncode == 0, (
        f"validate_skill.py failed on valid fixture:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    )


@pytest.mark.m1
@pytest.mark.parametrize(
    ("mutation", "expected_diag_token"),
    [
        ("missing_root_skill_md", "skill.md"),
        ("stray_nested_skill_md", "stray"),
        ("html_comment_before_frontmatter", "---"),
        ("invalid_skill_name", "name"),
        ("oversized_or_html_description", "description"),
        ("stray_agents_md", "agents.md"),
        ("stray_gemini_md", "gemini.md"),
        ("symlink_inside_repo", "symlink"),
        ("broken_relative_link", "broken link"),
        ("stub_r2_module_missing_pillar5", "pillar"),
        ("python_syntax_error_script", "py_compile"),
    ],
)
def test_validate_skill_rejects_negative_mutations(
    tmp_path: Path, mutation: str, expected_diag_token: str
) -> None:
    """validate_skill.py must reject all 11 negative packaging/link/R2/syntax mutations for the injected defect."""
    repo = materialize_skill_fixture(tmp_path, include_child=True, dest_name=f"repo_{mutation}")

    if mutation == "missing_root_skill_md":
        (repo / "SKILL.md").unlink()
    elif mutation == "stray_nested_skill_md":
        stray = repo / "references" / "nested" / "SKILL.md"
        stray.parent.mkdir(parents=True, exist_ok=True)
        stray.write_text("---\nname: stray\ndescription: stray\n---\n", encoding="utf-8")
    elif mutation == "html_comment_before_frontmatter":
        orig = (repo / "SKILL.md").read_text(encoding="utf-8")
        (repo / "SKILL.md").write_text("<!-- pre-comment -->\n" + orig, encoding="utf-8")
    elif mutation == "invalid_skill_name":
        orig = (repo / "SKILL.md").read_text(encoding="utf-8")
        (repo / "SKILL.md").write_text(
            orig.replace("name: appnwebsite-orchestrator", "name: Invalid_Skill_Name"),
            encoding="utf-8",
        )
    elif mutation == "oversized_or_html_description":
        orig = (repo / "SKILL.md").read_text(encoding="utf-8")
        bad_desc = "description: " + ("x" * 1050) + "<script>"
        lines = [bad_desc if l.startswith("description:") else l for l in orig.splitlines()]
        (repo / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    elif mutation == "stray_agents_md":
        (repo / "AGENTS.md").write_text("# Forbidden\n", encoding="utf-8")
    elif mutation == "stray_gemini_md":
        (repo / "skills" / "sample-child" / "GEMINI.md").write_text("# Forbidden\n", encoding="utf-8")
    elif mutation == "symlink_inside_repo":
        os.symlink(repo / "README.md", repo / "LINKED_README.md")
    elif mutation == "broken_relative_link":
        with (repo / "SKILL.md").open("a", encoding="utf-8") as fh:
            fh.write("\n- Broken: [Missing](references/does-not-exist.md)\n")
    elif mutation == "stub_r2_module_missing_pillar5":
        mod = repo / "references" / "00-spiral-governance" / "sample-module.md"
        mod.write_text(
            "# Stub\n\n## 1. Decision Framework\nTODO\n\n## 2. Step-by-Step Workflow\n1. Stub\n",
            encoding="utf-8",
        )
    elif mutation == "python_syntax_error_script":
        (repo / "scripts" / "broken.py").write_text("def broken(:\n    pass\n", encoding="utf-8")

    res = invoke_with_target(VALIDATE_SKILL, repo)
    assert_cli_rejected_cleanly(res, f"validate_skill:{mutation}")
    combined_low = (res.stdout + "\n" + res.stderr).lower()
    assert expected_diag_token in combined_low, (
        f"validate_skill.py failed on {mutation!r} without reporting {expected_diag_token!r}:\n{res.stdout}"
    )


@pytest.mark.m6
def test_validate_skill_require_all_active_passes_on_complete_repo() -> None:
    """validate_skill.py --require-all-active must pass on the complete repository at M6."""
    res = invoke_with_target(VALIDATE_SKILL, REPO_ROOT, extra_args=["--require-all-active"])
    assert res.returncode == 0, (
        f"validate_skill.py --require-all-active failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    )


@pytest.mark.m1
def test_query_skill_search_json_and_negative_boundaries() -> None:
    """query_skill.py must return compact search results, valid JSON, and safely reject traversal."""
    info = probe_cli_contract(QUERY_SKILL)
    flags = info["flags"]

    # Compact keyword search
    res = run_script(QUERY_SKILL, ["spiral"])
    assert res.returncode == 0, f"query_skill.py 'spiral' failed: {res.stderr}"
    assert res.stdout.strip(), "query_skill.py returned empty stdout for 'spiral'"
    assert len(res.stdout) < 15000, "query_skill.py output not compact (< 15 KB)"

    # JSON output if supported
    if "--json" in flags:
        jres = run_script(QUERY_SKILL, ["simplicity", "--json"])
        assert jres.returncode == 0, f"query_skill.py --json failed: {jres.stderr}"
        parsed = json.loads(jres.stdout)
        assert parsed, "query_skill.py --json returned empty structure"

    # Nonsense query must not crash with unhandled traceback
    nres = run_script(QUERY_SKILL, ["zxqv_nonexistent_token_999"])
    assert "Traceback (most recent call last)" not in nres.stderr

    # Path traversal safety
    tres = run_script(QUERY_SKILL, ["../../etc/passwd"])
    combined = tres.stdout + tres.stderr
    assert "root:x:0:0:" not in combined, "Path traversal leaked /etc/passwd!"
    assert "Traceback (most recent call last)" not in tres.stderr


@pytest.mark.exp
def test_audit_token_budget_runs_cleanly_and_flags_bloat(tmp_path: Path) -> None:
    """audit_token_budget.py must pass on clean isolated fixture and catch bloated SKILL.md."""
    info = probe_cli_contract(AUDIT_TOKEN_BUDGET)
    clean_repo = materialize_skill_fixture(tmp_path, include_child=True, dest_name="clean_repo")
    res = invoke_with_target(AUDIT_TOKEN_BUDGET, clean_repo)
    assert res.returncode == 0, (
        f"audit_token_budget.py failed on valid minimal fixture:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    )
    if "--json" in info["flags"]:
        jres = invoke_with_target(AUDIT_TOKEN_BUDGET, clean_repo, extra_args=["--json"])
        assert jres.returncode == 0
        payload = json.loads(jres.stdout)
        assert payload and payload.get("exit_code") == 0

    # Bloated SKILL.md (> 350 lines / > 20 KB) must fail or report over-budget cleanly
    bloated = materialize_skill_fixture(tmp_path, include_child=True, dest_name="bloated_repo")
    (bloated / "SKILL.md").write_text(
        (bloated / "SKILL.md").read_text(encoding="utf-8")
        + ("\nLine of duplicated bloat content exceeding lean router budget.\n" * 350),
        encoding="utf-8",
    )
    bres = invoke_with_target(AUDIT_TOKEN_BUDGET, bloated)
    combined_low = (bres.stdout + "\n" + bres.stderr).lower()
    assert "Traceback (most recent call last)" not in bres.stderr
    assert bres.returncode != 2, f"audit_token_budget.py returned rc=2 CLI usage error:\n{bres.stderr}"
    assert bres.returncode != 0 or re.search(
        r"\b(exceed(?:ed|s)?|over[- ]budget|fail(?:ed)?|bloat(?:ed)?|violation)\b",
        combined_low,
    ), f"audit_token_budget.py did not flag a 350+ line bloated SKILL.md:\n{bres.stdout}"


@pytest.mark.tier2
@pytest.mark.exp
def test_audit_token_budget_passes_on_full_repo() -> None:
    """audit_token_budget.py must pass cleanly on the full repository at M6."""
    info = probe_cli_contract(AUDIT_TOKEN_BUDGET)
    res = invoke_with_target(AUDIT_TOKEN_BUDGET, REPO_ROOT)
    assert res.returncode == 0, (
        f"audit_token_budget.py failed on repo:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    )
    if "--json" in info["flags"]:
        jres = invoke_with_target(AUDIT_TOKEN_BUDGET, REPO_ROOT, extra_args=["--json"])
        assert jres.returncode == 0
        assert json.loads(jres.stdout)


@pytest.mark.m1
def test_check_spiral_gates_passes_complete_and_rejects_incomplete(tmp_path: Path) -> None:
    """check_spiral_gates.py must pass complete Phase 3A + Simplicity + Risk workspace and fail incomplete/open-risk ones."""
    probe_cli_contract(CHECK_SPIRAL_GATES)

    complete_ws = tmp_path / "complete"
    shutil.copytree(FIXTURES_DIR / "spiral_gates" / "complete_workspace", complete_ws)
    ok = invoke_with_target(CHECK_SPIRAL_GATES, complete_ws)
    assert ok.returncode == 0, (
        f"check_spiral_gates.py failed on complete workspace:\nSTDOUT:\n{ok.stdout}\nSTDERR:\n{ok.stderr}"
    )

    for bad_name in ("missing_phase3a", "missing_simplicity"):
        bad_ws = tmp_path / bad_name
        shutil.copytree(FIXTURES_DIR / "spiral_gates" / bad_name, bad_ws)
        fail = invoke_with_target(CHECK_SPIRAL_GATES, bad_ws)
        assert_cli_rejected_cleanly(fail, f"check_spiral_gates:{bad_name}")

    # Negative: OPEN High/Critical risk in risk-spike-register.md must block Phase 3A
    open_risk_ws = tmp_path / "open_high_risk"
    shutil.copytree(FIXTURES_DIR / "spiral_gates" / "complete_workspace", open_risk_ws)
    rsk_path = open_risk_ws / "risk-spike-register.md"
    rsk_text = rsk_path.read_text(encoding="utf-8")
    rsk_path.write_text(
        rsk_text.replace("| MITIGATED |", "| OPEN |").replace(
            "Unmitigated High/Critical Risks**: 0", "Unmitigated High/Critical Risks**: 1"
        ),
        encoding="utf-8",
    )
    risk_fail = invoke_with_target(CHECK_SPIRAL_GATES, open_risk_ws)
    assert_cli_rejected_cleanly(risk_fail, "check_spiral_gates:open_high_risk")
    assert "RSK-001" in risk_fail.stdout or "OPEN" in risk_fail.stdout


def _run_contrast_pair(fg: str, bg: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    info = probe_cli_contract(CHECK_CONTRAST)
    flags = info["flags"]
    args = list(extra or [])
    if "--fg" in flags and "--bg" in flags:
        return run_script(CHECK_CONTRAST, ["--fg", fg, "--bg", bg, *args])
    if "--foreground" in flags and "--background" in flags:
        return run_script(CHECK_CONTRAST, ["--foreground", fg, "--background", bg, *args])
    return run_script(CHECK_CONTRAST, [fg, bg, *args])


@pytest.mark.m3
def test_check_contrast_wcag_boundaries_and_invalid_inputs() -> None:
    """check_contrast.py must enforce exact WCAG 2.1 AA/large/AAA contrast thresholds."""
    info = probe_cli_contract(CHECK_CONTRAST)
    flags = info["flags"]

    # High contrast PASS & same-color FAIL
    assert _run_contrast_pair("#000000", "#FFFFFF").returncode == 0
    assert_cli_rejected_cleanly(_run_contrast_pair("#000000", "#000000"), "contrast:same_color")

    # Normal text AA 4.5:1 exact boundary (#767676=4.54 PASS vs #777777=4.48 FAIL)
    assert _run_contrast_pair("#767676", "#FFFFFF").returncode == 0
    assert_cli_rejected_cleanly(_run_contrast_pair("#777777", "#FFFFFF"), "contrast:aa_fail")

    # Large text / UI 3.0:1 boundary (#949494=3.03 PASS vs #959595=2.99 FAIL)
    large_flag = pick_flag(flags, ("--large", "--large-text", "--ui"))
    if large_flag:
        assert _run_contrast_pair("#949494", "#FFFFFF", [large_flag]).returncode == 0
        assert_cli_rejected_cleanly(
            _run_contrast_pair("#959595", "#FFFFFF", [large_flag]), "contrast:large_fail"
        )
    elif "--size" in flags:
        assert _run_contrast_pair("#949494", "#FFFFFF", ["--size", "large"]).returncode == 0
        assert_cli_rejected_cleanly(
            _run_contrast_pair("#959595", "#FFFFFF", ["--size", "large"]), "contrast:size_large_fail"
        )
    elif "--level" in flags:
        aa_large = _run_contrast_pair("#949494", "#FFFFFF", ["--level", "AA-large"])
        assert aa_large.returncode == 0, (
            f"check_contrast.py --level AA-large failed for #949494/#FFFFFF: {aa_large.stderr}"
        )
        assert_cli_rejected_cleanly(
            _run_contrast_pair("#959595", "#FFFFFF", ["--level", "AA-large"]), "contrast:level_aa_large_fail"
        )
    else:
        pytest.fail(f"check_contrast.py --help missing 3.0:1 large-text/UI option; flags={sorted(flags)}")

    # AAA 7.0:1 boundary (#595959=7.00 PASS vs #5A5A5A=6.89 FAIL)
    aaa_flag = pick_flag(flags, ("--aaa",))
    if aaa_flag:
        assert _run_contrast_pair("#595959", "#FFFFFF", [aaa_flag]).returncode == 0
        assert_cli_rejected_cleanly(
            _run_contrast_pair("#5A5A5A", "#FFFFFF", [aaa_flag]), "contrast:aaa_fail"
        )
    elif "--level" in flags:
        assert _run_contrast_pair("#595959", "#FFFFFF", ["--level", "AAA"]).returncode == 0
        assert_cli_rejected_cleanly(
            _run_contrast_pair("#5A5A5A", "#FFFFFF", ["--level", "AAA"]), "contrast:level_aaa_fail"
        )

    # Invalid color input must fail cleanly without Python traceback
    bad = _run_contrast_pair("#GGGGGG", "#FFFFFF")
    assert_cli_rejected_cleanly(bad, "contrast:invalid_hex", allow_rc2_for_malformed=True)


@pytest.mark.m3
def test_check_anti_slop_flags_sloppy_and_passes_clean(tmp_path: Path) -> None:
    """check_anti_slop.py must catch banned fonts/icons/gradients/z-index/Lorem and pass clean UI + hero text gradient."""
    probe_cli_contract(CHECK_ANTI_SLOP)

    sloppy_dir = tmp_path / "sloppy"
    sloppy_dir.mkdir()
    for fname in ("sloppy_ui.tsx", "sloppy_styles.css"):
        shutil.copy2(FIXTURES_DIR / "ui_samples" / fname, sloppy_dir / fname)

    bad = invoke_with_target(CHECK_ANTI_SLOP, sloppy_dir)
    assert_cli_rejected_cleanly(bad, "anti_slop:sloppy_dir")

    # Individual slop rules check
    cases = {
        "banned_font": "body { font-family: 'Inter', sans-serif; }\n",
        "banned_icon": "import { ArrowRight } from 'lucide-react';\nexport const X = () => <ArrowRight />;\n",
        "arbitrary_gradient": ".card { background: linear-gradient(135deg, #6366f1, #a855f7); }\n",
        "z_index_9999": ".modal { z-index: 9999; }\n",
        "lorem_ipsum": "<p>Lorem ipsum dolor sit amet</p>\n",
    }
    for name, content in cases.items():
        ext = ".tsx" if "import " in content or "<p>" in content else ".css"
        fpath = tmp_path / f"{name}{ext}"
        fpath.write_text(content, encoding="utf-8")
        r = invoke_with_target(CHECK_ANTI_SLOP, fpath)
        assert_cli_rejected_cleanly(r, f"anti_slop:{name}")

    clean_dir = tmp_path / "clean"
    clean_dir.mkdir()
    for fname in ("clean_ui.tsx", "clean_styles.css"):
        shutil.copy2(FIXTURES_DIR / "ui_samples" / fname, clean_dir / fname)
    ok = invoke_with_target(CHECK_ANTI_SLOP, clean_dir)
    assert ok.returncode == 0, (
        f"check_anti_slop.py rejected clean fixture:\nSTDOUT:\n{ok.stdout}\nSTDERR:\n{ok.stderr}"
    )

    # Positive boundary: allowed hero text-only directional gradient (#FFFFFF -> #9B9B9B)
    hero_grad_dir = tmp_path / "hero_text_gradient"
    hero_grad_dir.mkdir()
    (hero_grad_dir / "hero.css").write_text(
        ".hero-title {\n"
        "  font-family: 'Space Grotesk', sans-serif;\n"
        "  background: linear-gradient(180deg, #FFFFFF 0%, #9B9B9B 100%);\n"
        "  -webkit-background-clip: text;\n"
        "  background-clip: text;\n"
        "  color: transparent;\n"
        "}\n",
        encoding="utf-8",
    )
    hero_ok = invoke_with_target(CHECK_ANTI_SLOP, hero_grad_dir)
    assert hero_ok.returncode == 0, (
        f"check_anti_slop.py wrongly rejected allowed hero text-only gradient:\nSTDOUT:\n{hero_ok.stdout}\nSTDERR:\n{hero_ok.stderr}"
    )


@pytest.mark.m3
def test_validate_tokens_dtcg_valid_and_negative_cases(tmp_path: Path) -> None:
    """validate_tokens.py must accept valid 3-tier DTCG JSON and reject missing/dangling/circular/invalid."""
    probe_cli_contract(VALIDATE_TOKENS)
    ui = FIXTURES_DIR / "ui_samples"

    ok = invoke_with_target(VALIDATE_TOKENS, ui / "tokens_valid.json")
    assert ok.returncode == 0, (
        f"validate_tokens.py rejected tokens_valid.json:\nSTDOUT:\n{ok.stdout}\nSTDERR:\n{ok.stderr}"
    )

    for bad_file in (
        "tokens_missing_value.json",
        "tokens_dangling_alias.json",
        "tokens_circular_alias.json",
    ):
        fail = invoke_with_target(VALIDATE_TOKENS, ui / bad_file)
        assert_cli_rejected_cleanly(fail, f"validate_tokens:{bad_file}")

    malformed = tmp_path / "malformed.json"
    shutil.copy2(ui / "tokens_invalid_syntax.json.txt", malformed)
    mfail = invoke_with_target(VALIDATE_TOKENS, malformed)
    assert_cli_rejected_cleanly(mfail, "validate_tokens:malformed", allow_rc2_for_malformed=True)


@pytest.mark.m3
def test_design_search_and_core_search_behavioral_and_negative_boundaries() -> None:
    """design_search.py and core_search.py must support valid queries and handle negative inputs cleanly."""
    d_info = probe_cli_contract(DESIGN_SEARCH)
    d_res = run_script(DESIGN_SEARCH, ["minimal developer saas", "--domain", "typography", "--json"])
    assert d_res.returncode == 0, f"design_search.py valid query failed: {d_res.stderr}"
    d_payload = json.loads(d_res.stdout)
    assert d_payload, "design_search.py --json returned empty payload"

    # Negative: unknown domain or nonsense query must not emit unhandled traceback
    bad_domain = run_script(DESIGN_SEARCH, ["saas", "--domain", "nonexistent_domain_xyz"])
    assert "Traceback (most recent call last)" not in bad_domain.stderr
    if "--domain" in d_info["flags"]:
        assert bad_domain.returncode != 0 or not bad_domain.stdout.strip() or "no " in bad_domain.stdout.lower()

    # core_search.py behavioral + negative
    c_info = probe_cli_contract(CORE_SEARCH)
    c_args = ["contrast typography"]
    if "--json" in c_info["flags"]:
        c_args.append("--json")
    c_res = run_script(CORE_SEARCH, c_args)
    assert c_res.returncode == 0, f"core_search.py valid query failed: {c_res.stderr}"
    assert c_res.stdout.strip(), "core_search.py returned empty output for valid query"
    if "--json" in c_info["flags"]:
        c_payload = json.loads(c_res.stdout)
        assert c_payload and c_payload.get("count", len(c_payload.get("results", []))) > 0
        assert c_payload.get("results"), "core_search.py --json returned empty results for real query"

    c_neg_args = ["zxqv_nonexistent_token_999"]
    if "--json" in c_info["flags"]:
        c_neg_args.append("--json")
    c_neg = run_script(CORE_SEARCH, c_neg_args)
    assert "Traceback (most recent call last)" not in c_neg.stderr
    assert c_neg.returncode == 0, f"core_search.py unknown token query failed: {c_neg.stderr}"
    if "--json" in c_info["flags"]:
        c_neg_payload = json.loads(c_neg.stdout)
        assert c_neg_payload.get("count") == 0, (
            f"Expected count == 0 for unknown token, got {c_neg_payload}"
        )
        assert c_neg_payload.get("results") == [], (
            f"Expected empty results for unknown token, got {c_neg_payload}"
        )

    c_bad_domain = run_script(CORE_SEARCH, ["saas", "--domain", "nonexistent_domain_xyz"])
    assert "Traceback (most recent call last)" not in c_bad_domain.stderr
    if "--domain" in c_info["flags"]:
        assert (
            c_bad_domain.returncode != 0
            or not c_bad_domain.stdout.strip()
            or "no " in c_bad_domain.stdout.lower()
        )


@pytest.mark.m4
def test_check_security_baseline_offline_and_catches_vulns(tmp_path: Path) -> None:
    """check_security_baseline.py must run offline without IDE daemon and flag OWASP defects."""
    probe_cli_contract(CHECK_SECURITY_BASELINE)
    empty_home = tmp_path / "empty_home"
    empty_home.mkdir()
    offline_env = {"SECURECODER_API_PORT": "", "HOME": str(empty_home)}

    vuln_dir = tmp_path / "vuln"
    vuln_dir.mkdir()
    for fname in ("vulnerable_handler.py", "vulnerable_client.tsx"):
        shutil.copy2(FIXTURES_DIR / "api_security_samples" / fname, vuln_dir / fname)

    bad = invoke_with_target(CHECK_SECURITY_BASELINE, vuln_dir, env=offline_env)
    assert_cli_rejected_cleanly(bad, "check_security_baseline:vuln")

    clean_dir = tmp_path / "clean_sec"
    clean_dir.mkdir()
    for fname in ("clean_handler.py", "clean_client.tsx"):
        shutil.copy2(FIXTURES_DIR / "api_security_samples" / fname, clean_dir / fname)

    ok = invoke_with_target(CHECK_SECURITY_BASELINE, clean_dir, env=offline_env)
    assert ok.returncode == 0, (
        f"check_security_baseline.py failed offline on clean sample:\nSTDOUT:\n{ok.stdout}\nSTDERR:\n{ok.stderr}"
    )
