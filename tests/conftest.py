"""Shared pytest configuration, static contracts, oracles, and fixture helpers.

All tests are opaque-box and derived strictly from ORIGINAL_REQUEST.md and PROJECT.md.
No files outside tests/ are ever created or modified by this suite.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any, Sequence

import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures"

PARENT_SKILL_NAME = "appnwebsite-orchestrator"

PARENT_GOVERNANCE_MODULES: tuple[str, ...] = (
    "references/orchestration-protocol.md",
    "references/00-spiral-governance/spiral-lifecycle.md",
    "references/00-spiral-governance/system-first-foundation-gate.md",
    "references/00-spiral-governance/anti-overengineering-simplicity-gate.md",
    "references/00-spiral-governance/token-economy-and-progressive-disclosure.md",
    "references/00-spiral-governance/risk-prototyping-and-spikes.md",
)

PARENT_TEMPLATES: tuple[str, ...] = (
    "templates/spiral-charter.md",
    "templates/system-foundation-gate.md",
    "templates/simplicity-interrogation-record.md",
    "templates/risk-spike-register.md",
)

CHILD_SKILLS: tuple[tuple[str, str], ...] = (
    ("product-discovery-and-specs", "m2"),
    ("system-data-architecture", "m2"),
    ("fullstack-api-engineering", "m2"),
    ("ui-design-craft", "m3"),
    ("figma-design-to-code", "m3"),
    ("frontend-surfaces-and-redesign", "m3"),
    ("security-engineering", "m4"),
    ("multi-layer-qa-testing", "m4"),
    ("observability-sre-release", "m5"),
    ("advanced-web-app-capabilities", "exp"),
    ("meta-plan-goal-teamwork", "exp"),
)

CONTRACTED_SCRIPTS: tuple[tuple[str, str], ...] = (
    ("scripts/validate_skill.py", "m1"),
    ("scripts/query_skill.py", "m1"),
    ("scripts/check_spiral_gates.py", "m1"),
    ("scripts/audit_token_budget.py", "exp"),
    ("skills/ui-design-craft/scripts/design_search.py", "m3"),
    ("skills/ui-design-craft/scripts/core_search.py", "m3"),
    ("skills/ui-design-craft/scripts/check_contrast.py", "m3"),
    ("skills/ui-design-craft/scripts/check_anti_slop.py", "m3"),
    ("skills/ui-design-craft/scripts/validate_tokens.py", "m3"),
    ("skills/security-engineering/scripts/check_security_baseline.py", "m4"),
)

META_PLAN_REQUIRED_MODULES: tuple[str, ...] = (
    "skills/meta-plan-goal-teamwork/references/plan-first-execution.md",
    "skills/meta-plan-goal-teamwork/references/goal-completion-evidence-loop.md",
    "skills/meta-plan-goal-teamwork/references/multi-agent-teamwork-orchestration.md",
)

REQUIRED_BLACKBOX_TECHNIQUES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Equivalence Partitioning", ("equivalence partitioning", "equivalence class")),
    ("Boundary Value Analysis", ("boundary value analysis", "bva")),
    ("State Transition", ("state transition", "state-transition")),
    ("Decision Tables", ("decision table", "decision tables")),
    ("Pairwise / Combinatorial", ("pairwise", "combinatorial")),
    ("Exploratory Testing", ("exploratory",)),
    ("E2E / UAT", ("e2e", "end-to-end", "uat", "user acceptance")),
    ("API Contract Black-Box", ("api contract", "contract verification", "openapi")),
)

BANNED_FONTS: tuple[str, ...] = ("Inter", "Roboto", "Arial", "Open Sans", "Helvetica")
BANNED_ICONS: tuple[str, ...] = (
    "Lucide",
    "Feather",
    "Heroicons",
    "Material Icons",
    "Material Symbols",
)
PREFERRED_ICONS: tuple[str, ...] = ("Phosphor", "Solar", "Iconamoon")

ALLOWED_FRONTMATTER_KEYS: frozenset[str] = frozenset(
    {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
)

STUB_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bTODO\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\[placeholder\]", re.IGNORECASE),
    re.compile(r"\bLorem\s+ipsum\b", re.IGNORECASE),
    re.compile(r"\bcoming\s+soon\b", re.IGNORECASE),
)

GIT_EXPECTED_AUTHOR_NAME = "nambuw"
GIT_EXPECTED_AUTHOR_EMAIL = "trungnam0708qwert@gmail.com"
GIT_EXPECTED_REMOTE = "https://github.com/NamBuw/appnwebsite-skill.git"

MAX_SKILL_MD_LINES = 280
MAX_SKILL_MD_BYTES = 18432
MIN_R2_NON_EMPTY_LINES = 120
MIN_R2_WORDS = 800
MIN_UNIFORMITY_RATIO = 0.35
MIN_UNIQUE_LINE_RATIO = 0.55
MAX_IDENTICAL_NONTRIVIAL_LINES = 4

_FENCE_OPEN_RE = re.compile(r"^[ ]{0,7}(?:(?:[-+*]|\d+[.)])[ ]+)?(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^[ ]{0,7}(`{3,}|~{3,})[ \t]*$")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_VIETNAMESE_DIACRITIC_RE = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯ\u1ea0-\u1ef9]")
_MOTTO_ALLOWLIST_RE = re.compile(r"['\"“”]?ít nhất mà tốt nhất['\"“”]?", re.IGNORECASE)
_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
_SEPARATOR_LINE_RE = re.compile(r"^(?:[-*_]{3,}|\|?[\s:\-|]+\|?|`{3,}.*|~{3,}.*)$")


def pytest_configure(config: pytest.Config) -> None:
    """Register project markers locally in conftest without touching repo root."""
    markers = (
        "tier1: Structural, frontmatter, packaging, and R2 6-pillar depth checks",
        "tier2: Boundary, negative, and validator/CLI behavioral checks",
        "tier3: Cross-feature links, registry DAG, CSV integrity, and conflict resolution",
        "tier4: Real-world E2E scenario and git identity checks",
        "m1: Milestone M1 (Parent orchestrator, registry, governance, core scripts)",
        "m2: Milestone M2 (Product, architecture, fullstack child skills)",
        "m3: Milestone M3 (UI craft, Figma, surfaces child skills + data/scripts)",
        "m4: Milestone M4 (Security and multi-layer QA child skills + security script)",
        "m5: Milestone M5 (Observability/SRE child skill + source-coverage inventory)",
        "exp: Expansion branch (advanced-web-app-capabilities, meta-plan-goal-teamwork, audit_token_budget)",
        "m6: Final integration milestone",
        "self_check: Suite self-integrity and isolated fixture/oracle verification",
    )
    for spec in markers:
        config.addinivalue_line("markers", spec)


def strip_fenced_code_blocks(text: str) -> str:
    """Remove fenced code blocks via CommonMark-aware line state machine, preserving line numbers."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    out_lines: list[str] = []
    fence_char: str | None = None
    fence_len = 0

    for line in normalized.split("\n"):
        if fence_char is None:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                marker, info = m.group(1), m.group(2)
                if marker[0] == "`" and "`" in info:
                    out_lines.append(line)
                else:
                    fence_char = marker[0]
                    fence_len = len(marker)
                    out_lines.append("")
            else:
                out_lines.append(line)
        else:
            cm = _FENCE_CLOSE_RE.match(line)
            if cm and cm.group(1)[0] == fence_char and len(cm.group(1)) >= fence_len:
                fence_char = None
                fence_len = 0
            out_lines.append("")

    return "\n".join(out_lines)


def strip_inline_code(text: str) -> str:
    """Remove inline backtick spans (`...`, ``...``, ```...```), without crossing paragraph breaks."""
    res: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "`":
            ticks = 0
            while i + ticks < n and text[i + ticks] == "`":
                ticks += 1
            j = i + ticks
            found_end = -1
            while j < n:
                if text[j] == "\n":
                    k = j + 1
                    while k < n and text[k] in (" ", "\t"):
                        k += 1
                    if k < n and (
                        text[k] == "\n"
                        or (text[k] == "\r" and k + 1 < n and text[k + 1] == "\n")
                    ):
                        break
                if text[j] == "`":
                    run = 0
                    while j + run < n and text[j + run] == "`":
                        run += 1
                    if run == ticks:
                        found_end = j
                        break
                    j += run
                else:
                    j += 1
            if found_end != -1:
                span = text[i : found_end + ticks]
                res.append("\n" * span.count("\n"))
                i = found_end + ticks
                continue
            res.append(text[i : i + ticks])
            i += ticks
        else:
            res.append(text[i])
            i += 1
    return "".join(res)


def check_english_prose_only(text: str) -> list[str]:
    """Return non-English prose detections outside fenced/inline code and allowlisted motto."""
    cleaned = strip_inline_code(strip_fenced_code_blocks(text))
    cleaned = _MOTTO_ALLOWLIST_RE.sub("", cleaned)
    issues: list[str] = []
    for lineno, line in enumerate(cleaned.splitlines(), start=1):
        if _CJK_RE.search(line):
            issues.append(f"Line {lineno}: CJK characters in prose: {line.strip()[:80]}")
        if _VIETNAMESE_DIACRITIC_RE.search(line):
            issues.append(f"Line {lineno}: Vietnamese diacritics in prose: {line.strip()[:80]}")
    return issues


def parse_yaml_frontmatter(md_path: Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter strictly enforcing line-1 '---' with no BOM or comments."""
    raw = md_path.read_text(encoding="utf-8")
    if raw.startswith("\ufeff"):
        raise AssertionError(f"{md_path}: UTF-8 BOM before YAML frontmatter is forbidden")
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        first = lines[0] if lines else "<empty>"
        raise AssertionError(
            f"{md_path}: Line 1 must be '---' (no pre-frontmatter HTML comments), got: {first!r}"
        )
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise AssertionError(f"{md_path}: Unclosed YAML frontmatter")
    yaml_text = "\n".join(lines[1:end_idx])
    meta = yaml.safe_load(yaml_text)
    if not isinstance(meta, dict):
        raise AssertionError(f"{md_path}: Frontmatter must parse to a YAML mapping")
    body = "\n".join(lines[end_idx + 1 :])
    return meta, body


def validate_frontmatter_contract(
    md_path: Path,
    expected_name: str,
    require_child_fields: bool = False,
) -> dict[str, Any]:
    """Validate skill YAML frontmatter against packaging rules."""
    meta, _ = parse_yaml_frontmatter(md_path)
    extra_keys = set(meta.keys()) - ALLOWED_FRONTMATTER_KEYS
    assert not extra_keys, f"{md_path}: Disallowed frontmatter keys: {sorted(extra_keys)}"
    name = meta.get("name")
    assert isinstance(name, str) and name == expected_name, (
        f"{md_path}: Expected frontmatter name {expected_name!r}, got {name!r}"
    )
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) and len(name) <= 64, (
        f"{md_path}: Invalid hyphen-case name: {name!r}"
    )
    desc = meta.get("description")
    assert isinstance(desc, str) and desc.strip(), f"{md_path}: Missing non-empty description"
    assert len(desc) <= 1024, f"{md_path}: Description exceeds 1024 chars ({len(desc)})"
    assert "<" not in desc and ">" not in desc, (
        f"{md_path}: Description must not contain '<' or '>'"
    )
    if require_child_fields:
        assert meta.get("license"), f"{md_path}: Child skill must declare 'license'"
        assert isinstance(meta.get("metadata"), dict) and meta["metadata"], (
            f"{md_path}: Child skill must declare non-empty 'metadata' mapping"
        )
    return meta


_PILLAR_HEADER_RE = re.compile(r"^##\s+([1-6])\.\s+(.+?)\s*$", re.MULTILINE)
_EXPECTED_PILLAR_KEYWORDS: dict[int, tuple[str, ...]] = {
    1: ("decision framework",),
    2: ("step-by-step workflow",),
    3: ("reusable artifact", "template"),
    4: ("verification checklist",),
    5: ("hard quality gate",),
    6: ("anti-pattern",),
}


def parse_r2_pillars(md_text: str) -> dict[str, Any]:
    """Extract pillars 1..6 after stripping fenced code blocks."""
    prose = strip_fenced_code_blocks(md_text)
    matches = list(_PILLAR_HEADER_RE.finditer(prose))
    order = [int(m.group(1)) for m in matches]
    pillars: dict[int, dict[str, Any]] = {}
    for idx, match in enumerate(matches):
        num = int(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(prose)
        body = prose[start:end].strip()
        ne_lines = [line for line in body.splitlines() if line.strip()]
        pillars[num] = {
            "title": title,
            "body": body,
            "non_empty_lines": len(ne_lines),
            "words": len(body.split()),
        }
    return {"order": order, "pillars": pillars, "prose": prose}


def _extract_raw_pillar(raw_md: str, pillar_num: int) -> str:
    """Return raw markdown slice (including fenced code) for a real outside-fence pillar number."""
    normalized = raw_md.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    fence_char: str | None = None
    fence_len = 0
    pillar_hdr_re = re.compile(r"^##\s+([1-6])\.\s+.+$")
    headers: list[tuple[int, int]] = []

    for idx, line in enumerate(lines):
        if fence_char is None:
            m = _FENCE_OPEN_RE.match(line)
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                continue
            hm = pillar_hdr_re.match(line)
            if hm:
                headers.append((idx, int(hm.group(1))))
        else:
            cm = _FENCE_CLOSE_RE.match(line)
            if cm and cm.group(1)[0] == fence_char and len(cm.group(1)) >= fence_len:
                fence_char = None
                fence_len = 0

    for pos, (line_idx, pnum) in enumerate(headers):
        if pnum == pillar_num:
            end_idx = headers[pos + 1][0] if pos + 1 < len(headers) else len(lines)
            return "\n".join(lines[line_idx + 1 : end_idx])
    return ""


def assert_r2_module_compliant(
    md_path: Path, require_deletion_pass: bool = True
) -> dict[str, Any]:
    """Assert full R2 6-pillar compliance, anti-boilerplate uniqueness, and depth floors."""
    assert md_path.is_file(), f"Missing domain reference module: {md_path}"
    raw = md_path.read_text(encoding="utf-8")
    all_non_empty = [line for line in raw.splitlines() if line.strip()]
    total_words = len(raw.split())

    assert len(all_non_empty) >= MIN_R2_NON_EMPTY_LINES, (
        f"{md_path}: Expected >= {MIN_R2_NON_EMPTY_LINES} non-empty lines, got {len(all_non_empty)}"
    )
    assert total_words >= MIN_R2_WORDS, (
        f"{md_path}: Expected >= {MIN_R2_WORDS} words, got {total_words}"
    )

    # Anti-boilerplate repetition checks
    content_lines = [
        ln.strip()
        for ln in all_non_empty
        if not _SEPARATOR_LINE_RE.match(ln.strip())
    ]
    if content_lines:
        unique_ratio = len(set(content_lines)) / len(content_lines)
        assert unique_ratio >= MIN_UNIQUE_LINE_RATIO, (
            f"{md_path}: Excessive line repetition (unique ratio {unique_ratio:.2f} < {MIN_UNIQUE_LINE_RATIO})"
        )
        nontrivial_lines = [ln for ln in content_lines if len(ln) >= 20]
        if nontrivial_lines:
            top_line, top_count = Counter(nontrivial_lines).most_common(1)[0]
            assert top_count <= MAX_IDENTICAL_NONTRIVIAL_LINES, (
                f"{md_path}: Boilerplate repetition detected ({top_count}x > {MAX_IDENTICAL_NONTRIVIAL_LINES}): {top_line[:60]!r}"
            )

    parsed = parse_r2_pillars(raw)
    prose = parsed["prose"]
    prose_no_inline = strip_inline_code(prose)
    for pat in STUB_PATTERNS:
        hit = pat.search(prose_no_inline)
        assert hit is None, f"{md_path}: Stub marker {hit.group(0)!r} found outside code spans"

    assert parsed["order"] == [1, 2, 3, 4, 5, 6], (
        f"{md_path}: Expected 6 pillars in order [1, 2, 3, 4, 5, 6], got {parsed['order']}"
    )
    pillars = parsed["pillars"]
    for num, keywords in _EXPECTED_PILLAR_KEYWORDS.items():
        title_lower = pillars[num]["title"].lower()
        assert any(kw in title_lower for kw in keywords), (
            f"{md_path}: Pillar {num} title {pillars[num]['title']!r} missing expected keywords {keywords}"
        )

    # Pillar 1: Decision Framework
    p1 = pillars[1]
    assert p1["non_empty_lines"] >= 12 and p1["words"] >= 100, (
        f"{md_path}: Pillar 1 too thin ({p1['non_empty_lines']} lines, {p1['words']} words)"
    )
    p1_body = p1["body"]
    has_table_or_tree = (
        ("|" in p1_body and "---" in p1_body)
        or ("├" in p1_body)
        or ("└" in p1_body)
        or ("->" in p1_body)
    )
    assert has_table_or_tree, f"{md_path}: Pillar 1 must include a decision table or decision tree"
    assert re.search(r"\d", p1_body), f"{md_path}: Pillar 1 must include quantitative thresholds/numbers"
    p1_lower = p1_body.lower()
    assert any(
        kw in p1_lower
        for kw in ("simplest", "high-craft", "anti-overengineering", "simplicity", "yagni", "least code")
    ), f"{md_path}: Pillar 1 must include Simplest High-Craft / Anti-Overengineering guidance"

    # Pillar 2: Step-by-Step Workflow
    p2 = pillars[2]
    assert p2["non_empty_lines"] >= 15 and p2["words"] >= 120, (
        f"{md_path}: Pillar 2 too thin ({p2['non_empty_lines']} lines, {p2['words']} words)"
    )
    numbered_steps = re.findall(r"(?m)^\s*\d+\.\s+", p2["body"])
    assert len(numbered_steps) >= 3, (
        f"{md_path}: Pillar 2 needs >= 3 numbered steps, found {len(numbered_steps)}"
    )
    p2_lower = p2["body"].lower()
    assert any(kw in p2_lower for kw in ("input", "output", "owner", "role", "tool", "script")), (
        f"{md_path}: Pillar 2 must declare inputs/outputs, roles, or tool references"
    )
    if require_deletion_pass:
        has_deletion_pass = any(
            kw in p2_lower
            for kw in (
                "deletion",
                "condensation",
                "complexity budget",
                "least code",
                "condense",
                "simplification",
            )
        ) or bool(
            re.search(
                r"\bsimplify\s+(?:the\s+)?(?:architecture|design|code|component|stack)\b",
                p2_lower,
            )
            or re.search(
                r"\bdelete\s+(?:unnecessary|redundant|unused)\b",
                p2_lower,
            )
        )
        assert has_deletion_pass, (
            f"{md_path}: Pillar 2 must include Complexity Budget / Deletion/Condensation pass"
        )

    # Pillar 3: Reusable Artifact & Template
    p3 = pillars[3]
    assert p3["non_empty_lines"] >= 8, (
        f"{md_path}: Pillar 3 needs >= 8 non-empty lines, got {p3['non_empty_lines']}"
    )
    assert "templates/" in p3["body"], (
        f"{md_path}: Pillar 3 must link to a reusable template under templates/"
    )
    has_schema = ("|" in p3["body"] and "---" in p3["body"]) or bool(
        re.search(r"(?m)^\s*[-*]\s+`?[a-zA-Z0-9_]+`?", p3["body"])
    )
    assert has_schema, f"{md_path}: Pillar 3 must include a structured field-level schema/contract"

    # Pillar 4: Verification Checklist
    p4 = pillars[4]
    checklist_items = re.findall(r"(?m)^\s*-\s*\[\s\]\s+(.+)$", p4["body"])
    assert len(checklist_items) >= 5, (
        f"{md_path}: Pillar 4 needs >= 5 '- [ ]' checklist items, got {len(checklist_items)}"
    )
    short_items = [item for item in checklist_items if len(item.split()) < 4]
    assert not short_items, f"{md_path}: Pillar 4 checklist items < 4 words: {short_items}"

    # Pillar 5: Hard Quality Gate
    p5 = pillars[5]
    assert p5["non_empty_lines"] >= 6, (
        f"{md_path}: Pillar 5 needs >= 6 non-empty lines, got {p5['non_empty_lines']}"
    )
    assert re.search(r"\bPASS\b", p5["body"]) and re.search(r"\bFAIL\b", p5["body"]), (
        f"{md_path}: Pillar 5 must define explicit binary PASS and FAIL criteria (word-boundary)"
    )
    p5_raw_section = _extract_raw_pillar(raw, 5)
    has_command = ("```" in p5_raw_section) or ("~~~" in p5_raw_section) or bool(
        re.search(r"`[^`\n]+\s+[^`\n]+`", p5_raw_section)
    )
    assert has_command, f"{md_path}: Pillar 5 must include at least 1 executable CLI/check command"

    # Pillar 6: Anti-Patterns
    p6 = pillars[6]
    assert p6["non_empty_lines"] >= 8, (
        f"{md_path}: Pillar 6 needs >= 8 non-empty lines, got {p6['non_empty_lines']}"
    )
    table_rows = [
        line
        for line in p6["body"].splitlines()
        if line.strip().startswith("|")
        and "---" not in line
        and not line.lower().strip().startswith("| pattern")
    ]
    bullet_or_subheads = re.findall(r"(?m)^(?:\s*[-*]\s+|\s*###\s+)\S+", p6["body"])
    assert max(len(table_rows), len(bullet_or_subheads)) >= 3, (
        f"{md_path}: Pillar 6 needs >= 3 structured anti-patterns"
    )

    return {
        "path": str(md_path),
        "words": total_words,
        "non_empty_lines": len(all_non_empty),
    }


def wcag_relative_luminance(hex_color: str) -> float:
    """Independent WCAG 2.1 relative luminance oracle for #RRGGBB colors."""
    cleaned = hex_color.strip().lstrip("#")
    if len(cleaned) == 3:
        cleaned = "".join(ch * 2 for ch in cleaned)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", cleaned):
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    channels = []
    for idx in (0, 2, 4):
        srgb = int(cleaned[idx : idx + 2], 16) / 255.0
        lin = srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4
        channels.append(lin)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def wcag_contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Independent WCAG 2.1 contrast ratio oracle (1.0 .. 21.0)."""
    l1 = wcag_relative_luminance(fg_hex)
    l2 = wcag_relative_luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def get_registry_entries(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract child skill entries cleanly supporting both 'children' and 'skills' schemas."""
    assert isinstance(registry, dict), "registry.json must be a JSON object"
    if "children" in registry:
        raw_entries = registry.get("children")
        key_label = "children"
    elif "skills" in registry:
        raw_entries = registry.get("skills")
        key_label = "skills"
    else:
        raise AssertionError("registry.json must contain a 'children' or 'skills' list or mapping")

    if isinstance(raw_entries, dict):
        entries = [
            {"id": k, **(v if isinstance(v, dict) else {"value": v})}
            for k, v in raw_entries.items()
        ]
    elif isinstance(raw_entries, list):
        entries = raw_entries
    else:
        raise AssertionError(f"registry.json {key_label!r} must be a list or mapping")

    assert entries, f"registry.json {key_label!r} must be non-empty"
    return entries


def validate_registry_dag(
    registry: dict[str, Any], expected_child_names: Sequence[str] | None = None
) -> None:
    """Validate registry.json structure, required fields, parity, and cycle-free DAG."""
    entries = get_registry_entries(registry)
    required_keys = ("spiral_stages", "triggers", "depends_on", "inputs", "outputs")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        assert isinstance(entry, dict), f"Invalid skill entry in registry: {entry!r}"
        sid = entry.get("id") or entry.get("name")
        assert isinstance(sid, str) and sid, f"Registry entry missing id/name: {entry!r}"
        assert sid not in by_id, f"Duplicate skill id in registry.json: {sid!r}"
        for key in required_keys:
            assert key in entry, f"Registry entry {sid!r} missing required key {key!r}"
        assert (
            "estimated_tokens" in entry or "token_budget" in entry
        ), f"Registry entry {sid!r} missing 'estimated_tokens' / 'token_budget'"
        assert (
            "entry_script" in entry or "path" in entry
        ), f"Registry entry {sid!r} missing 'entry_script' / 'path'"
        assert isinstance(entry["depends_on"], list), f"{sid!r}: depends_on must be a list"
        by_id[sid] = entry

    if expected_child_names is not None:
        expected_set = set(expected_child_names)
        actual_set = set(by_id.keys())
        missing = sorted(expected_set - actual_set)
        extra = sorted(actual_set - expected_set)
        assert not missing and not extra, (
            f"registry.json child parity mismatch — missing: {missing}, extra: {extra}"
        )

    # Topological sort (Kahn's algorithm) for strict cycle-free DAG verification
    indegree: dict[str, int] = {sid: 0 for sid in by_id}
    adj: dict[str, list[str]] = {sid: [] for sid in by_id}
    for sid, entry in by_id.items():
        for dep in entry["depends_on"]:
            assert dep in by_id, f"Registry skill {sid!r} depends_on unknown skill {dep!r}"
            assert dep != sid, f"Registry skill {sid!r} has self-dependency"
            adj[dep].append(sid)
            indegree[sid] += 1

    queue = deque(sid for sid, deg in indegree.items() if deg == 0)
    visited = 0
    while queue:
        cur = queue.popleft()
        visited += 1
        for nxt in adj[cur]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    assert visited == len(by_id), "registry.json depends_on graph contains a cycle!"


def run_script(
    script_path: Path,
    args: Sequence[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    """Execute a Python script with sys.executable and return CompletedProcess."""
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(cwd or REPO_ROOT),
        env=run_env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def probe_cli_contract(script_path: Path) -> dict[str, Any]:
    """Verify script exists, supports --help cleanly, and parse documented flags."""
    assert script_path.is_file(), f"Missing contracted script: {script_path}"
    res = run_script(script_path, ["--help"])
    assert res.returncode == 0, (
        f"{script_path} --help exited {res.returncode}.\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    )
    help_text = res.stdout + "\n" + res.stderr
    assert help_text.strip(), f"{script_path} --help produced empty output"
    flags = set(re.findall(r"--[a-zA-Z0-9][a-zA-Z0-9-]*", help_text))
    return {"help_text": help_text, "flags": flags}


def pick_flag(flags: set[str], candidates: Sequence[str]) -> str | None:
    """Return the first matching documented CLI flag from candidates."""
    for cand in candidates:
        if cand in flags:
            return cand
    return None


def invoke_with_target(
    script: Path,
    target: Path,
    extra_args: Sequence[str] | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoke a CLI script passing target via documented directory/file flag or positional arg."""
    info = probe_cli_contract(script)
    flags = info["flags"]
    args = list(extra_args or [])
    if target.is_dir():
        flag = pick_flag(
            flags, ("--project-dir", "--root", "--dir", "--path", "--workspace", "--target")
        )
    else:
        flag = pick_flag(flags, ("--file", "--path", "--input", "--target"))

    if flag:
        res = run_script(script, [flag, str(target), *args], env=env)
        if res.returncode == 2 and "unrecognized arguments" in res.stderr:
            return run_script(script, [str(target), *args], env=env)
        return res
    return run_script(script, [str(target), *args], env=env)


def assert_cli_rejected_cleanly(
    res: subprocess.CompletedProcess[str],
    context: str,
    *,
    allow_rc2_for_malformed: bool = False,
) -> None:
    """Assert a negative CLI run failed semantically without argparse/traceback errors."""
    stderr_low = res.stderr.lower()
    assert "Traceback (most recent call last)" not in res.stderr, (
        f"{context}: unhandled Python traceback in stderr:\n{res.stderr}"
    )
    assert (
        "unrecognized arguments" not in stderr_low
        and "arguments are required" not in stderr_low
        and "invalid choice" not in stderr_low
    ), f"{context}: argparse usage error (rc={res.returncode}):\n{res.stderr}"
    assert res.returncode != 0, f"{context}: expected non-zero exit code, got 0\nSTDOUT:\n{res.stdout}"
    if not allow_rc2_for_malformed:
        assert res.returncode != 2, (
            f"{context}: exited with rc=2 (CLI usage error instead of validation failure):\n{res.stderr}"
        )


def materialize_skill_fixture(
    tmp_path: Path, include_child: bool = True, dest_name: str = "skill_repo"
) -> Path:
    """Copy valid_minimal_skill into tmp_path and materialize SKILL.md and registry.json."""
    src = FIXTURES_DIR / "valid_minimal_skill"
    dst = tmp_path / dest_name
    shutil.copytree(src, dst)

    root_sample = dst / "skill_sample.md"
    if root_sample.exists():
        root_sample.rename(dst / "SKILL.md")

    reg_sample = dst / "registry_sample.json"
    if reg_sample.exists():
        reg_sample.rename(dst / "registry.json")

    child_dir = dst / "skills" / "sample-child"
    if include_child:
        child_sample = child_dir / "skill_sample.md"
        if child_sample.exists():
            child_sample.rename(child_dir / "SKILL.md")
    else:
        if (dst / "skills").exists():
            shutil.rmtree(dst / "skills")
        if (dst / "registry.json").exists():
            reg = json.loads((dst / "registry.json").read_text(encoding="utf-8"))
            if "children" in reg and isinstance(reg["children"], list):
                reg["children"] = [
                    c for c in reg["children"] if (c.get("id") or c.get("name")) != "sample-child"
                ]
            elif "skills" in reg:
                reg["skills"] = []
            (dst / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")

    return dst


def extract_markdown_links(md_text: str) -> list[tuple[str, str]]:
    """Extract non-image relative markdown links [label](target) outside fences and inline code."""
    prose = strip_inline_code(strip_fenced_code_blocks(md_text))
    links: list[tuple[str, str]] = []
    for label, target in _LINK_RE.findall(prose):
        cleaned = target.strip("<>").strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned) or cleaned.startswith("mailto:"):
            continue
        links.append((label, cleaned))
    return links


def markdown_heading_slugs(md_text: str) -> set[str]:
    """Generate GitHub-style heading anchor slugs (preserving double hyphens from ' & ')."""
    prose = strip_fenced_code_blocks(md_text)
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for _, heading in _HEADING_RE.findall(prose):
        base = heading.strip().lower()
        base = re.sub(r"`([^`]*)`", r"\1", base)
        base = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", base)
        base = re.sub(r"[^\w\s-]", "", base)
        base = re.sub(r"\s", "-", base).strip("-")
        if not base:
            continue
        idx = counts.get(base, 0)
        counts[base] = idx + 1
        slugs.add(base if idx == 0 else f"{base}-{idx}")
    return slugs
