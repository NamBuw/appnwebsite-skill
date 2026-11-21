"""Tier 3: Cross-Feature Links, Standalone Isolation, Registry DAG, CSV Alignment & Conflict Tests."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from conftest import (
    BANNED_FONTS,
    BANNED_ICONS,
    CHILD_SKILLS,
    PARENT_GOVERNANCE_MODULES,
    PREFERRED_ICONS,
    REPO_ROOT,
    extract_markdown_links,
    get_registry_entries,
    markdown_heading_slugs,
    probe_cli_contract,
    run_script,
    strip_fenced_code_blocks,
    validate_registry_dag,
)

pytestmark = pytest.mark.tier3

UI_DATA_DIR = REPO_ROOT / "skills" / "ui-design-craft" / "data"
DESIGN_SEARCH = REPO_ROOT / "skills" / "ui-design-craft" / "scripts" / "design_search.py"
QUERY_SKILL = REPO_ROOT / "scripts" / "query_skill.py"


def _verify_markdown_links_within_boundary(
    md_files: list[Path], boundary_root: Path
) -> list[str]:
    """Verify every relative markdown link exists on disk, resolves inside boundary, and matches #fragment."""
    errors: list[str] = []
    heading_cache: dict[Path, set[str]] = {}

    for src in md_files:
        text = src.read_text(encoding="utf-8")
        for _, raw_target in extract_markdown_links(text):
            rel_part, _, fragment = raw_target.partition("#")
            if not rel_part:
                target_file = src
            else:
                target_file = (src.parent / rel_part).resolve()

            try:
                target_file.relative_to(boundary_root.resolve())
            except ValueError:
                errors.append(
                    f"{src.relative_to(REPO_ROOT)}: link {raw_target!r} escapes {boundary_root.relative_to(REPO_ROOT)}"
                )
                continue

            if not target_file.exists():
                errors.append(
                    f"{src.relative_to(REPO_ROOT)}: broken relative link {raw_target!r} -> {target_file}"
                )
                continue

            if fragment and target_file.is_file() and target_file.suffix.lower() == ".md":
                if target_file not in heading_cache:
                    heading_cache[target_file] = markdown_heading_slugs(
                        target_file.read_text(encoding="utf-8")
                    )
                slug = fragment.strip().lower()
                if slug not in heading_cache[target_file]:
                    errors.append(
                        f"{src.relative_to(REPO_ROOT)}: missing #{fragment} heading in {target_file.name}"
                    )
    return errors


@pytest.mark.m1
def test_registry_json_valid_and_cycle_free_at_m1() -> None:
    """Root registry.json must exist, parse as valid JSON, and form a strict DAG."""
    reg_path = REPO_ROOT / "registry.json"
    assert reg_path.is_file(), f"Missing {reg_path}"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    validate_registry_dag(reg)


@pytest.mark.m6
def test_registry_json_full_11_child_parity_paths_and_dag() -> None:
    """registry.json must match all 11 skills/*/ folders 1:1 with valid paths and strict DAG."""
    reg_path = REPO_ROOT / "registry.json"
    assert reg_path.is_file(), f"Missing {reg_path}"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))

    expected_names = [name for name, _ in CHILD_SKILLS]
    validate_registry_dag(reg, expected_child_names=expected_names)

    skills_dir = REPO_ROOT / "skills"
    disk_dirs = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    assert disk_dirs == sorted(expected_names), (
        f"skills/ directory mismatch: disk={disk_dirs}, expected={sorted(expected_names)}"
    )

    entries = get_registry_entries(reg)
    for entry in entries:
        sid = entry.get("id") or entry.get("name")
        skill_path = entry.get("path")
        if skill_path:
            target = REPO_ROOT / skill_path
            assert target.is_file() or (target.is_dir() and (target / "SKILL.md").is_file()), (
                f"registry.json path for {sid!r} must be a file or dir containing SKILL.md: {skill_path}"
            )
        entry_script = entry.get("entry_script")
        if entry_script:
            es_path = (REPO_ROOT / entry_script) if (REPO_ROOT / entry_script).exists() else (REPO_ROOT / (skill_path or "") / entry_script)
            assert es_path.is_file(), (
                f"registry.json entry_script for {sid!r} does not exist: {entry_script}"
            )


@pytest.mark.m1
def test_parent_relative_markdown_links_and_template_reachability() -> None:
    """All parent relative markdown links must resolve, and zero parent templates may be orphaned."""
    parent_md = [
        REPO_ROOT / "SKILL.md",
        REPO_ROOT / "README.md",
        *[REPO_ROOT / rel for rel in PARENT_GOVERNANCE_MODULES],
        *sorted((REPO_ROOT / "templates").glob("*.md")),
    ]
    existing_md = [p for p in parent_md if p.is_file()]
    assert existing_md, "No parent markdown files found"
    errors = _verify_markdown_links_within_boundary(existing_md, REPO_ROOT)
    assert not errors, "Broken parent markdown links:\n" + "\n".join(errors)

    # Zero orphan templates in root templates/
    corpus_targets: set[Path] = set()
    for src in [
        REPO_ROOT / "SKILL.md",
        REPO_ROOT / "README.md",
        *sorted((REPO_ROOT / "references").rglob("*.md")),
    ]:
        if src.is_file():
            for _, target in extract_markdown_links(src.read_text(encoding="utf-8")):
                rel_part, _, _ = target.partition("#")
                if rel_part:
                    corpus_targets.add((src.parent / rel_part).resolve())

    orphans = [
        str(t.relative_to(REPO_ROOT))
        for t in sorted((REPO_ROOT / "templates").rglob("*"))
        if t.is_file() and t.resolve() not in corpus_targets
    ]
    assert not orphans, f"Orphan root templates unreferenced by SKILL/README/references: {orphans}"


@pytest.mark.parametrize(
    ("child_name", "milestone"),
    [
        pytest.param(name, ms, marks=getattr(pytest.mark, ms), id=name)
        for name, ms in CHILD_SKILLS
    ],
)
def test_child_skill_standalone_link_isolation_and_no_orphan_templates(
    child_name: str, milestone: str
) -> None:
    """Every child skill's links must resolve strictly inside skills/<child>/ with zero orphan templates."""
    child_dir = REPO_ROOT / "skills" / child_name
    assert child_dir.is_dir(), f"Missing child skill dir: {child_dir}"
    child_mds = sorted(child_dir.rglob("*.md"))
    assert child_mds, f"No markdown files inside {child_dir}"

    errors = _verify_markdown_links_within_boundary(child_mds, child_dir)
    assert not errors, f"Child skill {child_name} failed standalone link isolation:\n" + "\n".join(errors)

    tdir = child_dir / "templates"
    assert tdir.is_dir(), f"Child skill {child_name} missing templates/ directory"
    template_files = [p for p in sorted(tdir.rglob("*")) if p.is_file()]
    assert template_files, f"Child skill {child_name} has zero files in templates/"

    referenced: set[Path] = set()
    for src in child_mds:
        for _, target in extract_markdown_links(src.read_text(encoding="utf-8")):
            rel_part, _, _ = target.partition("#")
            if rel_part:
                referenced.add((src.parent / rel_part).resolve())
        # Also allow inline backticked template path references inside SKILL.md / references
        raw = src.read_text(encoding="utf-8")
        for tf in template_files:
            if tf.name in raw:
                referenced.add(tf.resolve())

    orphans = [
        str(tf.relative_to(child_dir))
        for tf in template_files
        if tf.resolve() not in referenced
    ]
    assert not orphans, f"Child skill {child_name} has orphan templates: {orphans}"


@pytest.mark.m3
def test_ui_design_data_csvs_utf8_well_formed_and_aligned() -> None:
    """skills/ui-design-craft/data CSVs must be valid UTF-8, rectangular, and key-aligned."""
    assert UI_DATA_DIR.is_dir(), f"Missing UI data directory: {UI_DATA_DIR}"
    required_csvs = (
        "products.csv",
        "colors.csv",
        "ui-reasoning.csv",
        "styles.csv",
        "typography.csv",
        "google-fonts.csv",
        "ux-guidelines.csv",
        "landing.csv",
        "charts.csv",
        "icons.csv",
        "app-interface.csv",
        "react-performance.csv",
    )
    for fname in required_csvs:
        fpath = UI_DATA_DIR / fname
        assert fpath.is_file(), f"Missing required UI dataset: {fpath}"

    stacks_dir = UI_DATA_DIR / "stacks"
    assert stacks_dir.is_dir(), f"Missing stacks directory: {stacks_dir}"
    stack_csvs = sorted(stacks_dir.glob("*.csv"))
    assert len(stack_csvs) >= 16, f"Expected >= 16 stack CSVs, found {len(stack_csvs)}"

    parsed_tables: dict[str, list[list[str]]] = {}
    for csv_path in [UI_DATA_DIR / f for f in required_csvs] + stack_csvs:
        with csv_path.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
        assert len(rows) >= 2, f"{csv_path.name} has < 2 rows"
        header_len = len(rows[0])
        bad_rows = [idx + 1 for idx, r in enumerate(rows) if len(r) != header_len]
        assert not bad_rows, (
            f"{csv_path.name}: ragged CSV rows (expected {header_len} cols) at lines {bad_rows[:10]}"
        )
        parsed_tables[csv_path.name] = rows

    # Check threejs.csv 9-col schema specifically if present
    if "threejs.csv" in parsed_tables:
        assert len(parsed_tables["threejs.csv"][0]) >= 9

    # Check products.csv, colors.csv, ui-reasoning.csv >= 161 rows & aligned keys
    prod_rows = parsed_tables["products.csv"][1:]
    color_rows = parsed_tables["colors.csv"][1:]
    reason_rows = parsed_tables["ui-reasoning.csv"][1:]
    assert len(prod_rows) >= 161 and len(color_rows) >= 161 and len(reason_rows) >= 161

    prod_types = {r[1].strip().lower() for r in prod_rows if len(r) > 1}
    color_types = {r[1].strip().lower() for r in color_rows if len(r) > 1}
    assert prod_types == color_types, (
        f"products.csv and colors.csv Product Type mismatch: "
        f"only_prod={sorted(prod_types - color_types)[:5]}, only_color={sorted(color_types - prod_types)[:5]}"
    )

    # Check design.csv non-tabular aesthetic DNA prose blocks if present
    design_csv = UI_DATA_DIR / "design.csv"
    if design_csv.is_file():
        d_text = design_csv.read_text(encoding="utf-8")
        assert len(d_text.splitlines()) >= 500, "design.csv appears truncated"


def _extract_search_result_items(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("results", "items", "matches", "rows"):
            val = payload.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
        return [payload]
    return []


@pytest.mark.m3
def test_cross_skill_font_icon_conflict_resolution_in_csv_and_search() -> None:
    """typography.csv, icons.csv, and design_search.py must exclude banned fonts/icons by default."""
    typo_csv = UI_DATA_DIR / "typography.csv"
    icons_csv = UI_DATA_DIR / "icons.csv"
    assert typo_csv.is_file() and icons_csv.is_file()

    # Check typography.csv default rows exclude banned fonts
    with typo_csv.open(encoding="utf-8", newline="") as fh:
        typo_rows = list(csv.DictReader(fh))
    assert len(typo_rows) >= 20
    banned_font_re = re.compile(
        r"\b(?:" + "|".join(re.escape(f) for f in BANNED_FONTS) + r")\b",
        re.IGNORECASE,
    )
    active_banned_fonts = []
    for row in typo_rows:
        heading = row.get("Heading Font", "")
        body = row.get("Body Font", "")
        status = (row.get("Status") or row.get("Quarantine") or "").lower()
        if "banned" in status or "legacy" in status or "deprecated" in status:
            continue
        if banned_font_re.search(heading) or banned_font_re.search(body):
            active_banned_fonts.append((row.get("Font Pairing Name"), heading, body))
    assert not active_banned_fonts, (
        f"typography.csv still exposes banned default fonts in active rows: {active_banned_fonts[:10]}"
    )

    # Check icons.csv standardizes on Phosphor/Solar/Iconamoon and excludes banned icon libs
    with icons_csv.open(encoding="utf-8", newline="") as fh:
        icon_rows = list(csv.DictReader(fh))
    assert len(icon_rows) >= 20
    libs = {row.get("Library", "") for row in icon_rows}
    assert any(
        pref.lower() in lib.lower() for lib in libs for pref in PREFERRED_ICONS
    ), f"icons.csv missing preferred icon libraries {PREFERRED_ICONS}; found {sorted(libs)}"

    banned_icon_re = re.compile(
        r"\b(?:" + "|".join(re.escape(i) for i in BANNED_ICONS) + r")\b",
        re.IGNORECASE,
    )
    active_banned_icons = [
        row.get("Library")
        for row in icon_rows
        if banned_icon_re.search(row.get("Library", ""))
        and "banned" not in (row.get("Status") or "").lower()
    ]
    assert not active_banned_icons, (
        f"icons.csv still contains banned icon libraries: {sorted(set(active_banned_icons))}"
    )

    # Execute design_search.py across multiple domains & stacks, checking actual font/icon fields (not Notes prose)
    probe_cli_contract(DESIGN_SEARCH)
    for domain, query in (
        ("typography", "modern developer saas"),
        ("icons", "dashboard navigation"),
        ("style", "minimal dark developer"),
        ("landing", "b2b saas analytics"),
    ):
        res = run_script(DESIGN_SEARCH, [query, "--domain", domain, "--json"])
        assert res.returncode == 0, f"design_search.py failed ({domain}): {res.stderr}"
        payload = json.loads(res.stdout)
        items = _extract_search_result_items(payload)
        assert items, f"design_search.py returned empty results for {domain}"
        if domain == "typography":
            for item in items:
                font_vals = [
                    str(v)
                    for k, v in item.items()
                    if any(tok in k.lower() for tok in ("heading", "body", "font", "pairing"))
                    and "note" not in k.lower()
                ]
                assert not any(banned_font_re.search(v) for v in font_vals), (
                    f"design_search.py typography emitted banned font in {item}"
                )
        elif domain == "icons":
            for item in items:
                lib_vals = [
                    str(v)
                    for k, v in item.items()
                    if any(tok in k.lower() for tok in ("library", "icon", "package", "name"))
                    and "note" not in k.lower()
                ]
                assert not any(banned_icon_re.search(v) for v in lib_vals), (
                    f"design_search.py icons emitted banned icon library in {item}"
                )

    for stack in ("nextjs", "react", "shadcn", "html-tailwind", "flutter", "swiftui"):
        sres = run_script(DESIGN_SEARCH, ["accessibility performance", "--stack", stack, "--json"])
        assert sres.returncode == 0, f"design_search.py failed on stack {stack}: {sres.stderr}"
        assert json.loads(sres.stdout).get("results"), f"Empty results for stack {stack}"


@pytest.mark.m4
def test_security_skill_vendor_neutral_without_ide_daemon_requirement() -> None:
    """security-engineering modules must specify vendor-neutral CLI tools as primary path."""
    sec_refs = sorted((REPO_ROOT / "skills" / "security-engineering" / "references").rglob("*.md"))
    assert sec_refs, "Missing security-engineering references"
    corpus = "\n".join(p.read_text(encoding="utf-8").lower() for p in sec_refs)
    for cli in ("semgrep", "bandit", "osv-scanner", "gitleaks"):
        assert cli in corpus, f"security-engineering missing vendor-neutral CLI {cli!r}"


@pytest.mark.m6
def test_token_efficiency_no_bulk_duplication_and_query_discoverability() -> None:
    """Parent SKILL.md must stay compact without bulk-copying references, and query_skill finds every child."""
    skill_md = REPO_ROOT / "SKILL.md"
    assert skill_md.is_file()
    skill_prose = strip_fenced_code_blocks(skill_md.read_text(encoding="utf-8"))
    skill_lines = [l.strip() for l in skill_prose.splitlines() if len(l.strip()) >= 35]

    # Check zero >= 5 consecutive identical prose lines copied from reference modules (including nested subdirs)
    ref_files = [
        *[REPO_ROOT / rel for rel in PARENT_GOVERNANCE_MODULES],
        *[
            p
            for p in sorted((REPO_ROOT / "skills").rglob("*.md"))
            if "references" in p.parts
        ],
    ]
    for rf in ref_files:
        if not rf.is_file():
            continue
        rtext = strip_fenced_code_blocks(rf.read_text(encoding="utf-8"))
        for idx in range(max(0, len(skill_lines) - 4)):
            block = "\n".join(skill_lines[idx : idx + 5])
            if block in rtext:
                pytest.fail(
                    f"SKILL.md duplicates >= 5 prose lines verbatim from {rf.relative_to(REPO_ROOT)}"
                )

    # Every contracted child skill must be discoverable via query_skill.py
    probe_cli_contract(QUERY_SKILL)
    for child_name, _ in CHILD_SKILLS:
        qres = run_script(QUERY_SKILL, [child_name])
        assert qres.returncode == 0 and qres.stdout.strip(), (
            f"query_skill.py could not discover child skill {child_name!r}"
        )
