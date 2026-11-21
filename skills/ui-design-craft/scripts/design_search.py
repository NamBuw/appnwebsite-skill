#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified design search and MASTER.md design-system generator for ui-design-craft.

Pure Python 3 standard library only (imports sibling core_search and check_contrast).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import check_contrast
from core_search import (
    AVAILABLE_STACKS,
    BANNED_FONT_RE,
    BANNED_ICON_RE,
    CSV_CONFIG,
    DATA_DIR,
    MAX_RESULTS,
    search,
    search_stack,
)

REASONING_FILE = "ui-reasoning.csv"
SEARCH_CONFIG: dict[str, int] = {
    "product": 1,
    "style": 3,
    "color": 2,
    "landing": 2,
    "typography": 2,
    "design": 1,
}

DEFAULT_HEADING_FONT = "Geist"
DEFAULT_BODY_FONT = "Manrope"
DEFAULT_ICON_STANDARD = "Phosphor (@phosphor-icons/react), Solar, or Iconamoon"


def _sanitize_clean_text(text: str) -> str:
    """Ensure generated MASTER.md/ASCII output never emits banned font/icon names."""
    out = BANNED_FONT_RE.sub("Geist", text or "")
    out = BANNED_ICON_RE.sub("Phosphor", out)
    return out


def _safe_wcag_contrast(fg: str, bg: str) -> str:
    if not fg or not bg:
        return "N/A"
    try:
        ev = check_contrast.evaluate_pair(fg, bg)
        badge = "PASS AA" if ev["wcag_pass"] else "CHECK (< 4.5:1)"
        return f"{ev['wcag_ratio']}:1 ({badge}, APCA Lc {ev['apca_lc']})"
    except ValueError:
        return "N/A"


class DesignSystemGenerator:
    """Aggregates multi-domain BM25 search and ui-reasoning.csv rules."""

    def __init__(self) -> None:
        self.reasoning_data = self._load_reasoning()

    def _load_reasoning(self) -> list[dict[str, str]]:
        filepath = DATA_DIR / REASONING_FILE
        if not filepath.is_file():
            return []
        with filepath.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def _find_reasoning_rule(self, category: str) -> dict[str, str]:
        cat_lower = category.lower().strip()
        for rule in self.reasoning_data:
            if rule.get("UI_Category", "").lower().strip() == cat_lower:
                return rule
        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            if ui_cat and (ui_cat in cat_lower or cat_lower in ui_cat):
                return rule
        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            kws = [k for k in re.split(r"[\s/-]+", ui_cat) if len(k) >= 3]
            if any(kw in cat_lower for kw in kws):
                return rule
        return {}

    def _apply_reasoning(self, category: str) -> dict[str, Any]:
        rule = self._find_reasoning_rule(category)
        if not rule:
            return {
                "pattern": "Hero + Features + CTA",
                "style_priority": ["Minimalism", "Flat Design"],
                "color_mood": "High-contrast semantic neutrals + single accent",
                "typography_mood": "Crisp geometric sans hierarchy",
                "key_effects": "Weighted decel transitions (200ms cubic-bezier(0.22, 1, 0.36, 1))",
                "anti_patterns": "",
                "decision_rules": {},
                "severity": "MEDIUM",
            }
        decision_rules: dict[str, Any] = {}
        try:
            decision_rules = json.loads(rule.get("Decision_Rules", "{}") or "{}")
        except json.JSONDecodeError:
            decision_rules = {}
        return {
            "pattern": rule.get("Recommended_Pattern", "Hero + Features + CTA"),
            "style_priority": [s.strip() for s in rule.get("Style_Priority", "").split("+") if s.strip()],
            "color_mood": rule.get("Color_Mood", ""),
            "typography_mood": rule.get("Typography_Mood", ""),
            "key_effects": rule.get("Key_Effects", ""),
            "anti_patterns": rule.get("Anti_Patterns", ""),
            "decision_rules": decision_rules,
            "severity": rule.get("Severity", "MEDIUM"),
        }

    def _select_best_style(self, results: list[dict[str, str]], priorities: list[str]) -> dict[str, str]:
        if not results:
            return {}
        for prio in priorities:
            pl = prio.lower()
            for res in results:
                sname = res.get("Style Category", "").lower()
                if pl in sname or sname in pl:
                    return res
        return results[0]

    def generate(
        self, query: str, project_name: str | None = None, allow_legacy: bool = False
    ) -> dict[str, Any]:
        product_res = search(query, domain="product", max_results=1, allow_legacy=allow_legacy)
        prod_rows = product_res.get("results", [])
        category = prod_rows[0].get("Product Type", "General") if prod_rows else "General"
        reasoning = self._apply_reasoning(category)

        style_prio = reasoning.get("style_priority", [])
        style_query = f"{query} {' '.join(style_prio[:2])}".strip()
        style_res = search(style_query, domain="style", max_results=SEARCH_CONFIG["style"], allow_legacy=allow_legacy)
        color_res = search(query, domain="color", max_results=SEARCH_CONFIG["color"], allow_legacy=allow_legacy)
        landing_res = search(query, domain="landing", max_results=SEARCH_CONFIG["landing"], allow_legacy=allow_legacy)
        typo_res = search(query, domain="typography", max_results=SEARCH_CONFIG["typography"], allow_legacy=allow_legacy)
        dna_res = search(query, domain="design", max_results=SEARCH_CONFIG["design"], allow_legacy=allow_legacy)

        best_style = self._select_best_style(style_res.get("results", []), style_prio)
        best_color = (color_res.get("results") or [{}])[0]
        best_landing = (landing_res.get("results") or [{}])[0]
        best_typo = (typo_res.get("results") or [{}])[0]
        best_dna = (dna_res.get("results") or [{}])[0]

        heading_font = best_typo.get("Heading Font") or DEFAULT_HEADING_FONT
        body_font = best_typo.get("Body Font") or DEFAULT_BODY_FONT
        if not allow_legacy:
            if BANNED_FONT_RE.search(heading_font):
                heading_font = DEFAULT_HEADING_FONT
            if BANNED_FONT_RE.search(body_font):
                body_font = DEFAULT_BODY_FONT

        fg_hex = best_color.get("Foreground", "#09090B")
        bg_hex = best_color.get("Background", "#FAFAFA")
        primary_hex = best_color.get("Primary", "#2563EB")
        on_primary_hex = best_color.get("On Primary", "#FAFAFA")

        return {
            "project_name": project_name or query.strip().title() or "PROJECT",
            "category": category,
            "pattern": {
                "name": best_landing.get("Pattern Name") or reasoning.get("pattern", "Hero + Features + CTA"),
                "sections": best_landing.get("Section Order", "Hero > Proof > Features > Pricing > CTA"),
                "cta_placement": best_landing.get("Primary CTA Placement", "Above fold"),
                "color_strategy": best_landing.get("Color Strategy", ""),
                "conversion": best_landing.get("Conversion Optimization", ""),
            },
            "style": {
                "name": best_style.get("Style Category", "Minimalism"),
                "type": best_style.get("Type", "General"),
                "effects": best_style.get("Effects & Animation", "") or reasoning.get("key_effects", ""),
                "keywords": best_style.get("Keywords", ""),
                "best_for": best_style.get("Best For", ""),
                "performance": best_style.get("Performance", ""),
                "accessibility": best_style.get("Accessibility", ""),
                "light_mode": best_style.get("Light Mode \u2713", ""),
                "dark_mode": best_style.get("Dark Mode \u2713", ""),
            },
            "aesthetic_dna": best_dna.get("Style", ""),
            "colors": {
                "primary": primary_hex,
                "on_primary": on_primary_hex,
                "secondary": best_color.get("Secondary", "#18181B"),
                "accent": best_color.get("Accent", "#059669"),
                "background": bg_hex,
                "foreground": fg_hex,
                "card": best_color.get("Card", "#FFFFFF"),
                "card_foreground": best_color.get("Card Foreground", fg_hex),
                "muted": best_color.get("Muted", "#F4F4F5"),
                "muted_foreground": best_color.get("Muted Foreground", "#52525B"),
                "border": best_color.get("Border", "#E4E4E7"),
                "destructive": best_color.get("Destructive", "#DC2626"),
                "ring": best_color.get("Ring", primary_hex),
                "notes": best_color.get("Notes", ""),
                "contrast_fg_bg": _safe_wcag_contrast(fg_hex, bg_hex),
                "contrast_on_primary": _safe_wcag_contrast(on_primary_hex, primary_hex),
            },
            "typography": {
                "heading": heading_font,
                "body": body_font,
                "mood": best_typo.get("Mood/Style Keywords", reasoning.get("typography_mood", "")),
                "best_for": best_typo.get("Best For", ""),
                "google_fonts_url": _sanitize_clean_text(best_typo.get("Google Fonts URL", "")),
                "css_import": _sanitize_clean_text(best_typo.get("CSS Import", "")),
            },
            "icons": {
                "standard": DEFAULT_ICON_STANDARD,
                "primary_package": "@phosphor-icons/react",
            },
            "key_effects": _sanitize_clean_text(best_style.get("Effects & Animation", "") or reasoning.get("key_effects", "")),
            "anti_patterns": _sanitize_clean_text(reasoning.get("anti_patterns", "")),
            "decision_rules": reasoning.get("decision_rules", {}),
            "severity": reasoning.get("severity", "MEDIUM"),
        }


def format_master_md(ds: dict[str, Any]) -> str:
    project = ds.get("project_name", "PROJECT")
    pattern = ds.get("pattern", {})
    style = ds.get("style", {})
    colors = ds.get("colors", {})
    typo = ds.get("typography", {})
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = [
        "# Design System Master File",
        "",
        "> **LOGIC:** When building a specific page, inspect `design-system/pages/[page-name].md` first.",
        "> If that file exists, its rules **override** this Master file. Otherwise, follow the tokens and specs below.",
        "",
        "---",
        "",
        f"**Project:** {project}",
        f"**Generated:** {timestamp}",
        f"**Category:** {ds.get('category', 'General')}",
        f"**Icon Standard:** {ds.get('icons', {}).get('standard', DEFAULT_ICON_STANDARD)}",
        "",
        "---",
        "",
        "## Global Rules",
        "",
        "### Color Palette & Contrast Verification",
        "",
        "| Role | Hex | CSS Variable |",
        "|------|-----|--------------|",
    ]
    for label, key, var in (
        ("Primary", "primary", "--color-primary"),
        ("On Primary", "on_primary", "--color-on-primary"),
        ("Secondary", "secondary", "--color-secondary"),
        ("Accent/CTA", "accent", "--color-accent"),
        ("Background", "background", "--color-background"),
        ("Foreground", "foreground", "--color-foreground"),
        ("Card", "card", "--color-card"),
        ("Card Foreground", "card_foreground", "--color-card-foreground"),
        ("Muted", "muted", "--color-muted"),
        ("Muted Foreground", "muted_foreground", "--color-muted-foreground"),
        ("Border", "border", "--color-border"),
        ("Destructive", "destructive", "--color-destructive"),
        ("Ring", "ring", "--color-ring"),
    ):
        val = colors.get(key, "")
        if val:
            lines.append(f"| {label} | `{val}` | `{var}` |")

    lines.extend([
        "",
        f"- **Foreground/Background Contrast:** {colors.get('contrast_fg_bg', 'N/A')}",
        f"- **On-Primary/Primary Contrast:** {colors.get('contrast_on_primary', 'N/A')}",
    ])
    if colors.get("notes"):
        lines.append(f"- **Palette Notes:** {_sanitize_clean_text(colors['notes'])}")

    lines.extend([
        "",
        "### Typography",
        "",
        f"- **Heading Font:** {typo.get('heading', DEFAULT_HEADING_FONT)}",
        f"- **Body Font:** {typo.get('body', DEFAULT_BODY_FONT)}",
    ])
    if typo.get("mood"):
        lines.append(f"- **Mood:** {_sanitize_clean_text(typo['mood'])}")
    if typo.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** [{typo.get('heading')} + {typo.get('body')}]({typo['google_fonts_url']})")
    if typo.get("css_import"):
        lines.extend(["", "```css", typo["css_import"], "```"])

    lines.extend([
        "",
        "### Spacing, Radius & Motion Tokens",
        "",
        "```css",
        ":root {",
        "  --space-0: 0px;",
        "  --space-50: 2px;",
        "  --space-100: 4px;",
        "  --space-200: 8px;",
        "  --space-300: 12px;",
        "  --space-400: 16px;",
        "  --space-500: 24px;",
        "  --space-600: 32px;",
        "  --space-700: 48px;",
        "  --space-800: 64px;",
        "  --space-900: 96px;",
        "  --radius-card: 12px;",
        "  --radius-control: 8px;",
        "  --ease-out-expo: cubic-bezier(0.22, 1, 0.36, 1);",
        "  --z-base: 0;",
        "  --z-sticky: 20;",
        "  --z-modal: 40;",
        "  --z-toast: 60;",
        "}",
        "```",
        "",
        "## Component Specs (Tokenized)",
        "",
        "```css",
        ".btn-primary {",
        "  background: var(--color-primary);",
        "  color: var(--color-on-primary);",
        "  padding: var(--space-200) var(--space-300);",
        "  border-radius: var(--radius-control);",
        "  font-weight: 600;",
        "  transition: transform 200ms var(--ease-out-expo), opacity 200ms var(--ease-out-expo);",
        "}",
        ".card {",
        "  background: var(--color-card);",
        "  color: var(--color-card-foreground);",
        "  border: 1px solid var(--color-border);",
        "  border-radius: var(--radius-card);",
        "  padding: var(--space-500);",
        "}",
        ".input {",
        "  border: 1px solid var(--color-border);",
        "  border-radius: var(--radius-control);",
        "  padding: var(--space-200) var(--space-300);",
        "}",
        "@media (prefers-reduced-motion: reduce) {",
        "  .btn-primary { transition: none; }",
        "}",
        "```",
        "",
        "## Style & Page Pattern",
        "",
        f"- **Style:** {_sanitize_clean_text(style.get('name', 'Minimalism'))}",
        f"- **Pattern:** {_sanitize_clean_text(pattern.get('name', ''))}",
        f"- **Section Order:** {_sanitize_clean_text(pattern.get('sections', ''))}",
        f"- **Key Effects:** {ds.get('key_effects', '')}",
        "",
        "## Anti-Patterns & Pre-Delivery Gate",
        "",
    ])
    if ds.get("anti_patterns"):
        for item in [a.strip() for a in ds["anti_patterns"].split("+") if a.strip()]:
            lines.append(f"- Avoid: {_sanitize_clean_text(item)}")
    lines.extend([
        "- Avoid generic default system sans fonts or legacy unapproved icon packs; standardize on Phosphor, Solar, or Iconamoon.",
        "- Avoid arbitrary `z-index` spikes (`>= 999`) or full-card background gradients.",
        "- [ ] Run `check_contrast.py` on all semantic fg/bg pairs (`>= 4.5:1` AA, APCA `|Lc| >= 60`).",
        "- [ ] Run `validate_tokens.py` on DTCG `tokens.json`.",
        "- [ ] Run `check_anti_slop.py` on generated UI & CSS files.",
        "",
    ])
    return _sanitize_clean_text("\n".join(lines))


def format_page_override_md(ds: dict[str, Any], page_name: str, page_query: str | None) -> str:
    title = page_name.replace("-", " ").replace("_", " ").title()
    ux_res = search(f"{page_name} {page_query or ''}", domain="ux", max_results=3)
    landing_res = search(f"{page_name} {page_query or ''}", domain="landing", max_results=1)
    lines = [
        f"# {title} Page Overrides",
        "",
        f"> **PROJECT:** {ds.get('project_name', 'PROJECT')}",
        "> **LOGIC:** Overrides `MASTER.md` only where listed below.",
        "",
        "## Layout & Section Overrides",
        "",
    ]
    if landing_res.get("results"):
        lr = landing_res["results"][0]
        lines.append(f"- **Recommended Sections:** {_sanitize_clean_text(lr.get('Section Order', ''))}")
        lines.append(f"- **CTA Placement:** {_sanitize_clean_text(lr.get('Primary CTA Placement', ''))}")
    else:
        lines.append("- Inherit Master container width (`1280px`) and 12-column responsive grid.")
    lines.extend(["", "## UX Guidance", ""])
    for ux in ux_res.get("results", []):
        if ux.get("Do"):
            lines.append(f"- **{ux.get('Category', 'UX')}:** {_sanitize_clean_text(ux['Do'])}")
    lines.append("")
    return _sanitize_clean_text("\n".join(lines))


def persist_design_system(
    ds: dict[str, Any],
    page: str | None = None,
    output_dir: str | None = None,
    page_query: str | None = None,
) -> dict[str, Any]:
    base_dir = Path(output_dir) if output_dir else Path.cwd()
    slug = re.sub(r"[^a-z0-9-]+", "-", (ds.get("project_name") or "default").lower()).strip("-") or "default"
    ds_dir = base_dir / "design-system" / slug
    pages_dir = ds_dir / "pages"
    ds_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    master_path = ds_dir / "MASTER.md"
    master_path.write_text(format_master_md(ds), encoding="utf-8")
    created.append(str(master_path))

    if page:
        page_slug = re.sub(r"[^a-z0-9-]+", "-", page.lower()).strip("-") or "page"
        page_path = pages_dir / f"{page_slug}.md"
        page_path.write_text(format_page_override_md(ds, page, page_query), encoding="utf-8")
        created.append(str(page_path))

    return {"status": "success", "design_system_dir": str(ds_dir), "created_files": created}


def format_markdown(ds: dict[str, Any]) -> str:
    return format_master_md(ds)


def format_ascii_box(ds: dict[str, Any]) -> str:
    colors = ds.get("colors", {})
    typo = ds.get("typography", {})
    lines = [
        "=" * 76,
        f"TARGET: {ds.get('project_name')} | Category: {ds.get('category')}",
        "=" * 76,
        f"Pattern : {ds.get('pattern', {}).get('name', '')}",
        f"Sections: {ds.get('pattern', {}).get('sections', '')}",
        f"Style   : {ds.get('style', {}).get('name', '')}",
        f"Fonts   : {typo.get('heading')} / {typo.get('body')}",
        f"Icons   : {ds.get('icons', {}).get('standard', DEFAULT_ICON_STANDARD)}",
        f"Colors  : primary={colors.get('primary')} bg={colors.get('background')} fg={colors.get('foreground')}",
        f"Contrast: {colors.get('contrast_fg_bg')}",
        "=" * 76,
    ]
    return _sanitize_clean_text("\n".join(lines))


def format_search_output(result: dict[str, Any]) -> str:
    if result.get("error"):
        return f"Error: {result['error']}"
    header = (
        f"## Stack Guidelines ({result['stack']})"
        if result.get("stack")
        else f"## Search Results ({result['domain']})"
    )
    lines = [header, f"**Query:** {result['query']} | **Found:** {result['count']}", ""]
    for idx, row in enumerate(result["results"], 1):
        lines.append(f"### Result {idx}")
        for k, v in row.items():
            s = str(v)
            if len(s) > 280:
                s = s[:280] + "..."
            lines.append(f"- **{k}:** {s}")
        lines.append("")
    return "\n".join(lines)


def run_self_test() -> dict[str, Any]:
    gen = DesignSystemGenerator()
    ds = gen.generate("B2B SaaS developer analytics", project_name="SelfTestApp")
    md = format_master_md(ds)
    has_banned = bool(BANNED_FONT_RE.search(md) or BANNED_ICON_RE.search(md))
    stack_ok = search_stack("accessibility performance", "nextjs", max_results=2)["count"] > 0
    return {
        "passed": (not has_banned) and stack_ok and bool(ds.get("colors", {}).get("primary")),
        "category": ds.get("category"),
        "fonts": f"{ds['typography']['heading']} / {ds['typography']['body']}",
        "banned_found": has_banned,
        "stack_ok": stack_ok,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified ui-design-craft CLI: BM25 search + Design System MASTER.md generator."
    )
    parser.add_argument("query", nargs="?", default="", help="Search or product description query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search specific domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Search stack-specific guidelines")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--design-system", "-ds", action="store_true", help="Generate full design system")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for design system")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Design system output format")
    parser.add_argument("--persist", action="store_true", help="Persist MASTER.md (and optional pages/<page>.md)")
    parser.add_argument("--page", type=str, default=None, help="Optional page-specific override file")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Output base directory for --persist")
    parser.add_argument("--allow-legacy", action="store_true", help="Allow legacy/banned font & icon rows")
    parser.add_argument("--self-test", action="store_true", help="Run built-in design_search self-test")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        rep = run_self_test()
        print(json.dumps(rep, indent=2) if args.json else f"design_search self-test: {'PASS' if rep['passed'] else 'FAIL'}")
        return 0 if rep["passed"] else 1

    if not args.query.strip():
        msg = "Query string is required unless --self-test is passed."
        print(json.dumps({"error": msg}) if args.json else f"Error: {msg}", file=sys.stderr if not args.json else sys.stdout)
        return 1

    if args.design_system:
        gen = DesignSystemGenerator()
        ds = gen.generate(args.query, project_name=args.project_name, allow_legacy=args.allow_legacy)
        persisted = None
        if args.persist:
            persisted = persist_design_system(ds, page=args.page, output_dir=args.output_dir, page_query=args.query)
        formatted = format_markdown(ds) if args.format == "markdown" else format_ascii_box(ds)
        if args.json:
            payload = {"design_system": ds, "persisted": persisted, "formatted": formatted}
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(formatted)
            if persisted:
                print("\nPersisted files:")
                for cf in persisted["created_files"]:
                    print(f"  - {cf}")
        return 0

    if args.stack:
        result = search_stack(args.query, args.stack, args.max_results, allow_legacy=args.allow_legacy)
    else:
        result = search(args.query, args.domain, args.max_results, allow_legacy=args.allow_legacy)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_search_output(result))
    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
