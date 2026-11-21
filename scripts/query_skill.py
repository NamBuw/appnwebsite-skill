#!/usr/bin/env python3
"""Minimal-token progressive-disclosure CLI for appnwebsite-skill (Python 3 stdlib only).

Indexes Parent SKILL.md, references/, templates/, registry.json, and active skills/*/.
Supports BM25 (k1=1.5, b=0.75) + MMR reranking, pillar extraction, stage/surface routing,
fence-aware --headings / --extract, and --audit-budget checks.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "with", "when",
    "will", "not", "all", "any", "only", "must", "can", "use", "using", "into", "if",
}

PILLAR_ALIASES: dict[str, tuple[int, str]] = {
    "1": (1, r"^##\s+1\.\s+Decision\s+Framework\b"),
    "decision": (1, r"^##\s+1\.\s+Decision\s+Framework\b"),
    "framework": (1, r"^##\s+1\.\s+Decision\s+Framework\b"),
    "2": (2, r"^##\s+2\.\s+Step-by-Step\s+Workflow\b"),
    "workflow": (2, r"^##\s+2\.\s+Step-by-Step\s+Workflow\b"),
    "3": (3, r"^##\s+3\.\s+Reusable\s+Artifact\s+(?:&|and)\s+Template\b"),
    "template": (3, r"^##\s+3\.\s+Reusable\s+Artifact\s+(?:&|and)\s+Template\b"),
    "artifact": (3, r"^##\s+3\.\s+Reusable\s+Artifact\s+(?:&|and)\s+Template\b"),
    "4": (4, r"^##\s+4\.\s+Verification\s+Checklist\b"),
    "checklist": (4, r"^##\s+4\.\s+Verification\s+Checklist\b"),
    "5": (5, r"^##\s+5\.\s+Hard\s+Quality\s+Gate\b"),
    "gate": (5, r"^##\s+5\.\s+Hard\s+Quality\s+Gate\b"),
    "gates": (5, r"^##\s+5\.\s+Hard\s+Quality\s+Gate\b"),
    "6": (6, r"^##\s+6\.\s+Anti-Patterns\b"),
    "antipattern": (6, r"^##\s+6\.\s+Anti-Patterns\b"),
    "antipatterns": (6, r"^##\s+6\.\s+Anti-Patterns\b"),
    "anti-pattern": (6, r"^##\s+6\.\s+Anti-Patterns\b"),
    "anti-patterns": (6, r"^##\s+6\.\s+Anti-Patterns\b"),
}

STAGE_ALIASES = {
    "q1": "Q1",
    "1": "Q1",
    "charter": "Q1",
    "q2": "Q2",
    "2": "Q2",
    "risk": "Q2",
    "3a": "3A",
    "q3a": "3A",
    "foundation": "3A",
    "3b": "3B",
    "q3b": "3B",
    "build": "3B",
    "3c": "3C",
    "q3c": "3C",
    "qa": "3C",
    "condensation": "3C",
    "q4": "Q4",
    "4": "Q4",
    "release": "Q4",
}

STAGE_GOVERNANCE_MODULES: dict[str, list[str]] = {
    "Q1": ["references/00-spiral-governance/spiral-lifecycle.md", "references/00-spiral-governance/anti-overengineering-simplicity-gate.md"],
    "Q2": ["references/00-spiral-governance/risk-prototyping-and-spikes.md", "references/00-spiral-governance/anti-overengineering-simplicity-gate.md"],
    "3A": ["references/00-spiral-governance/system-first-foundation-gate.md", "references/orchestration-protocol.md"],
    "3B": ["references/orchestration-protocol.md", "references/00-spiral-governance/token-economy-and-progressive-disclosure.md"],
    "3C": ["references/00-spiral-governance/anti-overengineering-simplicity-gate.md", "references/orchestration-protocol.md"],
    "Q4": ["references/00-spiral-governance/spiral-lifecycle.md", "references/00-spiral-governance/token-economy-and-progressive-disclosure.md"],
}

SURFACE_ALIASES = {
    "landing": "landing-page",
    "landing-page": "landing-page",
    "marketing": "landing-page",
    "web": "web-app",
    "web-app": "web-app",
    "webapp": "web-app",
    "saas": "web-app",
    "mobile": "mobile-app",
    "mobile-app": "mobile-app",
    "dashboard": "dashboard",
    "design-system": "design-system",
    "redesign": "ui-redesign",
    "ui-redesign": "ui-redesign",
    "backend": "backend-api",
    "api": "backend-api",
    "backend-api": "backend-api",
    "fullstack": "fullstack",
    "full-stack": "fullstack",
}


def est_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9_-]*", text.lower())
    out: list[str] = []
    for t in tokens:
        if t in STOPWORDS or len(t) < 2:
            continue
        # lightweight plural stemming
        if len(t) > 4 and t.endswith("ies"):
            t = t[:-3] + "y"
        elif len(t) > 4 and t.endswith("es") and not t.endswith("ses"):
            t = t[:-2]
        elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


def parse_headings_fence_aware(text: str) -> list[dict[str, Any]]:
    """Return all Markdown headings outside code fences with start/end line ranges."""
    lines = text.splitlines()
    fence_char: str | None = None
    fence_len = 0
    raw_headings: list[tuple[int, int, str]] = []

    for idx, line in enumerate(lines, start=1):
        fm = re.match(r"^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$", line)
        if fm:
            marker = fm.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len and not fm.group(2).strip():
                fence_char = None
                fence_len = 0
            continue
        if fence_char is None:
            hm = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", line)
            if hm:
                raw_headings.append((idx, len(hm.group(1)), hm.group(2).strip()))

    headings: list[dict[str, Any]] = []
    total = len(lines)
    for i, (start_ln, level, title) in enumerate(raw_headings):
        end_ln = total
        for j in range(i + 1, len(raw_headings)):
            if raw_headings[j][1] <= level:
                end_ln = raw_headings[j][0] - 1
                break
        next_any = raw_headings[i + 1][0] - 1 if i + 1 < len(raw_headings) else total
        chunk = "\n".join(lines[start_ln - 1 : end_ln])
        headings.append(
            {
                "level": level,
                "title": title,
                "start_line": start_ln,
                "end_line": end_ln,
                "direct_end_line": next_any,
                "tokens_est": est_tokens(chunk),
            }
        )
    return headings


def load_registry(root: Path) -> dict[str, Any]:
    reg_path = root / "registry.json"
    if not reg_path.exists():
        return {}
    try:
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def discover_indexed_files(root: Path) -> dict[str, Any]:
    references: list[Path] = []
    templates: list[Path] = []
    skill_files: list[Path] = []

    if (root / "SKILL.md").exists():
        skill_files.append(root / "SKILL.md")
    if (root / "references").is_dir():
        for p in sorted((root / "references").rglob("*.md")):
            references.append(p)
    if (root / "templates").is_dir():
        for p in sorted((root / "templates").glob("*.md")):
            templates.append(p)

    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for cdir in sorted(skills_dir.iterdir()):
            if not cdir.is_dir():
                continue
            if (cdir / "SKILL.md").exists():
                skill_files.append(cdir / "SKILL.md")
            if (cdir / "references").is_dir():
                for p in sorted((cdir / "references").rglob("*.md")):
                    references.append(p)
            if (cdir / "templates").is_dir():
                for p in sorted((cdir / "templates").glob("*.md")):
                    templates.append(p)

    return {
        "skill_files": skill_files,
        "references": references,
        "templates": templates,
    }


def first_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return fallback


def domain_of(rel_path: str) -> str:
    parts = Path(rel_path).parts
    if len(parts) >= 3 and parts[0] == "skills":
        return parts[1]
    if len(parts) >= 2 and parts[0] == "references":
        if len(parts) == 2:
            return "orchestration"
        return parts[1]
    if parts and parts[0] == "templates":
        return "templates"
    return "root"


def build_section_chunks(
    root: Path, include_templates: bool = False, domain_filter: str | None = None
) -> list[dict[str, Any]]:
    idx = discover_indexed_files(root)
    files = list(idx["references"])
    if include_templates:
        files.extend(idx["templates"])

    chunks: list[dict[str, Any]] = []
    for fp in files:
        rel = fp.relative_to(root).as_posix()
        dom = domain_of(rel)
        if domain_filter:
            df = domain_filter.lower()
            if df not in dom.lower() and df not in rel.lower():
                continue
        try:
            text = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        headings = [h for h in parse_headings_fence_aware(text) if h["level"] in (2, 3)]
        if not headings:
            chunks.append(
                {
                    "file": rel,
                    "domain": dom,
                    "heading": first_title(text, fp.stem),
                    "start_line": 1,
                    "end_line": len(lines),
                    "body": text,
                }
            )
            continue
        for h in headings:
            s = h["start_line"]
            e = h["direct_end_line"]
            body = "\n".join(lines[s - 1 : e])
            chunks.append(
                {
                    "file": rel,
                    "domain": dom,
                    "heading": h["title"],
                    "start_line": s,
                    "end_line": e,
                    "body": body,
                }
            )
    return chunks


def bm25_mmr_search(
    chunks: list[dict[str, Any]],
    query: str,
    limit: int = 5,
    mmr_lambda: float = 0.7,
) -> list[dict[str, Any]]:
    q_tokens = tokenize(query)
    if not q_tokens or not chunks:
        return []

    doc_tf: list[Counter[str]] = []
    doc_token_sets: list[set[str]] = []
    doc_lens: list[int] = []
    df: Counter[str] = Counter()

    for ch in chunks:
        h_toks = tokenize(ch["heading"])
        b_toks = tokenize(ch["body"])
        # 2x heading weight
        weighted = h_toks * 2 + b_toks
        c = Counter(weighted)
        doc_tf.append(c)
        doc_token_sets.append(set(c.keys()))
        dl = sum(c.values())
        doc_lens.append(dl)
        for term in set(c.keys()):
            df[term] += 1

    n_docs = len(chunks)
    avgdl = (sum(doc_lens) / n_docs) if n_docs else 1.0
    k1 = 1.5
    b = 0.75

    scored: list[tuple[float, int]] = []
    for idx, ch in enumerate(chunks):
        tf = doc_tf[idx]
        dl = doc_lens[idx]
        score = 0.0
        for qt in set(q_tokens):
            f = tf.get(qt, 0)
            if f == 0:
                continue
            idf = math.log(1.0 + (n_docs - df[qt] + 0.5) / (df[qt] + 0.5))
            denom = f + k1 * (1.0 - b + b * (dl / avgdl))
            score += idf * ((f * (k1 + 1.0)) / denom)
        if score > 0.0:
            scored.append((score, idx))

    if not scored:
        return []

    scored.sort(key=lambda x: x[0], reverse=True)
    pool = scored[: max(limit * 4, 20)]
    max_score = pool[0][0] or 1.0

    # MMR diversity reranking
    selected: list[tuple[float, int]] = []
    remaining = list(pool)
    lam = max(0.0, min(1.0, mmr_lambda))

    while remaining and len(selected) < limit:
        if not selected or lam >= 0.999:
            chosen = remaining.pop(0)
            selected.append(chosen)
            continue
        best_pos = 0
        best_mmr = -1e9
        for pos, (rel_score, idx) in enumerate(remaining):
            norm_rel = rel_score / max_score
            cand_set = doc_token_sets[idx]
            max_sim = 0.0
            for _, sel_idx in selected:
                sel_set = doc_token_sets[sel_idx]
                union = len(cand_set | sel_set)
                sim = (len(cand_set & sel_set) / union) if union else 0.0
                if sim > max_sim:
                    max_sim = sim
            mmr_val = lam * norm_rel - (1.0 - lam) * max_sim
            if mmr_val > best_mmr:
                best_mmr = mmr_val
                best_pos = pos
        selected.append(remaining.pop(best_pos))

    results: list[dict[str, Any]] = []
    for score, idx in selected:
        ch = chunks[idx]
        excerpt_lines = [ln.strip() for ln in ch["body"].splitlines() if ln.strip() and not ln.strip().startswith("#")]
        excerpt = " ".join(excerpt_lines)[:280]
        results.append(
            {
                "file": ch["file"],
                "domain": ch["domain"],
                "heading": ch["heading"],
                "lines": f"{ch['start_line']}-{ch['end_line']}",
                "score": round(score, 3),
                "excerpt": excerpt,
                "body": ch["body"][:700],
            }
        )
    return results


def resolve_module(root: Path, mod_arg: str) -> Path | None:
    p = root / mod_arg
    if p.exists() and p.is_file():
        return p
    idx = discover_indexed_files(root)
    q = mod_arg.lower().removesuffix(".md")
    matches: list[Path] = []
    for rp in idx["references"]:
        rel = rp.relative_to(root).as_posix().lower().removesuffix(".md")
        if rp.stem.lower() == q or rel == q or q in rel:
            matches.append(rp)
    return matches[0] if matches else None


def extract_pillar_text(text: str, pillar_arg: str) -> tuple[str | None, str | None]:
    key = pillar_arg.strip().lower()
    if key not in PILLAR_ALIASES:
        return None, f"Unknown pillar '{pillar_arg}'. Use 1..6 or decision|workflow|template|checklist|gate|antipatterns."
    num, pat_str = PILLAR_ALIASES[key]
    pat = re.compile(pat_str)
    headings = parse_headings_fence_aware(text)
    lines = text.splitlines()
    for h in headings:
        if h["level"] == 2:
            line_text = lines[h["start_line"] - 1]
            if pat.match(line_text):
                return "\n".join(lines[h["start_line"] - 1 : h["end_line"]]), None
    return None, f"Pillar {num} heading not found in module."


def summarize_markdown(text: str, max_lines: int = 38) -> str:
    kept: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if (
            s.startswith("#")
            or s.startswith("|")
            or s.startswith("- [")
            or s.startswith("- **")
            or s.startswith("1.")
            or s.startswith("2.")
            or s.startswith("3.")
            or s.startswith("4.")
            or s.startswith("python3 ")
        ):
            kept.append(ln)
        if len(kept) >= max_lines:
            break
    return "\n".join(kept)


def cmd_audit_budget(root: Path, as_json: bool) -> int:
    idx = discover_indexed_files(root)
    reg = load_registry(root)
    issues: list[dict[str, Any]] = []
    skills_report: list[dict[str, Any]] = []

    for smd in idx["skill_files"]:
        rel = smd.relative_to(root).as_posix()
        content = smd.read_text(encoding="utf-8")
        lines = content.splitlines()
        fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", content, re.DOTALL)
        fm_text = fm_match.group(1) if fm_match else ""
        body = content[fm_match.end() :] if fm_match else content
        desc_match = re.search(r"description\s*:\s*(?:>-\s*\n((?:\s+.*\n?)+)|([^\n]+))", fm_text)
        desc_len = len(desc_match.group(0)) if desc_match else 0
        l1_tokens = est_tokens(fm_text)
        l2_tokens = est_tokens(body)
        body_lines = len(body.splitlines())

        # Check 1-level relative links and @ imports
        deep_links: list[str] = []
        eager_at: list[str] = []
        for ln in body.splitlines():
            if re.search(r"(?:^|\s)@(?:references|templates|scripts|skills)/", ln):
                eager_at.append(ln.strip())
            for lm in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", ln):
                tgt = lm.group(1)
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", tgt) or tgt.startswith("#"):
                    continue
                if tgt.startswith("references/") and len(Path(tgt).parts) > 3:
                    deep_links.append(tgt)

        status = "PASS"
        if body_lines > 800 or eager_at:
            status = "FAIL"
            if body_lines > 800:
                issues.append({"severity": "ERROR", "file": rel, "msg": f"SKILL.md body {body_lines} lines > 800 error cap"})
            if eager_at:
                issues.append({"severity": "ERROR", "file": rel, "msg": "Eager '@' import found"})
        elif body_lines > 500 or l1_tokens > 180:
            status = "WARN"
            if body_lines > 500:
                issues.append({"severity": "WARN", "file": rel, "msg": f"SKILL.md body {body_lines} lines > 500 warn cap"})
            if l1_tokens > 180:
                issues.append({"severity": "WARN", "file": rel, "msg": f"L1 frontmatter {l1_tokens} tokens > 180"})

        if deep_links:
            issues.append({"severity": "WARN", "file": rel, "msg": f"Deep (>1 level) reference links: {deep_links}"})

        skills_report.append(
            {
                "file": rel,
                "total_lines": len(lines),
                "body_lines": body_lines,
                "desc_block_chars": desc_len,
                "l1_trigger_tokens_est": l1_tokens,
                "l2_router_tokens_est": l2_tokens,
                "status": status,
            }
        )

    l3_refs: list[dict[str, Any]] = []
    total_l3_tokens = 0
    for rp in idx["references"]:
        rel = rp.relative_to(root).as_posix()
        txt = rp.read_text(encoding="utf-8")
        lines = txt.splitlines()
        toks = est_tokens(txt)
        total_l3_tokens += toks
        has_toc = bool(re.search(r"(?:^>\s*\*\*Contents\*\*:|^##\s+Contents|^##\s+Table of Contents)", txt, re.MULTILINE | re.IGNORECASE))
        if len(lines) > 250 and not has_toc:
            issues.append({"severity": "WARN", "file": rel, "msg": f"Reference {len(lines)} lines > 250 missing Top TOC"})
        l3_refs.append({"file": rel, "lines": len(lines), "tokens_est": toks, "has_toc": has_toc})

    has_error = any(i["severity"] == "ERROR" for i in issues)
    report = {
        "status": "FAIL" if has_error else "PASS",
        "suite_children_registered": len(reg.get("children", [])),
        "skills": skills_report,
        "references_count": len(l3_refs),
        "l3_deferred_tokens_est": total_l3_tokens,
        "references": l3_refs,
        "issues": issues,
    }

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Token Budget Audit: {report['status']} | L3 deferred est={total_l3_tokens} tokens across {len(l3_refs)} refs")
        for s in skills_report:
            print(
                f"  - {s['file']}: {s['total_lines']} lines | L1~{s['l1_trigger_tokens_est']} tok | L2~{s['l2_router_tokens_est']} tok [{s['status']}]"
            )
        for iss in issues:
            print(f"  [{iss['severity']}] {iss['file']}: {iss['msg']}")
    return 1 if has_error else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Minimal-token progressive-disclosure CLI for appnwebsite-skill."
    )
    parser.add_argument("pos_query", nargs="?", help="Optional positional search query")
    parser.add_argument("--root", help="Suite root directory (defaults to repo root)")
    parser.add_argument("--list", "--list-modules", "--list-skills", dest="list_all", action="store_true", help="List parent modules and all registered child skills")
    parser.add_argument("--skill", help="Inspect or query a registered child skill by id/name")
    parser.add_argument("--module", help="Target reference module slug or path")
    parser.add_argument("--pillar", "--section", dest="pillar", help="Extract R2 pillar (1..6 or decision|workflow|template|checklist|gate|antipatterns)")
    parser.add_argument("--stage", help="Filter/route by Spiral stage (Q1|Q2|3A|3B|3C|Q4)")
    parser.add_argument("--surface", help="Filter/route by surface (landing-page|web-app|mobile-app|dashboard|design-system|ui-redesign|backend-api|fullstack)")
    parser.add_argument("--search", "--query", dest="query_opt", help="BM25+MMR section search query")
    parser.add_argument("--mmr", type=float, default=0.7, help="MMR lambda diversity factor (default: 0.7)")
    parser.add_argument("-n", "--max-results", "--limit", dest="limit", type=int, default=5, help="Max search results (default: 5)")
    parser.add_argument("--domain", help="Filter search by domain folder or child skill id")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    parser.add_argument("--template", help="Show template outline or full text (with --full)")
    parser.add_argument("--full", action="store_true", help="Print full template text")
    parser.add_argument("--include-templates", action="store_true", help="Include templates in BM25 search")
    parser.add_argument("--headings", help="List fence-aware headings & line ranges for a Markdown path")
    parser.add_argument("--extract", nargs=2, metavar=("PATH", "HEADING"), help="Extract exact section by heading substring")
    parser.add_argument("--body", action="store_true", help="Omit heading line in --extract output")
    parser.add_argument("--audit-budget", action="store_true", help="Audit SKILL.md & reference token budgets")
    parser.add_argument("--summary", action="store_true", help="Compact minimal-token output")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"ERROR: Invalid root directory: {root}", file=sys.stderr)
        return 2

    reg = load_registry(root)
    idx = discover_indexed_files(root)

    # 1. --audit-budget
    if args.audit_budget:
        return cmd_audit_budget(root, args.json)

    # 2. --headings
    if args.headings:
        target = Path(args.headings)
        if not target.is_absolute():
            target = root / args.headings
        if not target.is_file():
            print(f"ERROR: Markdown file not found: {args.headings}", file=sys.stderr)
            return 1
        hs = parse_headings_fence_aware(target.read_text(encoding="utf-8"))
        if args.json:
            print(json.dumps({"file": args.headings, "headings": hs}, indent=2))
        else:
            for h in hs:
                print(f"L{h['start_line']}-L{h['end_line']} | H{h['level']} | {h['title']} (~{h['tokens_est']} tok)")
        return 0

    # 3. --extract PATH HEADING
    if args.extract:
        epath, h_query = args.extract
        target = Path(epath) if Path(epath).is_absolute() else (root / epath)
        if not target.is_file():
            print(f"ERROR: Markdown file not found: {epath}", file=sys.stderr)
            return 1
        txt = target.read_text(encoding="utf-8")
        lines = txt.splitlines()
        hs = parse_headings_fence_aware(txt)
        hq = h_query.strip().lower()
        match = next((h for h in hs if hq in h["title"].lower()), None)
        if not match:
            print(f"ERROR: Heading matching '{h_query}' not found in {epath}", file=sys.stderr)
            return 1
        start = match["start_line"] + (1 if args.body else 0)
        extracted = "\n".join(lines[start - 1 : match["end_line"]])
        if args.json:
            print(
                json.dumps(
                    {
                        "file": epath,
                        "heading": match["title"],
                        "lines": f"{start}-{match['end_line']}",
                        "content": extracted,
                    },
                    indent=2,
                )
            )
        else:
            print(extracted)
        return 0

    # 4. --list / --list-modules / --list-skills
    if args.list_all:
        mods = []
        for rp in idx["references"]:
            rel = rp.relative_to(root).as_posix()
            txt = rp.read_text(encoding="utf-8")
            mods.append(
                {
                    "path": rel,
                    "domain": domain_of(rel),
                    "title": first_title(txt, rp.stem),
                    "lines": len(txt.splitlines()),
                    "tokens_est": est_tokens(txt),
                }
            )
        children_out = []
        for ch in reg.get("children", []):
            cdir = root / ch["path"]
            on_disk = (cdir / "SKILL.md").exists()
            children_out.append(
                {
                    "id": ch["id"],
                    "milestone": ch["milestone"],
                    "status": "active" if on_disk and ch["status"] == "active" else ch["status"],
                    "on_disk": on_disk,
                    "spiral_stages": ch["spiral_stages"],
                    "surfaces": ch["surfaces"],
                    "estimated_tokens": ch["estimated_tokens"],
                }
            )
        payload = {"parent": reg.get("parent", {}).get("id", "appnwebsite-orchestrator"), "modules": mods, "children": children_out}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Parent Orchestrator: {payload['parent']} ({len(mods)} indexed references, {len(idx['templates'])} templates)")
            for m in mods:
                print(f"  [ref] {m['path']} ({m['lines']}L, ~{m['tokens_est']} tok) — {m['title']}")
            print(f"\nRegistered Child Skills ({len(children_out)}):")
            for c in children_out:
                print(
                    f"  - {c['id']} [{c['status']} | {c['milestone']}] stages={','.join(c['spiral_stages'])} ~{c['estimated_tokens']} tok"
                )
        return 0

    # 5. --list-templates
    if args.list_templates:
        tlist = []
        for tp in idx["templates"]:
            txt = tp.read_text(encoding="utf-8")
            tlist.append(
                {
                    "name": tp.stem,
                    "path": tp.relative_to(root).as_posix(),
                    "lines": len(txt.splitlines()),
                    "title": first_title(txt, tp.stem),
                }
            )
        if args.json:
            print(json.dumps({"templates": tlist}, indent=2))
        else:
            for t in tlist:
                print(f"  - {t['name']} ({t['path']}, {t['lines']}L): {t['title']}")
        return 0

    # 6. --template NAME
    if args.template:
        q = args.template.lower().removesuffix(".md")
        found = next((tp for tp in idx["templates"] if tp.stem.lower() == q or q in tp.stem.lower()), None)
        if not found:
            print(f"ERROR: Template '{args.template}' not found.", file=sys.stderr)
            return 1
        txt = found.read_text(encoding="utf-8")
        out_txt = txt if args.full and not args.summary else summarize_markdown(txt, max_lines=45)
        if args.json:
            print(
                json.dumps(
                    {
                        "template": found.stem,
                        "path": found.relative_to(root).as_posix(),
                        "full": bool(args.full and not args.summary),
                        "content": out_txt,
                    },
                    indent=2,
                )
            )
        else:
            print(f"# Template: {found.relative_to(root).as_posix()}\n{out_txt}")
        return 0

    # 7. --skill NAME
    if args.skill:
        sq = args.skill.strip().lower()
        ch = next((c for c in reg.get("children", []) if c["id"].lower() == sq or sq in c["id"].lower()), None)
        if not ch:
            print(f"ERROR: Child skill '{args.skill}' not found in registry.json.", file=sys.stderr)
            return 1
        cdir = root / ch["path"]
        skill_md = cdir / "SKILL.md"
        result: dict[str, Any] = dict(ch)
        result["on_disk"] = skill_md.exists()
        if skill_md.exists():
            txt = skill_md.read_text(encoding="utf-8")
            result["skill_summary"] = summarize_markdown(txt, max_lines=30) if args.summary else txt[:1600]
        else:
            result["message"] = (
                f"Child skill '{ch['id']}' is registered with status '{ch['status']}' "
                f"(milestone {ch['milestone']}, not yet authored on disk). Use Parent governance modules for Q1-3A."
            )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Skill: {ch['id']} [{ch['status']} | milestone={ch['milestone']}]")
            print(f"  Path: {ch['path']} | Stages: {', '.join(ch['spiral_stages'])} | Surfaces: {', '.join(ch['surfaces'])}")
            print(f"  Depends On: {', '.join(ch['depends_on']) or 'None'} | Est Tokens: {ch['estimated_tokens']}")
            print(f"  Inputs: {', '.join(ch['inputs'])}")
            print(f"  Outputs: {', '.join(ch['outputs'])}")
            if "message" in result:
                print(f"  Note: {result['message']}")
            elif "skill_summary" in result:
                print("\n" + result["skill_summary"])
        return 0

    # 8. --module [with optional --pillar]
    if args.module:
        mod_path = resolve_module(root, args.module)
        if not mod_path:
            print(f"ERROR: Module '{args.module}' not found on disk.", file=sys.stderr)
            return 1
        txt = mod_path.read_text(encoding="utf-8")
        rel = mod_path.relative_to(root).as_posix()
        if args.pillar:
            sec_txt, err = extract_pillar_text(txt, args.pillar)
            if err or sec_txt is None:
                print(f"ERROR: {err}", file=sys.stderr)
                return 1
            out_txt = summarize_markdown(sec_txt) if args.summary else sec_txt
        else:
            out_txt = summarize_markdown(txt, max_lines=45) if args.summary else txt
        if args.json:
            print(json.dumps({"module": rel, "pillar": args.pillar, "summary": args.summary, "content": out_txt}, indent=2))
        else:
            print(f"# Module: {rel}\n{out_txt}")
        return 0

    # 9. --stage / --surface routing
    if args.stage or args.surface:
        norm_stage = STAGE_ALIASES.get(args.stage.strip().lower(), args.stage.strip().upper()) if args.stage else None
        norm_surface = SURFACE_ALIASES.get(args.surface.strip().lower(), args.surface.strip().lower()) if args.surface else None
        matched_children: list[dict[str, Any]] = []
        for ch in reg.get("children", []):
            st_ok = (norm_stage is None) or (norm_stage in ch.get("spiral_stages", []))
            sf_ok = (norm_surface is None) or (norm_surface in ch.get("surfaces", []))
            if st_ok and sf_ok:
                cdir = root / ch["path"]
                matched_children.append(
                    {
                        "id": ch["id"],
                        "milestone": ch["milestone"],
                        "status": ch["status"],
                        "on_disk": (cdir / "SKILL.md").exists(),
                        "spiral_stages": ch["spiral_stages"],
                        "surfaces": ch["surfaces"],
                        "inputs": ch["inputs"],
                        "outputs": ch["outputs"],
                    }
                )
        gov_mods = STAGE_GOVERNANCE_MODULES.get(norm_stage or "3A", STAGE_GOVERNANCE_MODULES["3A"])
        payload = {
            "stage": norm_stage,
            "surface": norm_surface,
            "governance_modules": gov_mods,
            "matched_children": matched_children,
            "active_ceiling_note": "Load Parent + <= 2 Child Skills concurrently.",
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Routing for stage={norm_stage or 'ANY'} surface={norm_surface or 'ANY'}:")
            print("  Parent Governance:")
            for gm in gov_mods:
                print(f"    - {gm}")
            print(f"  Matched Child Skills ({len(matched_children)}, load <= 2 concurrently):")
            for mc in matched_children:
                print(f"    - {mc['id']} [{mc['status']} | {mc['milestone']}] outputs={', '.join(mc['outputs'])}")
        return 0

    # 10. Search (--search / --query / positional)
    q = args.query_opt or args.pos_query
    if q:
        chunks = build_section_chunks(root, include_templates=args.include_templates, domain_filter=args.domain)
        hits = bm25_mmr_search(chunks, q, limit=args.limit, mmr_lambda=args.mmr)
        if args.json:
            out_hits = []
            for h in hits:
                item = {
                    "file": h["file"],
                    "domain": h["domain"],
                    "heading": h["heading"],
                    "lines": h["lines"],
                    "score": h["score"],
                    "excerpt": h["excerpt"],
                }
                if not args.summary:
                    item["body"] = h["body"]
                out_hits.append(item)
            print(json.dumps({"query": q, "count": len(out_hits), "results": out_hits}, indent=2))
        else:
            if not hits:
                print(f"No matches for '{q}' across {len(chunks)} indexed sections.")
                return 0
            for i, h in enumerate(hits, start=1):
                print(f"[{i}] {h['file']}:{h['lines']} | {h['heading']} (score={h['score']})")
                print(f"    {h['excerpt']}")
                if not args.summary:
                    print(h["body"])
                    print("-" * 40)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
