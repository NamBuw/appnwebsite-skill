#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static UI/CSS/TSX/HTML/copy anti-AI-slop scanner and redesign regression checker.

Pure Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

SCAN_EXTENSIONS: frozenset[str] = frozenset({
    ".css", ".scss", ".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro"
})
SKIP_DIRS: frozenset[str] = frozenset({
    "node_modules", ".git", "dist", "build", ".next", "__pycache__", ".venv", "venv"
})

DEFAULT_BANNED_FONTS: tuple[str, ...] = ("Inter", "Roboto", "Arial", "Open Sans", "Helvetica")
DEFAULT_BANNED_ICONS: tuple[str, ...] = (
    "lucide-react", "lucide", "feather-icons", "react-feather",
    "@heroicons/", "heroicons", "material-icons", "material-symbols",
)
AI_BUZZWORD_PATTERNS: tuple[str, ...] = (
    r"\bLorem\s+ipsum\b",
    r"\bYour\s+headline\s+here\b",
    r"\bcoming\s+soon\b",
    r"\bsynergy\b",
    r"\bnext-gen\b",
    r"\brevolutionize\b",
    r"\bsupercharge\b",
    r"\bcutting-edge\b",
    r"\beffortless(?:ly)?\b",
    r"\bharness\s+the\s+power\b",
    r"\bworld-class\b",
    r"\btransform\s+your\s+workflow\b",
)

_FONT_DECL_RE = re.compile(
    r"""(?:font-family|fontFamily|fonts\.googleapis\.com/css2\?family=|next/font/google)[^\n;{}]*""",
    re.IGNORECASE,
)
_GRADIENT_RE = re.compile(r"(?:linear-gradient|radial-gradient|conic-gradient)\s*\(", re.IGNORECASE)
_ZINDEX_RE = re.compile(r"(?:z-index\s*:\s*(-?\d+)|zIndex\s*:\s*(-?\d+)|z-\[(-?\d+)\])", re.IGNORECASE)
_CSS_ANIM_RE = re.compile(r"\b(?:transition|animation)\s*:|@keyframes\b", re.IGNORECASE)
_REDUCED_MOTION_RE = re.compile(r"prefers-reduced-motion", re.IGNORECASE)
_ONE_SIDED_BORDER_RE = re.compile(r"\.card[^{]*\{[^}]*\bborder-(?:top|left|right|bottom)\s*:", re.IGNORECASE | re.DOTALL)
_DEFAULT_EASE_RE = re.compile(r"\btransition\s*:[^;{}]*\b(?:ease|linear|ease-in-out)\b(?:\s*;|\s)", re.IGNORECASE)
_SCROLL_LISTENER_RE = re.compile(r"window\.addEventListener\(\s*['\"]scroll['\"]", re.IGNORECASE)


class _AnchorFormExtractor(HTMLParser):
    """Extract hrefs, forms, and testids from HTML/JSX-like markup."""

    def __init__(self) -> None:
        super().__init__()
        self.markers: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag in ("a", "link") and attr_map.get("href"):
            self.markers.add(f"href:{attr_map['href']}")
        if tag == "form":
            self.markers.add(f"form:{attr_map.get('id') or attr_map.get('action') or 'anonymous'}")
        if attr_map.get("data-testid"):
            self.markers.add(f"testid:{attr_map['data-testid']}")


def _collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files: list[Path] = []
    for root, dirs, names in os.walk(target):
        dirs[:] = [d for d in sorted(dirs) if d not in SKIP_DIRS]
        for name in sorted(names):
            p = Path(root) / name
            if p.suffix.lower() in SCAN_EXTENSIONS:
                files.append(p)
    return files


_JS_COMMENT_OR_STRING_RE = re.compile(
    r"""('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)|(/\*[\s\S]*?\*/|(?<!:)//[^\n]*)"""
)
_CSS_COMMENT_OR_STRING_RE = re.compile(
    r"""('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*")|(/\*[\s\S]*?\*/)"""
)
_NEXT_FONT_NAMED_RE = re.compile(
    r"""import\s*\{([^}]*)\}\s*from\s*['"]next/font/google['"]"""
)
_NEXT_FONT_DEFAULT_RE = re.compile(
    r"""import\s+([A-Za-z0-9_]+)\s+from\s*['"]next/font/google['"]"""
)


def _mask_comments_preserve_lines(text: str, ext: str) -> str:
    """Replace comments with spaces while preserving newlines and string literals."""
    if ext == ".css":
        pat = _CSS_COMMENT_OR_STRING_RE
    elif ext in (".js", ".jsx", ".ts", ".tsx", ".scss"):
        pat = _JS_COMMENT_OR_STRING_RE
    else:
        return text

    def _repl(match: re.Match[str]) -> str:
        if match.group(1) is not None:
            return match.group(1)
        comment = match.group(2)
        return "".join("\n" if ch == "\n" else " " for ch in comment)

    return pat.sub(_repl, text)


def _is_icon_token_allowlisted(tok: str, allowed_i: set[str]) -> bool:
    if not allowed_i:
        return False
    if tok in allowed_i:
        return True
    for allow in allowed_i:
        base = allow.rstrip("/")
        if base and (tok == base or tok.startswith(base + "/")):
            return True
    return False


def _extract_structural_markers(directory: Path) -> set[str]:
    markers: set[str] = set()
    handler_counts: Counter[str] = Counter()
    for fpath in _collect_files(directory):
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        parser = _AnchorFormExtractor()
        try:
            parser.feed(text)
            markers.update(parser.markers)
        except Exception:
            pass
        for m in re.finditer(r"""<(?:a|Link)\b[^>]*\b(?:href|to)=['"]([^'"]+)['"]""", text):
            markers.add(f"href:{m.group(1)}")
        for m in re.finditer(r"""<form\b[^>]*>""", text):
            markers.add("form:present")
        for m in re.finditer(r"""\b(onClick|onSubmit)\s*=""", text):
            event = m.group(1)
            handler_counts[event] += 1
            idx = handler_counts[event]
            markers.add(f"handler:{event}" if idx == 1 else f"handler:{event}#{idx}")
        for m in re.finditer(r"""data-testid=['"]([^'"]+)['"]""", text):
            markers.add(f"testid:{m.group(1)}")
    return markers


def scan_target(
    target: Path,
    allow_fonts: set[str] | None = None,
    allow_icons: set[str] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    if not target.exists():
        return {"passed": False, "error": f"Path not found: {target}", "findings": []}

    allowed_f = {f.lower() for f in (allow_fonts or set())}
    allowed_i = {i.lower() for i in (allow_icons or set())}
    files = _collect_files(target)
    if not files:
        return {"passed": False, "error": f"No scannable UI files under {target}", "findings": []}

    findings: list[dict[str, Any]] = []
    css_has_motion = False
    css_has_reduced_motion = False

    def add_finding(rule: str, tier: str, fpath: Path, line: int, detail: str, fail_flag: bool) -> None:
        findings.append({
            "rule": rule,
            "tier": tier,
            "file": str(fpath),
            "line": line,
            "detail": detail,
            "blocking": fail_flag or (strict and tier == "FINISH"),
        })

    for fpath in files:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        ext = fpath.suffix.lower()
        masked_text = _mask_comments_preserve_lines(text, ext)
        lines = text.splitlines()
        masked_lines = masked_text.splitlines()
        is_css = ext in (".css", ".scss")
        seen_font_findings: set[tuple[int, str]] = set()

        if is_css:
            if _CSS_ANIM_RE.search(masked_text):
                css_has_motion = True
            if _REDUCED_MOTION_RE.search(masked_text):
                css_has_reduced_motion = True
            if _ONE_SIDED_BORDER_RE.search(masked_text):
                add_finding("SLOP-BORDER-01", "FINISH", fpath, 1, "Single-sided border on .card selector", strict)

        # Multi-line & single-line next/font/google import scan (comment-masked, exact line numbers)
        for imp_m in _NEXT_FONT_NAMED_RE.finditer(masked_text):
            body = imp_m.group(1)
            body_start = imp_m.start(1)
            for spec_m in re.finditer(r"[^,]+", body):
                ident_m = re.match(r"\s*([A-Za-z0-9_]+)", spec_m.group(0))
                if not ident_m:
                    continue
                ident_norm = ident_m.group(1).replace("_", " ").lower()
                for font in DEFAULT_BANNED_FONTS:
                    if font.lower() in allowed_f:
                        continue
                    if ident_norm == font.lower():
                        abs_pos = body_start + spec_m.start() + ident_m.start(1)
                        flino = text.count("\n", 0, abs_pos) + 1
                        if (flino, font.lower()) not in seen_font_findings:
                            seen_font_findings.add((flino, font.lower()))
                            add_finding("SLOP-FONT-01", "REFLEX", fpath, flino, f"Banned default font {font!r} detected", True)
        for imp_m in _NEXT_FONT_DEFAULT_RE.finditer(masked_text):
            ident_norm = imp_m.group(1).replace("_", " ").lower()
            for font in DEFAULT_BANNED_FONTS:
                if font.lower() in allowed_f:
                    continue
                if ident_norm == font.lower():
                    flino = text.count("\n", 0, imp_m.start(1)) + 1
                    if (flino, font.lower()) not in seen_font_findings:
                        seen_font_findings.add((flino, font.lower()))
                        add_finding("SLOP-FONT-01", "REFLEX", fpath, flino, f"Banned default font {font!r} detected", True)

        for lineno, line in enumerate(lines, 1):
            check_line = masked_lines[lineno - 1] if lineno - 1 < len(masked_lines) else line
            # 1. SLOP-FONT-01
            if _FONT_DECL_RE.search(check_line) or re.search(
                r"""import\s*\{[^}]*\b(?:Inter|Roboto|Open_Sans|Arial|Helvetica)\b[^}]*\}\s*from\s*['"]next/font/google['"]""",
                check_line,
            ):
                for font in DEFAULT_BANNED_FONTS:
                    if font.lower() in allowed_f or (lineno, font.lower()) in seen_font_findings:
                        continue
                    font_pat = r"\b" + r"[\s_]+".join(re.escape(part) for part in font.split()) + r"\b"
                    if re.search(font_pat, check_line, re.IGNORECASE):
                        seen_font_findings.add((lineno, font.lower()))
                        add_finding("SLOP-FONT-01", "REFLEX", fpath, lineno, f"Banned default font {font!r} detected", True)

            # 2. SLOP-ICON-01
            low_line = check_line.lower()
            reported_icons: set[str] = set()
            for tok_m in re.finditer(r"[@a-z0-9_.-]+(?:/[@a-z0-9_.-]+)*", low_line):
                tok = tok_m.group(0)
                if _is_icon_token_allowlisted(tok, allowed_i):
                    continue
                for icon_pkg in DEFAULT_BANNED_ICONS:
                    pkg_low = icon_pkg.lower()
                    if pkg_low in allowed_i:
                        continue
                    if pkg_low == "@heroicons/" and "heroicons" in allowed_i:
                        continue
                    if pkg_low == "@heroicons/":
                        matched = tok.startswith("@heroicons/") or "/@heroicons/" in tok
                    else:
                        matched = bool(re.search(r"(?<![a-z0-9])" + re.escape(pkg_low) + r"(?![a-z0-9])", tok))
                    if matched:
                        if icon_pkg not in reported_icons:
                            reported_icons.add(icon_pkg)
                            add_finding("SLOP-ICON-01", "REFLEX", fpath, lineno, f"Banned icon pack {icon_pkg!r} detected", True)
                        break
            for icon_pkg, sp_pat in (("material-icons", r"\bmaterial\s+icons\b"), ("material-symbols", r"\bmaterial\s+symbols\b")):
                if icon_pkg not in allowed_i and icon_pkg not in reported_icons and re.search(sp_pat, low_line):
                    reported_icons.add(icon_pkg)
                    add_finding("SLOP-ICON-01", "REFLEX", fpath, lineno, f"Banned icon pack {icon_pkg!r} detected", True)

            # 3. SLOP-GRAD-01 (allow hero text-only directional clip)
            if _GRADIENT_RE.search(line):
                ctx_start = max(0, lineno - 3)
                ctx_end = min(len(lines), lineno + 3)
                context_blob = "\n".join(lines[ctx_start:ctx_end]).lower()
                if not any(clip in context_blob for clip in ("background-clip: text", "-webkit-background-clip: text", "bg-clip-text", "webkitbackgroundclip")):
                    add_finding("SLOP-GRAD-01", "REFLEX", fpath, lineno, "Background gradient without hero text-clip exception", True)

            # 4. SLOP-ZIDX-01
            for m in _ZINDEX_RE.finditer(line):
                raw_num = next((g for g in m.groups() if g is not None), "0")
                zval = int(raw_num)
                if zval >= 999 or zval < 0:
                    add_finding("SLOP-ZIDX-01", "REFLEX", fpath, lineno, f"Out-of-scale z-index ({zval}); use semantic layer 0..70", True)

            # 5. SLOP-COPY-01
            for pat in AI_BUZZWORD_PATTERNS:
                mm = re.search(pat, line, re.IGNORECASE)
                if mm:
                    add_finding("SLOP-COPY-01", "FLOOR", fpath, lineno, f"AI slop / placeholder copy detected: {mm.group(0)!r}", True)

            # 6. Default transition easing / unthrottled scroll
            if is_css and _DEFAULT_EASE_RE.search(line):
                add_finding("SLOP-MOTION-01", "FINISH", fpath, lineno, "Generic default easing (ease/linear); prefer cubic-bezier(0.22,1,0.36,1)", strict)
            if _SCROLL_LISTENER_RE.search(line):
                add_finding("SLOP-PERF-01", "FINISH", fpath, lineno, "Raw window scroll listener; prefer IntersectionObserver or CSS view timeline", strict)

    if css_has_motion and not css_has_reduced_motion:
        css_files = [f for f in files if f.suffix.lower() in (".css", ".scss")]
        add_finding("SLOP-A11Y-01", "FLOOR", css_files[0], 1, "CSS transitions/animations declared without @media (prefers-reduced-motion: reduce)", True)

    blocking_count = sum(1 for item in findings if item["blocking"])
    return {
        "passed": blocking_count == 0,
        "target": str(target),
        "files_scanned": len(files),
        "blocking_count": blocking_count,
        "findings": findings,
    }


def check_redesign_retention(
    before_dir: Path,
    kept_dir: Path,
    allow_removed: set[str] | None = None,
) -> dict[str, Any]:
    if not before_dir.is_dir() or not kept_dir.is_dir():
        return {"passed": False, "error": "--before and --kept must both be existing directories", "dropped": []}
    before_markers = _extract_structural_markers(before_dir)
    kept_markers = _extract_structural_markers(kept_dir)
    allowed = allow_removed or set()
    dropped = sorted(
        m for m in (before_markers - kept_markers)
        if m not in allowed and not (m.startswith("handler:") and m.split("#", 1)[0] in allowed)
    )
    return {
        "passed": len(dropped) == 0,
        "before_count": len(before_markers),
        "kept_count": len(kept_markers),
        "dropped": dropped,
    }


def run_self_test() -> dict[str, Any]:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        bad_css = td / "bad.css"
        bad_css.write_text("body { font-family: 'Inter', sans-serif; }\n.c { z-index: 9999; transition: all 200ms ease; }\n", encoding="utf-8")
        clean_css = td / "clean" / "ok.css"
        clean_css.parent.mkdir()
        clean_css.write_text(
            "body { font-family: 'Geist', sans-serif; }\n"
            ".btn { transition: transform 200ms cubic-bezier(0.22, 1, 0.36, 1); }\n"
            "@media (prefers-reduced-motion: reduce) { .btn { transition: none; } }\n",
            encoding="utf-8",
        )
        r_bad = scan_target(bad_css)
        r_ok = scan_target(clean_css.parent)
        passed = (not r_bad["passed"]) and r_ok["passed"]
        return {"passed": passed, "bad_findings": len(r_bad["findings"]), "clean_findings": len(r_ok["findings"])}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Anti-AI-slop static scanner and redesign regression checker."
    )
    parser.add_argument("target", nargs="?", default=None, help="File or directory to scan")
    parser.add_argument("--path", "--dir", "--root", "--file", "--target", dest="opt_target", help="Target file or directory")
    parser.add_argument("--allow-font", action="append", default=[], help="Allowlist a font family (repeatable)")
    parser.add_argument("--allow-icon", action="append", default=[], help="Allowlist an icon package (repeatable)")
    parser.add_argument("--strict", action="store_true", help="Fail on FINISH-tier findings as well as FLOOR/REFLEX")
    parser.add_argument("--before", type=str, default=None, help="Original UI directory for redesign retention check")
    parser.add_argument("--kept", type=str, default=None, help="Redesigned UI directory for redesign retention check")
    parser.add_argument("--allow-removed", action="append", default=[], help="Allowlisted removed marker (href:..., testid:...)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in anti-slop checks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        rep = run_self_test()
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"check_anti_slop self-test: {'PASS' if rep['passed'] else 'FAIL'}")
        return 0 if rep["passed"] else 1

    if args.before or args.kept:
        if not (args.before and args.kept):
            msg = "Both --before and --kept directories are required for redesign retention check."
            print(json.dumps({"passed": False, "error": msg}) if args.json else f"Error: {msg}", file=sys.stderr if not args.json else sys.stdout)
            return 2
        rep = check_redesign_retention(Path(args.before), Path(args.kept), set(args.allow_removed))
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"[{'PASS' if rep['passed'] else 'FAIL'}] Redesign retention: {len(rep['dropped'])} dropped markers")
            for d in rep["dropped"]:
                print(f"  DROPPED: {d}", file=sys.stderr)
        return 0 if rep["passed"] else 1

    target_str = args.opt_target or args.target or "."
    rep = scan_target(
        Path(target_str),
        allow_fonts=set(args.allow_font),
        allow_icons=set(args.allow_icon),
        strict=args.strict,
    )
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        if rep.get("error"):
            print(f"Error: {rep['error']}", file=sys.stderr)
            return 2
        status = "PASS" if rep["passed"] else "FAIL"
        print(f"[{status}] Scanned {rep['files_scanned']} file(s) -> {rep['blocking_count']} blocking issue(s)")
        for item in rep["findings"]:
            tag = "FAIL" if item["blocking"] else "WARN"
            print(f"  [{tag}] {item['rule']} ({item['tier']}) {item['file']}:{item['line']} — {item['detail']}")
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
