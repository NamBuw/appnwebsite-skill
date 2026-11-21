"""Tier 1: Structural, Packaging, Frontmatter, Registry, Simplicity, Token-Efficiency & R2 Depth Tests."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

from conftest import (
    BANNED_FONTS,
    BANNED_ICONS,
    CHILD_SKILLS,
    MAX_SKILL_MD_BYTES,
    MAX_SKILL_MD_LINES,
    META_PLAN_REQUIRED_MODULES,
    MIN_R2_WORDS,
    MIN_UNIFORMITY_RATIO,
    PARENT_GOVERNANCE_MODULES,
    PARENT_SKILL_NAME,
    PARENT_TEMPLATES,
    PREFERRED_ICONS,
    REPO_ROOT,
    REQUIRED_BLACKBOX_TECHNIQUES,
    assert_r2_module_compliant,
    check_english_prose_only,
    get_registry_entries,
    validate_frontmatter_contract,
)

pytestmark = pytest.mark.tier1


def _repo_markdown_files() -> list[Path]:
    """Return all .md files inside the repo excluding tests/ and .git/."""
    files: list[Path] = []
    for p in sorted(REPO_ROOT.rglob("*.md")):
        rel_parts = p.relative_to(REPO_ROOT).parts
        if rel_parts and rel_parts[0] in {"tests", ".git"}:
            continue
        files.append(p)
    return files


@pytest.mark.m1
def test_root_skill_md_exists_and_no_stray_outside_skills() -> None:
    """Root SKILL.md must exist, and no SKILL.md may exist outside root or skills/<child>/."""
    root_skill = REPO_ROOT / "SKILL.md"
    assert root_skill.is_file(), f"Missing root Parent Orchestrator: {root_skill}"

    stray: list[str] = []
    for p in REPO_ROOT.rglob("SKILL.md"):
        rel = p.relative_to(REPO_ROOT)
        parts = rel.parts
        if parts[0] in {"tests", ".git"}:
            continue
        if rel == Path("SKILL.md"):
            continue
        if len(parts) == 3 and parts[0] == "skills":
            continue
        stray.append(str(rel))

    assert not stray, f"Stray SKILL.md files outside root or skills/<child>/: {stray}"


@pytest.mark.m6
def test_exact_12_skill_md_files_present() -> None:
    """Suite must contain exact 12 SKILL.md files (1 Parent + 11 Child Skills)."""
    found = {
        str(p.relative_to(REPO_ROOT))
        for p in REPO_ROOT.rglob("SKILL.md")
        if p.relative_to(REPO_ROOT).parts[0] not in {"tests", ".git"}
    }
    expected = {"SKILL.md"} | {f"skills/{name}/SKILL.md" for name, _ in CHILD_SKILLS}
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    assert not missing and not extra, (
        f"SKILL.md topology mismatch — missing: {missing}, extra: {extra}"
    )


@pytest.mark.m1
def test_parent_skill_frontmatter_contract() -> None:
    """Root SKILL.md must satisfy YAML frontmatter contract for appnwebsite-orchestrator."""
    root_skill = REPO_ROOT / "SKILL.md"
    assert root_skill.is_file(), f"Missing {root_skill}"
    validate_frontmatter_contract(root_skill, expected_name=PARENT_SKILL_NAME)


@pytest.mark.m1
def test_zero_agents_or_gemini_md() -> None:
    """Repository must contain zero AGENTS.md or GEMINI.md files."""
    hits = [
        str(p.relative_to(REPO_ROOT))
        for p in REPO_ROOT.rglob("*")
        if p.name in {"AGENTS.md", "GEMINI.md"}
        and p.relative_to(REPO_ROOT).parts[0] not in {"tests", ".git"}
    ]
    assert not hits, f"Forbidden AGENTS.md/GEMINI.md files found: {hits}"


@pytest.mark.m1
def test_zero_symlinks_in_repo() -> None:
    """Repository must contain zero symlinks (real files only)."""
    symlinks = [
        str(p.relative_to(REPO_ROOT))
        for p in REPO_ROOT.rglob("*")
        if p.is_symlink() and p.relative_to(REPO_ROOT).parts[0] != ".git"
    ]
    assert not symlinks, f"Symlinks are forbidden in repository: {symlinks}"


@pytest.mark.m1
def test_readme_and_license_present() -> None:
    """README.md (with install instructions) and LICENSE must exist and be non-empty."""
    readme = REPO_ROOT / "README.md"
    lic = REPO_ROOT / "LICENSE"
    assert readme.is_file() and readme.stat().st_size > 200, "README.md missing or too short"
    assert lic.is_file() and lic.stat().st_size > 100, "LICENSE missing or too short"
    readme_text = readme.read_text(encoding="utf-8")
    assert "MIT" in lic.read_text(encoding="utf-8"), "LICENSE must contain MIT license text"
    assert any(
        agent in readme_text.lower() for agent in ("antigravity", "claude", "codex", "cursor")
    ), "README.md must document multi-ecosystem installation"


@pytest.mark.m1
def test_english_prose_only_across_repo_markdown() -> None:
    """All repository markdown documentation prose must be English-only."""
    md_files = _repo_markdown_files()
    assert md_files, "No markdown documentation files found in repository"
    all_issues: list[str] = []
    for p in md_files:
        issues = check_english_prose_only(p.read_text(encoding="utf-8"))
        for issue in issues:
            all_issues.append(f"{p.relative_to(REPO_ROOT)}: {issue}")
    assert not all_issues, "Non-English prose detected:\n" + "\n".join(all_issues[:20])


@pytest.mark.m1
def test_parent_skill_md_lean_token_budget_and_lazy_loading() -> None:
    """Parent SKILL.md must be a lean progressive-disclosure router within token budget."""
    root_skill = REPO_ROOT / "SKILL.md"
    assert root_skill.is_file(), f"Missing {root_skill}"
    raw = root_skill.read_text(encoding="utf-8")
    lines = raw.splitlines()
    byte_len = len(raw.encode("utf-8"))

    assert len(lines) <= MAX_SKILL_MD_LINES, (
        f"SKILL.md exceeds lean router ceiling ({len(lines)} > {MAX_SKILL_MD_LINES} lines)"
    )
    assert byte_len <= MAX_SKILL_MD_BYTES, (
        f"SKILL.md exceeds byte ceiling ({byte_len} > {MAX_SKILL_MD_BYTES} bytes)"
    )

    lower = raw.lower()
    assert any(
        phrase in lower
        for phrase in ("never bulk-load", "never bulk load", "only the", "progressive disclosure", "lazy")
    ), "SKILL.md must state explicit Progressive Disclosure / active-stage-only loading rules"
    assert "registry.json" in raw, "SKILL.md must reference registry.json"
    assert "orchestration-protocol.md" in raw, "SKILL.md must reference orchestration-protocol.md"
    assert "query_skill.py" in raw, "SKILL.md must reference scripts/query_skill.py"


@pytest.mark.exp
def test_execution_mode_routing_and_anti_over_orchestration_guard() -> None:
    """Parent SKILL.md and registry.json must document /plan, /goal, /teamwork, Direct + guard."""
    root_skill = REPO_ROOT / "SKILL.md"
    reg_file = REPO_ROOT / "registry.json"
    assert root_skill.is_file() and reg_file.is_file()

    skill_text = root_skill.read_text(encoding="utf-8")
    reg_raw = reg_file.read_text(encoding="utf-8")
    combined_lower = (skill_text + "\n" + reg_raw).lower()

    for mode in ("/plan", "/goal", "/teamwork"):
        assert mode in skill_text, f"Parent SKILL.md missing execution mode {mode!r}"
        assert mode in reg_raw, f"registry.json missing execution mode {mode!r}"
    assert "direct" in combined_lower, "Execution Mode Routing must include 'Direct' mode"
    assert any(
        kw in combined_lower
        for kw in ("anti-over-orchestration", "over-orchestration", "simplest", "radical simplicity")
    ), "Execution Mode Routing must include Radical Simplicity / anti-over-orchestration guard"


@pytest.mark.m1
def test_spiral_q1_to_q4_and_phase3a_foundation_gate() -> None:
    """Parent Spiral governance must enforce Q1-Q4 quadrants and Phase 3A Foundation Gate."""
    spiral_doc = REPO_ROOT / "references" / "00-spiral-governance" / "spiral-lifecycle.md"
    gate_doc = REPO_ROOT / "references" / "00-spiral-governance" / "system-first-foundation-gate.md"
    assert spiral_doc.is_file(), f"Missing {spiral_doc}"
    assert gate_doc.is_file(), f"Missing {gate_doc}"

    spiral_text = spiral_doc.read_text(encoding="utf-8")
    gate_text = gate_doc.read_text(encoding="utf-8")
    combined = (spiral_text + "\n" + gate_text).lower()

    for q in ("q1", "q2", "q3", "q4"):
        assert q in combined, f"Spiral lifecycle missing quadrant {q.upper()}"
    assert "phase 3a" in combined, "Must enforce Phase 3A System-First Foundation Gate"
    for foundation_req in ("architecture", "data model", "contract", "adr", "skeleton"):
        assert foundation_req in combined, (
            f"Phase 3A Foundation Gate missing requirement: {foundation_req}"
        )


@pytest.mark.m1
def test_simplicity_gate_module_and_parent_templates() -> None:
    """Anti-Overengineering & Radical Simplicity protocol and 4 parent templates must exist."""
    simp_doc = (
        REPO_ROOT / "references" / "00-spiral-governance" / "anti-overengineering-simplicity-gate.md"
    )
    assert simp_doc.is_file(), f"Missing {simp_doc}"
    raw_text = simp_doc.read_text(encoding="utf-8")
    text = raw_text.lower()

    assert "simplest high-craft option" in text
    assert "complexity budget" in text
    assert "deletion" in text and "condensation" in text
    assert any(kw in text for kw in ("yagni", "premature abstraction"))
    assert "least code" in text or "ít nhất mà tốt nhất" in text or "minimal" in text

    for rel in PARENT_TEMPLATES:
        tpath = REPO_ROOT / rel
        assert tpath.is_file() and tpath.stat().st_size > 100, (
            f"Missing or empty parent template: {rel}"
        )


@pytest.mark.m1
@pytest.mark.parametrize("rel_path", PARENT_GOVERNANCE_MODULES)
def test_parent_governance_module_r2_depth(rel_path: str) -> None:
    """Every parent governance/orchestration module must pass R2 6-pillar compliance."""
    assert_r2_module_compliant(REPO_ROOT / rel_path, require_deletion_pass=True)


@pytest.mark.parametrize(
    ("child_name", "milestone"),
    [
        pytest.param(name, ms, marks=getattr(pytest.mark, ms), id=name)
        for name, ms in CHILD_SKILLS
    ],
)
def test_child_skill_standalone_and_r2_depth(child_name: str, milestone: str) -> None:
    """Every contracted Child Skill must exist, pass frontmatter/router checks, and pass R2 on all modules."""
    child_dir = REPO_ROOT / "skills" / child_name
    skill_md = child_dir / "SKILL.md"
    assert skill_md.is_file(), f"Missing child skill SKILL.md: {skill_md}"

    validate_frontmatter_contract(
        skill_md, expected_name=child_name, require_child_fields=True
    )
    raw = skill_md.read_text(encoding="utf-8")
    lines = raw.splitlines()
    assert len(lines) <= MAX_SKILL_MD_LINES, (
        f"{skill_md}: Child SKILL.md exceeds {MAX_SKILL_MD_LINES} lines ({len(lines)})"
    )
    assert len(raw.encode("utf-8")) <= MAX_SKILL_MD_BYTES, (
        f"{skill_md}: Child SKILL.md exceeds {MAX_SKILL_MD_BYTES} bytes"
    )

    refs_dir = child_dir / "references"
    assert refs_dir.is_dir(), f"Missing child references/ directory: {refs_dir}"
    ref_modules = sorted(refs_dir.rglob("*.md"))
    assert ref_modules, f"Child skill {child_name} has zero .md modules under references/"

    for mod in ref_modules:
        assert_r2_module_compliant(mod, require_deletion_pass=True)

    # Confirm child skill is registered in root registry.json (supports 'children' and 'skills')
    reg_path = REPO_ROOT / "registry.json"
    assert reg_path.is_file(), "Missing root registry.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    entries = get_registry_entries(reg)
    reg_ids = {entry.get("id") or entry.get("name") for entry in entries if isinstance(entry, dict)}
    assert child_name in reg_ids, f"Child skill {child_name!r} missing from root registry.json"


@pytest.mark.exp
@pytest.mark.parametrize("rel_path", META_PLAN_REQUIRED_MODULES)
def test_meta_plan_goal_teamwork_required_modules(rel_path: str) -> None:
    """EXP meta-plan-goal-teamwork must contain its 3 contracted R2 modules."""
    assert_r2_module_compliant(REPO_ROOT / rel_path, require_deletion_pass=True)


@pytest.mark.m4
def test_blackbox_testing_all_8_techniques_covered() -> None:
    """multi-layer-qa-testing must cover all 8 black-box techniques plus white-box & non-functional QA."""
    qa_refs = sorted((REPO_ROOT / "skills" / "multi-layer-qa-testing" / "references").rglob("*.md"))
    assert qa_refs, "Missing multi-layer-qa-testing reference modules"
    corpus = "\n".join(p.read_text(encoding="utf-8").lower() for p in qa_refs)

    missing = [
        label
        for label, aliases in REQUIRED_BLACKBOX_TECHNIQUES
        if not any(alias in corpus for alias in aliases)
    ]
    assert not missing, f"multi-layer-qa-testing missing black-box techniques: {missing}"

    # White-box / unit / integration / mutation & non-functional testing coverage
    for term_group in (
        ("unit",),
        ("integration",),
        ("mutation",),
        ("k6", "locust"),
        ("wcag 2.2", "wcag2.2"),
        ("chaos", "fault injection", "fault-injection"),
    ):
        assert any(t in corpus for t in term_group), (
            f"multi-layer-qa-testing missing white-box/non-functional coverage for {term_group}"
        )


@pytest.mark.m3
def test_anti_ai_slop_policy_declared_in_ui_design_craft() -> None:
    """ui-design-craft must declare banned fonts/icons, preferred icons, and hero text-only gradient rule."""
    ui_refs = sorted((REPO_ROOT / "skills" / "ui-design-craft" / "references").rglob("*.md"))
    assert ui_refs, "Missing ui-design-craft reference modules"
    corpus = "\n".join(p.read_text(encoding="utf-8") for p in ui_refs)
    corpus_lower = corpus.lower()

    for font in BANNED_FONTS:
        assert font in corpus, f"ui-design-craft references missing banned font rule for {font!r}"
    for icon in BANNED_ICONS:
        assert icon in corpus, f"ui-design-craft references missing banned icon rule for {icon!r}"
    for pref in PREFERRED_ICONS:
        assert pref in corpus, f"ui-design-craft references missing preferred icon {pref!r}"

    assert "flat" in corpus_lower and "gradient" in corpus_lower, (
        "ui-design-craft must declare flat-surface default and gradient discipline"
    )
    assert any(hx in corpus.upper() for hx in ("#9B9B9B", "#666666")) or "directional gradient" in corpus_lower, (
        "ui-design-craft must declare hero text-only directional gradient exception (#FFFFFF -> #9B9B9B / #000000 -> #666666)"
    )


@pytest.mark.m3
def test_figma_design_to_code_domain_coverage() -> None:
    """figma-design-to-code must cover Variables, Auto Layout, Code Connect, Figma MCP, and DTCG."""
    refs = sorted((REPO_ROOT / "skills" / "figma-design-to-code" / "references").rglob("*.md"))
    assert refs, "Missing figma-design-to-code reference modules"
    corpus = "\n".join(p.read_text(encoding="utf-8").lower() for p in refs)
    for term_group in (
        ("variables",),
        ("auto layout", "auto-layout"),
        ("code connect",),
        ("mcp",),
        ("dtcg", "style dictionary"),
    ):
        assert any(t in corpus for t in term_group), (
            f"figma-design-to-code missing required coverage for {term_group}"
        )


@pytest.mark.m3
def test_frontend_surfaces_skill_covers_all_6_surfaces() -> None:
    """frontend-surfaces-and-redesign must cover landing, SaaS web app, mobile, dashboard, design system, redesign."""
    refs = sorted((REPO_ROOT / "skills" / "frontend-surfaces-and-redesign" / "references").rglob("*.md"))
    assert refs, "Missing frontend-surfaces-and-redesign reference modules"
    corpus = "\n".join(p.read_text(encoding="utf-8").lower() for p in refs)
    for surface_group in (
        ("landing",),
        ("saas", "web app"),
        ("mobile", "expo", "swiftui", "flutter"),
        ("dashboard", "data visualization"),
        ("design system",),
        ("redesign",),
    ):
        assert any(t in corpus for t in surface_group), (
            f"frontend-surfaces-and-redesign missing surface coverage for {surface_group}"
        )


@pytest.mark.exp
def test_advanced_web_app_capabilities_domain_coverage() -> None:
    """advanced-web-app-capabilities must cover payments idempotency, AI prompt-injection, PWA/offline, and SEO/CWV."""
    refs = sorted((REPO_ROOT / "skills" / "advanced-web-app-capabilities" / "references").rglob("*.md"))
    assert refs, "Missing advanced-web-app-capabilities reference modules"
    corpus = "\n".join(p.read_text(encoding="utf-8").lower() for p in refs)
    for topic_group in (
        ("payment", "billing", "webhook"),
        ("idempoten",),
        ("prompt injection", "prompt-injection"),
        ("pwa", "offline"),
        ("seo",),
        ("core web vitals", "cwv"),
    ):
        assert any(t in corpus for t in topic_group), (
            f"advanced-web-app-capabilities missing required coverage for {topic_group}"
        )


@pytest.mark.m5
def test_source_coverage_inventory_and_json_cross_check() -> None:
    """classified-skills-inventory.json and source-coverage-inventory.md must cross-check cleanly."""
    inv_json_path = REPO_ROOT / "data" / "classified-skills-inventory.json"
    inv_md_path = REPO_ROOT / "references" / "source-coverage-inventory.md"
    assert inv_json_path.is_file(), f"Missing {inv_json_path}"
    assert inv_md_path.is_file(), f"Missing {inv_md_path}"

    data = json.loads(inv_json_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        records = None
        for key in ("skills", "records", "entries", "inventory", "local_skills"):
            if isinstance(data.get(key), list):
                records = list(data[key])
                break
        if records is not None:
            for extra_key in ("github_skills", "web_skills", "external_skills"):
                if isinstance(data.get(extra_key), list):
                    records.extend(data[extra_key])
    else:
        records = None

    assert isinstance(records, list) and len(records) >= 481, (
        f"Expected >= 481 classified skill records, got {len(records) if isinstance(records, list) else type(records)}"
    )

    relevant_names: set[str] = set()
    partial_names: set[str] = set()
    out_names: set[str] = set()
    all_names: set[str] = set()

    for rec in records:
        assert isinstance(rec, dict), "Each inventory entry must be a JSON object"
        raw_dir = str(rec.get("skill_dir") or rec.get("path") or "").rstrip("/")
        if raw_dir.endswith("/SKILL.md"):
            raw_dir = raw_dir[: -len("/SKILL.md")]
        fallback_name = Path(raw_dir).name if raw_dir else ""
        name = (
            rec.get("name")
            or (rec.get("frontmatter") or {}).get("name")
            or rec.get("id")
            or fallback_name
        )
        assert name, f"Inventory record missing skill name: {rec}"
        all_names.add(str(name))
        cls = str(rec.get("classification", "")).lower()
        assert rec.get("rationale"), f"Inventory record {name!r} missing rationale"
        if "partial" in cls:
            partial_names.add(str(name))
        elif "relevant" in cls:
            relevant_names.add(str(name))
        elif "out of scope" in cls or "excluded" in cls or "irrelevant" in cls:
            out_names.add(str(name))

    assert len(relevant_names) >= 306, f"Expected >= 306 unique Relevant skills, got {len(relevant_names)}"
    assert len(partial_names) >= 175, f"Expected >= 175 unique Partially Relevant skills, got {len(partial_names)}"
    assert len(out_names) >= 363, f"Expected >= 363 Out of Scope skills, got {len(out_names)}"
    assert len(all_names) >= 841, f"Expected >= 841 unique local+web skills, got {len(all_names)}"

    md_text = inv_md_path.read_text(encoding="utf-8")
    md_lower = md_text.lower()
    assert len(md_text.splitlines()) >= 150, "source-coverage-inventory.md must be >= 150 lines"
    assert "github.com" in md_lower or "http" in md_lower, (
        "source-coverage-inventory.md must document vetted GitHub/web sources with URLs"
    )
    assert "star" in md_lower or "★" in md_text, (
        "source-coverage-inventory.md must document GitHub star counts for curated external skills"
    )
    assert "license" in md_lower or "mit" in md_lower or "apache" in md_lower, (
        "source-coverage-inventory.md must document licenses for external curated skills"
    )
    assert sum(1 for dec in ("adopt", "merge", "reject") if dec in md_lower) >= 2, (
        "source-coverage-inventory.md must record explicit ADOPT/MERGE/REJECT curation decisions"
    )
    missing_in_md = sorted(n for n in relevant_names if n not in md_text)
    assert not missing_in_md, (
        f"Relevant skills missing from source-coverage-inventory.md (first 15): {missing_in_md[:15]}"
    )


@pytest.mark.m6
def test_uniform_r2_depth_across_entire_suite() -> None:
    """All domain modules across Parent + 11 Child Skills must have uniform exhaustive depth."""
    modules: list[Path] = [REPO_ROOT / rel for rel in PARENT_GOVERNANCE_MODULES]
    for child_name, _ in CHILD_SKILLS:
        child_refs = sorted((REPO_ROOT / "skills" / child_name / "references").rglob("*.md"))
        assert child_refs, f"Child skill {child_name} missing references/*.md"
        modules.extend(child_refs)

    word_counts: dict[str, int] = {}
    for mod in modules:
        assert mod.is_file(), f"Missing module for uniformity audit: {mod}"
        words = len(mod.read_text(encoding="utf-8").split())
        word_counts[str(mod.relative_to(REPO_ROOT))] = words

    assert len(word_counts) >= 17, f"Expected >= 17 total domain modules, got {len(word_counts)}"
    min_mod, min_words = min(word_counts.items(), key=lambda kv: kv[1])
    med_words = statistics.median(word_counts.values())

    assert min_words >= MIN_R2_WORDS, (
        f"Shallowest module {min_mod} has {min_words} words (< {MIN_R2_WORDS})"
    )
    assert min_words >= MIN_UNIFORMITY_RATIO * med_words, (
        f"Depth variance too high: {min_mod} has {min_words} words vs median {med_words} "
        f"(ratio {min_words / med_words:.2f} < {MIN_UNIFORMITY_RATIO})"
    )
