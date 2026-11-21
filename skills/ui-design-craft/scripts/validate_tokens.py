#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W3C Design Tokens Community Group (DTCG) structural, alias, cycle, and type validator.

Pure Python 3 standard library only (optionally imports sibling check_contrast for --contrast).
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

SUPPORTED_DTCG_TYPES: frozenset[str] = frozenset({
    "color", "dimension", "fontFamily", "fontWeight", "duration",
    "cubicBezier", "number", "shadow", "typography", "border",
    "strokeStyle", "transition", "gradient",
})

_ALIAS_FULL_RE = re.compile(r"^\{([a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*)\}$")
_ALIAS_EMBED_RE = re.compile(r"\{([a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*)\}")
_COLOR_RE = re.compile(
    r"^(?:#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})|"
    r"rgba?\([^)]+\)|hsla?\([^)]+\)|oklch\([^)]+\)|oklab\([^)]+\))$",
    re.IGNORECASE,
)
_DIMENSION_RE = re.compile(r"^(?:0|-?\d+(?:\.\d+)?(?:px|rem|em|%|vw|vh|dvh|pt))$")
_DURATION_RE = re.compile(r"^\d+(?:\.\d+)?(?:ms|s)$")
_BANNED_FONT_RE = re.compile(
    r"\b(?:Inter|Roboto|Arial|Open Sans|Helvetica)\b", re.IGNORECASE
)
_FONT_WEIGHT_WORDS = frozenset({
    "thin", "hairline", "extralight", "ultra-light", "light",
    "normal", "regular", "medium", "semibold", "semi-bold",
    "bold", "extrabold", "extra-bold", "black", "heavy",
})


def _extract_aliases(val: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(val, str):
        refs.extend(_ALIAS_EMBED_RE.findall(val))
    elif isinstance(val, dict):
        for v in val.values():
            refs.extend(_extract_aliases(v))
    elif isinstance(val, list):
        for item in val:
            refs.extend(_extract_aliases(item))
    return refs


def _collect_leaves(
    node: dict[str, Any],
    path_parts: list[str],
    inherited_type: str | None,
    leaves: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    group_type = node.get("$type", inherited_type)
    non_meta = {k: v for k, v in node.items() if not k.startswith("$")}

    # A dict is a token leaf if it declares $value, has no non-meta children (malformed $-only dict),
    # or declares $type with no child groups/tokens.
    if (
        "$value" in node
        or (path_parts and not non_meta)
        or ("$type" in node and not any(isinstance(v, dict) for v in non_meta.values()) and path_parts)
    ):
        dotted = ".".join(path_parts)
        if "$value" not in node or node["$value"] is None:
            errors.append(f"Token '{dotted}' is missing required '$value'.")
            return
        resolved_type = node.get("$type") or inherited_type
        if not resolved_type:
            errors.append(f"Token '{dotted}' has no '$type' and no inherited group '$type'.")
            return
        if resolved_type not in SUPPORTED_DTCG_TYPES:
            errors.append(f"Token '{dotted}' has unsupported '$type': {resolved_type!r}.")
            return
        leaves[dotted] = {
            "path": dotted,
            "type": resolved_type,
            "value": node["$value"],
            "aliases": _extract_aliases(node["$value"]),
        }
        return

    for k, v in non_meta.items():
        if isinstance(v, dict):
            _collect_leaves(v, [*path_parts, k], group_type, leaves, errors)
        else:
            dotted = ".".join([*path_parts, k])
            errors.append(f"Invalid non-object token entry at '{dotted}': {type(v).__name__}")


def _detect_cycles_and_dangling(
    leaves: dict[str, dict[str, Any]], errors: list[str]
) -> dict[str, Any]:
    # Check dangling aliases first
    for path, info in leaves.items():
        for ref in info["aliases"]:
            if ref not in leaves:
                errors.append(f"Dangling alias in '{path}': '{{{ref}}}' does not exist.")

    # 3-color DFS cycle detection: 0=UNVISITED, 1=VISITING, 2=DONE
    state: dict[str, int] = {p: 0 for p in leaves}
    stack: list[str] = []
    cycles_found: set[tuple[str, ...]] = set()

    def dfs(cur: str) -> None:
        state[cur] = 1
        stack.append(cur)
        for nxt in leaves[cur]["aliases"]:
            if nxt not in leaves:
                continue
            if state[nxt] == 1:
                idx = stack.index(nxt)
                cyc = tuple([*stack[idx:], nxt])
                if cyc not in cycles_found:
                    cycles_found.add(cyc)
                    errors.append("Circular alias detected: " + " -> ".join(cyc))
            elif state[nxt] == 0:
                dfs(nxt)
        stack.pop()
        state[cur] = 2

    for node_path in leaves:
        if state[node_path] == 0:
            dfs(node_path)

    if errors:
        return {}

    # Resolve full alias values
    resolved: dict[str, Any] = {}

    def resolve_val(val: Any) -> Any:
        if isinstance(val, str):
            m = _ALIAS_FULL_RE.match(val.strip())
            if m:
                return resolve_token(m.group(1))
            return _ALIAS_EMBED_RE.sub(lambda mm: str(resolve_token(mm.group(1))), val)
        if isinstance(val, dict):
            return {k: resolve_val(v) for k, v in val.items()}
        if isinstance(val, list):
            return [resolve_val(x) for x in val]
        return val

    def resolve_token(path: str) -> Any:
        if path in resolved:
            return resolved[path]
        val = resolve_val(leaves[path]["value"])
        resolved[path] = val
        return val

    for p in leaves:
        resolve_token(p)
    return resolved


def _validate_value_syntax(
    path: str,
    tok_type: str,
    val: Any,
    strict: bool,
    allow_banned_fonts: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    if tok_type == "color":
        if not isinstance(val, str) or not _COLOR_RE.match(val.strip()):
            errors.append(f"Token '{path}' ($type=color) has invalid color value: {val!r}")
    elif tok_type == "dimension":
        if not isinstance(val, str) or not _DIMENSION_RE.match(val.strip()):
            errors.append(f"Token '{path}' ($type=dimension) has invalid dimension: {val!r}")
    elif tok_type == "duration":
        if not isinstance(val, str) or not _DURATION_RE.match(val.strip()):
            errors.append(f"Token '{path}' ($type=duration) has invalid duration: {val!r}")
    elif tok_type == "number":
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            errors.append(f"Token '{path}' ($type=number) must be numeric, got {val!r}")
    elif tok_type == "fontFamily":
        families = [val] if isinstance(val, str) else val if isinstance(val, list) else []
        if not families or not all(isinstance(f, str) and f.strip() for f in families):
            errors.append(f"Token '{path}' ($type=fontFamily) must be a non-empty string or string list")
        elif not allow_banned_fonts:
            for fam in families:
                if _BANNED_FONT_RE.search(fam):
                    msg = f"Token '{path}' uses banned default font family: {fam!r}"
                    if strict:
                        errors.append(msg)
                    else:
                        warnings.append(msg)
    elif tok_type == "fontWeight":
        if isinstance(val, int) and not isinstance(val, bool):
            if not (100 <= val <= 950):
                errors.append(f"Token '{path}' ($type=fontWeight) out of range: {val}")
            elif strict and val >= 900:
                errors.append(f"Token '{path}' ($type=fontWeight) >= 900 forbidden in --strict mode: {val}")
        elif isinstance(val, str):
            if val.lower().strip() not in _FONT_WEIGHT_WORDS:
                errors.append(f"Token '{path}' ($type=fontWeight) invalid keyword: {val!r}")
        else:
            errors.append(f"Token '{path}' ($type=fontWeight) invalid type: {val!r}")
    elif tok_type == "cubicBezier":
        if (
            not isinstance(val, list)
            or len(val) != 4
            or any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in val)
            or not (0.0 <= float(val[0]) <= 1.0 and 0.0 <= float(val[2]) <= 1.0)
        ):
            errors.append(f"Token '{path}' ($type=cubicBezier) must be [x1,y1,x2,y2] with 0<=x1,x2<=1")
    elif tok_type == "typography":
        if not isinstance(val, dict):
            errors.append(f"Token '{path}' ($type=typography) must be an object, got {val!r}")
        else:
            if "fontFamily" in val and val["fontFamily"] is not None:
                _validate_value_syntax(
                    f"{path}.fontFamily", "fontFamily", val["fontFamily"], strict, allow_banned_fonts, errors, warnings
                )
            if "fontWeight" in val and val["fontWeight"] is not None:
                _validate_value_syntax(
                    f"{path}.fontWeight", "fontWeight", val["fontWeight"], strict, allow_banned_fonts, errors, warnings
                )


def validate_token_document(
    data: Any,
    strict: bool = False,
    allow_banned_fonts: bool = False,
    check_contrast_flag: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return {
            "passed": False,
            "token_count": 0,
            "errors": ["Token document root must be a JSON object."],
            "warnings": [],
        }

    leaves: dict[str, dict[str, Any]] = {}
    _collect_leaves(data, [], data.get("$type"), leaves, errors)
    if not leaves and not errors:
        errors.append("No DTCG token definitions found in document.")

    resolved = _detect_cycles_and_dangling(leaves, errors)
    if resolved:
        for path, info in leaves.items():
            _validate_value_syntax(
                path, info["type"], resolved[path], strict, allow_banned_fonts, errors, warnings
            )

    if check_contrast_flag and resolved and not errors:
        try:
            import check_contrast
            colors = {p: str(resolved[p]) for p, info in leaves.items() if info["type"] == "color"}
            surfaces: dict[str, str] = {}
            texts: dict[str, str] = {}
            for k, v in colors.items():
                low = k.lower()
                parts = set(re.split(r"[._-]+", low))
                if (
                    bool(parts & {"bg", "surface", "canvas", "background", "elevated"})
                    or any(t in low for t in ("surface.", "canvas", "background", "elevated", "bg.", ".bg", "bg-"))
                ) and "button" not in low:
                    surfaces[k] = v
                if (
                    bool(parts & {"text", "foreground"})
                    or any(t in low for t in ("text.", "foreground", "text-"))
                ) and "on-" not in low and "on." not in low and "primary-fg" not in low:
                    texts[k] = v
            for fk, fv in texts.items():
                for bk, bv in surfaces.items():
                    ev = check_contrast.evaluate_pair(fv, bv)
                    if not ev["passed"]:
                        errors.append(
                            f"Contrast failure ({fk} on {bk}): {ev['wcag_ratio']}:1 < {ev['wcag_threshold']}:1"
                        )
        except Exception as exc:
            errors.append(f"Contrast check failed: {exc}")

    return {
        "passed": len(errors) == 0,
        "token_count": len(leaves),
        "resolved_count": len(resolved),
        "errors": errors,
        "warnings": warnings,
    }


def validate_token_file(
    filepath: Path,
    strict: bool = False,
    allow_banned_fonts: bool = False,
    check_contrast_flag: bool = False,
) -> dict[str, Any]:
    if not filepath.is_file():
        return {
            "passed": False,
            "file": str(filepath),
            "token_count": 0,
            "errors": [f"File not found: {filepath}"],
            "warnings": [],
        }
    try:
        raw = filepath.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "passed": False,
            "file": str(filepath),
            "token_count": 0,
            "errors": [f"Malformed JSON in {filepath.name}: {exc}"],
            "warnings": [],
        }
    rep = validate_token_document(
        data,
        strict=strict,
        allow_banned_fonts=allow_banned_fonts,
        check_contrast_flag=check_contrast_flag,
    )
    rep["file"] = str(filepath)
    return rep


def run_self_test() -> dict[str, Any]:
    valid_doc = {
        "primitive": {
            "color": {
                "zinc-950": {"$value": "#09090b", "$type": "color"},
                "zinc-50": {"$value": "#fafafa", "$type": "color"},
            }
        },
        "semantic": {
            "surface": {"canvas": {"$value": "{primitive.color.zinc-950}", "$type": "color"}},
            "text": {"primary": {"$value": "{primitive.color.zinc-50}", "$type": "color"}},
        },
    }
    missing_val = {"primitive": {"color": {"brand": {"$type": "color"}}}}
    dangling = {"semantic": {"a": {"$value": "{primitive.color.missing}", "$type": "color"}}}
    circular = {
        "semantic": {
            "a": {"$value": "{semantic.b}", "$type": "color"},
            "b": {"$value": "{semantic.a}", "$type": "color"},
        }
    }
    r_ok = validate_token_document(valid_doc, check_contrast_flag=True)
    r_miss = validate_token_document(missing_val)
    r_dang = validate_token_document(dangling)
    r_circ = validate_token_document(circular)
    passed = r_ok["passed"] and not r_miss["passed"] and not r_dang["passed"] and not r_circ["passed"]
    return {
        "passed": passed,
        "cases": {
            "valid": r_ok["passed"],
            "missing_value_rejected": not r_miss["passed"],
            "dangling_rejected": not r_dang["passed"],
            "circular_rejected": not r_circ["passed"],
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate W3C DTCG token JSON files ($value/$type, aliases, cycles, contrast)."
    )
    parser.add_argument("target", nargs="?", default=None, help="Path to DTCG tokens JSON file")
    parser.add_argument("--file", "--path", "--input", "--target", dest="filepath", help="Path to DTCG tokens JSON file")
    parser.add_argument("--strict", action="store_true", help="Treat banned font tokens and 900 weights as errors")
    parser.add_argument("--allow-banned-fonts", action="store_true", help="Allow legacy/banned font families")
    parser.add_argument("--contrast", action="store_true", help="Also run WCAG 2.1 contrast checks on fg/bg pairs")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator tests")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        rep = run_self_test()
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"validate_tokens self-test: {'PASS' if rep['passed'] else 'FAIL'}")
        return 0 if rep["passed"] else 1

    target_str = args.filepath or args.target
    if not target_str:
        msg = {"passed": False, "errors": ["Provide a token JSON path or --file <path>."]}
        if args.json:
            print(json.dumps(msg, indent=2))
        else:
            print("Error: Provide a token JSON path or --file <path>.", file=sys.stderr)
        return 2

    report = validate_token_file(
        Path(target_str),
        strict=args.strict,
        allow_banned_fonts=args.allow_banned_fonts,
        check_contrast_flag=args.contrast,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["passed"] else "FAIL"
        print(f"[{status}] {report['file']} ({report['token_count']} tokens)")
        for err in report["errors"]:
            print(f"  ERROR: {err}", file=sys.stderr)
        for warn in report["warnings"]:
            print(f"  WARN: {warn}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
