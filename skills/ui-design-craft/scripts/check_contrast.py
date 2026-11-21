#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WCAG 2.1, APCA (W3), and Color Vision Deficiency (CVD) contrast validator.

Supports #RGB/#RRGGBB/#RRGGBBAA, rgb(...), oklch(...), DTCG JSON, and CSS files.
Pure Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

_HEX_RE = re.compile(r"^#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_RGB_RE = re.compile(
    r"^rgba?\(\s*([0-9.]+%?)\s*[,\s]\s*([0-9.]+%?)\s*[,\s]\s*([0-9.]+%?)"
    r"(?:\s*[,/]\s*([0-9.]+%?))?\s*\)$",
    re.IGNORECASE,
)
_OKLCH_RE = re.compile(
    r"^oklch\(\s*([0-9.]+%?)\s+([0-9.]+%?)\s+([0-9.+-]+(?:deg|rad|turn)?)"
    r"(?:\s*/\s*([0-9.]+%?))?\s*\)$",
    re.IGNORECASE,
)

# Viénot (1999) / Brettel linear-sRGB simulation 3x3 matrices for dichromacy
_CVD_MATRICES: dict[str, tuple[tuple[float, float, float], ...]] = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(lin: float) -> float:
    lin = max(0.0, min(1.0, lin))
    return 12.92 * lin if lin <= 0.0031308 else 1.055 * (lin ** (1.0 / 2.4)) - 0.055


def _parse_num_or_pct(token: str, scale: float) -> float:
    if token.endswith("%"):
        return float(token[:-1]) / 100.0 * scale
    return float(token)


def parse_color(spec: str) -> tuple[float, float, float, float]:
    """Parse #RGB/#RRGGBB/#RRGGBBAA, rgb(), or oklch() into (r, g, b, a) in 0..1."""
    raw = (spec or "").strip()
    if not raw:
        raise ValueError("Empty color string")

    if raw.startswith("#") or re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8}", raw):
        if not _HEX_RE.match(raw):
            raise ValueError(f"Invalid hex color: {spec!r}")
        h = raw.lstrip("#")
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        a = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
        return (r, g, b, a)

    m_rgb = _RGB_RE.match(raw)
    if m_rgb:
        r = max(0.0, min(1.0, _parse_num_or_pct(m_rgb.group(1), 255.0) / 255.0))
        g = max(0.0, min(1.0, _parse_num_or_pct(m_rgb.group(2), 255.0) / 255.0))
        b = max(0.0, min(1.0, _parse_num_or_pct(m_rgb.group(3), 255.0) / 255.0))
        a = 1.0
        if m_rgb.group(4):
            a = max(0.0, min(1.0, _parse_num_or_pct(m_rgb.group(4), 1.0)))
        return (r, g, b, a)

    m_ok = _OKLCH_RE.match(raw)
    if m_ok:
        L = float(m_ok.group(1)[:-1]) / 100.0 if m_ok.group(1).endswith("%") else float(m_ok.group(1))
        C = float(m_ok.group(2)[:-1]) / 100.0 * 0.4 if m_ok.group(2).endswith("%") else float(m_ok.group(2))
        h_raw = m_ok.group(3).lower()
        if h_raw.endswith("rad"):
            h_rad = float(h_raw[:-3])
        elif h_raw.endswith("turn"):
            h_rad = float(h_raw[:-4]) * 2.0 * math.pi
        else:
            h_deg = float(h_raw[:-3]) if h_raw.endswith("deg") else float(h_raw)
            h_rad = math.radians(h_deg)
        a_ok = C * math.cos(h_rad)
        b_ok = C * math.sin(h_rad)

        l_ = L + 0.3963377774 * a_ok + 0.2158037573 * b_ok
        m_ = L - 0.1055613458 * a_ok - 0.0638541728 * b_ok
        s_ = L - 0.0894841775 * a_ok - 1.2914855480 * b_ok

        l = l_ ** 3
        m = m_ ** 3
        s = s_ ** 3

        r_lin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

        alpha = 1.0
        if m_ok.group(4):
            alpha = max(0.0, min(1.0, _parse_num_or_pct(m_ok.group(4), 1.0)))
        return (_linear_to_srgb(r_lin), _linear_to_srgb(g_lin), _linear_to_srgb(b_lin), alpha)

    raise ValueError(f"Unsupported or invalid color syntax: {spec!r}")


def composite_over(fg: tuple[float, float, float, float], bg: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Alpha-composite foreground sRGB over background sRGB."""
    alpha = fg[3]
    if alpha >= 1.0:
        return (fg[0], fg[1], fg[2])
    return (
        alpha * fg[0] + (1.0 - alpha) * bg[0],
        alpha * fg[1] + (1.0 - alpha) * bg[1],
        alpha * fg[2] + (1.0 - alpha) * bg[2],
    )


def wcag_luminance(rgb: tuple[float, float, float]) -> float:
    r_lin = _srgb_to_linear(rgb[0])
    g_lin = _srgb_to_linear(rgb[1])
    b_lin = _srgb_to_linear(rgb[2])
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def wcag_ratio(fg_rgb: tuple[float, float, float], bg_rgb: tuple[float, float, float]) -> float:
    l1 = wcag_luminance(fg_rgb)
    l2 = wcag_luminance(bg_rgb)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def apca_lc(fg_rgb: tuple[float, float, float], bg_rgb: tuple[float, float, float]) -> float:
    """Compute APCA W3 (0.0.98G-4g) perceptual lightness contrast Lc."""
    def _ys(rgb: tuple[float, float, float]) -> float:
        y = 0.2126729 * (rgb[0] ** 2.4) + 0.7151522 * (rgb[1] ** 2.4) + 0.0721750 * (rgb[2] ** 2.4)
        return y if y >= 0.022 else y + (0.022 - y) ** 1.414

    txt_y = _ys(fg_rgb)
    bg_y = _ys(bg_rgb)
    if abs(bg_y - txt_y) < 0.0005:
        return 0.0

    if bg_y > txt_y:  # Dark text on light bg (BoW)
        sapc = ((bg_y ** 0.56) - (txt_y ** 0.57)) * 1.14
        if sapc < 0.1:
            return 0.0
        return (sapc - 0.027) * 100.0
    else:  # Light text on dark bg (WoB)
        sapc = ((bg_y ** 0.65) - (txt_y ** 0.62)) * 1.14
        if sapc > -0.1:
            return 0.0
        return (sapc + 0.027) * 100.0


def simulate_cvd(rgb: tuple[float, float, float], kind: str) -> tuple[float, float, float]:
    mat = _CVD_MATRICES[kind]
    lin = [_srgb_to_linear(c) for c in rgb]
    out_lin = [
        mat[0][0] * lin[0] + mat[0][1] * lin[1] + mat[0][2] * lin[2],
        mat[1][0] * lin[0] + mat[1][1] * lin[1] + mat[1][2] * lin[2],
        mat[2][0] * lin[0] + mat[2][1] * lin[1] + mat[2][2] * lin[2],
    ]
    return (_linear_to_srgb(out_lin[0]), _linear_to_srgb(out_lin[1]), _linear_to_srgb(out_lin[2]))


def evaluate_pair(
    fg_spec: str,
    bg_spec: str,
    large: bool = False,
    level: str = "AA",
    check_apca: bool = False,
    check_cvd: bool = False,
) -> dict[str, Any]:
    """Evaluate WCAG 2.1, optional APCA Lc, and optional CVD simulation on a fg/bg pair."""
    fg_rgba = parse_color(fg_spec)
    bg_rgba = parse_color(bg_spec)
    bg_rgb = (bg_rgba[0], bg_rgba[1], bg_rgba[2])
    fg_rgb = composite_over(fg_rgba, bg_rgba)

    ratio = wcag_ratio(fg_rgb, bg_rgb)
    if level.upper() == "AAA":
        wcag_min = 4.5 if large else 7.0
    else:
        wcag_min = 3.0 if large else 4.5

    wcag_pass = ratio >= wcag_min
    lc = apca_lc(fg_rgb, bg_rgb)
    apca_min = 45.0 if large else 60.0
    apca_pass = (abs(lc) >= apca_min) if check_apca else True

    cvd_results: dict[str, dict[str, Any]] = {}
    cvd_pass = True
    if check_cvd:
        for kind in ("protanopia", "deuteranopia", "tritanopia"):
            sim_fg = simulate_cvd(fg_rgb, kind)
            sim_bg = simulate_cvd(bg_rgb, kind)
            sim_ratio = wcag_ratio(sim_fg, sim_bg)
            ok = sim_ratio >= 3.0
            if not ok:
                cvd_pass = False
            cvd_results[kind] = {"wcag_ratio": round(sim_ratio, 2), "passes_min_3_0": ok}

    passed = wcag_pass and apca_pass and cvd_pass
    return {
        "fg": fg_spec,
        "bg": bg_spec,
        "wcag_ratio": round(ratio, 2),
        "wcag_threshold": wcag_min,
        "wcag_pass": wcag_pass,
        "apca_lc": round(lc, 1),
        "apca_threshold": apca_min if check_apca else None,
        "apca_pass": apca_pass,
        "cvd": cvd_results if check_cvd else None,
        "cvd_pass": cvd_pass,
        "passed": passed,
    }


def _collect_dtcg_tokens(node: Any, prefix: str = "", out: dict[str, str] | None = None) -> dict[str, str]:
    if out is None:
        out = {}
    if not isinstance(node, dict):
        return out
    if "$value" in node:
        val = node["$value"]
        if isinstance(val, str):
            out[prefix] = val
        return out
    for k, v in node.items():
        if k.startswith("$"):
            continue
        next_prefix = f"{prefix}.{k}" if prefix else k
        _collect_dtcg_tokens(v, next_prefix, out)
    return out


def _resolve_dtcg_aliases(tokens: dict[str, str]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for key, val in tokens.items():
        cur = val
        seen: set[str] = set()
        while isinstance(cur, str) and cur.startswith("{") and cur.endswith("}"):
            ref = cur[1:-1]
            if ref in seen or ref not in tokens:
                break
            seen.add(ref)
            cur = tokens[ref]
        resolved[key] = cur
    return resolved


def _extract_pairs_from_file(filepath: Path) -> list[tuple[str, str, str, str]]:
    """Extract candidate (label, fg, bg) semantic pairs from DTCG JSON or CSS."""
    text = filepath.read_text(encoding="utf-8")
    tokens: dict[str, str] = {}
    if filepath.suffix.lower() == ".json":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Token JSON root must be an object")
        tokens = _resolve_dtcg_aliases(_collect_dtcg_tokens(data))
    else:
        for m in re.finditer(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", text):
            tokens[m.group(1).lstrip("-").replace("-", ".")] = m.group(2).strip()

    color_tokens: dict[str, str] = {}
    for k, v in tokens.items():
        try:
            parse_color(v)
            color_tokens[k] = v
        except ValueError:
            continue

    pairs: list[tuple[str, str, str, str]] = []
    bgs: dict[str, str] = {}
    fgs: dict[str, str] = {}
    for k, v in color_tokens.items():
        low = k.lower()
        parts = set(re.split(r"[._-]+", low))
        if (
            bool(parts & {"bg", "surface", "canvas", "background", "elevated"})
            or any(t in low for t in ("surface.", "canvas", "background", "elevated", "bg.", ".bg", "bg-"))
        ) and "button" not in low:
            bgs[k] = v
        if (
            bool(parts & {"text", "foreground"})
            or any(t in low for t in ("text.", "foreground", "text-"))
        ) and "on-" not in low and "on." not in low and "primary-fg" not in low:
            fgs[k] = v
    for fk, fv in fgs.items():
        for bk, bv in bgs.items():
            pairs.append((f"{fk} on {bk}", fv, bv, fk))
    return pairs


def run_self_test() -> dict[str, Any]:
    cases = [
        ("#000000", "#FFFFFF", False, "AA", True),
        ("#767676", "#FFFFFF", False, "AA", True),
        ("#777777", "#FFFFFF", False, "AA", False),
        ("#949494", "#FFFFFF", True, "AA", True),
        ("#959595", "#FFFFFF", True, "AA", False),
        ("#595959", "#FFFFFF", False, "AAA", True),
        ("#5A5A5A", "#FFFFFF", False, "AAA", False),
        ("oklch(0.985 0.002 247)", "#09090B", False, "AA", True),
    ]
    results = []
    all_ok = True
    for fg, bg, large, lvl, expected in cases:
        ev = evaluate_pair(fg, bg, large=large, level=lvl, check_apca=True, check_cvd=True)
        ok = ev["passed"] == expected
        if not ok:
            all_ok = False
        results.append({"fg": fg, "bg": bg, "expected": expected, "actual": ev["passed"], "ratio": ev["wcag_ratio"]})
    return {"passed": all_ok, "results": results}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WCAG 2.1, APCA (W3), and CVD contrast validator for color pairs and DTCG/CSS files."
    )
    parser.add_argument("colors", nargs="*", help="Optional positional foreground and background colors")
    parser.add_argument("--fg", "--foreground", dest="fg", help="Foreground color (#hex, rgb(), oklch())")
    parser.add_argument("--bg", "--background", dest="bg", help="Background color (#hex, rgb(), oklch())")
    parser.add_argument("--file", "--path", "--input", "--target", dest="filepath", help="DTCG JSON or CSS token file")
    parser.add_argument("--large", "--large-text", "--ui", dest="large", action="store_true", help="Use 3.0:1 large text / UI threshold")
    parser.add_argument("--aaa", action="store_true", help="Enforce WCAG AAA (7.0:1 normal / 4.5:1 large)")
    parser.add_argument("--level", choices=["AA", "AAA"], default="AA", help="WCAG level (default: AA)")
    parser.add_argument("--apca", action="store_true", help="Also enforce APCA |Lc| threshold (60 normal / 45 large)")
    parser.add_argument("--cvd", action="store_true", help="Simulate protanopia/deuteranopia/tritanopia (>= 3.0:1)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in boundary verification")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        rep = run_self_test()
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"check_contrast self-test: {'PASS' if rep['passed'] else 'FAIL'}")
        return 0 if rep["passed"] else 1

    level = "AAA" if args.aaa else args.level

    try:
        if args.filepath:
            p = Path(args.filepath)
            if not p.is_file():
                raise ValueError(f"File not found: {p}")
            pairs = _extract_pairs_from_file(p)
            if not pairs:
                raise ValueError(f"No foreground/background color pairs detected in {p}")
            evaluations = []
            overall_pass = True
            for label, fg_v, bg_v, _ in pairs:
                ev = evaluate_pair(fg_v, bg_v, large=args.large, level=level, check_apca=args.apca, check_cvd=args.cvd)
                ev["pair"] = label
                if not ev["passed"]:
                    overall_pass = False
                evaluations.append(ev)
            out = {"file": str(p), "passed": overall_pass, "pairs": evaluations}
            if args.json:
                print(json.dumps(out, indent=2))
            else:
                for ev in evaluations:
                    status = "PASS" if ev["passed"] else "FAIL"
                    print(f"[{status}] {ev['pair']}: WCAG {ev['wcag_ratio']}:1 (min {ev['wcag_threshold']}:1) | APCA Lc {ev['apca_lc']}")
            return 0 if overall_pass else 1

        fg_val = args.fg or (args.colors[0] if len(args.colors) >= 1 else None)
        bg_val = args.bg or (args.colors[1] if len(args.colors) >= 2 else None)
        if not fg_val or not bg_val:
            raise ValueError("Provide --fg and --bg, two positional colors, or --file <tokens.json|styles.css>.")

        res = evaluate_pair(fg_val, bg_val, large=args.large, level=level, check_apca=args.apca, check_cvd=args.cvd)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status = "PASS" if res["passed"] else "FAIL"
            print(
                f"[{status}] {res['fg']} on {res['bg']} -> WCAG {res['wcag_ratio']}:1 "
                f"(required >= {res['wcag_threshold']}:1) | APCA Lc {res['apca_lc']}"
            )
            if res["cvd"]:
                for kind, info in res["cvd"].items():
                    print(f"  CVD {kind}: {info['wcag_ratio']}:1 ({'PASS' if info['passes_min_3_0'] else 'FAIL'})")
        return 0 if res["passed"] else 1
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        if args.json:
            print(json.dumps({"passed": False, "error": str(exc)}, indent=2))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
