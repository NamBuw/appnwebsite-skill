#!/usr/bin/env python3
"""Progressive-disclosure & token-budget profiler for appnwebsite-skill.

MIT License — Pure Python 3.10+ stdlib only (zero third-party dependencies).
Audits Hygiene, L1 frontmatter metadata & XML injection, L2 router budgets,
L3 supporting file budgets / TOCs / orphans / child link isolation,
cross-file prose duplication, registry.json parity & token drift, and
active-stage context savings ratio.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import pathlib
import re
import sys
import tempfile
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ALLOWED_FRONTMATTER_KEYS = frozenset(
    {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
)
SKIP_DIRS = frozenset({".git", "__pycache__", "node_modules", ".pytest_cache"})
STAGES = ("Q1", "Q2", "3A", "3B", "3C", "Q4")

_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_EAGER_AT_RE = re.compile(r"(?:^|\s)@(?:references|templates|scripts|skills)/")
_R2_PILLAR_HEADING_RE = re.compile(r"^##\s+[1-6]\.\s+")
_STRUCTURAL_HEADING_RE = re.compile(
    r"^##\s+(?:[1-6]\.\s+|contents$|table\s+of\s+contents$|related\b.*\bmodules$)",
    re.IGNORECASE,
)
_TOC_MARKER_RE = re.compile(
    r"(?:^>\s*\*\*Contents\*\*:|^##\s+Contents\b|^##\s+Table\s+of\s+Contents\b)",
    re.IGNORECASE,
)
_ANCHOR_LINK_RE = re.compile(r"\[[^\]]+\]\(#[^)\s]+\)")
_BLOCK_SCALAR_HEADER_RE = re.compile(
    r"^([|>])(?:([-+]?)([1-9]?)|([1-9])([-+]?))(?:[ \t]+#.*)?$"
)
_XML_HEADER_STRIP_RE = re.compile(
    r"^([A-Za-z0-9_.-]+\s*:\s*)[|>](?:[-+]?[1-9]?|[1-9][-+]?)(?:[ \t]+#.*|[ \t]*)$"
)


@dataclasses.dataclass
class Finding:
    id: str
    severity: str  # PASS | INFO | WARN | ERROR
    target: str
    message: str
    planned_pending: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "target": self.target,
            "message": self.message,
        }


@dataclasses.dataclass
class FrontmatterResult:
    raw_yaml: str
    body: str
    data: dict[str, Any]
    errors: list[tuple[str, str]]
    warnings: list[tuple[str, str]]


def strip_fenced_code_blocks(text: str) -> str:
    """Strip CommonMark fenced code blocks while preserving 1-based line numbers."""
    out_lines: list[str] = []
    open_marker: str | None = None
    open_len = 0

    for line in text.splitlines():
        if open_marker is None:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                fence = m.group(1)
                info = m.group(2)
                # CommonMark: backtick fence info string cannot contain backticks
                if fence[0] == "`" and "`" in info:
                    out_lines.append(line)
                    continue
                open_marker = fence[0]
                open_len = len(fence)
                out_lines.append("")
                continue
            out_lines.append(line)
        else:
            cm = _FENCE_CLOSE_RE.match(line)
            if cm:
                close_fence = cm.group(1)
                if close_fence[0] == open_marker and len(close_fence) >= open_len:
                    open_marker = None
                    open_len = 0
            out_lines.append("")

    return "\n".join(out_lines)


def strip_inline_code(line: str) -> str:
    """Remove inline backtick spans from a single line."""
    out: list[str] = []
    i = 0
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
        out.append(line[i])
        i += 1
    return "".join(out)


def estimate_tokens(text: str) -> dict[str, int]:
    """Compute dual stdlib token estimates (hybrid est_tokens + chars/4)."""
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    est = max(1, round((words * 1.3 + chars / 4.0) / 2.0)) if text.strip() else 0
    chars_div_4 = math.ceil(chars / 4) if chars > 0 else 0
    return {
        "est_tokens": est,
        "chars_div_4": chars_div_4,
        "words": words,
        "chars": chars,
    }


def _has_unclosed_quote(val: str) -> bool:
    s = val.strip()
    if not s:
        return False
    if s[0] in ('"', "'"):
        quote = s[0]
        if len(s) == 1:
            return True
        if quote == '"':
            # Check trailing unescaped quote (allow trailing # comment after closing quote)
            i = 1
            escaped = False
            while i < len(s):
                ch = s[i]
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    rest = s[i + 1 :].strip()
                    return bool(rest and not rest.startswith("#"))
                i += 1
            return True
        else:
            # Single-quoted YAML escapes '' inside
            i = 1
            while i < len(s):
                if s[i] == "'":
                    if i + 1 < len(s) and s[i + 1] == "'":
                        i += 2
                        continue
                    rest = s[i + 1 :].strip()
                    return bool(rest and not rest.startswith("#"))
                i += 1
            return True
    return False


def _unquote(val: str) -> str:
    s = val.strip()
    if len(s) >= 2 and (
        (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")
    ):
        inner = s[1:-1]
        if s[0] == '"':
            return inner.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
        return inner.replace("''", "'")
    return s


def parse_frontmatter(md_text: str) -> FrontmatterResult:
    """Parse SKILL.md YAML frontmatter using pure stdlib."""
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    if md_text.startswith("\ufeff"):
        errors.append(("FM_BOM", "UTF-8 BOM before opening '---' is forbidden"))
        md_text = md_text.lstrip("\ufeff")

    lines = md_text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        first = lines[0] if lines else "<empty>"
        errors.append(("FM_MISSING", f"Line 1 must be '---', got {first!r}"))
        return FrontmatterResult(
            raw_yaml="",
            body=md_text,
            data={},
            errors=errors,
            warnings=warnings,
        )

    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip() == "---" and not lines[idx].startswith((" ", "\t")):
            end_idx = idx
            break

    if end_idx is None:
        errors.append(("FM_UNCLOSED", "Unclosed YAML frontmatter (missing closing '---')"))
        return FrontmatterResult(
            raw_yaml="\n".join(lines[1:]),
            body="",
            data={},
            errors=errors,
            warnings=warnings,
        )

    fm_lines = lines[1:end_idx]
    raw_yaml = "\n".join(fm_lines)
    body = "\n".join(lines[end_idx + 1 :])
    data: dict[str, Any] = {}

    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        lineno = i + 2
        leading = raw[: len(raw) - len(raw.lstrip(" \t"))]
        if "\t" in leading:
            errors.append(("FM_YAML_TAB", f"Frontmatter line {lineno}: tab indentation is forbidden"))
            i += 1
            continue

        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if raw.startswith(" "):
            errors.append(("FM_YAML_SYNTAX", f"Frontmatter line {lineno}: unexpected top-level indent"))
            i += 1
            continue

        m = re.match(r"^([A-Za-z0-9_-]+)\s*:(.*)$", raw)
        if not m:
            errors.append(("FM_YAML_SYNTAX", f"Frontmatter line {lineno}: invalid YAML line {raw!r}"))
            i += 1
            continue

        key = m.group(1)
        rest = m.group(2).strip()
        if key in data:
            errors.append(("FM_YAML_DUP", f"Frontmatter line {lineno}: duplicate key {key!r}"))
            i += 1
            continue

        if key not in ALLOWED_FRONTMATTER_KEYS:
            warnings.append(("FM_EXTRA_KEY", f"Frontmatter line {lineno}: non-standard key {key!r}"))

        # Block scalar: |, >, |-, >-, |+, >+, |2, >2, etc.
        bm = _BLOCK_SCALAR_HEADER_RE.match(rest)
        if bm:
            folded = bm.group(1) == ">"
            chomp = bm.group(2) or bm.group(5) or ""
            indent_str = bm.group(3) or bm.group(4) or ""
            block_lines: list[str] = []
            j = i + 1
            base_indent: int | None = int(indent_str) if indent_str else None
            while j < len(fm_lines):
                nxt = fm_lines[j]
                if nxt.strip() == "":
                    block_lines.append("")
                    j += 1
                    continue
                nxt_leading = nxt[: len(nxt) - len(nxt.lstrip(" \t"))]
                if "\t" in nxt_leading:
                    errors.append(("FM_YAML_TAB", f"Frontmatter line {j + 2}: tab indentation is forbidden"))
                    j += 1
                    continue
                indent = len(nxt) - len(nxt.lstrip(" "))
                if indent == 0:
                    break
                if base_indent is None:
                    base_indent = indent
                block_lines.append(nxt[min(indent, base_indent) :])
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
                data[key] = "\n".join(paras)
            else:
                joined = "\n".join(block_lines)
                data[key] = joined if chomp == "+" else joined.rstrip("\n")
            i = j
            continue

        # Inline list
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            items = [_unquote(x) for x in inner.split(",") if x.strip()] if inner else []
            data[key] = items
            i += 1
            continue

        # Nested mapping or list
        if rest == "":
            j = i + 1
            nested_dict: dict[str, Any] = {}
            nested_list: list[Any] = []
            mode: str | None = None
            while j < len(fm_lines):
                nxt = fm_lines[j]
                if nxt.strip() == "" or nxt.strip().startswith("#"):
                    j += 1
                    continue
                nxt_leading = nxt[: len(nxt) - len(nxt.lstrip(" \t"))]
                if "\t" in nxt_leading:
                    errors.append(("FM_YAML_TAB", f"Frontmatter line {j + 2}: tab indentation is forbidden"))
                    j += 1
                    continue
                if not nxt.startswith(" "):
                    break
                sub = nxt.strip()
                if sub.startswith("- "):
                    if mode == "dict":
                        errors.append(
                            (
                                "FM_YAML_MIXED",
                                f"Frontmatter line {j + 2}: mixed list item inside dict {key!r}",
                            )
                        )
                    mode = mode or "list"
                    val_part = sub[2:].strip()
                    if _has_unclosed_quote(val_part):
                        errors.append(("FM_YAML_QUOTE", f"Frontmatter line {j + 2}: unclosed quote"))
                    nested_list.append(_unquote(val_part))
                else:
                    sm = re.match(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$", sub)
                    if not sm:
                        errors.append(("FM_YAML_SYNTAX", f"Frontmatter line {j + 2}: invalid nested YAML {nxt!r}"))
                    else:
                        if mode == "list":
                            errors.append(
                                (
                                    "FM_YAML_MIXED",
                                    f"Frontmatter line {j + 2}: mixed dict key inside list {key!r}",
                                )
                            )
                        mode = mode or "dict"
                        if _has_unclosed_quote(sm.group(2)):
                            errors.append(("FM_YAML_QUOTE", f"Frontmatter line {j + 2}: unclosed quote"))
                        nested_dict[sm.group(1)] = _unquote(sm.group(2))
                j += 1
            data[key] = nested_list if mode == "list" else nested_dict
            i = j
            continue

        if _has_unclosed_quote(rest):
            errors.append(("FM_YAML_QUOTE", f"Frontmatter line {lineno}: unclosed quote in value"))
        data[key] = _unquote(rest)
        i += 1

    return FrontmatterResult(
        raw_yaml=raw_yaml,
        body=body,
        data=data,
        errors=errors,
        warnings=warnings,
    )


def _extract_links(md_text: str) -> list[str]:
    prose = "\n".join(
        strip_inline_code(line)
        for line in strip_fenced_code_blocks(md_text).splitlines()
    )
    targets: list[str] = []
    for _, raw_target in _LINK_RE.findall(prose):
        cleaned = raw_target.strip("<>").strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned) or cleaned.startswith("mailto:"):
            continue
        targets.append(cleaned)
    return targets


def _check_xml_injection(fm: FrontmatterResult) -> list[str]:
    hits: list[str] = []
    name_val = str(fm.data.get("name", ""))
    desc_val = str(fm.data.get("description", ""))
    if "<" in name_val or ">" in name_val:
        hits.append("frontmatter 'name' contains '<' or '>'")
    if "<" in desc_val or ">" in desc_val:
        hits.append("frontmatter 'description' contains '<' or '>'")

    for idx, line in enumerate(fm.raw_yaml.splitlines(), start=2):
        # Strip block scalar header indicator like `description: >` or `description: >-`
        sanitized = _XML_HEADER_STRIP_RE.sub(r"\1", line)
        if "<" in sanitized or ">" in sanitized:
            hits.append(f"raw YAML line {idx} contains '<' or '>'")
    return hits


def _has_top_toc(lines: list[str]) -> bool:
    head = lines[:35]
    anchor_count = 0
    for line in head:
        if _TOC_MARKER_RE.search(line.strip()):
            return True
        anchor_count += len(_ANCHOR_LINK_RE.findall(line))
    return anchor_count >= 3


def _collect_md_files(base_dir: pathlib.Path, sub: str) -> list[pathlib.Path]:
    target = base_dir / sub
    if not target.is_dir():
        return []
    return sorted(p for p in target.rglob("*.md") if p.is_file())


def _audit_single_skill(
    *,
    root: pathlib.Path,
    skill_dir: pathlib.Path,
    skill_name: str,
    is_parent: bool,
    findings: list[Finding],
) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    rel_skill = skill_md.relative_to(root).as_posix()

    metrics: dict[str, Any] = {
        "name": skill_name,
        "path": skill_dir.relative_to(root).as_posix() if skill_dir != root else ".",
        "l1_chars": 0,
        "l1_tokens": 0,
        "l1_chars_div_4": 0,
        "l2_lines": 0,
        "l2_bytes": 0,
        "l2_tokens": 0,
        "l2_chars_div_4": 0,
        "l3_files": 0,
        "l3_tokens": 0,
        "l3_chars_div_4": 0,
        "ref_token_list": [],
        "text_docs": {},  # rel_path -> (raw_text, is_skill_md)
    }

    if not skill_md.is_file():
        code = "L2-PARENT-MISSING" if is_parent else "L2-CHILD-MISSING"
        findings.append(
            Finding(code, "ERROR", rel_skill, f"Missing required {rel_skill}")
        )
        return metrics

    raw_text = skill_md.read_text(encoding="utf-8", errors="replace")
    raw_bytes = len(raw_text.encode("utf-8"))
    lines = raw_text.splitlines()
    l2_est = estimate_tokens(raw_text)

    metrics["l2_lines"] = len(lines)
    metrics["l2_bytes"] = raw_bytes
    metrics["l2_tokens"] = l2_est["est_tokens"]
    metrics["l2_chars_div_4"] = l2_est["chars_div_4"]

    # Frontmatter & L1 checks
    fm = parse_frontmatter(raw_text)
    for err_code, err_msg in fm.errors:
        findings.append(Finding(err_code, "ERROR", rel_skill, err_msg))
    for warn_code, warn_msg in fm.warnings:
        findings.append(Finding(warn_code, "WARN", rel_skill, warn_msg))

    if isinstance(fm.data.get("name"), str) and fm.data["name"].strip():
        metrics["name"] = fm.data["name"].strip()

    l1_est = estimate_tokens(fm.raw_yaml)
    metrics["l1_tokens"] = l1_est["est_tokens"]
    metrics["l1_chars_div_4"] = l1_est["chars_div_4"]

    desc = fm.data.get("description")
    desc_str = desc if isinstance(desc, str) else ""
    metrics["l1_chars"] = len(desc_str)

    if not desc_str.strip():
        findings.append(
            Finding("L1-DESC-LEN", "ERROR", rel_skill, "Missing or empty frontmatter description")
        )
    elif len(desc_str) > 1024:
        findings.append(
            Finding(
                "L1-DESC-LEN",
                "ERROR",
                rel_skill,
                f"Description length {len(desc_str)} chars exceeds hard limit of 1024 chars",
            )
        )
    elif len(desc_str) > 350:
        findings.append(
            Finding(
                "L1-DESC-LEN",
                "WARN",
                rel_skill,
                f"Description length {len(desc_str)} chars exceeds target 350 chars (<= 1024 cap)",
            )
        )
    else:
        findings.append(
            Finding(
                "L1-DESC-LEN",
                "PASS",
                rel_skill,
                f"Description length {len(desc_str)} chars within <= 350 target",
            )
        )

    if l1_est["est_tokens"] > 150:
        findings.append(
            Finding(
                "L1-TOKENS",
                "ERROR",
                rel_skill,
                f"Frontmatter YAML {l1_est['est_tokens']} est. tokens exceeds hard limit 150",
            )
        )
    elif l1_est["est_tokens"] > 120:
        findings.append(
            Finding(
                "L1-TOKENS",
                "WARN",
                rel_skill,
                f"Frontmatter YAML {l1_est['est_tokens']} est. tokens above <= 120 target",
            )
        )
    else:
        findings.append(
            Finding(
                "L1-TOKENS",
                "PASS",
                rel_skill,
                f"Frontmatter YAML {l1_est['est_tokens']} est. tokens within <= 120 target",
            )
        )

    xml_hits = _check_xml_injection(fm)
    if xml_hits:
        findings.append(
            Finding(
                "L1-XML-INJECT",
                "ERROR",
                rel_skill,
                "; ".join(xml_hits),
            )
        )

    # Hygiene: @path eager imports outside code fences & inline code
    prose_body = strip_fenced_code_blocks(fm.body)
    for b_idx, b_line in enumerate(prose_body.splitlines(), start=1):
        cleaned_line = strip_inline_code(b_line)
        if _EAGER_AT_RE.search(cleaned_line):
            findings.append(
                Finding(
                    "HYG-EAGER-AT",
                    "ERROR",
                    rel_skill,
                    f"Eager '@' import directive detected near body line {b_idx}: {b_line.strip()[:80]}",
                )
            )
            break

    metrics["text_docs"][rel_skill] = (prose_body, True)

    # L2 Size check
    if is_parent:
        if len(lines) > 280 or raw_bytes > 18432 or l2_est["est_tokens"] > 4500:
            findings.append(
                Finding(
                    "L2-PARENT-SIZE",
                    "ERROR",
                    rel_skill,
                    (
                        f"Parent SKILL.md exceeds limit/budget "
                        f"(lines={len(lines)}/280, bytes={raw_bytes}/18432, "
                        f"est_tokens={l2_est['est_tokens']}/4500)"
                    ),
                )
            )
        elif len(lines) > 250 or l2_est["est_tokens"] > 2500:
            findings.append(
                Finding(
                    "L2-PARENT-SIZE",
                    "WARN",
                    rel_skill,
                    (
                        f"Parent SKILL.md over target budget "
                        f"(lines={len(lines)}/250 target, bytes={raw_bytes}, "
                        f"est_tokens={l2_est['est_tokens']}/2500 target)"
                    ),
                )
            )
        else:
            findings.append(
                Finding(
                    "L2-PARENT-SIZE",
                    "PASS",
                    rel_skill,
                    (
                        f"Parent SKILL.md within budget "
                        f"(lines={len(lines)}, bytes={raw_bytes}, est_tokens={l2_est['est_tokens']})"
                    ),
                )
            )
    else:
        if len(lines) > 500 or raw_bytes > 18432 or l2_est["est_tokens"] > 4500:
            findings.append(
                Finding(
                    "L2-CHILD-SIZE",
                    "ERROR",
                    rel_skill,
                    (
                        f"Child SKILL.md exceeds limit/budget "
                        f"(lines={len(lines)}/500, bytes={raw_bytes}/18432, "
                        f"est_tokens={l2_est['est_tokens']}/4500)"
                    ),
                )
            )
        elif len(lines) > 280 or l2_est["est_tokens"] > 2500:
            findings.append(
                Finding(
                    "L2-CHILD-SIZE",
                    "WARN",
                    rel_skill,
                    (
                        f"Child SKILL.md over target budget "
                        f"(lines={len(lines)}/280 target, bytes={raw_bytes}, "
                        f"est_tokens={l2_est['est_tokens']}/2500 target)"
                    ),
                )
            )
        else:
            findings.append(
                Finding(
                    "L2-CHILD-SIZE",
                    "PASS",
                    rel_skill,
                    (
                        f"Child SKILL.md within budget "
                        f"(lines={len(lines)}, bytes={raw_bytes}, est_tokens={l2_est['est_tokens']})"
                    ),
                )
            )

    # Collect L3 files for this skill
    refs = _collect_md_files(skill_dir, "references")
    tpls = _collect_md_files(skill_dir, "templates")
    l3_all = refs + tpls
    metrics["l3_files"] = len(l3_all)

    # Track linked files from SKILL.md and from references
    skill_resolved_links: set[pathlib.Path] = set()
    ref_resolved_links: set[pathlib.Path] = set()
    boundary = root.resolve() if is_parent else skill_dir.resolve()

    def _inspect_links(md_file: pathlib.Path, md_raw: str, collector: set[pathlib.Path] | None) -> None:
        rel_src = md_file.relative_to(root).as_posix()
        for tgt in _extract_links(md_raw):
            file_part = tgt.split("#", 1)[0]
            if not file_part:
                continue
            resolved = (md_file.parent / file_part).resolve()
            if not resolved.is_relative_to(boundary):
                findings.append(
                    Finding(
                        "L3-LINK-ESCAPE",
                        "ERROR",
                        rel_src,
                        f"Relative link {tgt!r} escapes skill boundary {boundary.name}",
                    )
                )
                continue
            if not resolved.exists():
                findings.append(
                    Finding(
                        "L3-LINK-ESCAPE",
                        "ERROR",
                        rel_src,
                        f"Broken relative link {tgt!r} -> {resolved} does not exist",
                    )
                )
                continue
            if collector is not None:
                collector.add(resolved)

    _inspect_links(skill_md, raw_text, skill_resolved_links)

    # Also treat explicit relative path mentions in SKILL.md prose as references
    skill_dir_resolved = skill_dir.resolve()
    for l3_path in l3_all:
        rel_from_skill = l3_path.relative_to(skill_dir).as_posix()
        if rel_from_skill in prose_body:
            skill_resolved_links.add(l3_path.resolve())

    for ref_path in refs:
        ref_rel = ref_path.relative_to(root).as_posix()
        ref_raw = ref_path.read_text(encoding="utf-8", errors="replace")
        ref_lines = ref_raw.splitlines()
        ref_est = estimate_tokens(ref_raw)
        is_non_runtime_catalog = (
            is_parent and ref_rel == "references/source-coverage-inventory.md"
        )
        metrics["l3_tokens"] += ref_est["est_tokens"]
        metrics["l3_chars_div_4"] += ref_est["chars_div_4"]
        if not is_non_runtime_catalog:
            metrics["ref_token_list"].append(ref_est["est_tokens"])

        if is_non_runtime_catalog:
            findings.append(
                Finding(
                    "L3-NON-RUNTIME-CATALOG",
                    "INFO",
                    ref_rel,
                    (
                        f"Non-runtime R1 provenance catalog exempted from 6000-token runtime cap "
                        f"(lines={len(ref_lines)}, est_tokens={ref_est['est_tokens']})"
                    ),
                )
            )
        elif len(ref_lines) > 800 or ref_est["est_tokens"] > 6000:
            findings.append(
                Finding(
                    "L3-REF-SIZE",
                    "ERROR",
                    ref_rel,
                    f"Reference exceeds hard cap (lines={len(ref_lines)}/800, est_tokens={ref_est['est_tokens']}/6000)",
                )
            )
        elif len(ref_lines) > 450 or ref_est["est_tokens"] > 4000:
            findings.append(
                Finding(
                    "L3-REF-SIZE",
                    "WARN",
                    ref_rel,
                    f"Reference over target budget (lines={len(ref_lines)}/450, est_tokens={ref_est['est_tokens']}/4000)",
                )
            )

        if len(ref_lines) > 250 and not _has_top_toc(ref_lines):
            sev = "ERROR" if len(ref_lines) > 300 else "WARN"
            findings.append(
                Finding(
                    "L3-TOC-MISSING",
                    sev,
                    ref_rel,
                    f"Reference has {len(ref_lines)} lines (> 250) without Top TOC in first 35 lines",
                )
            )

        _inspect_links(ref_path, ref_raw, ref_resolved_links)
        ref_prose = strip_fenced_code_blocks(ref_raw)
        for tpl_path in tpls:
            if tpl_path.name in ref_prose or tpl_path.relative_to(skill_dir).as_posix() in ref_prose:
                ref_resolved_links.add(tpl_path.resolve())

        if ref_path.resolve() not in skill_resolved_links:
            findings.append(
                Finding(
                    "L3-ORPHAN-REF",
                    "ERROR",
                    ref_rel,
                    f"Reference {ref_path.relative_to(skill_dir).as_posix()} is not linked by {rel_skill}",
                )
            )

        metrics["text_docs"][ref_rel] = (ref_prose, False)

    for tpl_path in tpls:
        tpl_rel = tpl_path.relative_to(root).as_posix()
        tpl_raw = tpl_path.read_text(encoding="utf-8", errors="replace")
        tpl_lines = tpl_raw.splitlines()
        tpl_est = estimate_tokens(tpl_raw)
        metrics["l3_tokens"] += tpl_est["est_tokens"]
        metrics["l3_chars_div_4"] += tpl_est["chars_div_4"]

        if len(tpl_lines) > 800 or tpl_est["est_tokens"] > 6000:
            findings.append(
                Finding(
                    "L3-REF-SIZE",
                    "ERROR",
                    tpl_rel,
                    f"Template exceeds hard cap (lines={len(tpl_lines)}/800, est_tokens={tpl_est['est_tokens']}/6000)",
                )
            )
        elif len(tpl_lines) > 450 or tpl_est["est_tokens"] > 4000:
            findings.append(
                Finding(
                    "L3-REF-SIZE",
                    "WARN",
                    tpl_rel,
                    f"Template over target budget (lines={len(tpl_lines)}/450, est_tokens={tpl_est['est_tokens']}/4000)",
                )
            )

        _inspect_links(tpl_path, tpl_raw, None)
        tpl_res = tpl_path.resolve()
        if tpl_res not in skill_resolved_links:
            if tpl_res in ref_resolved_links:
                findings.append(
                    Finding(
                        "L3-ORPHAN-TPL",
                        "WARN",
                        tpl_rel,
                        f"Template {tpl_path.relative_to(skill_dir).as_posix()} is linked in references/ but not directly in {rel_skill}",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "L3-ORPHAN-TPL",
                        "ERROR",
                        tpl_rel,
                        f"Orphan template {tpl_path.relative_to(skill_dir).as_posix()} is unreferenced by {rel_skill} and references/",
                    )
                )
        metrics["text_docs"][tpl_rel] = (strip_fenced_code_blocks(tpl_raw), False)

    _ = skill_dir_resolved
    return metrics


def _detect_cross_file_duplication(
    docs: dict[str, tuple[str, bool]],
    findings: list[Finding],
) -> list[dict[str, Any]]:
    """Detect duplicated paragraphs, 5-line windows, and non-R2 headings across files."""
    para_map: dict[str, set[str]] = {}
    para_samples: dict[str, str] = {}
    win_map: dict[str, set[str]] = {}
    win_samples: dict[str, str] = {}
    head_map: dict[str, set[str]] = {}
    head_samples: dict[str, str] = {}

    is_skill_map = {rel: is_skill for rel, (_, is_skill) in docs.items()}

    for rel, (prose, _) in docs.items():
        # 1. Normalized paragraphs
        for blk in re.split(r"\n\s*\n", prose):
            stripped = blk.strip()
            if not stripped:
                continue
            if stripped.lower().startswith("> **contents**:"):
                continue
            if re.fullmatch(r"#{1,6}\s+[^\n]+", stripped):
                continue
            norm = " ".join(stripped.split()).lower()
            if len(norm.split()) >= 35 or len(norm) >= 200:
                h = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]
                para_map.setdefault(h, set()).add(rel)
                para_samples.setdefault(h, stripped[:120].replace("\n", " "))

        # 2. 5-line consecutive prose windows (>= 35 chars/line)
        norm_lines: list[str] = []
        raw_lines: list[str] = []
        for ln in prose.splitlines():
            s = ln.strip()
            if not s:
                continue
            if s.lower().startswith("> **contents**:"):
                continue
            if _R2_PILLAR_HEADING_RE.match(s):
                continue
            norm_s = re.sub(r"\s+", " ", s).lower()
            norm_lines.append(norm_s)
            raw_lines.append(s)

        for idx in range(max(0, len(norm_lines) - 4)):
            win = norm_lines[idx : idx + 5]
            if all(len(w) >= 35 for w in win):
                key_str = "\n".join(win)
                h = hashlib.sha256(key_str.encode("utf-8")).hexdigest()[:16]
                win_map.setdefault(h, set()).add(rel)
                win_samples.setdefault(h, raw_lines[idx][:100])

        # 3. Non-R2 headings (SKILL.md and references/ only; templates share section titles)
        if "/templates/" in rel or rel.startswith("templates/"):
            continue
        for ln in prose.splitlines():
            hm = re.match(r"^(#{2,6})\s+(.+?)\s*$", ln)
            if not hm:
                continue
            full_h = hm.group(0).strip()
            if _STRUCTURAL_HEADING_RE.match(full_h):
                continue
            norm_h = re.sub(r"\s+", " ", full_h).lower()
            head_map.setdefault(norm_h, set()).add(rel)
            head_samples.setdefault(norm_h, full_h)

    duplicates: list[dict[str, Any]] = []

    for h, files in sorted(win_map.items()):
        if len(files) < 2:
            continue
        flist = sorted(files)
        has_skill = any(is_skill_map.get(f, False) for f in flist)
        has_ref = any("/references/" in f or f.startswith("references/") for f in flist)
        sev = "ERROR" if (has_skill and has_ref) else "WARN"
        msg = f"5+ consecutive duplicated prose lines across {flist}: {win_samples[h]!r}"
        duplicates.append({"kind": "5-line-window", "severity": sev, "files": flist, "sample": win_samples[h]})
        findings.append(Finding("DUP-CROSS-FILE", sev, ", ".join(flist), msg))

    for h, files in sorted(para_map.items()):
        if len(files) < 2:
            continue
        flist = sorted(files)
        msg = f"Duplicated paragraph across {flist}: {para_samples[h]!r}"
        duplicates.append({"kind": "paragraph", "severity": "WARN", "files": flist, "sample": para_samples[h]})
        findings.append(Finding("DUP-CROSS-FILE", "WARN", ", ".join(flist), msg))

    for norm_h, files in sorted(head_map.items()):
        if len(files) < 2:
            continue
        flist = sorted(files)
        msg = f"Duplicated non-R2 heading {head_samples[norm_h]!r} across {flist}"
        duplicates.append({"kind": "heading", "severity": "WARN", "files": flist, "sample": head_samples[norm_h]})
        findings.append(Finding("DUP-CROSS-FILE", "WARN", ", ".join(flist), msg))

    return duplicates


def _load_registry(root: pathlib.Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str | None]:
    reg_path = root / "registry.json"
    if not reg_path.is_file():
        return None, [], "Missing registry.json"
    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [], f"Invalid registry.json: {exc}"
    if not isinstance(reg, dict):
        return None, [], "registry.json root must be a JSON object"

    raw_children = reg.get("children")
    if raw_children is None:
        raw_children = reg.get("skills")

    entries: list[dict[str, Any]] = []
    if isinstance(raw_children, list):
        for item in raw_children:
            if isinstance(item, dict):
                entries.append(item)
    elif isinstance(raw_children, dict):
        for k, v in raw_children.items():
            if isinstance(v, dict):
                merged = {"id": k, **v}
                entries.append(merged)
    else:
        return reg, [], "registry.json missing 'children' or 'skills' list/mapping"

    return reg, entries, None


def _resolve_registry_child_paths(root: pathlib.Path, entry: dict[str, Any], cid: str) -> tuple[pathlib.Path, pathlib.Path]:
    raw_path = entry.get("path") or f"skills/{cid}"
    p = pathlib.Path(str(raw_path))
    if p.name == "SKILL.md" or p.suffix == ".md":
        skill_md = root / p
        skill_dir = skill_md.parent
    else:
        skill_dir = root / p
        skill_md = skill_dir / "SKILL.md"
    return skill_dir, skill_md


def _check_hygiene(root: pathlib.Path, findings: list[Finding]) -> None:
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dp = pathlib.Path(dirpath)
        rel_dir = dp.relative_to(root)

        # Prune .git and cache directories; check symlinks on dirs first
        kept_dirs: list[str] = []
        for d in dirnames:
            cand = dp / d
            if d == ".git":
                continue
            if cand.is_symlink():
                findings.append(
                    Finding(
                        "HYG-SYMLINK",
                        "ERROR",
                        cand.relative_to(root).as_posix(),
                        f"Symlink directory forbidden: {cand.relative_to(root).as_posix()}",
                    )
                )
                continue
            if d in SKIP_DIRS:
                continue
            kept_dirs.append(d)
        dirnames[:] = kept_dirs

        in_tests = bool(rel_dir.parts and rel_dir.parts[0] == "tests")
        for fn in filenames:
            cand = dp / fn
            rel_file = cand.relative_to(root).as_posix()
            if cand.is_symlink():
                findings.append(
                    Finding(
                        "HYG-SYMLINK",
                        "ERROR",
                        rel_file,
                        f"Symlink file forbidden: {rel_file}",
                    )
                )
            if not in_tests and fn in {"AGENTS.md", "GEMINI.md"}:
                findings.append(
                    Finding(
                        "HYG-FORBIDDEN-MD",
                        "ERROR",
                        rel_file,
                        f"Forbidden always-on instruction filename: {rel_file}",
                    )
                )


def audit_repository(
    root: pathlib.Path,
    *,
    skill_filter: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    findings: list[Finding] = []

    _check_hygiene(root, findings)

    reg, reg_entries, reg_err = _load_registry(root)
    if reg_err:
        sev = "ERROR" if (root / "skills").is_dir() else "WARN"
        findings.append(Finding("REG-PARITY", sev, "registry.json", reg_err))

    # Map registered children
    reg_by_id: dict[str, dict[str, Any]] = {}
    for entry in reg_entries:
        cid = str(entry.get("id") or entry.get("name") or "").strip()
        if cid:
            reg_by_id[cid] = entry

    # Discover active on-disk child skill directories (must have SKILL.md, or non-planned dir)
    disk_children: dict[str, pathlib.Path] = {}
    skills_root = root / "skills"
    if skills_root.is_dir():
        for child_dir in sorted(skills_root.iterdir()):
            if child_dir.is_dir() and not child_dir.name.startswith(".") and child_dir.name != "__pycache__":
                reg_entry = reg_by_id.get(child_dir.name)
                is_planned = bool(reg_entry and str(reg_entry.get("status", "")).strip().lower() == "planned")
                if (child_dir / "SKILL.md").is_file() or (not is_planned and any(child_dir.iterdir())):
                    disk_children[child_dir.name] = child_dir

    # Validate skill filter if provided
    parent_id = "appnwebsite-orchestrator"
    if isinstance(reg, dict) and isinstance(reg.get("parent"), dict):
        parent_id = str(reg["parent"].get("id") or reg["parent"].get("name") or parent_id)

    if skill_filter:
        known = {parent_id, "parent", *reg_by_id.keys(), *disk_children.keys()}
        if skill_filter not in known:
            findings.append(
                Finding(
                    "SKILL-NOT-FOUND",
                    "ERROR",
                    skill_filter,
                    f"Skill {skill_filter!r} not found in registry.json or skills/",
                )
            )

    # Registry parity reconciliation
    planned_pending = 0
    unregistered: list[str] = []
    missing_non_planned: list[str] = []
    token_drift_list: list[dict[str, Any]] = []

    for disk_name in sorted(disk_children):
        if skill_filter and skill_filter not in {disk_name, parent_id, "parent"}:
            continue
        if disk_name not in reg_by_id and reg is not None:
            unregistered.append(disk_name)
            findings.append(
                Finding(
                    "REG-PARITY",
                    "ERROR",
                    f"skills/{disk_name}",
                    f"On-disk child skill skills/{disk_name} is missing from registry.json",
                )
            )

    for cid, entry in reg_by_id.items():
        if skill_filter and skill_filter not in {cid, parent_id, "parent"}:
            continue
        _, skill_md_path = _resolve_registry_child_paths(root, entry, cid)
        status_val = str(entry.get("status", "")).strip().lower()
        if not skill_md_path.is_file():
            if status_val == "planned":
                planned_pending += 1
                findings.append(
                    Finding(
                        "REG-PARITY",
                        "INFO",
                        cid,
                        f"Planned child skill {cid!r} not yet materialized on disk (status=planned)",
                        planned_pending=True,
                    )
                )
            else:
                missing_non_planned.append(cid)
                findings.append(
                    Finding(
                        "REG-PARITY",
                        "ERROR",
                        cid,
                        f"Registered child skill {cid!r} missing {skill_md_path.relative_to(root).as_posix()} on disk",
                    )
                )

    # Audit Parent
    audit_parent = (skill_filter is None) or (skill_filter in {parent_id, "parent"})
    parent_metrics: dict[str, Any]
    if audit_parent:
        parent_metrics = _audit_single_skill(
            root=root,
            skill_dir=root,
            skill_name=parent_id,
            is_parent=True,
            findings=findings,
        )
    else:
        # Measure parent silently for active-stage calculation if present
        p_md = root / "SKILL.md"
        p_tok = estimate_tokens(p_md.read_text(encoding="utf-8", errors="replace"))["est_tokens"] if p_md.is_file() else 0
        parent_metrics = {
            "name": parent_id,
            "path": ".",
            "l1_chars": 0,
            "l1_tokens": 0,
            "l2_lines": 0,
            "l2_bytes": 0,
            "l2_tokens": p_tok,
            "l3_files": 0,
            "l3_tokens": 0,
            "ref_token_list": [],
            "text_docs": {},
        }

    # Audit Active Children
    children_report: list[dict[str, Any]] = []
    all_docs: dict[str, tuple[str, bool]] = dict(parent_metrics.get("text_docs", {}))
    all_ref_tokens: list[int] = list(parent_metrics.get("ref_token_list", []))
    active_child_tokens_by_id: dict[str, int] = {}

    for disk_name, child_dir in sorted(disk_children.items()):
        if skill_filter and skill_filter != disk_name:
            continue
        cm = _audit_single_skill(
            root=root,
            skill_dir=child_dir,
            skill_name=disk_name,
            is_parent=False,
            findings=findings,
        )
        all_docs.update(cm.pop("text_docs", {}))
        all_ref_tokens.extend(cm.pop("ref_token_list", []))
        active_child_tokens_by_id[disk_name] = cm["l2_tokens"]

        # Token drift check against registry.json
        entry = reg_by_id.get(disk_name)
        if entry is not None:
            reg_est = entry.get("estimated_tokens")
            if reg_est is None:
                reg_est = entry.get("token_budget")
            if not isinstance(reg_est, (int, float)) or reg_est <= 0:
                findings.append(
                    Finding(
                        "REG-TOKEN-DRIFT",
                        "WARN",
                        disk_name,
                        f"Registry entry {disk_name!r} missing valid positive estimated_tokens",
                    )
                )
            else:
                measured = cm["l2_tokens"]
                drift = abs(measured - float(reg_est)) / max(1.0, float(reg_est))
                drift_pct = round(drift * 100.0, 1)
                token_drift_list.append(
                    {
                        "id": disk_name,
                        "registry_estimated_tokens": int(reg_est),
                        "measured_l2_tokens": measured,
                        "drift_percent": drift_pct,
                    }
                )
                if drift > 0.60:
                    findings.append(
                        Finding(
                            "REG-TOKEN-DRIFT",
                            "WARN",
                            disk_name,
                            f"Token drift {drift_pct}% > 60% (registry={int(reg_est)}, measured={measured})",
                        )
                    )
                elif drift > 0.35:
                    findings.append(
                        Finding(
                            "REG-TOKEN-DRIFT",
                            "WARN",
                            disk_name,
                            f"Token drift {drift_pct}% > 35% (registry={int(reg_est)}, measured={measured})",
                        )
                    )

        children_report.append(
            {
                "name": cm["name"],
                "path": cm["path"],
                "l1_chars": cm["l1_chars"],
                "l1_tokens": cm["l1_tokens"],
                "l2_lines": cm["l2_lines"],
                "l2_bytes": cm["l2_bytes"],
                "l2_tokens": cm["l2_tokens"],
                "l3_files": cm["l3_files"],
                "l3_tokens": cm["l3_tokens"],
            }
        )

    parent_metrics.pop("text_docs", None)
    parent_metrics.pop("ref_token_list", None)

    # Cross-file duplication check
    duplicates = _detect_cross_file_duplication(all_docs, findings)

    # Active-Stage Context Savings Ratio (CTX-SAVINGS)
    full_suite_tokens = (
        parent_metrics["l2_tokens"]
        + parent_metrics["l3_tokens"]
        + sum(c["l2_tokens"] + c["l3_tokens"] for c in children_report)
    )
    planned_projected_extra = 0
    for cid, entry in reg_by_id.items():
        if cid not in active_child_tokens_by_id:
            est = entry.get("estimated_tokens") or entry.get("token_budget") or 2200
            planned_projected_extra += int(est) + 4000
    projected_full_suite_tokens = full_suite_tokens + planned_projected_extra

    ceiling = 2
    if isinstance(reg, dict) and isinstance(reg.get("parent"), dict):
        c_val = reg["parent"].get("active_child_ceiling")
        if isinstance(c_val, int) and c_val > 0:
            ceiling = c_val

    sorted_child_l2 = sorted((c["l2_tokens"] for c in children_report), reverse=True)
    top_k_child_l2 = sum(sorted_child_l2[:ceiling])

    if all_ref_tokens:
        s_refs = sorted(all_ref_tokens)
        mid = len(s_refs) // 2
        median_ref = s_refs[mid] if len(s_refs) % 2 == 1 else round((s_refs[mid - 1] + s_refs[mid]) / 2)
    else:
        median_ref = 0

    active_stage_tokens = parent_metrics["l2_tokens"] + top_k_child_l2 + median_ref + 400
    if full_suite_tokens > 0:
        savings_ratio = max(0.0, round(1.0 - (active_stage_tokens / full_suite_tokens), 4))
    else:
        savings_ratio = 0.0

    # Per-stage budget estimates
    stage_budgets: dict[str, int] = {}
    for st in STAGES:
        stage_child_toks: list[int] = []
        for cid, entry in reg_by_id.items():
            c_stages = [str(s).upper() for s in entry.get("spiral_stages", [])]
            if st.upper() in c_stages:
                if cid in active_child_tokens_by_id:
                    stage_child_toks.append(active_child_tokens_by_id[cid])
                else:
                    est = entry.get("estimated_tokens") or entry.get("token_budget") or 0
                    stage_child_toks.append(int(est))
        top_stage_children = sum(sorted(stage_child_toks, reverse=True)[:ceiling])
        stage_budgets[st] = parent_metrics["l2_tokens"] + top_stage_children + median_ref + 400

    findings.append(
        Finding(
            "CTX-SAVINGS",
            "INFO",
            "suite",
            (
                f"full_suite_tokens={full_suite_tokens}, active_stage_tokens={active_stage_tokens}, "
                f"savings_ratio={savings_ratio:.4f}"
            ),
        )
    )

    # Apply --strict promotion
    if strict:
        for f in findings:
            if f.severity == "WARN" or (f.id == "REG-PARITY" and f.planned_pending):
                f.severity = "ERROR"

    errors_count = sum(1 for f in findings if f.severity == "ERROR")
    warnings_count = sum(1 for f in findings if f.severity == "WARN")
    exit_code = 1 if errors_count > 0 else 0
    overall_status = "FAIL" if errors_count > 0 else ("WARN" if warnings_count > 0 else "PASS")

    skills_audited = (1 if audit_parent and (root / "SKILL.md").is_file() else 0) + len(children_report)

    return {
        "schema_version": "1.0.0",
        "root": str(root),
        "status": overall_status,
        "exit_code": exit_code,
        "summary": {
            "errors": errors_count,
            "warnings": warnings_count,
            "skills_audited": skills_audited,
            "planned_pending": planned_pending,
            "full_suite_tokens": full_suite_tokens,
            "projected_full_suite_tokens": projected_full_suite_tokens,
            "active_stage_tokens": active_stage_tokens,
            "active_stage_savings_ratio": savings_ratio,
        },
        "parent": {
            "name": parent_metrics["name"],
            "l1_chars": parent_metrics["l1_chars"],
            "l1_tokens": parent_metrics["l1_tokens"],
            "l1_chars_div_4": parent_metrics.get("l1_chars_div_4", 0),
            "l2_lines": parent_metrics["l2_lines"],
            "l2_bytes": parent_metrics["l2_bytes"],
            "l2_tokens": parent_metrics["l2_tokens"],
            "l2_chars_div_4": parent_metrics.get("l2_chars_div_4", 0),
            "l3_files": parent_metrics["l3_files"],
            "l3_tokens": parent_metrics["l3_tokens"],
            "l3_chars_div_4": parent_metrics.get("l3_chars_div_4", 0),
        },
        "children": children_report,
        "stage_budgets": stage_budgets,
        "duplicates": duplicates,
        "registry_parity": {
            "registered": len(reg_by_id),
            "on_disk": len(disk_children),
            "planned_pending": planned_pending,
            "unregistered": unregistered,
            "missing": missing_non_planned,
            "token_drift": token_drift_list,
        },
        "findings": [f.to_dict() for f in findings],
    }


def _make_r2_doc(title: str, extra_lines: int = 0, include_toc: bool = False) -> str:
    toc = (
        "> **Contents**: [1. Decision Framework](#1-decision-framework) | "
        "[2. Step-by-Step Workflow](#2-step-by-step-workflow) | "
        "[3. Reusable Artifact & Template](#3-reusable-artifact--template) | "
        "[4. Verification Checklist](#4-verification-checklist) | "
        "[5. Hard Quality Gate](#5-hard-quality-gate) | "
        "[6. Anti-Patterns](#6-anti-patterns)\n\n"
        if include_toc
        else ""
    )
    body = (
        f"# {title}\n\n"
        f"{toc}"
        "## 1. Decision Framework\n\n"
        "Evaluate the simplest high-craft option before adding any complex dependency.\n\n"
        "## 2. Step-by-Step Workflow\n\n"
        "1. Gather constraints and verify inputs before making edits.\n\n"
        "## 3. Reusable Artifact & Template\n\n"
        "Document schema fields cleanly in [Template](../templates/sample-tpl.md).\n\n"
        "## 4. Verification Checklist\n\n"
        "- [ ] Confirm deterministic validation commands exit zero.\n\n"
        "## 5. Hard Quality Gate\n\n"
        "PASS when all checks succeed; FAIL on any broken link.\n\n"
        "## 6. Anti-Patterns\n\n"
        "- Avoid copying long reference prose into SKILL.md.\n"
    )
    if extra_lines > 0:
        filler = "\n".join(
            f"- Unique technical guideline item {i} for {title} covering boundary validation."
            for i in range(1, extra_lines + 1)
        )
        body += "\n" + filler + "\n"
    return body


def _build_base_valid_suite(base: pathlib.Path) -> None:
    (base / "references").mkdir(parents=True, exist_ok=True)
    (base / "templates").mkdir(parents=True, exist_ok=True)
    (base / "skills" / "child-alpha" / "references").mkdir(parents=True, exist_ok=True)
    (base / "skills" / "child-alpha" / "templates").mkdir(parents=True, exist_ok=True)

    parent_md = (
        "---\n"
        "name: appnwebsite-orchestrator\n"
        "description: Lean parent router for progressive disclosure and Spiral verification.\n"
        "license: MIT\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
        "---\n\n"
        "# Parent Orchestrator\n\n"
        "- [Core Governance](references/core-gov.md)\n"
        "- [Spiral Guide](references/spiral-guide.md)\n"
        "- [Charter Template](templates/charter.md)\n"
        "- [Child Alpha](skills/child-alpha/SKILL.md)\n"
    )
    (base / "SKILL.md").write_text(parent_md, encoding="utf-8")

    # Parent references (one > 260 lines WITH Top TOC + fenced code block containing fake xml/headings)
    core_gov = _make_r2_doc("Core Governance", extra_lines=255, include_toc=True)
    core_gov += (
        "\n```xml\n"
        "<fake-xml-inside-fence>allowed</fake-xml-inside-fence>\n"
        "## 1. Decision Framework\n"
        "```\n"
    )
    (base / "references" / "core-gov.md").write_text(core_gov, encoding="utf-8")
    (base / "references" / "spiral-guide.md").write_text(
        _make_r2_doc("Spiral Guide", extra_lines=40, include_toc=False).replace(
            "../templates/sample-tpl.md", "../templates/charter.md"
        ),
        encoding="utf-8",
    )
    (base / "references" / "core-gov.md").write_text(
        core_gov.replace("../templates/sample-tpl.md", "../templates/charter.md"),
        encoding="utf-8",
    )
    (base / "templates" / "charter.md").write_text("# Charter Template\n\nMinimal charter fields.\n", encoding="utf-8")

    # Child alpha
    child_md = (
        "---\n"
        "name: child-alpha\n"
        "description: Standalone child skill for progressive disclosure self-test verification.\n"
        "license: MIT\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
        "---\n\n"
        "# Child Alpha\n\n"
        "- [Child Spec](references/child-spec.md)\n"
        "- [Child Template](templates/child-tpl.md)\n"
    )
    (base / "skills" / "child-alpha" / "SKILL.md").write_text(child_md, encoding="utf-8")
    (base / "skills" / "child-alpha" / "references" / "child-spec.md").write_text(
        _make_r2_doc("Child Alpha Specification", extra_lines=50).replace(
            "../templates/sample-tpl.md", "../templates/child-tpl.md"
        ),
        encoding="utf-8",
    )
    (base / "skills" / "child-alpha" / "templates" / "child-tpl.md").write_text(
        "# Child Alpha Template\n\nConcrete output artifact.\n", encoding="utf-8"
    )

    # Estimate child tokens cleanly for registry parity
    child_toks = estimate_tokens(child_md)["est_tokens"]
    reg = {
        "schema_version": "1.0.0",
        "parent": {"id": "appnwebsite-orchestrator", "active_child_ceiling": 2},
        "skills": [
            {
                "id": "child-alpha",
                "name": "child-alpha",
                "path": "skills/child-alpha/SKILL.md",
                "spiral_stages": ["Q1", "3A"],
                "triggers": ["alpha"],
                "depends_on": [],
                "inputs": ["charter.md"],
                "outputs": ["child-tpl.md"],
                "estimated_tokens": child_toks,
                "status": "active",
            }
        ],
    }
    (base / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")


def run_self_tests() -> tuple[bool, list[dict[str, Any]]]:
    """Run all 10 isolated self-test scenarios in tempfile.TemporaryDirectory."""
    results: list[dict[str, Any]] = []

    def _record(name: str, passed: bool, detail: str) -> None:
        results.append({"test": name, "passed": passed, "detail": detail})

    # 1. test_valid_minimal_suite_passes
    with tempfile.TemporaryDirectory(prefix="atb_t1_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        rep = audit_repository(root)
        ok = (
            rep["exit_code"] == 0
            and rep["summary"]["errors"] == 0
            and rep["summary"]["active_stage_savings_ratio"] > 0
        )
        _record(
            "test_valid_minimal_suite_passes",
            ok,
            f"exit={rep['exit_code']} errors={rep['summary']['errors']} ratio={rep['summary']['active_stage_savings_ratio']}",
        )

    # 2. test_l1_xml_injection_fails
    with tempfile.TemporaryDirectory(prefix="atb_t2_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        # First verify fenced <script> in body does NOT trigger L1-XML-INJECT
        s_path = root / "SKILL.md"
        orig = s_path.read_text(encoding="utf-8")
        s_path.write_text(orig + "\n```html\n<script>safe_in_fence()</script>\n```\n", encoding="utf-8")
        rep_clean = audit_repository(root)
        no_false_xml = not any(f["id"] == "L1-XML-INJECT" for f in rep_clean["findings"])

        # Now inject <script> into frontmatter description
        s_path.write_text(
            orig.replace(
                "Lean parent router for progressive disclosure and Spiral verification.",
                "Lean router <script>alert(1)</script> injection.",
            ),
            encoding="utf-8",
        )
        rep_bad = audit_repository(root)
        has_xml_err = rep_bad["exit_code"] == 1 and any(
            f["id"] == "L1-XML-INJECT" and f["severity"] == "ERROR" for f in rep_bad["findings"]
        )
        _record(
            "test_l1_xml_injection_fails",
            no_false_xml and has_xml_err,
            f"no_false_xml={no_false_xml} has_xml_err={has_xml_err}",
        )

    # 3. test_l2_line_and_token_bloat_fails
    with tempfile.TemporaryDirectory(prefix="atb_t3_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        s_path = root / "SKILL.md"
        bloat = "\n".join(f"- Unique bloated router entry {i} exceeding line budget." for i in range(1, 361))
        s_path.write_text(s_path.read_text(encoding="utf-8") + "\n" + bloat + "\n", encoding="utf-8")
        rep = audit_repository(root)
        ok = rep["exit_code"] == 1 and any(
            f["id"] == "L2-PARENT-SIZE" and f["severity"] == "ERROR" for f in rep["findings"]
        )
        _record("test_l2_line_and_token_bloat_fails", ok, f"exit={rep['exit_code']}")

    # 4. test_l3_orphan_and_child_escape_fails
    with tempfile.TemporaryDirectory(prefix="atb_t4_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        (root / "references" / "orphan.md").write_text("# Orphan Ref\n\nUnlinked.\n", encoding="utf-8")
        (root / "templates" / "orphan-tpl.md").write_text("# Orphan Tpl\n\nUnlinked.\n", encoding="utf-8")
        child_md = root / "skills" / "child-alpha" / "SKILL.md"
        child_md.write_text(
            child_md.read_text(encoding="utf-8") + "\n- [Escape](../../SKILL.md)\n",
            encoding="utf-8",
        )
        rep = audit_repository(root)
        err_ids = {f["id"] for f in rep["findings"] if f["severity"] == "ERROR"}
        ok = rep["exit_code"] == 1 and {"L3-ORPHAN-REF", "L3-ORPHAN-TPL", "L3-LINK-ESCAPE"}.issubset(err_ids)
        _record("test_l3_orphan_and_child_escape_fails", ok, f"err_ids={sorted(err_ids)}")

    # 5. test_cross_file_duplication_detected
    with tempfile.TemporaryDirectory(prefix="atb_t5_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        dup_block = "\n".join(
            f"Duplicated guidance line number {i} exceeding thirty-five characters easily."
            for i in range(1, 7)
        )
        dup_para = (
            "This intentionally duplicated forty word paragraph verifies that cross file prose "
            "duplication detection flags large copy pasted explanation blocks across distinct "
            "reference modules while ignoring standard structural pillar headings and table of "
            "contents strips cleanly across the entire repository."
        )
        s_path = root / "SKILL.md"
        s_path.write_text(s_path.read_text(encoding="utf-8") + "\n" + dup_block + "\n", encoding="utf-8")
        r1 = root / "references" / "spiral-guide.md"
        r1.write_text(r1.read_text(encoding="utf-8") + "\n" + dup_block + "\n\n" + dup_para + "\n", encoding="utf-8")
        r2 = root / "references" / "core-gov.md"
        r2.write_text(r2.read_text(encoding="utf-8") + "\n" + dup_para + "\n", encoding="utf-8")

        rep = audit_repository(root)
        dup_findings = [f for f in rep["findings"] if f["id"] == "DUP-CROSS-FILE"]
        no_r2_false = not any("1. Decision Framework" in f["message"] for f in dup_findings)
        ok = bool(dup_findings) and no_r2_false
        _record("test_cross_file_duplication_detected", ok, f"dups={len(dup_findings)} no_r2_false={no_r2_false}")

    # 6. test_registry_mismatch_detected
    with tempfile.TemporaryDirectory(prefix="atb_t6_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        # Add unregistered on-disk child
        unreg = root / "skills" / "unreg-beta"
        unreg.mkdir(parents=True, exist_ok=True)
        (unreg / "SKILL.md").write_text(
            "---\nname: unreg-beta\ndescription: Unregistered child.\nlicense: MIT\nmetadata:\n  version: \"1.0.0\"\n---\n# Beta\n",
            encoding="utf-8",
        )
        # Skew child-alpha estimated_tokens > 60% and add missing active child
        reg_path = root / "registry.json"
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        reg["skills"][0]["estimated_tokens"] = 9000
        reg["skills"].append(
            {
                "id": "missing-gamma",
                "name": "missing-gamma",
                "path": "skills/missing-gamma/SKILL.md",
                "spiral_stages": ["3B"],
                "triggers": ["gamma"],
                "depends_on": [],
                "inputs": [],
                "outputs": [],
                "estimated_tokens": 1200,
                "status": "active",
            }
        )
        reg_path.write_text(json.dumps(reg, indent=2), encoding="utf-8")
        rep = audit_repository(root)
        f_ids = {f["id"] for f in rep["findings"]}
        ok = rep["exit_code"] == 1 and {"REG-PARITY", "REG-TOKEN-DRIFT"}.issubset(f_ids)
        _record("test_registry_mismatch_detected", ok, f"ids={sorted(f_ids)}")

    # 7. test_block_scalar_trailing_ws_and_variants_pass
    with tempfile.TemporaryDirectory(prefix="atb_t7_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        s_path = root / "SKILL.md"
        orig = s_path.read_text(encoding="utf-8")
        target_line = "description: Lean parent router for progressive disclosure and Spiral verification."
        headers = (">  ", ">-  ", ">+", "|+", ">2", "|2", ">-2", "|+2", ">  # comment")
        all_hdr_ok = True
        for hdr in headers:
            s_path.write_text(
                orig.replace(
                    target_line,
                    f"description: {hdr}\n  Lean parent router for progressive disclosure and Spiral verification.",
                ),
                encoding="utf-8",
            )
            rep = audit_repository(root)
            if rep["exit_code"] != 0 or any(
                f["severity"] == "ERROR" for f in rep["findings"]
            ):
                all_hdr_ok = False
                break
        # Negative sub-check: inline XML or unspaced comment injection must still fail
        neg_xml_ok = True
        for bad_hdr in ("> <script>", "># <script>"):
            s_path.write_text(
                orig.replace(
                    target_line,
                    f"description: {bad_hdr}\n  Lean parent router.",
                ),
                encoding="utf-8",
            )
            rep_bad = audit_repository(root)
            if not (
                rep_bad["exit_code"] == 1
                and any(
                    f["id"] == "L1-XML-INJECT" and f["severity"] == "ERROR"
                    for f in rep_bad["findings"]
                )
            ):
                neg_xml_ok = False
                break
        ok = all_hdr_ok and neg_xml_ok
        _record(
            "test_block_scalar_trailing_ws_and_variants_pass",
            ok,
            f"all_hdr_ok={all_hdr_ok} neg_xml_ok={neg_xml_ok}",
        )

    # 8. test_inline_code_link_immunity
    with tempfile.TemporaryDirectory(prefix="atb_t8_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        s_path = root / "SKILL.md"
        orig = s_path.read_text(encoding="utf-8")
        s_path.write_text(
            orig
            + "\nExample prose: `[foo](missing.md)` and `` `[bar](../../outside.md)` `` and [`Core`](references/core-gov.md)\n",
            encoding="utf-8",
        )
        rep_ok = audit_repository(root)
        clean_ok = rep_ok["exit_code"] == 0 and not any(
            f["id"] == "L3-LINK-ESCAPE" for f in rep_ok["findings"]
        )
        # Negative sub-check: real broken link outside inline code must fail
        s_path.write_text(orig + "\nReal broken: [real](missing.md)\n", encoding="utf-8")
        rep_bad = audit_repository(root)
        bad_ok = rep_bad["exit_code"] == 1 and any(
            f["id"] == "L3-LINK-ESCAPE" and f["severity"] == "ERROR"
            for f in rep_bad["findings"]
        )
        _record(
            "test_inline_code_link_immunity",
            clean_ok and bad_ok,
            f"clean_ok={clean_ok} bad_ok={bad_ok}",
        )

    # 9. test_mixed_list_in_dict_frontmatter_fails
    with tempfile.TemporaryDirectory(prefix="atb_t9_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        child_md = root / "skills" / "child-alpha" / "SKILL.md"
        orig_child = child_md.read_text(encoding="utf-8")
        child_md.write_text(
            orig_child.replace(
                '  version: "1.0.0"',
                '  version: "1.0.0"\n  spiral_stages:\n    - Q1\n    - 3A',
            ),
            encoding="utf-8",
        )
        rep1 = audit_repository(root)
        list_in_dict_ok = rep1["exit_code"] == 1 and any(
            f["id"] == "FM_YAML_MIXED" and f["severity"] == "ERROR"
            for f in rep1["findings"]
        )
        # Also test dict key inside nested list
        child_md.write_text(
            orig_child.replace(
                "metadata:",
                "tags:\n  - alpha\n  bad: beta\nmetadata:",
            ),
            encoding="utf-8",
        )
        rep2 = audit_repository(root)
        dict_in_list_ok = rep2["exit_code"] == 1 and any(
            f["id"] == "FM_YAML_MIXED" and f["severity"] == "ERROR"
            for f in rep2["findings"]
        )
        _record(
            "test_mixed_list_in_dict_frontmatter_fails",
            list_in_dict_ok and dict_in_list_ok,
            f"list_in_dict={list_in_dict_ok} dict_in_list={dict_in_list_ok}",
        )

    # 10. test_non_runtime_catalog_size_exemption_and_strict_runtime_cap
    with tempfile.TemporaryDirectory(prefix="atb_t10_") as td:
        root = pathlib.Path(td)
        _build_base_valid_suite(root)
        base_rep = audit_repository(root)
        base_active_tokens = base_rep["summary"]["active_stage_tokens"]

        parent_md = root / "SKILL.md"
        orig_parent = parent_md.read_text(encoding="utf-8")
        inv_path = root / "references" / "source-coverage-inventory.md"

        catalog_rows = "\n".join(
            f"| skill-{i:03d} | MIT | Relevant | Reused pattern {i} for catalog entry verification across lifecycle stage Q{(i % 4) + 1} |"
            for i in range(1, 315)
        )
        inv_with_toc = (
            "# Source-Coverage Inventory\n\n"
            "> **Contents**: [1. Local Skills](#1-local-skills)\n\n"
            "## 1. Local Skills\n\n"
            "| Skill | License | Classification | Disposition |\n"
            "|---|---|---|---|\n"
            f"{catalog_rows}\n"
        )
        inv_path.write_text(inv_with_toc, encoding="utf-8")
        parent_md.write_text(
            orig_parent + "- [Inventory](references/source-coverage-inventory.md)\n",
            encoding="utf-8",
        )
        rep_ok = audit_repository(root)
        info_ok = (
            rep_ok["exit_code"] == 0
            and any(
                f["id"] == "L3-NON-RUNTIME-CATALOG"
                and f["severity"] == "INFO"
                and f["target"] == "references/source-coverage-inventory.md"
                for f in rep_ok["findings"]
            )
            and not any(
                f["id"] == "L3-REF-SIZE"
                and f["target"] == "references/source-coverage-inventory.md"
                for f in rep_ok["findings"]
            )
            and rep_ok["summary"]["active_stage_tokens"] == base_active_tokens + (rep_ok["parent"]["l2_tokens"] - base_rep["parent"]["l2_tokens"])
        )

        # Without Top TOC and without link in SKILL.md, L3-TOC-MISSING and L3-ORPHAN-REF must STILL fail
        inv_no_toc = (
            "# Source-Coverage Inventory\n\n"
            "## 1. Local Skills\n\n"
            "| Skill | License | Classification | Disposition |\n"
            "|---|---|---|---|\n"
            f"{catalog_rows}\n"
        )
        inv_path.write_text(inv_no_toc, encoding="utf-8")
        parent_md.write_text(orig_parent, encoding="utf-8")
        rep_unlinked = audit_repository(root)
        inv_errs = {
            f["id"]
            for f in rep_unlinked["findings"]
            if f["severity"] == "ERROR"
            and f["target"] == "references/source-coverage-inventory.md"
        }
        toc_orphan_enforced = rep_unlinked["exit_code"] == 1 and {
            "L3-TOC-MISSING",
            "L3-ORPHAN-REF",
        }.issubset(inv_errs)

        # Normal runtime reference > 6000 tokens must STILL fail L3-REF-SIZE ERROR
        inv_path.write_text(inv_with_toc, encoding="utf-8")
        parent_md.write_text(
            orig_parent
            + "- [Inventory](references/source-coverage-inventory.md)\n"
            + "- [Huge Runtime](references/huge-runtime.md)\n",
            encoding="utf-8",
        )
        huge_rows = "\n".join(
            f"- Runtime guideline entry {i:03d} with unique technical decision criteria and operational details for strict verification."
            for i in range(1, 310)
        )
        huge_ref = root / "references" / "huge-runtime.md"
        huge_ref.write_text(
            "# Huge Runtime\n\n> **Contents**: [1. Decision Framework](#1-decision-framework)\n\n"
            "## 1. Decision Framework\n\n" + huge_rows + "\n",
            encoding="utf-8",
        )
        rep_huge = audit_repository(root)
        runtime_cap_enforced = rep_huge["exit_code"] == 1 and any(
            f["id"] == "L3-REF-SIZE"
            and f["severity"] == "ERROR"
            and f["target"] == "references/huge-runtime.md"
            for f in rep_huge["findings"]
        )

        # Child skill reference named source-coverage-inventory.md must NOT be exempted
        huge_ref.unlink()
        parent_md.write_text(
            orig_parent + "- [Inventory](references/source-coverage-inventory.md)\n",
            encoding="utf-8",
        )
        child_inv = root / "skills" / "child-alpha" / "references" / "source-coverage-inventory.md"
        child_inv.write_text(
            "# Child Catalog\n\n> **Contents**: [1. Items](#1-items)\n\n## 1. Items\n\n" + huge_rows + "\n",
            encoding="utf-8",
        )
        child_md = root / "skills" / "child-alpha" / "SKILL.md"
        child_md.write_text(
            child_md.read_text(encoding="utf-8") + "- [Child Inv](references/source-coverage-inventory.md)\n",
            encoding="utf-8",
        )
        rep_child_inv = audit_repository(root)
        child_not_exempt = rep_child_inv["exit_code"] == 1 and any(
            f["id"] == "L3-REF-SIZE"
            and f["severity"] == "ERROR"
            and f["target"] == "skills/child-alpha/references/source-coverage-inventory.md"
            for f in rep_child_inv["findings"]
        )

        ok = info_ok and toc_orphan_enforced and runtime_cap_enforced and child_not_exempt
        _record(
            "test_non_runtime_catalog_size_exemption_and_strict_runtime_cap",
            ok,
            (
                f"info_ok={info_ok} toc_orphan_enforced={toc_orphan_enforced} "
                f"runtime_cap_enforced={runtime_cap_enforced} child_not_exempt={child_not_exempt}"
            ),
        )

    all_passed = all(r["passed"] for r in results)
    return all_passed, results


def _print_human_report(report: dict[str, Any]) -> None:
    s = report["summary"]
    p = report["parent"]
    print(
        f"[{report['status']}] root={report['root']} | "
        f"skills={s['skills_audited']} planned_pending={s['planned_pending']} "
        f"errors={s['errors']} warnings={s['warnings']}"
    )
    print(
        f"  Parent ({p['name']}): L1={p['l1_chars']}c/{p['l1_tokens']}tok | "
        f"L2={p['l2_lines']}L/{p['l2_bytes']}B/{p['l2_tokens']}tok | "
        f"L3={p['l3_files']}files/{p['l3_tokens']}tok"
    )
    print(
        f"  Context Savings: full_suite={s['full_suite_tokens']}tok | "
        f"active_stage={s['active_stage_tokens']}tok | "
        f"savings_ratio={s['active_stage_savings_ratio']:.2%}"
    )
    for ch in report["children"]:
        print(
            f"  Child ({ch['name']}): L1={ch['l1_chars']}c/{ch['l1_tokens']}tok | "
            f"L2={ch['l2_lines']}L/{ch['l2_bytes']}B/{ch['l2_tokens']}tok | "
            f"L3={ch['l3_files']}files/{ch['l3_tokens']}tok"
        )
    for f in report["findings"]:
        if f["severity"] in {"ERROR", "WARN"}:
            print(f"  {f['severity']:5s} [{f['id']}] {f['target']}: {f['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="audit_token_budget.py",
        usage="audit_token_budget.py [--root PATH] [--skill NAME] [--json] [--strict] [--self-test] [path]",
        description="Audit L1/L2/L3 token budgets, progressive disclosure, links, duplication, and registry parity.",
    )
    # Rename default argparse group title so help text avoids the word 'positional'
    parser._positionals.title = "target path"  # noqa: SLF001
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Optional suite root directory override",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Suite root directory to audit (default: .)",
    )
    parser.add_argument(
        "--skill",
        default=None,
        help="Filter audit to one skill ID (parent or child)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON report only to stdout",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote all warnings and planned-pending gaps to errors",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated self-test suite in temporary directories",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        passed, results = run_self_tests()
        if args.json:
            print(json.dumps({"self_test_passed": passed, "results": results}, indent=2))
        else:
            for r in results:
                tag = "PASS" if r["passed"] else "FAIL"
                print(f"[{tag}] {r['test']}: {r['detail']}")
            print(f"Self-test summary: {sum(1 for r in results if r['passed'])}/{len(results)} passed")
        return 0 if passed else 1

    target = pathlib.Path(args.path if args.path is not None else args.root)
    if not target.exists() or not target.is_dir():
        msg = f"Target root directory does not exist: {target}"
        if args.json:
            print(json.dumps({"status": "ERROR", "exit_code": 2, "error": msg}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    report = audit_repository(target, skill_filter=args.skill, strict=args.strict)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human_report(report)

    return int(report["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
