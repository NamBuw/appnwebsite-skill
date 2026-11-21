#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core BM25 search engine for ui-design-craft across 12 domains and 22 stacks.

Pure Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3

BANNED_FONT_RE = re.compile(
    r"\b(?:Inter(?!-page\b)|Roboto|Arial|Open Sans|Helvetica)\b", re.IGNORECASE
)
BANNED_ICON_RE = re.compile(
    r"\b(?:Lucide|Feather|Heroicons|Material Icons|Material Symbols)\b", re.IGNORECASE
)

CSV_CONFIG: dict[str, dict[str, Any]] = {
    "style": {
        "file": "styles.csv",
        "search_cols": ["Style Category", "Keywords", "Best For", "Type", "AI Prompt Keywords"],
        "output_cols": [
            "Style Category", "Type", "Keywords", "Primary Colors", "Effects & Animation",
            "Best For", "Light Mode \u2713", "Dark Mode \u2713", "Performance",
            "Accessibility", "Framework Compatibility", "Complexity", "AI Prompt Keywords",
            "CSS/Technical Keywords", "Implementation Checklist", "Design System Variables",
        ],
    },
    "color": {
        "file": "colors.csv",
        "search_cols": ["Product Type", "Notes"],
        "output_cols": [
            "Product Type", "Primary", "On Primary", "Secondary", "On Secondary",
            "Accent", "On Accent", "Background", "Foreground", "Card", "Card Foreground",
            "Muted", "Muted Foreground", "Border", "Destructive", "On Destructive",
            "Ring", "Notes",
        ],
    },
    "chart": {
        "file": "charts.csv",
        "search_cols": [
            "Data Type", "Keywords", "Best Chart Type", "When to Use",
            "When NOT to Use", "Accessibility Notes",
        ],
        "output_cols": [
            "Data Type", "Keywords", "Best Chart Type", "Secondary Options",
            "When to Use", "When NOT to Use", "Data Volume Threshold", "Color Guidance",
            "Accessibility Grade", "Accessibility Notes", "A11y Fallback",
            "Library Recommendation", "Interactive Level",
        ],
    },
    "landing": {
        "file": "landing.csv",
        "search_cols": ["Pattern Name", "Keywords", "Conversion Optimization", "Section Order"],
        "output_cols": [
            "Pattern Name", "Keywords", "Section Order", "Primary CTA Placement",
            "Color Strategy", "Conversion Optimization",
        ],
    },
    "product": {
        "file": "products.csv",
        "search_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Key Considerations"],
        "output_cols": [
            "Product Type", "Keywords", "Primary Style Recommendation", "Secondary Styles",
            "Landing Page Pattern", "Dashboard Style (if applicable)", "Color Palette Focus",
        ],
    },
    "ux": {
        "file": "ux-guidelines.csv",
        "search_cols": ["Category", "Issue", "Description", "Platform"],
        "output_cols": [
            "Category", "Issue", "Platform", "Description", "Do", "Don't",
            "Code Example Good", "Code Example Bad", "Severity",
        ],
    },
    "typography": {
        "file": "typography.csv",
        "search_cols": [
            "Font Pairing Name", "Category", "Mood/Style Keywords",
            "Best For", "Heading Font", "Body Font",
        ],
        "output_cols": [
            "Font Pairing Name", "Category", "Heading Font", "Body Font",
            "Mood/Style Keywords", "Best For", "Google Fonts URL",
            "CSS Import", "Tailwind Config", "Notes",
        ],
    },
    "icons": {
        "file": "icons.csv",
        "search_cols": ["Category", "Icon Name", "Keywords", "Best For", "Library"],
        "output_cols": [
            "Category", "Icon Name", "Keywords", "Library",
            "Import Code", "Usage", "Best For", "Style",
        ],
    },
    "react": {
        "file": "react-performance.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": [
            "Category", "Issue", "Platform", "Description", "Do", "Don't",
            "Code Example Good", "Code Example Bad", "Severity",
        ],
    },
    "web": {
        "file": "app-interface.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": [
            "Category", "Issue", "Platform", "Description", "Do", "Don't",
            "Code Example Good", "Code Example Bad", "Severity",
        ],
    },
    "google-fonts": {
        "file": "google-fonts.csv",
        "search_cols": [
            "Family", "Category", "Stroke", "Classifications",
            "Keywords", "Subsets", "Designers",
        ],
        "output_cols": [
            "Family", "Category", "Stroke", "Classifications", "Styles",
            "Variable Axes", "Subsets", "Designers", "Popularity Rank", "Google Fonts URL",
        ],
    },
    "design": {
        "file": "design.csv",
        "parser": "design_blocks",
        "search_cols": ["Style", "Vibe", "Typography", "Colors", "Components", "Layout"],
        "output_cols": ["Style", "Vibe", "Colors", "Typography", "Icons", "Layout", "Summary"],
    },
}

STACK_CONFIG: dict[str, dict[str, str]] = {
    "react": {"file": "stacks/react.csv"},
    "nextjs": {"file": "stacks/nextjs.csv"},
    "vue": {"file": "stacks/vue.csv"},
    "svelte": {"file": "stacks/svelte.csv"},
    "astro": {"file": "stacks/astro.csv"},
    "swiftui": {"file": "stacks/swiftui.csv"},
    "react-native": {"file": "stacks/react-native.csv"},
    "flutter": {"file": "stacks/flutter.csv"},
    "nuxtjs": {"file": "stacks/nuxtjs.csv"},
    "nuxt-ui": {"file": "stacks/nuxt-ui.csv"},
    "html-tailwind": {"file": "stacks/html-tailwind.csv"},
    "shadcn": {"file": "stacks/shadcn.csv"},
    "jetpack-compose": {"file": "stacks/jetpack-compose.csv"},
    "threejs": {"file": "stacks/threejs.csv"},
    "angular": {"file": "stacks/angular.csv"},
    "laravel": {"file": "stacks/laravel.csv"},
    "javafx": {"file": "stacks/javafx.csv"},
    "wpf": {"file": "stacks/wpf.csv"},
    "winui": {"file": "stacks/winui.csv"},
    "avalonia": {"file": "stacks/avalonia.csv"},
    "uno": {"file": "stacks/uno.csv"},
    "uwp": {"file": "stacks/uwp.csv"},
}

_STACK_COLS: dict[str, list[str]] = {
    "search_cols": ["Category", "Guideline", "Description", "Do", "Don't"],
    "output_cols": [
        "Category", "Guideline", "Description", "Do", "Don't",
        "Code Good", "Code Bad", "Severity", "Docs URL",
    ],
}

AVAILABLE_STACKS: list[str] = list(STACK_CONFIG.keys())


class BM25:
    """Okapi BM25 text ranking implementation."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.corpus: list[list[str]] = []
        self.doc_lengths: list[int] = []
        self.avgdl: float = 0.0
        self.idf: dict[str, float] = {}
        self.doc_freqs: dict[str, int] = defaultdict(int)
        self.N: int = 0

    def tokenize(self, text: Any) -> list[str]:
        cleaned = re.sub(r"[^\w\s]", " ", str(text).lower())
        return [w for w in cleaned.split() if len(w) >= 2]

    def fit(self, documents: list[str]) -> None:
        self.corpus = [self.tokenize(doc) for doc in documents]
        self.N = len(self.corpus)
        if self.N == 0:
            return
        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_lengths) / self.N or 1.0

        for doc in self.corpus:
            for word in set(doc):
                self.doc_freqs[word] += 1

        for word, freq in self.doc_freqs.items():
            self.idf[word] = math.log((self.N - freq + 0.5) / (freq + 0.5) + 1.0)

    def score(self, query: str) -> list[tuple[int, float]]:
        query_tokens = self.tokenize(query)
        if not query_tokens or self.N == 0:
            return []
        scores: list[tuple[int, float]] = []
        for idx, doc in enumerate(self.corpus):
            total = 0.0
            doc_len = self.doc_lengths[idx]
            term_freqs: dict[str, int] = defaultdict(int)
            for word in doc:
                term_freqs[word] += 1
            for token in query_tokens:
                if token in self.idf:
                    tf = term_freqs[token]
                    idf = self.idf[token]
                    num = tf * (self.k1 + 1.0)
                    den = tf + self.k1 * (1.0 - self.b + self.b * doc_len / self.avgdl)
                    total += idf * num / den
            scores.append((idx, total))
        return sorted(scores, key=lambda pair: pair[1], reverse=True)


def _is_unsafe_or_empty_query(query: str) -> bool:
    q = (query or "").strip()
    if not q:
        return True
    if ".." in q or q.startswith(("/", "\\")) or "/etc/" in q:
        return True
    return False


def _load_csv(filepath: Path) -> list[dict[str, str]]:
    with filepath.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


_BLOCK_HEADER_RE = re.compile(
    r'^(?:"?(?:Bauhaus|Minimalist Monochrome|Modern Dark|SaaS|Terminal|Kinetic|'
    r'Flat Design|Material Design|Neo Brutalism|Bold Typography|Academia|Cyberpunk|'
    r'Claymorphism|Enterprise|Sketch|Neumorphism)\s*\(|"?web3"?$)',
    re.IGNORECASE,
)


def _truncate_word_boundary(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    clipped = text[:limit]
    if text[limit : limit + 1].isspace():
        return clipped.rstrip()
    if " " in clipped:
        return clipped.rsplit(" ", 1)[0].rstrip()
    return clipped


def _load_design_blocks(filepath: Path) -> list[dict[str, str]]:
    """Parse multi-block aesthetic DNA specs from design.csv into structured records."""
    if not filepath.is_file():
        return []
    lines = filepath.read_text(encoding="utf-8").splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if _BLOCK_HEADER_RE.match(line.strip()) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)

    records: list[dict[str, str]] = []
    for blk in blocks:
        text = "\n".join(blk)
        title = blk[0].strip().strip('"')
        vibe = ""
        for cand in blk[1:5]:
            s = cand.strip().strip('"')
            if s and not s[0].isdigit() and "<design-system>" not in s:
                vibe = s
                break

        def _extract_section(patterns: tuple[str, ...]) -> str:
            hits: list[str] = []
            for ln in blk:
                low = ln.lower()
                if any(p in low for p in patterns):
                    hits.append(ln.strip())
            return _truncate_word_boundary(" | ".join(hits[:6]), 400)

        records.append({
            "Style": title,
            "Vibe": _truncate_word_boundary(vibe, 300),
            "Colors": _extract_section(("color", "palette", "background", "accent", "#")),
            "Typography": _extract_section(("font", "typography", "headline", "body", "mono")),
            "Icons": _extract_section(("icon", "phosphor", "solar", "iconamoon")),
            "Components": _extract_section(("button", "card", "badge", "input", "modal")),
            "Layout": _extract_section(("grid", "layout", "radius", "border", "shadow", "spacing")),
            "Summary": _truncate_word_boundary(re.sub(r"\s+", " ", text), 450),
        })
    return records


def _row_is_filtered(row: dict[str, str], domain: str, allow_legacy: bool) -> bool:
    if allow_legacy:
        return False
    status = (row.get("Status") or row.get("Quarantine") or "").lower()
    if any(tag in status for tag in ("banned", "legacy", "deprecated")):
        return True
    if domain == "typography":
        combined = " ".join([
            row.get("Heading Font", ""),
            row.get("Body Font", ""),
            row.get("Font Pairing Name", ""),
        ])
        if BANNED_FONT_RE.search(combined):
            return True
    elif domain == "google-fonts":
        if BANNED_FONT_RE.search(row.get("Family", "")):
            return True
    elif domain == "icons":
        combined = " ".join([row.get("Library", ""), row.get("Import Code", "")])
        if BANNED_ICON_RE.search(combined):
            return True
    return False


def _search_records(
    records: list[dict[str, str]],
    search_cols: list[str],
    output_cols: list[str],
    query: str,
    max_results: int,
    domain: str,
    allow_legacy: bool,
) -> list[dict[str, str]]:
    filtered = [r for r in records if not _row_is_filtered(r, domain, allow_legacy)]
    if not filtered:
        return []
    documents = [" ".join(str(row.get(col, "")) for col in search_cols) for row in filtered]
    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)
    results: list[dict[str, str]] = []
    for idx, sc in ranked[:max_results]:
        if sc > 0:
            row = filtered[idx]
            results.append({col: row.get(col, "") for col in output_cols if col in row})
    return results


def detect_domain(query: str) -> str:
    """Auto-detect the most relevant UI domain from query keywords."""
    query_lower = query.lower()
    domain_keywords: dict[str, list[str]] = {
        "color": [
            "color", "palette", "hex", "rgb", "oklch", "token", "semantic",
            "accent", "destructive", "muted", "foreground", "contrast",
        ],
        "chart": ["chart", "graph", "visualization", "trend", "bar", "pie", "scatter", "heatmap", "funnel"],
        "landing": ["landing", "page", "cta", "conversion", "hero", "testimonial", "pricing", "section"],
        "product": [
            "saas", "ecommerce", "e-commerce", "fintech", "healthcare", "gaming",
            "portfolio", "crypto", "dashboard", "fitness", "restaurant", "hotel",
            "travel", "music", "education", "learning", "legal", "insurance",
            "medical", "beauty", "pharmacy", "dental", "pet", "dating", "booking",
            "crm", "invoice", "telemetry", "analytics", "developer",
        ],
        "design": ["dna", "aesthetic dna", "bauhaus", "monochrome", "cyberpunk", "claymorphism", "neumorphism"],
        "style": [
            "style", "design", "ui", "minimalism", "glassmorphism", "brutalism",
            "dark mode", "flat", "aurora", "prompt", "css", "variable", "tailwind",
        ],
        "ux": ["ux", "usability", "accessibility", "wcag", "touch", "scroll", "animation", "keyboard", "navigation", "mobile"],
        "typography": ["font pairing", "typography pairing", "heading font", "body font", "typography"],
        "google-fonts": ["google font", "font family", "font weight", "variable font", "noto", "monospace font", "serif font"],
        "icons": ["icon", "icons", "phosphor", "solar", "iconamoon", "symbol", "glyph", "svg icon"],
        "react": ["react", "next.js", "nextjs", "suspense", "memo", "rerender", "bundle", "barrel", "rsc"],
        "web": ["aria", "focus", "outline", "semantic", "virtualize", "autocomplete", "form", "preconnect"],
    }
    scores = {
        domain: sum(1 for kw in kws if re.search(r"\b" + re.escape(kw) + r"\b", query_lower))
        for domain, kws in domain_keywords.items()
    }
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "style"


def search(
    query: str,
    domain: str | None = None,
    max_results: int = MAX_RESULTS,
    allow_legacy: bool = False,
) -> dict[str, Any]:
    """Search a domain dataset using BM25 with conflict filtering."""
    if _is_unsafe_or_empty_query(query):
        return {
            "domain": domain or "style",
            "query": query,
            "file": "",
            "count": 0,
            "results": [],
        }
    if domain is None:
        domain = detect_domain(query)
    config = CSV_CONFIG.get(domain, CSV_CONFIG["style"])
    filepath = DATA_DIR / config["file"]
    if not filepath.is_file():
        return {"error": f"Dataset not found: {filepath.name}", "domain": domain, "count": 0, "results": []}

    try:
        if config.get("parser") == "design_blocks":
            records = _load_design_blocks(filepath)
        else:
            records = _load_csv(filepath)
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        return {"error": f"Failed to load dataset {filepath.name}: {exc}", "domain": domain, "count": 0, "results": []}

    results = _search_records(
        records,
        config["search_cols"],
        config["output_cols"],
        query,
        max(1, max_results),
        domain,
        allow_legacy,
    )
    return {
        "domain": domain,
        "query": query,
        "file": config["file"],
        "count": len(results),
        "results": results,
    }


def search_stack(
    query: str,
    stack: str,
    max_results: int = MAX_RESULTS,
    allow_legacy: bool = False,
) -> dict[str, Any]:
    """Search stack-specific guidelines for any of the 22 supported stacks."""
    if stack not in STACK_CONFIG:
        return {
            "error": f"Unknown stack: {stack}. Available: {', '.join(AVAILABLE_STACKS)}",
            "count": 0,
            "results": [],
        }
    if _is_unsafe_or_empty_query(query):
        return {"domain": "stack", "stack": stack, "query": query, "file": STACK_CONFIG[stack]["file"], "count": 0, "results": []}

    filepath = DATA_DIR / STACK_CONFIG[stack]["file"]
    if not filepath.is_file():
        return {"error": f"Stack dataset not found: {filepath.name}", "stack": stack, "count": 0, "results": []}

    try:
        records = _load_csv(filepath)
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        return {"error": f"Failed to load stack dataset {filepath.name}: {exc}", "stack": stack, "count": 0, "results": []}

    results = _search_records(
        records,
        _STACK_COLS["search_cols"],
        _STACK_COLS["output_cols"],
        query,
        max(1, max_results),
        "stack",
        allow_legacy,
    )
    return {
        "domain": "stack",
        "stack": stack,
        "query": query,
        "file": STACK_CONFIG[stack]["file"],
        "count": len(results),
        "results": results,
    }


def run_self_test() -> dict[str, Any]:
    """Verify datasets, BM25 ranking, conflict filtering, and path safety."""
    checks: list[dict[str, Any]] = []
    typo_res = search("modern developer saas", domain="typography", max_results=5)
    serialized_typo = json.dumps(typo_res)
    checks.append({
        "check": "typography_clean",
        "count": typo_res["count"],
        "banned_found": bool(BANNED_FONT_RE.search(serialized_typo)),
    })
    icon_res = search("dashboard navigation", domain="icons", max_results=5)
    serialized_icon = json.dumps(icon_res)
    checks.append({
        "check": "icons_clean",
        "count": icon_res["count"],
        "banned_found": bool(BANNED_ICON_RE.search(serialized_icon)),
    })
    design_res = search("bauhaus geometric", domain="design", max_results=2)
    checks.append({"check": "design_blocks", "count": design_res["count"]})
    stack_res = search_stack("accessibility performance", "nextjs", max_results=2)
    checks.append({"check": "stack_nextjs", "count": stack_res["count"]})
    trav_res = search("../../etc/passwd")
    checks.append({"check": "traversal_safe", "count": trav_res["count"]})

    passed = (
        typo_res["count"] > 0
        and not checks[0]["banned_found"]
        and icon_res["count"] > 0
        and not checks[1]["banned_found"]
        and design_res["count"] > 0
        and stack_res["count"] > 0
        and trav_res["count"] == 0
    )
    return {"passed": passed, "checks": checks}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BM25 UI/UX search engine across 12 domains and 22 stacks."
    )
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Target domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Target stack")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--allow-legacy", action="store_true", help="Include legacy/banned font & icon entries")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification checks")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        report = run_self_test()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"core_search self-test: {'PASS' if report['passed'] else 'FAIL'}")
        return 0 if report["passed"] else 1

    if not args.query.strip():
        msg = {"error": "Query string is required unless --self-test is passed.", "count": 0, "results": []}
        if args.json:
            print(json.dumps(msg, indent=2))
        else:
            print(msg["error"], file=sys.stderr)
        return 1

    if args.stack:
        result = search_stack(args.query, args.stack, args.max_results, allow_legacy=args.allow_legacy)
    else:
        result = search(args.query, args.domain, args.max_results, allow_legacy=args.allow_legacy)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("error"):
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1
        print(f"Domain: {result.get('stack') or result.get('domain')} | Query: {result['query']} | Results: {result['count']}")
        for idx, row in enumerate(result["results"], 1):
            print(f"\n--- Result {idx} ---")
            for k, v in row.items():
                val = str(v)
                if len(val) > 260:
                    val = val[:260] + "..."
                print(f"{k}: {val}")
    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
