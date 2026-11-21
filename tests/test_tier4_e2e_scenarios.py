"""Tier 4: Real-World End-to-End Scenarios (a)-(e)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import (
    BANNED_FONTS,
    BANNED_ICONS,
    FIXTURES_DIR,
    GIT_EXPECTED_AUTHOR_EMAIL,
    GIT_EXPECTED_AUTHOR_NAME,
    GIT_EXPECTED_REMOTE,
    REPO_ROOT,
    assert_cli_rejected_cleanly,
    get_registry_entries,
    invoke_with_target,
    probe_cli_contract,
    run_script,
)

pytestmark = pytest.mark.tier4

QUERY_SKILL = REPO_ROOT / "scripts" / "query_skill.py"
CHECK_SPIRAL_GATES = REPO_ROOT / "scripts" / "check_spiral_gates.py"
AUDIT_TOKEN_BUDGET = REPO_ROOT / "scripts" / "audit_token_budget.py"

UI_SCRIPTS = REPO_ROOT / "skills" / "ui-design-craft" / "scripts"
DESIGN_SEARCH = UI_SCRIPTS / "design_search.py"
CHECK_CONTRAST = UI_SCRIPTS / "check_contrast.py"
CHECK_ANTI_SLOP = UI_SCRIPTS / "check_anti_slop.py"
VALIDATE_TOKENS = UI_SCRIPTS / "validate_tokens.py"

CHECK_SECURITY = (
    REPO_ROOT / "skills" / "security-engineering" / "scripts" / "check_security_baseline.py"
)


@pytest.mark.m6
def test_e2e_scenario_a_greenfield_saas_spiral_and_simplicity(tmp_path: Path) -> None:
    """Scenario (a): Registry routing + query_skill + Phase 3A + Simplicity + Token Budget."""
    reg = json.loads((REPO_ROOT / "registry.json").read_text(encoding="utf-8"))
    entries = get_registry_entries(reg)
    by_id = {(e.get("id") or e.get("name")): e for e in entries}
    assert "product-discovery-and-specs" in by_id
    assert "system-data-architecture" in by_id

    for topic in ("spiral", "phase 3a", "simplicity"):
        qres = run_script(QUERY_SKILL, [topic])
        assert qres.returncode == 0 and qres.stdout.strip(), f"query_skill failed for {topic!r}"

    ws = tmp_path / "pulsemetrics_saas"
    shutil.copytree(FIXTURES_DIR / "spiral_gates" / "complete_workspace", ws)
    ok = invoke_with_target(CHECK_SPIRAL_GATES, ws)
    assert ok.returncode == 0, f"check_spiral_gates failed on complete workspace:\n{ok.stdout}\n{ok.stderr}"

    # Removing Simplicity Interrogation Record must block Q3 gate progression
    (ws / "simplicity-interrogation-record.md").unlink()
    fail = invoke_with_target(CHECK_SPIRAL_GATES, ws)
    assert_cli_rejected_cleanly(fail, "scenario_a:missing_simplicity")

    # Token budget profiler passes on the suite
    budget_ok = invoke_with_target(AUDIT_TOKEN_BUDGET, REPO_ROOT)
    assert budget_ok.returncode == 0, (
        f"audit_token_budget.py failed on repo:\n{budget_ok.stdout}\n{budget_ok.stderr}"
    )


@pytest.mark.m3
def test_e2e_scenario_b_landing_page_design_system_contrast_and_antislop(
    tmp_path: Path,
) -> None:
    """Scenario (b): design_search --design-system --persist -> MASTER.md + contrast + anti-slop."""
    probe_cli_contract(DESIGN_SEARCH)
    res = run_script(
        DESIGN_SEARCH,
        [
            "B2B SaaS developer analytics landing page",
            "--design-system",
            "-p",
            "PulseMetrics",
            "-f",
            "markdown",
            "--persist",
            "--page",
            "pricing",
            "-o",
            str(tmp_path),
        ],
    )
    assert res.returncode == 0, f"design_search --design-system failed:\n{res.stderr}"

    master_files = list(tmp_path.rglob("MASTER.md"))
    assert master_files, f"Expected persisted MASTER.md under {tmp_path}"
    master_text = master_files[0].read_text(encoding="utf-8")
    assert len(master_text.strip()) >= 200

    page_files = list(tmp_path.rglob("pricing.md"))
    assert page_files, f"Expected persisted pages/pricing.md under {tmp_path}"

    banned_re = re.compile(
        r"\b(?:" + "|".join(re.escape(x) for x in (*BANNED_FONTS, *BANNED_ICONS)) + r")\b",
        re.IGNORECASE,
    )
    assert not banned_re.search(master_text), (
        f"Persisted MASTER.md emitted banned default font/icon: {banned_re.findall(master_text)}"
    )

    # Validate contrast of clean dark SaaS palette and clean UI against anti-slop
    c_info = probe_cli_contract(CHECK_CONTRAST)
    if "--fg" in c_info["flags"] and "--bg" in c_info["flags"]:
        cres = run_script(CHECK_CONTRAST, ["--fg", "#FAFAFA", "--bg", "#09090B"])
    else:
        cres = run_script(CHECK_CONTRAST, ["#FAFAFA", "#09090B"])
    assert cres.returncode == 0

    clean_dir = tmp_path / "clean_landing"
    clean_dir.mkdir()
    shutil.copy2(FIXTURES_DIR / "ui_samples" / "clean_ui.tsx", clean_dir / "Hero.tsx")
    shutil.copy2(FIXTURES_DIR / "ui_samples" / "clean_styles.css", clean_dir / "styles.css")
    assert invoke_with_target(CHECK_ANTI_SLOP, clean_dir).returncode == 0


@pytest.mark.m3
def test_e2e_scenario_c_ui_redesign_audit_and_dtcg_tokens(tmp_path: Path) -> None:
    """Scenario (c): Legacy sloppy UI + broken tokens FAIL all 3 checks -> remediated PASS all 3."""
    before_dir = tmp_path / "before_ui"
    before_dir.mkdir()
    shutil.copy2(FIXTURES_DIR / "ui_samples" / "sloppy_ui.tsx", before_dir / "Hero.tsx")
    shutil.copy2(FIXTURES_DIR / "ui_samples" / "sloppy_styles.css", before_dir / "styles.css")

    assert_cli_rejected_cleanly(invoke_with_target(CHECK_ANTI_SLOP, before_dir), "scenario_c:anti_slop")
    assert_cli_rejected_cleanly(
        invoke_with_target(VALIDATE_TOKENS, FIXTURES_DIR / "ui_samples" / "tokens_dangling_alias.json"),
        "scenario_c:tokens_dangling",
    )

    c_info = probe_cli_contract(CHECK_CONTRAST)
    if "--fg" in c_info["flags"] and "--bg" in c_info["flags"]:
        assert_cli_rejected_cleanly(
            run_script(CHECK_CONTRAST, ["--fg", "#777777", "--bg", "#FFFFFF"]),
            "scenario_c:contrast_fail",
        )
        assert run_script(CHECK_CONTRAST, ["--fg", "#FAFAFA", "--bg", "#09090B"]).returncode == 0
    else:
        assert_cli_rejected_cleanly(
            run_script(CHECK_CONTRAST, ["#777777", "#FFFFFF"]),
            "scenario_c:contrast_fail",
        )
        assert run_script(CHECK_CONTRAST, ["#FAFAFA", "#09090B"]).returncode == 0

    after_dir = tmp_path / "after_ui"
    after_dir.mkdir()
    shutil.copy2(FIXTURES_DIR / "ui_samples" / "clean_ui.tsx", after_dir / "Hero.tsx")
    shutil.copy2(FIXTURES_DIR / "ui_samples" / "clean_styles.css", after_dir / "styles.css")

    assert invoke_with_target(CHECK_ANTI_SLOP, after_dir).returncode == 0
    assert invoke_with_target(
        VALIDATE_TOKENS, FIXTURES_DIR / "ui_samples" / "tokens_valid.json"
    ).returncode == 0


@pytest.mark.m4
def test_e2e_scenario_d_api_security_and_blackbox_qa_gates(tmp_path: Path) -> None:
    """Scenario (d): Offline security gate catches vulnerable API -> passes hardened + QA templates."""
    sec_templates = list((REPO_ROOT / "skills" / "security-engineering" / "templates").glob("*"))
    qa_templates = list((REPO_ROOT / "skills" / "multi-layer-qa-testing" / "templates").glob("*"))
    assert sec_templates, "security-engineering missing templates/"
    assert qa_templates, "multi-layer-qa-testing missing templates/"

    empty_home = tmp_path / "empty_home"
    empty_home.mkdir()
    offline_env = {"SECURECODER_API_PORT": "", "HOME": str(empty_home)}

    vuln_dir = tmp_path / "api_vuln"
    vuln_dir.mkdir()
    shutil.copy2(FIXTURES_DIR / "api_security_samples" / "vulnerable_handler.py", vuln_dir / "handler.py")
    shutil.copy2(FIXTURES_DIR / "api_security_samples" / "vulnerable_client.tsx", vuln_dir / "client.tsx")
    assert_cli_rejected_cleanly(
        invoke_with_target(CHECK_SECURITY, vuln_dir, env=offline_env),
        "scenario_d:security_vuln",
    )

    clean_dir = tmp_path / "api_clean"
    clean_dir.mkdir()
    shutil.copy2(FIXTURES_DIR / "api_security_samples" / "clean_handler.py", clean_dir / "handler.py")
    shutil.copy2(FIXTURES_DIR / "api_security_samples" / "clean_client.tsx", clean_dir / "client.tsx")
    assert invoke_with_target(CHECK_SECURITY, clean_dir, env=offline_env).returncode == 0


@pytest.mark.m1
def test_e2e_scenario_e_git_repository_and_commit_identity() -> None:
    """Scenario (e): Verify git repo on main, HTTPS origin, and 100% nambuw commit identity."""
    def _git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True,
            text=True,
            timeout=15,
        )

    inside = _git("rev-parse", "--is-inside-work-tree")
    assert inside.returncode == 0 and inside.stdout.strip() == "true", (
        f"Repository not initialized as git work tree: {inside.stderr}"
    )

    branch = _git("branch", "--show-current")
    assert branch.returncode == 0 and branch.stdout.strip() == "main", (
        f"Expected current branch 'main', got {branch.stdout.strip()!r}"
    )

    origin = _git("remote", "get-url", "origin")
    assert origin.returncode == 0 and origin.stdout.strip() == GIT_EXPECTED_REMOTE, (
        f"Expected origin {GIT_EXPECTED_REMOTE!r}, got {origin.stdout.strip()!r}"
    )

    cfg_name = _git("config", "--local", "user.name")
    cfg_email = _git("config", "--local", "user.email")
    assert cfg_name.returncode == 0 and cfg_name.stdout.strip() == GIT_EXPECTED_AUTHOR_NAME
    assert cfg_email.returncode == 0 and cfg_email.stdout.strip() == GIT_EXPECTED_AUTHOR_EMAIL

    log = _git("log", "--format=%H|%an|%ae|%cn|%ce")
    assert log.returncode == 0 and log.stdout.strip(), "Git repository has zero commits"
    bad_commits: list[str] = []
    for line in log.stdout.strip().splitlines():
        sha, an, ae, cn, ce = line.split("|", 4)
        if not (
            an == GIT_EXPECTED_AUTHOR_NAME
            and ae == GIT_EXPECTED_AUTHOR_EMAIL
            and cn == GIT_EXPECTED_AUTHOR_NAME
            and ce == GIT_EXPECTED_AUTHOR_EMAIL
        ):
            bad_commits.append(f"{sha}: author={an} <{ae}>, committer={cn} <{ce}>")
    assert not bad_commits, f"Commits with wrong identity:\n" + "\n".join(bad_commits)
