#!/usr/bin/env python3
"""Suite-aware hierarchical validator for appnwebsite-skill (Python 3 stdlib only).

Validates Parent SKILL.md, standalone Child Skills under skills/*, registry.json parity,
zero AGENTS.md/GEMINI.md, zero symlinks, relative Markdown links & anchors, script/JSON syntax,
and R2 6-Pillar reference module uniformity.
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache"}
R2_PILLARS = [
    (1, re.compile(r"^##\s+1\.\s+Decision\s+Framework\b")),
    (2, re.compile(r"^##\s+2\.\s+Step-by-Step\s+Workflow\b")),
    (3, re.compile(r"^##\s+3\.\s+Reusable\s+Artifact\s+(?:&|and)\s+Template\b")),
    (4, re.compile(r"^##\s+4\.\s+Verification\s+Checklist\b")),
    (5, re.compile(r"^##\s+5\.\s+Hard\s+Quality\s+Gate\b")),
    (6, re.compile(r"^##\s+6\.\s+Anti-Patterns\b")),
]
REQUIRED_CHILD_FIELDS = {
    "id",
    "name",
    "path",
    "milestone",
    "spiral_stages",
    "surfaces",
    "triggers",
    "depends_on",
    "inputs",
    "outputs",
    "estimated_tokens",
    "entry_script",
    "status",
}
REQUIRED_CORE_CHILDREN = {
    "product-discovery-and-specs",
    "system-data-architecture",
    "fullstack-api-engineering",
    "ui-design-craft",
    "figma-design-to-code",
    "frontend-surfaces-and-redesign",
    "security-engineering",
    "multi-layer-qa-testing",
    "observability-sre-release",
    "advanced-web-app-capabilities",
    "meta-plan-goal-teamwork",
}


def _unquote(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and (
        (val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")
    ):
        inner = val[1:-1]
        if val[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
        else:
            inner = inner.replace("''", "'")
        return inner
    return val


def parse_yaml_frontmatter_stdlib(fm_text: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Strict pure-stdlib subset YAML parser for SKILL.md frontmatter."""
    errors: list[str] = []
    data: dict[str, Any] = {}
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        lineno = i + 2  # account for opening --- on line 1
        if "\t" in raw[: len(raw) - len(raw.lstrip(" \t"))]:
            errors.append(f"Frontmatter line {lineno}: tabs are forbidden in YAML indentation")
            i += 1
            continue
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if raw.startswith(" "):
            errors.append(f"Frontmatter line {lineno}: unexpected indentation at top level: {raw!r}")
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:(.*)$", raw)
        if not m:
            errors.append(f"Frontmatter line {lineno}: cannot parse key/value: {raw!r}")
            i += 1
            continue
        key = m.group(1)
        rest = m.group(2).strip()
        if key in data:
            errors.append(f"Frontmatter line {lineno}: duplicate top-level key '{key}'")
            i += 1
            continue

        # Block scalar (|, >, |-, >-)
        if rest in {"|", ">", "|-", ">-"}:
            folded = rest.startswith(">")
            strip_tail = rest.endswith("-")
            block_lines: list[str] = []
            j = i + 1
            base_indent: int | None = None
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "":
                    block_lines.append("")
                    j += 1
                    continue
                indent = len(nxt) - len(nxt.lstrip(" "))
                if indent == 0:
                    break
                if base_indent is None:
                    base_indent = indent
                block_lines.append(nxt[min(indent, base_indent):])
                j += 1
            if folded:
                paras: list[str] = []
                cur: list[str] = []
                for bl in block_lines:
                    if bl == "":
                        if cur:
                            paras.append(" ".join(cur))
                            cur = []
                    else:
                        cur.append(bl.strip())
                if cur:
                    paras.append(" ".join(cur))
                val_str = "\n".join(paras)
            else:
                val_str = "\n".join(block_lines)
            if not strip_tail and block_lines:
                val_str = val_str.rstrip("\n")
            data[key] = val_str
            i = j
            continue

        # Inline list [a, b]
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            items = [_unquote(x) for x in inner.split(",") if x.strip()] if inner else []
            data[key] = items
            i += 1
            continue

        # Nested dict or list
        if rest == "":
            j = i + 1
            nested_dict: dict[str, Any] = {}
            nested_list: list[Any] = []
            mode: str | None = None
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "" or nxt.strip().startswith("#"):
                    j += 1
                    continue
                if "\t" in nxt[: len(nxt) - len(nxt.lstrip(" \t"))]:
                    errors.append(f"Frontmatter line {j + 2}: tabs forbidden in YAML indentation")
                    j += 1
                    continue
                if not nxt.startswith(" "):
                    break
                sub = nxt.strip()
                if sub.startswith("- "):
                    if mode == "dict":
                        errors.append(f"Frontmatter line {j + 2}: mixed list item inside dict '{key}'")
                    mode = "list"
                    nested_list.append(_unquote(sub[2:]))
                else:
                    sm = re.match(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$", sub)
                    if not sm:
                        errors.append(f"Frontmatter line {j + 2}: invalid nested YAML line: {nxt!r}")
                    else:
                        if mode == "list":
                            errors.append(f"Frontmatter line {j + 2}: mixed dict key inside list '{key}'")
                        mode = "dict"
                        nested_key = sm.group(1)
                        if nested_key in nested_dict:
                            errors.append(
                                f"Frontmatter line {j + 2}: duplicate nested key '{nested_key}' inside '{key}'"
                            )
                        else:
                            nested_dict[nested_key] = _unquote(sm.group(2))
                j += 1
            data[key] = nested_list if mode == "list" else nested_dict
            i = j
            continue

        data[key] = _unquote(rest)
        i += 1

    return (None if errors else data), errors


def strip_fenced_blocks(text: str) -> list[tuple[int, str]]:
    """Return list of (1-based line_number, line_text) excluding fenced code blocks."""
    out: list[tuple[int, str]] = []
    fence_char: str | None = None
    fence_len = 0
    for idx, line in enumerate(text.splitlines(), start=1):
        m = re.match(r"^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$", line)
        if m:
            marker = m.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len and not m.group(2).strip():
                fence_char = None
                fence_len = 0
            continue
        if fence_char is None:
            out.append((idx, line))
    return out


def strip_inline_code(line: str) -> str:
    """Remove inline backtick spans (`...`, ``...``) cleanly."""
    i = 0
    res: list[str] = []
    n = len(line)
    while i < n:
        if line[i] == "`":
            ticks = 0
            while i + ticks < n and line[i + ticks] == "`":
                ticks += 1
            end = line.find("`" * ticks, i + ticks)
            if end != -1:
                i = end + ticks
                continue
        res.append(line[i])
        i += 1
    return "".join(res)


def github_slug(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s", "-", s)
    return s


def extract_heading_slugs(md_path: Path) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return slugs
    for _, line in strip_fenced_blocks(text):
        hm = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if hm:
            base = github_slug(hm.group(1))
            if base in counts:
                counts[base] += 1
                slugs.add(f"{base}-{counts[base]}")
            else:
                counts[base] = 0
                slugs.add(base)
    return slugs


def validate_skill_md(
    skill_dir: Path,
    expect_name: str | None,
    strict: bool,
    is_child: bool = False,
) -> tuple[str | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"Missing SKILL.md at {skill_dir}")
        return None, errors, warnings

    try:
        content = skill_md.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        errors.append(f"{skill_md}: invalid UTF-8 ({exc})")
        return None, errors, warnings

    if content.startswith("\ufeff"):
        errors.append(f"{skill_md}: UTF-8 BOM before opening '---' is forbidden")
    if not content.startswith("---\n") and not content.startswith("---\r\n"):
        errors.append(f"{skill_md}: line 1 MUST be '---' (no leading comments or whitespace)")
        return None, errors, warnings

    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.DOTALL)
    if not match:
        errors.append(f"{skill_md}: invalid or unclosed YAML frontmatter")
        return None, errors, warnings

    fm_data, fm_errors = parse_yaml_frontmatter_stdlib(match.group(1))
    if fm_errors or fm_data is None:
        for err in fm_errors:
            errors.append(f"{skill_md}: {err}")
        return None, errors, warnings

    unexpected = set(fm_data.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        errors.append(
            f"{skill_md}: unexpected frontmatter key(s): {', '.join(sorted(unexpected))}"
        )

    for req in ("name", "description"):
        if req not in fm_data:
            errors.append(f"{skill_md}: missing required frontmatter key '{req}'")

    name = fm_data.get("name")
    skill_name: str | None = None
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{skill_md}: 'name' must be a non-empty string")
        else:
            skill_name = name.strip()
            if not re.match(r"^[a-z0-9-]+$", skill_name):
                errors.append(f"{skill_md}: 'name' '{skill_name}' must match ^[a-z0-9-]+$")
            if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
                errors.append(
                    f"{skill_md}: 'name' '{skill_name}' cannot start/end with '-' or contain '--'"
                )
            if len(skill_name) > 64:
                errors.append(f"{skill_md}: 'name' exceeds 64 chars ({len(skill_name)})")
            if expect_name and skill_name != expect_name:
                errors.append(
                    f"{skill_md}: expected name '{expect_name}', got '{skill_name}'"
                )
            if is_child and skill_name != skill_dir.name:
                errors.append(
                    f"{skill_md}: child skill name '{skill_name}' MUST equal folder name '{skill_dir.name}'"
                )

    desc = fm_data.get("description")
    if desc is not None:
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{skill_md}: 'description' must be a non-empty string")
        else:
            d = desc.strip()
            if len(d) > 1024:
                errors.append(f"{skill_md}: 'description' exceeds 1024 chars ({len(d)})")
            if "<" in d or ">" in d:
                errors.append(f"{skill_md}: 'description' cannot contain '<' or '>'")
            if "[TODO:" in d:
                errors.append(f"{skill_md}: 'description' contains '[TODO:' placeholder")

    compat = fm_data.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            errors.append(f"{skill_md}: 'compatibility' must be a string")
        elif len(compat) > 500:
            errors.append(f"{skill_md}: 'compatibility' exceeds 500 chars ({len(compat)})")

    body = content[match.end() :]
    for lineno, line in strip_fenced_blocks(body):
        if "[TODO:" in line:
            errors.append(f"{skill_md}:{lineno}: unfinished '[TODO:' placeholder in body")
        if re.search(r"(?:^|\s)@(?:references|templates|scripts|skills)/", line):
            errors.append(f"{skill_md}:{lineno}: '@' eager import syntax is forbidden")

    total_lines = len(content.splitlines())
    if total_lines > 500:
        msg = f"{skill_md}: {total_lines} lines exceeds recommended 500-line lean router cap"
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    return skill_name, errors, warnings


def validate_r2_module(
    md_path: Path, rel_str: str, strict: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{rel_str}: cannot read UTF-8 ({exc})"], warnings

    lines_outside = strip_fenced_blocks(text)
    found: list[tuple[int, int, str]] = []
    for lineno, line in lines_outside:
        for num, pat in R2_PILLARS:
            if pat.match(line):
                found.append((num, lineno, line))
                break

    found_nums = [x[0] for x in found]
    expected_nums = [1, 2, 3, 4, 5, 6]
    if found_nums != expected_nums:
        missing = [n for n in expected_nums if n not in found_nums]
        if missing:
            errors.append(f"{rel_str}: missing R2 pillar heading(s): {missing}")
        else:
            errors.append(f"{rel_str}: R2 pillar headings out of order or duplicated: {found_nums}")
        return errors, warnings

    # Slice body per section
    raw_lines = text.splitlines()
    for idx, (num, start_ln, _) in enumerate(found):
        end_ln = found[idx + 1][1] - 1 if idx + 1 < len(found) else len(raw_lines)
        sec_lines = raw_lines[start_ln:end_ln]
        non_ws = "".join(sec_lines).strip()
        if len(non_ws) < 20:
            errors.append(f"{rel_str}: R2 pillar {num} has empty/insufficient body (<20 chars)")
        if strict:
            if num == 4:
                checks = sum(1 for ln in sec_lines if re.match(r"^\s*[-*]\s+\[\s*[xX ]?\s*\]", ln))
                if checks < 3:
                    errors.append(f"{rel_str}: R2 pillar 4 requires >= 3 checklist items ('- [ ]'), found {checks}")
            if num == 5:
                joined = "\n".join(sec_lines)
                if "PASS" not in joined or "FAIL" not in joined:
                    errors.append(f"{rel_str}: R2 pillar 5 must specify explicit PASS and FAIL gate criteria")
            if num == 6:
                if not any("|" in ln for ln in sec_lines):
                    errors.append(f"{rel_str}: R2 pillar 6 must include a structured Markdown table")

    if strict:
        total_lines = len(raw_lines)
        word_count = len(re.findall(r"\S+", text))
        if total_lines < 120 or word_count < 600:
            errors.append(
                f"{rel_str}: R2 strict depth check failed ({total_lines} lines / {word_count} words; need >= 120 lines and >= 600 words)"
            )

    return errors, warnings


def validate_markdown_links(
    md_files: list[Path],
    suite_root: Path,
    strict: bool,
) -> tuple[int, list[str]]:
    errors: list[str] = []
    checked = 0
    root_resolved = suite_root.resolve()
    heading_cache: dict[Path, set[str]] = {}

    inline_re = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
    ref_re = re.compile(r"^\[[^\]]+\]:\s*(\S+)")

    for md_path in md_files:
        rel_md = md_path.relative_to(suite_root).as_posix()
        child_boundary: Path | None = None
        parts = md_path.relative_to(suite_root).parts
        if len(parts) >= 2 and parts[0] == "skills":
            child_boundary = (suite_root / "skills" / parts[1]).resolve()

        try:
            text = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{rel_md}: unreadable markdown ({exc})")
            continue

        for lineno, raw_line in strip_fenced_blocks(text):
            cleaned = strip_inline_code(raw_line)
            targets: list[str] = []
            for m in inline_re.finditer(cleaned):
                targets.append(m.group(1))
            rm = ref_re.match(cleaned.strip())
            if rm:
                targets.append(rm.group(1))

            for tgt in targets:
                tgt = tgt.strip()
                if tgt.startswith("<") and tgt.endswith(">"):
                    tgt = tgt[1:-1]
                if not tgt:
                    continue
                if tgt.startswith("#"):
                    checked += 1
                    if strict:
                        frag = tgt[1:]
                        resolved_self = md_path.resolve()
                        if resolved_self not in heading_cache:
                            heading_cache[resolved_self] = extract_heading_slugs(resolved_self)
                        if not frag or frag.lower() not in heading_cache[resolved_self]:
                            errors.append(
                                f"{rel_md}:{lineno}: broken same-file heading anchor '{tgt}'"
                            )
                    continue
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", tgt):
                    continue
                checked += 1
                if tgt.startswith("/"):
                    errors.append(f"{rel_md}:{lineno}: absolute link '{tgt}' is forbidden")
                    continue
                path_part, _, frag = tgt.partition("#")
                path_part, _, _ = path_part.partition("?")
                if not path_part:
                    continue
                resolved = (md_path.parent / path_part).resolve()
                try:
                    resolved.relative_to(root_resolved)
                except ValueError:
                    errors.append(f"{rel_md}:{lineno}: relative link '{tgt}' escapes skill root")
                    continue
                if child_boundary is not None:
                    try:
                        resolved.relative_to(child_boundary)
                    except ValueError:
                        errors.append(
                            f"{rel_md}:{lineno}: child skill link '{tgt}' escapes standalone boundary '{child_boundary.name}/'"
                        )
                        continue
                if not resolved.exists():
                    errors.append(f"{rel_md}:{lineno}: broken link target '{tgt}'")
                    continue
                if strict and frag and resolved.is_file() and resolved.suffix.lower() == ".md":
                    if resolved not in heading_cache:
                        heading_cache[resolved] = extract_heading_slugs(resolved)
                    if frag.lower() not in heading_cache[resolved]:
                        errors.append(
                            f"{rel_md}:{lineno}: broken heading anchor '#{frag}' in '{path_part}'"
                        )

    return checked, errors


def check_registry_parity(
    suite_root: Path,
    strict: bool,
    require_all_active: bool,
) -> tuple[list[Path], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    active_child_dirs: list[Path] = []
    reg_path = suite_root / "registry.json"
    skills_dir = suite_root / "skills"

    disk_children: set[str] = set()
    if skills_dir.exists() and skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            if entry.is_dir() and entry.name not in SKIP_DIRS:
                disk_children.add(entry.name)

    if not reg_path.exists():
        if require_all_active:
            errors.append("Missing registry.json while --require-all-active was specified")
        for child_name in sorted(disk_children):
            active_child_dirs.append(skills_dir / child_name)
        return active_child_dirs, errors, warnings

    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return active_child_dirs, [f"registry.json: invalid JSON ({exc})"], warnings

    if not isinstance(reg, dict):
        return active_child_dirs, ["registry.json: top-level JSON must be an object"], warnings

    for k in ("schema_version", "suite_name", "parent", "children"):
        if k not in reg:
            errors.append(f"registry.json: missing top-level key '{k}'")

    parent = reg.get("parent")
    if isinstance(parent, dict):
        for pk in ("id", "name", "path", "skill_file", "estimated_tokens", "scripts", "templates"):
            if pk not in parent:
                errors.append(f"registry.json: parent missing key '{pk}'")
        for sp in parent.get("scripts", []) or []:
            if not (suite_root / sp).exists():
                errors.append(f"registry.json: parent script missing on disk: {sp}")
        for tp in parent.get("templates", []) or []:
            if not (suite_root / tp).exists():
                errors.append(f"registry.json: parent template missing on disk: {tp}")
        for rp in parent.get("references", []) or []:
            if not (suite_root / rp).exists():
                errors.append(f"registry.json: parent reference missing on disk: {rp}")
    else:
        errors.append("registry.json: 'parent' must be an object")

    children = reg.get("children")
    if not isinstance(children, list):
        errors.append("registry.json: 'children' must be an array")
        return active_child_dirs, errors, warnings

    seen_ids: set[str] = set()
    child_deps: dict[str, list[str]] = {}
    for idx, ch in enumerate(children):
        if not isinstance(ch, dict):
            errors.append(f"registry.json: children[{idx}] must be an object")
            continue
        missing = sorted(REQUIRED_CHILD_FIELDS - set(ch.keys()))
        cid = str(ch.get("id", f"index-{idx}"))
        if missing:
            errors.append(f"registry.json: child '{cid}' missing field(s): {', '.join(missing)}")
            continue
        if cid in seen_ids:
            errors.append(f"registry.json: duplicate child id '{cid}'")
        seen_ids.add(cid)
        if ch["name"] != cid:
            errors.append(f"registry.json: child '{cid}' name mismatch '{ch['name']}'")
        expected_path = f"skills/{cid}"
        if ch["path"] != expected_path:
            errors.append(f"registry.json: child '{cid}' path should be '{expected_path}', got '{ch['path']}'")
        if not isinstance(ch["estimated_tokens"], int) or ch["estimated_tokens"] <= 0:
            errors.append(f"registry.json: child '{cid}' estimated_tokens must be positive int")
        child_deps[cid] = list(ch.get("depends_on") or [])

        status = ch.get("status")
        cdir = suite_root / ch["path"]
        if status == "planned":
            if require_all_active:
                errors.append(f"registry.json: child '{cid}' has status 'planned' under --require-all-active")
            elif cdir.exists():
                warnings.append(
                    f"registry.json: child '{cid}' folder exists on disk while status is 'planned' (skipped until marked 'active')"
                )
        elif status == "active":
            if not cdir.is_dir() or not (cdir / "SKILL.md").exists():
                errors.append(f"registry.json: active child '{cid}' missing '{ch['path']}/SKILL.md'")
            else:
                active_child_dirs.append(cdir)
            es = ch.get("entry_script")
            if es is not None:
                es_path = (suite_root / es) if (suite_root / es).exists() else (cdir / es)
                if not es_path.exists():
                    errors.append(f"registry.json: active child '{cid}' entry_script missing: {es}")
        else:
            errors.append(f"registry.json: child '{cid}' has invalid status '{status}'")

    missing_core = sorted(REQUIRED_CORE_CHILDREN - seen_ids)
    if missing_core:
        errors.append(f"registry.json: missing required core child skill(s): {', '.join(missing_core)}")

    for cid, deps in child_deps.items():
        for d in deps:
            if d not in seen_ids:
                errors.append(f"registry.json: child '{cid}' depends_on unknown id '{d}'")

    unregistered = sorted(disk_children - seen_ids)
    for u in unregistered:
        errors.append(f"skills/{u}/ exists on disk but is missing from registry.json")

    return active_child_dirs, errors, warnings


def validate_repo(
    skill_dir: Path,
    strict: bool = False,
    require_all_active: bool = False,
    expect_name: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    root = skill_dir.resolve()
    is_suite = (root / "registry.json").exists() or (root / "skills").is_dir()

    # Registry & Child Skills (discover active vs planned first so planned/in-flight children don't cause mid-write errors)
    active_children, reg_errs, reg_warns = check_registry_parity(
        root, strict=strict, require_all_active=require_all_active
    )
    errors.extend(reg_errs)
    warnings.extend(reg_warns)

    active_child_names = {c.name for c in active_children}

    # Walk tree once for symlinks, forbidden rule files, and scripts/json/md
    all_md: list[Path] = []
    all_scripts: list[Path] = []
    all_json: list[Path] = []
    skill_md_locations: list[Path] = []
    symlink_hits: list[str] = []
    rule_pollution: list[str] = []

    for cur_root, dirs, files in os.walk(root, topdown=True, followlinks=False):
        cur_path = Path(cur_root)
        rel_cur = cur_path.relative_to(root)

        # Check directory symlinks before pruning
        kept_dirs: list[str] = []
        for d in dirs:
            dp = cur_path / d
            if d in SKIP_DIRS:
                continue
            if rel_cur == Path(".") and d == "tests":
                continue
            if is_suite and rel_cur == Path("skills") and d not in active_child_names:
                # Skip planned/in-flight child directories from deep link/syntax scans until active
                if dp.is_symlink():
                    symlink_hits.append(dp.relative_to(root).as_posix())
                continue
            if dp.is_symlink():
                symlink_hits.append(dp.relative_to(root).as_posix())
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for f in files:
            fp = cur_path / f
            rel_f = fp.relative_to(root).as_posix()
            if fp.is_symlink():
                symlink_hits.append(rel_f)
                continue
            if f in {"AGENTS.md", "GEMINI.md"}:
                rule_pollution.append(rel_f)
            if f == "SKILL.md":
                parts = fp.relative_to(root).parts
                if not (len(parts) >= 2 and parts[0] == "evals"):
                    skill_md_locations.append(fp)
            if fp.suffix.lower() == ".md":
                all_md.append(fp)
            elif fp.suffix.lower() in {".py", ".sh", ".bash", ".js", ".mjs", ".cjs"}:
                all_scripts.append(fp)
            elif fp.suffix.lower() == ".json":
                all_json.append(fp)

    for s in symlink_hits:
        errors.append(f"Symlink forbidden in repository: {s}")
    for rp in rule_pollution:
        errors.append(f"Forbidden auto-loaded rule file: {rp}")

    # Single SKILL.md per skill root check
    allowed_skill_mds: set[Path] = {root / "SKILL.md"}
    if is_suite and (root / "skills").is_dir():
        for child in (root / "skills").iterdir():
            if child.is_dir() and child.name not in SKIP_DIRS:
                allowed_skill_mds.add(child / "SKILL.md")

    for smd in skill_md_locations:
        if smd not in allowed_skill_mds:
            errors.append(
                f"Stray nested SKILL.md outside valid skill root: {smd.relative_to(root).as_posix()}"
            )

    parent_name, fm_errs, fm_warns = validate_skill_md(root, expect_name, strict, is_child=False)
    errors.extend(fm_errs)
    warnings.extend(fm_warns)

    for cdir in active_children:
        _, cerrs, cwarns = validate_skill_md(cdir, None, strict, is_child=True)
        errors.extend(cerrs)
        warnings.extend(cwarns)

    # Strict root packaging docs
    if strict and is_suite:
        for req_doc in ("README.md", "LICENSE"):
            if not (root / req_doc).exists():
                errors.append(f"Missing required root file in --strict mode: {req_doc}")

    # Markdown relative links
    links_checked, link_errs = validate_markdown_links(all_md, root, strict=strict)
    errors.extend(link_errs)

    # Scripts & JSON syntax
    bash_bin = shutil.which("bash")
    node_bin = shutil.which("node")
    scripts_checked = 0
    for sp in all_scripts:
        rel_s = sp.relative_to(root).as_posix()
        scripts_checked += 1
        suf = sp.suffix.lower()
        if suf == ".py":
            try:
                py_compile.compile(str(sp), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"{rel_s}: py_compile failed: {exc}")
        elif suf in {".sh", ".bash"}:
            if not bash_bin:
                msg = f"{rel_s}: bash not found to syntax-check shell script"
                (errors if strict else warnings).append(msg)
            else:
                proc = subprocess.run([bash_bin, "-n", str(sp)], capture_output=True, text=True)
                if proc.returncode != 0:
                    errors.append(f"{rel_s}: bash -n failed: {proc.stderr.strip()}")
        elif suf in {".js", ".mjs", ".cjs"}:
            if not node_bin:
                msg = f"{rel_s}: node not found to syntax-check JS script"
                (errors if strict else warnings).append(msg)
            else:
                proc = subprocess.run([node_bin, "--check", str(sp)], capture_output=True, text=True)
                if proc.returncode != 0:
                    errors.append(f"{rel_s}: node --check failed: {proc.stderr.strip()}")

    for jp in all_json:
        rel_j = jp.relative_to(root).as_posix()
        try:
            json.loads(jp.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{rel_j}: invalid JSON ({exc})")

    # R2 6-Pillar validation across Parent references/**/*.md + Child skills/*/references/**/*.md
    r2_targets: list[Path] = []
    parent_refs = root / "references"
    if parent_refs.is_dir():
        for p in sorted(parent_refs.rglob("*.md")):
            rel_p = p.relative_to(root).as_posix()
            if rel_p in {"references/source-coverage-inventory.md", "references/README.md"}:
                continue
            r2_targets.append(p)
    for cdir in active_children:
        crefs = cdir / "references"
        if crefs.is_dir():
            for p in sorted(crefs.rglob("*.md")):
                if p.name == "README.md":
                    continue
                r2_targets.append(p)

    r2_errs_count = 0
    for rp in r2_targets:
        rel_p = rp.relative_to(root).as_posix()
        rerrs, rwarns = validate_r2_module(rp, rel_p, strict=strict)
        if rerrs:
            r2_errs_count += len(rerrs)
            errors.extend(rerrs)
        warnings.extend(rwarns)

    valid = len(errors) == 0
    checks = {
        "single_skill_md": "PASS" if not any("SKILL.md" in e for e in errors) else "FAIL",
        "frontmatter": "PASS" if not fm_errs else "FAIL",
        "no_agents_gemini_md": "PASS" if not rule_pollution else "FAIL",
        "no_symlinks": "PASS" if not symlink_hits else "FAIL",
        "markdown_links": "PASS" if not link_errs else "FAIL",
        "script_and_json_syntax": "PASS"
        if not any(
            ("py_compile" in e or "bash -n" in e or "node --check" in e or "invalid JSON" in e)
            for e in errors
        )
        else "FAIL",
        "r2_six_pillars": "PASS" if r2_errs_count == 0 else "FAIL",
        "registry_parity": "PASS" if not reg_errs else "FAIL",
    }

    return {
        "valid": valid,
        "strict": strict,
        "require_all_active": require_all_active,
        "skill_root": str(root),
        "skill_name": parent_name,
        "summary": {
            "markdown_links_checked": links_checked,
            "scripts_checked": scripts_checked,
            "json_checked": len(all_json),
            "r2_modules_checked": len(r2_targets),
            "active_children_checked": len(active_children),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate appnwebsite-skill suite (Parent + Child Skills + registry.json + R2 6-pillars)."
    )
    parser.add_argument("skill_dir", nargs="?", default=".", help="Skill or suite root directory (default: .)")
    parser.add_argument("--root", dest="root_override", help="Explicit skill/suite root override")
    parser.add_argument("--strict", action="store_true", help="Enforce strict R2 depth, anchors, and doc rules")
    parser.add_argument(
        "--require-all-active",
        action="store_true",
        help="Fail if any child skill in registry.json still has status 'planned'",
    )
    parser.add_argument("--expect-name", help="Assert root SKILL.md frontmatter name equals this value")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--verbose", action="store_true", help="Show detailed warnings and check breakdown")
    args = parser.parse_args(argv)

    target = Path(args.root_override or args.skill_dir)
    if not target.exists() or not target.is_dir():
        msg = f"Invalid skill directory: {target}"
        if args.json:
            print(json.dumps({"valid": False, "errors": [msg]}))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    report = validate_repo(
        target,
        strict=args.strict,
        require_all_active=args.require_all_active,
        expect_name=args.expect_name,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["valid"] else "FAIL"
        s = report["summary"]
        print(
            f"[{status}] {report['skill_name'] or target} | "
            f"links={s['markdown_links_checked']} scripts={s['scripts_checked']} "
            f"r2_modules={s['r2_modules_checked']} children={s['active_children_checked']} "
            f"errors={s['errors']} warnings={s['warnings']}"
        )
        if args.verbose:
            for k, v in report["checks"].items():
                print(f"  - {k}: {v}")
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        for e in report["errors"]:
            print(f"  ERR:  {e}")

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
