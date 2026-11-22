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
    r"\bseamless(?:ly)?\b",
    r"\bempower(?:ing)?\b",
    r"\brobust\b",
    r"\bdelve\b",
    r"\bunlock\s+your\s+potential\b",
    r"\belevate\s+your\b",
    r"\bgame-chang(?:er|ing)\b",
    r"\bstate-of-the-art\b",
    r"trích xuất từ kho",
    r"\bchuẩn hóa\b",
    r"\btrọn vị\b",
    r"\bnhịp bếp\b",
    r"\bnâng tầm\b",
    r"\btối ưu hóa quy trình\b",
)
_AI_IMAGE_SLOP_RE = re.compile(
    r"""\b(?:ai-generated|generated\s+by\s+ai|midjourney|dall-e|stable-diffusion|tastoria\s+studio)\b""",
    re.IGNORECASE,
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
_PITCH_BLACK_BG_RE = re.compile(
    r"""(?:--bg|background(?:-color)?|backgroundColor|\bbg)\s*:\s*['"]?#000(?:000)?(?:\b|['";,\s}])""",
    re.IGNORECASE,
)
_INDIGO_SLOP_RE = re.compile(
    r"""(?:#6366f1|#8b5cf6|#a855f7|\bbg-indigo-[56]00\b|\bfrom-indigo-|\bto-purple-|\bto-violet-)""",
    re.IGNORECASE,
)
_WARM_CREAM_RE = re.compile(r"""(?:#fafaf8|#faf8f5|#fdfbf7|#f5f2eb)\b""", re.IGNORECASE)
_TERRACOTTA_RE = re.compile(r"""(?:#d97757|#bd3d1e|#e05a34|#f28263|#c85a32)\b""", re.IGNORECASE)
_THEME_TOGGLE_ID_RE = re.compile(r"""\bid\s*=\s*['"]theme-toggle['"]""", re.IGNORECASE)
_THEME_SWITCH_CONTROL_RE = re.compile(
    r"""(?:data-testid\s*=\s*['"]theme-toggle['"]|testID\s*=\s*['"]theme-toggle['"]|<ThemeToggle\b|class\s*=\s*['"][^'"]*\bmode-switch\b)""",
    re.IGNORECASE,
)
_PRIMITIVE_SHAPE_RE = re.compile(r"""<(?:circle|ellipse|rect)\b""", re.IGNORECASE)
_GLASS_BLUR_RE = re.compile(r"""(?<!-)backdrop-filter\s*:\s*blur\(\s*(?:1[2-9]|[2-9]\d)px\s*\)""", re.IGNORECASE)
_GRID_3COL_RE = re.compile(r"""(?:grid-template-columns\s*:\s*repeat\(\s*3\s*,|\bgrid-cols-3\b)""", re.IGNORECASE)
_EYEBROW_MARK_RE = re.compile(r"""(?:class\s*=\s*['"][^'"]*eyebrow|\bv\s*=\s*['"]eyebrow['"])""", re.IGNORECASE)
_PILL_BADGE_RE = re.compile(r"""(?:borderRadius\s*:\s*(?:radius\.pill|9999)|\brounded-full\b)""", re.IGNORECASE)
_DECORATIVE_EMOJI_RE = re.compile(r"[✨🚀🔥⚡💡🎯🎉💎🤖]")
_FAKE_PERSONA_RE = re.compile(r"""\b(?:Jane\s+Doe|John\s+Doe|Acme\s+Corp)\b""", re.IGNORECASE)
_ML_JARGON_RE = re.compile(
    r"""(?:\bmAP@50\b|\bval\s+mAP\b|\bECE\b|\bCP[- ]SAT\b|\bf1-score\b|\bHeldout\s+OOD\b|\bONNX\s+Runtime\b|\bTemperature\s+Scaling\b|\bAES-256-GCM\b|\bWord2Vec\b|\bpgvector\b|\bNDCG@)"""
)
_FAKE_DEVICE_RE = re.compile(
    r"""(?:\.(?:phone-notch|phone-frame|device-notch|browser-dots)\b|class\s*=\s*['"][^'"]*(?:phone-notch|device-notch|browser-dots))""",
    re.IGNORECASE,
)
_HTML_CARD_CLASS_RE = re.compile(r"""class\s*=\s*['"][^'"]*\bcard\b""", re.IGNORECASE)
_AMBER_WARM_RE = re.compile(r"""#fffbeb\b""", re.IGNORECASE)
_SLATE_COLD_RE = re.compile(r"""(?:#0f172a|#475569)\b""", re.IGNORECASE)
_DECOR_DOT_RE = re.compile(r"""class\s*=\s*['"][^'"]*\b(?:fresh-dot|status-dot|pulse-dot|live-dot)\b""", re.IGNORECASE)
_FEATURE_ICON_BOX_RE = re.compile(r"""class\s*=\s*['"][^'"]*\bfeature-icon\b""", re.IGNORECASE)
_TRANSITION_ALL_RE = re.compile(r"""\btransition\s*:\s*all\b""", re.IGNORECASE)
_INFINITE_ANIM_RE = re.compile(r"""\banimate-(?:bounce|ping)\b""", re.IGNORECASE)
_RN_MAGIC_WIDTH_RE = re.compile(r"""\bwidth\s*:\s*['"](?:48\.5|48|49|31|32)%['"]""")
_RN_BREAKPOINT_RE = re.compile(r"""\bwidth\s*(?:>=|<)\s*\d+\b""")
_CARD_TAG_RE = re.compile(r"""<Card\b""")
_BRAND_CONTAINER_RE = re.compile(
    r"""<(?P<tag>a|div|span)\b[^>]*class\s*=\s*['"][^'"]*\b(?:brand|logo|wordmark)\b[^'"]*['"][^>]*>[\s\S]*?</(?P=tag)>""",
    re.IGNORECASE,
)
_HEADER_BLOCK_RE = re.compile(r"""<header\b[^>]*>[\s\S]*?</header>""", re.IGNORECASE)
_INLINE_SVG_RE = re.compile(r"""<svg\b([^>]*)>([\s\S]*?)</svg>""", re.IGNORECASE)
_SVG_DIM_RE = re.compile(r"""\b(?:width|height)\s*=\s*['"]?\s*(\d+)""", re.IGNORECASE)
_HERO_SECTION_RE = re.compile(
    r"""<section\b[^>]*(?:\bid\s*=\s*['"]hero['"]|\bclass\s*=\s*['"][^'"]*\bhero\b[^'"]*['"])[^>]*>[\s\S]*?</section>""",
    re.IGNORECASE,
)
_RASTER_IMG_RE = re.compile(
    r"""<img\b[^>]*\bsrc\s*=\s*['"][^'"]+\.(?:jpg|jpeg|webp|png|avif)(?:[?#][^'"]*)?['"]""",
    re.IGNORECASE,
)
_COMPETING_RED_ACCENT_RE = re.compile(r"""(?:#9e2b1b|#bd3d1e|#dc2626|#b91c1c)\b""", re.IGNORECASE)
_COMPETING_GREEN_ACCENT_RE = re.compile(r"""(?:#235334|#16a34a|#15803d|#059669)\b""", re.IGNORECASE)
_WARM_LINEN_RE = re.compile(r"""(?:#faf7f2|#f4f1ea)\b""", re.IGNORECASE)
_COLD_SLATE_HARMONY_RE = re.compile(r"""(?:#f8fafc|#e2e8f0|#0f172a)\b""", re.IGNORECASE)


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


def _is_palette_allowed(family: str, allowed_p: set[str]) -> bool:
    return "all" in allowed_p or family in allowed_p


def scan_target(
    target: Path,
    allow_fonts: set[str] | None = None,
    allow_icons: set[str] | None = None,
    allow_palettes: set[str] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    if not target.exists():
        return {"passed": False, "error": f"Path not found: {target}", "findings": []}

    allowed_f = {f.lower() for f in (allow_fonts or set())}
    allowed_i = {i.lower() for i in (allow_icons or set())}
    allowed_p = {p.lower() for p in (allow_palettes or set())}
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
        is_html = ext in (".html", ".htm")
        is_rn_tsx = ext in (".tsx", ".jsx")
        seen_font_findings: set[tuple[int, str]] = set()

        if is_css:
            if _CSS_ANIM_RE.search(masked_text):
                css_has_motion = True
            if _REDUCED_MOTION_RE.search(masked_text):
                css_has_reduced_motion = True
            if _ONE_SIDED_BORDER_RE.search(masked_text):
                add_finding("SLOP-BORDER-01", "FINISH", fpath, 1, "Single-sided border on .card selector", strict)
            glass_hits = list(_GLASS_BLUR_RE.finditer(masked_text))
            if len(glass_hits) >= 2:
                glino = text.count("\n", 0, glass_hits[0].start()) + 1
                add_finding("SLOP-GLASS-01", "FINISH", fpath, glino, f"Excessive glassmorphism blur ({len(glass_hits)} heavy backdrop-filter blur rules >= 12px)", strict)
            if not _is_palette_allowed("color-harmony", allowed_p):
                red_m = _COMPETING_RED_ACCENT_RE.search(masked_text)
                green_m = _COMPETING_GREEN_ACCENT_RE.search(masked_text)
                linen_m = _WARM_LINEN_RE.search(masked_text)
                cold_m = _COLD_SLATE_HARMONY_RE.search(masked_text)
                if red_m and green_m:
                    chlino = text.count("\n", 0, green_m.start()) + 1
                    add_finding(
                        "SLOP-COLOR-HARMONY-01",
                        "FINISH",
                        fpath,
                        chlino,
                        "Competing high-chroma red and green accents detected; commit to 1 restrained focal accent",
                        strict,
                    )
                elif linen_m and cold_m:
                    chlino = text.count("\n", 0, cold_m.start()) + 1
                    add_finding(
                        "SLOP-COLOR-HARMONY-01",
                        "FINISH",
                        fpath,
                        chlino,
                        "Warm linen mixed with cold slate neutrals; commit to 1 unified neutral hue temperature",
                        strict,
                    )

        if not _is_palette_allowed("cream-terracotta", allowed_p):
            cream_m = _WARM_CREAM_RE.search(masked_text)
            terra_m = _TERRACOTTA_RE.search(masked_text)
            if cream_m and terra_m:
                plino = text.count("\n", 0, terra_m.start()) + 1
                add_finding("SLOP-PALETTE-01", "REFLEX", fpath, plino, "AI-convergence cream+terracotta palette pair detected without ADR waiver", True)

        if not _is_palette_allowed("amber-slate", allowed_p):
            amber_m = _AMBER_WARM_RE.search(masked_text)
            slate_m = _SLATE_COLD_RE.search(masked_text)
            if amber_m and slate_m:
                clino = text.count("\n", 0, slate_m.start()) + 1
                add_finding("SLOP-COLOR-CLASH-01", "REFLEX", fpath, clino, "Tailwind warm #FFFBEB + cold slate (#0F172A/#475569) temperature clash", True)

        if is_css or is_html:
            fake_dev = _FAKE_DEVICE_RE.search(masked_text)
            if fake_dev:
                dlino = text.count("\n", 0, fake_dev.start()) + 1
                add_finding("SLOP-FAKE-DEVICE-01", "REFLEX", fpath, dlino, "CSS-drawn fake phone/browser notch mockup detected; use real screenshot/photography", True)

        if is_html:
            toggle_m = _THEME_TOGGLE_ID_RE.search(masked_text)
            if toggle_m or ("icon-sun" in masked_text and "icon-moon" in masked_text):
                tlino = text.count("\n", 0, toggle_m.start()) + 1 if toggle_m else 1
                add_finding("SLOP-TOGGLE-01", "REFLEX", fpath, tlino, "Sun/moon theme toggle clutter detected on marketing landing HTML", True)
            dot_m = _DECOR_DOT_RE.search(masked_text)
            if dot_m:
                dotlino = text.count("\n", 0, dot_m.start()) + 1
                add_finding("SLOP-DOT-01", "REFLEX", fpath, dotlino, "Decorative status/live dot chrome detected in landing HTML", True)
            card_cls_hits = list(_HTML_CARD_CLASS_RE.finditer(masked_text))
            if len(card_cls_hits) >= 8:
                wclino = text.count("\n", 0, card_cls_hits[7].start()) + 1
                add_finding("SLOP-WALL-CARDS-01", "REFLEX", fpath, wclino, f"Wall-of-cards layout monotony ({len(card_cls_hits)} .card containers in one HTML page)", True)
            ficon_hits = list(_FEATURE_ICON_BOX_RE.finditer(masked_text))
            if len(ficon_hits) >= 3:
                filino = text.count("\n", 0, ficon_hits[2].start()) + 1
                add_finding("SLOP-ICON-BOX-01", "FINISH", fpath, filino, f"Cookie-cutter icon-in-tinted-box feature pattern ({len(ficon_hits)} occurrences)", strict)

            svg_logo_lines: set[int] = set()
            for bm in _BRAND_CONTAINER_RE.finditer(masked_text):
                if _INLINE_SVG_RE.search(bm.group(0)):
                    svg_logo_lines.add(text.count("\n", 0, bm.start()) + 1)
            for hm in _HEADER_BLOCK_RE.finditer(masked_text):
                for svgm in _INLINE_SVG_RE.finditer(hm.group(0)):
                    attrs, body = svgm.group(1), svgm.group(2)
                    dims = [int(d) for d in _SVG_DIM_RE.findall(attrs)]
                    is_primitive_logo = (max(dims) >= 24 if dims else False) or bool(
                        re.search(r"<(?:rect|circle|polygon|ellipse)\b", body, re.IGNORECASE)
                    )
                    if is_primitive_logo:
                        svg_logo_lines.add(text.count("\n", 0, hm.start() + svgm.start()) + 1)
            for slino in sorted(svg_logo_lines):
                add_finding(
                    "SLOP-SVG-LOGO-01",
                    "REFLEX",
                    fpath,
                    slino,
                    "Hand-coded inline <svg> brand mark detected; use a crisp typographic wordmark or real raster emblem asset",
                    True,
                )

            for hero_m in _HERO_SECTION_RE.finditer(masked_text):
                hero_blob = hero_m.group(0)
                hero_lino = text.count("\n", 0, hero_m.start()) + 1
                has_raster_photo = bool(_RASTER_IMG_RE.search(hero_blob))
                has_large_svg = False
                for svgm in _INLINE_SVG_RE.finditer(hero_blob):
                    dims = [int(d) for d in _SVG_DIM_RE.findall(svgm.group(1))]
                    if dims and max(dims) >= 64:
                        has_large_svg = True
                        break
                if has_large_svg or not has_raster_photo:
                    detail = (
                        "Large hand-drawn inline <svg> in hero section; replace with high-resolution editorial photography"
                        if has_large_svg
                        else "Hero section lacks real raster photography (<img> in .jpg/.webp/.png/.avif)"
                    )
                    add_finding("SLOP-HERO-NO-PHOTO", "REFLEX", fpath, hero_lino, detail, True)

        grid3_hits = list(_GRID_3COL_RE.finditer(masked_text))
        if len(grid3_hits) >= 2:
            g3lino = text.count("\n", 0, grid3_hits[1].start()) + 1
            add_finding("SLOP-GRID-01", "REFLEX", fpath, g3lino, f"Repetitive 3-equal-column card grid detected ({len(grid3_hits)} occurrences)", True)

        eyebrow_hits = list(_EYEBROW_MARK_RE.finditer(masked_text))
        if len(eyebrow_hits) >= 3:
            elino = text.count("\n", 0, eyebrow_hits[2].start()) + 1
            add_finding("SLOP-EYEBROW-01", "REFLEX", fpath, elino, f"Repetitive eyebrow label overload ({len(eyebrow_hits)} occurrences)", True)
        else:
            for eb in eyebrow_hits:
                eb_line = text.count("\n", 0, eb.start()) + 1
                win_start = max(0, eb_line - 6)
                win_end = min(len(masked_lines), eb_line + 5)
                if _PILL_BADGE_RE.search("\n".join(masked_lines[win_start:win_end])):
                    add_finding("SLOP-EYEBROW-01", "REFLEX", fpath, eb_line, "Pill-shaped eyebrow badge cliché detected", True)
                    break

        if not is_css:
            middots = [i + 1 for i, ml in enumerate(masked_lines) for _ in re.finditer("\u00b7", ml)]
            if len(middots) >= 3:
                add_finding("SLOP-EYEBROW-01", "REFLEX", fpath, middots[2], f"Mid-dot (·) metadata salad detected ({len(middots)} occurrences)", True)

        if is_rn_tsx:
            bp_hits = list(_RN_BREAKPOINT_RE.finditer(masked_text))
            if len(bp_hits) >= 3:
                blino = text.count("\n", 0, bp_hits[0].start()) + 1
                add_finding("SLOP-RN-LAYOUT-01", "REFLEX", fpath, blino, f"Ad-hoc inline width breakpoint ternaries ({len(bp_hits)} checks); centralize responsive grid/container", True)
            card_hits = list(_CARD_TAG_RE.finditer(masked_text))
            if len(card_hits) >= 5:
                clino = text.count("\n", 0, card_hits[4].start()) + 1
                add_finding("SLOP-CARD-NEST-01", "FINISH", fpath, clino, f"Wall-of-cards layout ({len(card_hits)} <Card> wrappers in one screen)", strict)

        if is_html or is_rn_tsx:
            tsw_m = _THEME_SWITCH_CONTROL_RE.search(masked_text)
            if tsw_m:
                tswlino = text.count("\n", 0, tsw_m.start()) + 1
                add_finding(
                    "SLOP-THEME-SWITCH-01",
                    "REFLEX",
                    fpath,
                    tswlino,
                    "Manual theme-toggle button detected; follow OS prefers-color-scheme / useColorScheme() unless explicitly requested",
                    True,
                )
            for svgm in _INLINE_SVG_RE.finditer(masked_text):
                attrs, body = svgm.group(1), svgm.group(2)
                if re.search(r"\b(?:chart|sparkline|recharts)\b", attrs, re.IGNORECASE):
                    continue
                if len(_PRIMITIVE_SHAPE_RE.findall(body)) >= 6:
                    slino = text.count("\n", 0, svgm.start()) + 1
                    add_finding(
                        "SLOP-SVG-ART-01",
                        "REFLEX",
                        fpath,
                        slino,
                        "Multi-shape hand-coded SVG art/illustration (>= 6 primitives); use real curated photography or crisp minimal typography",
                        True,
                    )

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

            # 3. SLOP-GRAD-01 (allow hero text-only directional clip OR neutral dark photo readability scrims)
            if _GRADIENT_RE.search(line):
                ctx_start = max(0, lineno - 4)
                ctx_end = min(len(lines), lineno + 3)
                context_blob = "\n".join(lines[ctx_start:ctx_end]).lower()
                is_text_clip = any(
                    clip in context_blob
                    for clip in ("background-clip: text", "-webkit-background-clip: text", "bg-clip-text", "webkitbackgroundclip")
                )
                is_neutral_photo_scrim = (
                    ("scrim" in context_blob or "hero-overlay" in context_blob)
                    and "rgba(" in line.lower()
                    and not _INDIGO_SLOP_RE.search(context_blob)
                )
                if not is_text_clip and not is_neutral_photo_scrim:
                    add_finding("SLOP-GRAD-01", "REFLEX", fpath, lineno, "Background gradient without hero text-clip exception", True)

            # 4. SLOP-ZIDX-01
            for m in _ZINDEX_RE.finditer(line):
                raw_num = next((g for g in m.groups() if g is not None), "0")
                zval = int(raw_num)
                if zval >= 999 or zval < 0:
                    add_finding("SLOP-ZIDX-01", "REFLEX", fpath, lineno, f"Out-of-scale z-index ({zval}); use semantic layer 0..70", True)

            # 5. SLOP-COPY-01 & SLOP-AI-IMAGE-01
            for pat in AI_BUZZWORD_PATTERNS:
                mm = re.search(pat, line, re.IGNORECASE)
                if mm:
                    add_finding("SLOP-COPY-01", "FLOOR", fpath, lineno, f"AI slop / placeholder copy detected: {mm.group(0)!r}", True)
            aim = _AI_IMAGE_SLOP_RE.search(line)
            if aim:
                add_finding("SLOP-AI-IMAGE-01", "FLOOR", fpath, lineno, f"Synthetic AI image marker {aim.group(0)!r} detected; use authentic web/client photography", True)

            # 6. Default transition easing / transition: all / infinite animations / unthrottled scroll
            if is_css and _TRANSITION_ALL_RE.search(check_line):
                add_finding("SLOP-MOTION-02", "REFLEX", fpath, lineno, "Wildcard transition: all detected; transition explicit GPU properties only", True)
            if is_css and _DEFAULT_EASE_RE.search(check_line):
                add_finding("SLOP-MOTION-01", "FINISH", fpath, lineno, "Generic default easing (ease/linear); prefer cubic-bezier(0.22,1,0.36,1)", strict)
            if _INFINITE_ANIM_RE.search(check_line):
                add_finding("SLOP-MOTION-02", "REFLEX", fpath, lineno, "Unjustified infinite attention animation (animate-bounce/ping) detected", True)
            if _SCROLL_LISTENER_RE.search(check_line):
                add_finding("SLOP-PERF-01", "FINISH", fpath, lineno, "Raw window scroll listener; prefer IntersectionObserver or CSS view timeline", strict)

            # 7. Pitch-black dark backgrounds, indigo/violet defaults, decorative emojis, fake copy, RN magic widths
            if _PITCH_BLACK_BG_RE.search(check_line):
                add_finding("SLOP-DARK-01", "REFLEX", fpath, lineno, "Pure #000/#000000 dark background; use calibrated neutral (#09090B or #111113)", True)
            if not _is_palette_allowed("indigo-violet", allowed_p) and _INDIGO_SLOP_RE.search(check_line):
                add_finding("SLOP-PALETTE-01", "REFLEX", fpath, lineno, "Default indigo/violet SaaS cliché token detected", True)
            em = _DECORATIVE_EMOJI_RE.search(check_line)
            if em:
                add_finding("SLOP-EMOJI-01", "REFLEX", fpath, lineno, f"Decorative UI emoji {em.group(0)!r} detected; use monoline SVG icon", True)
            fp = _FAKE_PERSONA_RE.search(check_line)
            if fp:
                add_finding("SLOP-COPY-02", "FLOOR", fpath, lineno, f"Placeholder persona/company {fp.group(0)!r} detected", True)
            if is_html:
                mj = _ML_JARGON_RE.search(check_line)
                if mj:
                    add_finding("SLOP-COPY-02", "FLOOR", fpath, lineno, f"Internal ML/solver jargon {mj.group(0)!r} leaked into consumer HTML", True)
            if is_rn_tsx and _RN_MAGIC_WIDTH_RE.search(check_line):
                add_finding("SLOP-RN-LAYOUT-01", "REFLEX", fpath, lineno, "Magic fractional percentage width in React Native component; use flex/gap grid", True)

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
        bad_css.write_text(
            "body { font-family: 'Inter', sans-serif; --bg: #000000; background: #FFFBEB; color: #0F172A; }\n"
            ":root { --accent: #9E2B1B; --herb: #235334; }\n"
            ".c { z-index: 9999; transition: all 200ms ease; backdrop-filter: blur(16px); }\n"
            ".d { backdrop-filter: blur(20px); } .phone-notch { width: 64px; }\n",
            encoding="utf-8",
        )
        bad_html = td / "bad.html"
        bad_html.write_text(
            "<header><a class='wordmark'><svg width='28' height='28'><rect width='20' height='20'/></svg></a>"
            "<button class='mode-switch' data-testid='theme-toggle'>Dark</button></header>\n"
            "<section id='hero' class='hero'><h1>Title</h1><svg width='180' height='120'>"
            + "".join("<circle cx='60' cy='60' r='10'/>" for _ in range(6))
            + "</svg></section>\n"
            "<span class='fresh-dot'></span><p>Val mAP@50 ONNX Runtime · midjourney ai-generated</p>\n"
            + "".join("<div class='card feature-icon'>x</div>" for _ in range(8)),
            encoding="utf-8",
        )
        bad_tsx = td / "bad.tsx"
        bad_tsx.write_text(
            "const tokens = { bg: '#FAFAF8', accent: '#BD3D1E' };\n"
            "export const X = () => (\n"
            "  <View style={{ width: '48.5%', borderRadius: 9999 }}>\n"
            "    <ThemeToggle testID='theme-toggle' />\n"
            "    <Svg width={100} height={100}>"
            + "".join("<Circle cx='10' cy='10' r='5' />" for _ in range(6))
            + "</Svg>\n"
            "    <T v='eyebrow'>A · B · C · D</T>\n"
            "    <Text>✨ Ship seamless robust magic</Text>\n"
            "  </View>\n"
            ");\n",
            encoding="utf-8",
        )
        clean_css = td / "clean" / "ok.css"
        clean_css.parent.mkdir()
        clean_css.write_text(
            "body { font-family: 'Geist', sans-serif; background: #09090B; }\n"
            ".hero-scrim { background: linear-gradient(180deg, rgba(18, 14, 11, 0) 0%, rgba(18, 14, 11, 0.78) 100%); }\n"
            ".btn { transition: transform 200ms cubic-bezier(0.22, 1, 0.36, 1); }\n"
            "@media (prefers-reduced-motion: reduce) { .btn { transition: none; } }\n",
            encoding="utf-8",
        )
        clean_tsx = td / "clean" / "ok.tsx"
        clean_tsx.write_text(
            "import { ArrowRight } from '@phosphor-icons/react';\n"
            "export const Ok = () => <a href='#spec'>Inspect spec <ArrowRight aria-hidden='true' /></a>;\n",
            encoding="utf-8",
        )
        r_bad_css = scan_target(bad_css, strict=True)
        r_bad_html = scan_target(bad_html, strict=True)
        r_bad_tsx = scan_target(bad_tsx, strict=True)
        r_ok = scan_target(clean_css.parent, strict=True)
        rules_css = {f["rule"] for f in r_bad_css["findings"]}
        rules_html = {f["rule"] for f in r_bad_html["findings"]}
        rules_tsx = {f["rule"] for f in r_bad_tsx["findings"]}
        passed = (
            (not r_bad_css["passed"])
            and (not r_bad_html["passed"])
            and (not r_bad_tsx["passed"])
            and r_ok["passed"]
            and {"SLOP-FONT-01", "SLOP-DARK-01", "SLOP-COLOR-CLASH-01", "SLOP-COLOR-HARMONY-01", "SLOP-FAKE-DEVICE-01", "SLOP-ZIDX-01", "SLOP-MOTION-02", "SLOP-GLASS-01"}.issubset(rules_css)
            and {"SLOP-DOT-01", "SLOP-COPY-02", "SLOP-WALL-CARDS-01", "SLOP-ICON-BOX-01", "SLOP-SVG-LOGO-01", "SLOP-HERO-NO-PHOTO", "SLOP-AI-IMAGE-01", "SLOP-THEME-SWITCH-01", "SLOP-SVG-ART-01"}.issubset(rules_html)
            and {"SLOP-PALETTE-01", "SLOP-RN-LAYOUT-01", "SLOP-EYEBROW-01", "SLOP-EMOJI-01", "SLOP-COPY-01", "SLOP-THEME-SWITCH-01", "SLOP-SVG-ART-01"}.issubset(rules_tsx)
        )
        return {
            "passed": passed,
            "bad_css_rules": sorted(rules_css),
            "bad_html_rules": sorted(rules_html),
            "bad_tsx_rules": sorted(rules_tsx),
            "clean_findings": len(r_ok["findings"]),
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Anti-AI-slop static scanner and redesign regression checker."
    )
    parser.add_argument("target", nargs="?", default=None, help="File or directory to scan")
    parser.add_argument("--path", "--dir", "--root", "--file", "--target", dest="opt_target", help="Target file or directory")
    parser.add_argument("--allow-font", action="append", default=[], help="Allowlist a font family (repeatable)")
    parser.add_argument("--allow-icon", action="append", default=[], help="Allowlist an icon package (repeatable)")
    parser.add_argument("--allow-palette", action="append", default=[], help="Allowlist a palette rule (indigo-violet, cream-terracotta, all)")
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
        allow_palettes=set(args.allow_palette),
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
