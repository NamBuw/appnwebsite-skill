#!/usr/bin/env python3
"""Deterministic Spiral Charter, Simplicity, Q2 Risk & Phase 3A Foundation Gate checker.

Python 3 stdlib only. Enforces:
- Verdict Precedence: FAIL > CONCERNS > NOT ASSESSED > PASS (NOT ASSESSED outranks PASS)
- Rigor Tiers: minimal | standard | full (aliases: micro -> minimal, enterprise -> full)
- Placeholder guard against unfilled [...] templates
- Phase 3A Foundation Gate & SYSTEM_FIRST_VIOLATION detection
- ADR Status: Accepted + acyclic Depends On DAG check
- Q2 Risk Register (OPEN High/Critical blocker, 3-PIVOT-to-KILL, SPIKE_LEAK scan)
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VERDICT_RANK = {"PASS": 0, "NOT ASSESSED": 1, "CONCERNS": 2, "FAIL": 3}
TIER_ALIASES = {"micro": "minimal", "minimal": "minimal", "standard": "standard", "enterprise": "full", "full": "full"}
CODE_DIRS = ("src", "app", "pages", "components", "lib", "server", "api")
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".swift", ".kt", ".dart"}
SKELETON_STEMS = {"__init__", "health", "healthz", "skeleton", "main_skeleton", "env", "config"}
SKIP_WALK_DIRS = {".git", "node_modules", "__pycache__", ".next", ".venv", "venv", "dist", "build"}


def worse_verdict(a: str, b: str) -> str:
    return a if VERDICT_RANK.get(a, 1) >= VERDICT_RANK.get(b, 1) else b


CANONICAL_SOCRATIC_PROMPTS: dict[str, list[str]] = {
    "Q1": [
        "For this feature/requirement, is there a simpler approach that delivers equal or HIGHER quality, UX, reliability, and maintainability?",
        "For this feature or requirement, is there a simpler approach that delivers equal or HIGHER quality, UX, reliability, and maintainability?",
        "Is there a simpler approach delivering equal or HIGHER quality, UX, reliability, and maintainability?",
        "Explain the simplest alternative evaluated and why it delivers equal/higher craft, or provide measured proof if a richer mechanism is strictly required.",
    ],
    "Q2": [
        "What layers, dependencies, abstractions, or moving parts can be deleted or replaced with native platform/language/database/browser primitives?",
        "What layers, third-party dependencies, wrappers, state stores, or moving parts can be deleted or replaced with native platform, language, database, or browser primitives?",
        "What layers, dependencies, wrappers, or state stores can be deleted or replaced with native platform/language/DB/HTML/CSS primitives?",
        "List specific wrappers, libraries, caches, or JS widgets replaced by stdlib, SQL/Postgres primitives, HTTP semantics, <dialog>/<details>, CSS Grid/:has()/clamp(), etc.",
    ],
    "Q3": [
        "Are we solving a real, verified constraint right now or inventing complexity for hypothetical scale?",
        "Are we solving a real, verified constraint right now (backed by PRD/NFR/telemetry), or inventing complexity for hypothetical future scale?",
        "Are we solving a verified current constraint right now or inventing complexity for hypothetical scale (YAGNI)?",
        "Cite exact PRD/NFR/telemetry locator proving any non-minimal choice, and list speculative features/abstractions cut right now.",
    ],
    "Q4": [
        "How do we make the code and technical architecture as concise, dense, readable, and minimal as possible while maximizing craft?",
        "How do we make code and architecture maximally concise, dense, readable, and minimal while maximizing craft?",
        "Detail module consolidation, Rule-of-Three adherence, direct function calls, and deletion targets.",
    ],
}


def _norm_tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


ALL_PROMPT_VOCAB: set[str] = {
    tok for prompts in CANONICAL_SOCRATIC_PROMPTS.values() for p in prompts for tok in _norm_tokens(p)
}

TECHNICAL_PRIMITIVE_WORDS: set[str] = {
    "sql",
    "postgres",
    "http",
    "html",
    "css",
    "dialog",
    "details",
    "grid",
    "clamp",
    "stdlib",
    "js",
    "db",
    "prd",
    "nfr",
    "telemetry",
}

GENERIC_FILLER_VOCAB: set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "of", "in", "on", "at", "to", "for", "with", "by",
    "from", "as", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that",
    "these", "those", "it", "its", "we", "our", "us", "you", "your", "they", "their", "them",
    "there", "here", "what", "which", "who", "whom", "how", "why", "when", "where", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "just", "also", "already", "still", "even", "now",
    "then", "well", "yes", "ok", "okay", "sure", "true", "false", "confirm", "confirmed",
    "confirming", "carefully", "evaluate", "evaluated", "evaluating", "evaluation", "review",
    "reviewed", "reviewing", "check", "checked", "checking", "verify", "verified", "verifying",
    "assess", "assessed", "assessing", "assessment", "analyze", "analyzed", "analyzing",
    "analysis", "consider", "considered", "considering", "choose", "chosen", "choosing", "choice",
    "select", "selected", "selecting", "current", "currently", "existing", "proposed", "approach",
    "solution", "design", "architecture", "implementation", "system", "feature", "requirement",
    "project", "app", "application", "code", "minimal", "simple", "simpler", "simplest", "clean",
    "cleaner", "cleanest", "concise", "dense", "readable", "good", "better", "best", "optimal",
    "high", "higher", "highest", "quality", "reliability", "maintainability", "ux", "craft",
    "sufficient", "adequate", "appropriate", "needed", "necessary", "required", "none", "nothing",
    "everything", "anything", "something", "team", "agree", "agreed", "done", "complete",
    "completed", "pass", "passed", "works", "working", "fine", "great", "today", "detail",
    "details", "ensured", "ensure", "remains", "remain", "unnecessary", "complexity", "specific",
    "particular", "overall", "basically", "actually", "really", "simply", "truly",
    "actual", "fit", "fits", "fitting", "keep", "kept", "keeping", "tight", "tiny",
    "make", "making", "made", "use", "used", "using", "way", "here",
}

PROMPT_SYNONYM_MAP: dict[str, str] = {
    "easier": "simpler",
    "easy": "simpler",
    "codebase": "code",
    "technical": "architecture",
    "packages": "dependencies",
    "package": "dependencies",
    "libs": "dependencies",
    "libraries": "dependencies",
    "library": "dependencies",
    "remove": "deleted",
    "removed": "deleted",
    "removing": "deleted",
    "drop": "deleted",
    "dropped": "deleted",
    "eliminate": "deleted",
    "eliminated": "deleted",
    "swap": "replaced",
    "swapped": "replaced",
    "substitute": "replaced",
    "substituted": "replaced",
    "limitation": "constraint",
    "limitations": "constraint",
    "constraints": "constraint",
    "extra": "hypothetical",
    "additional": "hypothetical",
    "future": "hypothetical",
}


def _concrete_substance_tokens(tokens: list[str]) -> set[str]:
    non_tech_prompt_vocab = ALL_PROMPT_VOCAB - TECHNICAL_PRIMITIVE_WORDS
    out: set[str] = set()
    for t in tokens:
        t_canon = PROMPT_SYNONYM_MAP.get(t, t)
        if (
            t not in non_tech_prompt_vocab
            and t_canon not in non_tech_prompt_vocab
            and t not in GENERIC_FILLER_VOCAB
            and t_canon not in GENERIC_FILLER_VOCAB
        ):
            out.add(t)
    return out


def is_prompt_echo(ans: str, qn: str, extra_prompt: str = "", _depth: int = 0) -> bool:
    ans_tokens = _norm_tokens(ans)
    if not ans_tokens:
        return True
    norm_ans = " ".join(ans_tokens)
    ans_set = set(ans_tokens)
    syn_ans_set = {PROMPT_SYNONYM_MAP.get(t, t) for t in ans_tokens}
    is_question = ans.strip().endswith("?")

    refs = list(CANONICAL_SOCRATIC_PROMPTS.get(qn, []))
    if extra_prompt:
        refs.append(extra_prompt)
    for ref in refs:
        p_tokens = _norm_tokens(ref)
        if len(p_tokens) < 4:
            continue
        norm_p = " ".join(p_tokens)
        if norm_ans == norm_p or norm_ans in norm_p:
            return True
        if norm_p in norm_ans:
            residual = norm_ans
            for r in refs:
                rt = _norm_tokens(r)
                if len(rt) >= 4:
                    nr = " ".join(rt)
                    if nr in residual:
                        residual = " ".join(residual.replace(nr, " ").split())
            res_tokens = residual.split()
            res_no_ws = "".join(res_tokens)
            if len(res_no_ws) < 20:
                return True
            if len(_concrete_substance_tokens(res_tokens)) < 3:
                return True
            if _depth == 0 and is_prompt_echo(residual, qn, extra_prompt="", _depth=1):
                return True
            return False

        p_set = set(p_tokens)
        jaccard = len(ans_set & p_set) / len(ans_set | p_set)
        recall = len(ans_set & p_set) / len(p_set)
        extra_novel = len(ans_set - p_set)
        if jaccard >= 0.50 and extra_novel < 10:
            return True
        if recall >= 0.70 and extra_novel < 10:
            return True
        if is_question and recall >= 0.55:
            return True

        syn_p_set = {PROMPT_SYNONYM_MAP.get(t, t) for t in p_tokens}
        syn_jaccard = len(syn_ans_set & syn_p_set) / len(syn_ans_set | syn_p_set)
        syn_recall = len(syn_ans_set & syn_p_set) / len(syn_p_set)
        syn_extra = len(syn_ans_set - syn_p_set)
        if syn_jaccard >= 0.50 and syn_extra < 10:
            return True
        if syn_recall >= 0.70 and syn_extra < 10:
            return True
        if is_question and syn_recall >= 0.55:
            return True

    if len(ans_tokens) >= 6 and len(ans_set - ALL_PROMPT_VOCAB) < 3:
        return True
    if len(_concrete_substance_tokens(ans_tokens)) < 2:
        return True
    return False


def strip_fences_keep_lines(text: str) -> str:
    """Blank out lines inside fenced code blocks while preserving line structure outside."""
    out_lines: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in text.splitlines():
        m = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if m:
            marker = m.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_len = len(marker)
                out_lines.append("")
                continue
            elif marker[0] == fence_char and len(marker) >= fence_len and not m.group(2).strip():
                fence_char = None
                fence_len = 0
                out_lines.append("")
                continue
        out_lines.append("" if fence_char is not None else line)
    return "\n".join(out_lines)


def strip_for_placeholder_scan(text: str) -> str:
    """Remove fenced code blocks, Markdown checkboxes, and Markdown links before checking [...] placeholders."""
    out_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^\s*(?:```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        cleaned = re.sub(r"^\s*[-*]\s+\[[ xX]\]", "- CHECKBOX", line)
        cleaned = re.sub(r"!?\[[^\]]*\]\([^)]+\)", "LINK", cleaned)
        out_lines.append(cleaned)
    return "\n".join(out_lines)


def find_placeholders(text: str) -> list[str]:
    cleaned = strip_for_placeholder_scan(text)
    hits: list[str] = []
    for m in re.finditer(r"\[([^\]\n]{1,90})\]", cleaned):
        inner = m.group(1).strip()
        if not inner:
            continue
        # Ignore markdown reference labels like [1] or [^1]
        if re.fullmatch(r"\^?\d+", inner):
            continue
        hits.append(f"[{inner}]")
    for m in re.finditer(r"<fill[^>]*>|PLACEHOLDER|TODO|TBD|TO BE CONFIGURED", cleaned, re.IGNORECASE):
        hits.append(m.group(0))
    # Deduplicate preserving order
    seen: set[str] = set()
    uniq: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    return uniq


def parse_meta_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]\s+\*\*([^*]+)\*\*\s*:\s*(.+?)\s*$", line)
        if m:
            k = m.group(1).strip().lower()
            v = m.group(2).strip()
            # strip trailing italic note *(...)*
            v = re.sub(r"\s*\*\([^)]*\)\*\s*$", "", v).strip()
            fields[k] = v
    return fields


def parse_header_meta(text: str, stop_pattern: str = r"(?m)^##\s+") -> dict[str, str]:
    """Parse key-value metadata strictly from the top-level header block before section headings."""
    header_block = re.split(stop_pattern, text, maxsplit=1)[0]
    return parse_meta_fields(header_block)


def extract_verdict_token(raw: str | None) -> str:
    if not raw:
        return "NOT ASSESSED"
    s = raw.strip()
    if s.startswith("[") and s.endswith("]"):
        return "NOT ASSESSED"
    up = s.upper()
    for tok in ("FAIL", "CONCERNS", "NOT ASSESSED", "PASS", "APPROVED", "GO", "PIVOT", "KILL"):
        if re.search(rf"\b{re.escape(tok)}\b", up):
            if tok == "APPROVED":
                return "PASS"
            return tok
    return "NOT ASSESSED"


def detect_file_type(text: str, path: Path) -> str:
    low_name = path.name.lower()
    if "charter" in low_name:
        return "charter"
    if "foundation" in low_name:
        return "foundation"
    if "simplicity" in low_name:
        return "simplicity"
    if "risk" in low_name or "spike" in low_name:
        return "q2-risk"
    head = text.lower()[:350]
    if "spiral charter" in head:
        return "charter"
    if "system-first foundation gate" in head or "phase 3a" in head:
        return "foundation"
    if "simplicity interrogation" in head or "socratic" in head:
        return "simplicity"
    if "risk & spike" in head or "throwaway spike" in head:
        return "q2-risk"
    return "unknown"


def discover_project_artifacts(project_dir: Path) -> dict[str, Any]:
    def first_existing(candidates: list[str], glob_pat: str | None = None) -> Path | None:
        for rel in candidates:
            p = project_dir / rel
            if p.is_file():
                return p
        if glob_pat:
            matches = sorted(project_dir.glob(glob_pat))
            if matches:
                return matches[0]
        return None

    charter = first_existing(
        ["docs/spiral/spiral-charter.md", "docs/spiral-charter.md", ".spiral/spiral-charter.md", "spiral-charter.md"],
        "docs/spiral/*charter*.md",
    )
    foundation = first_existing(
        [
            "docs/spiral/system-foundation-gate.md",
            "docs/architecture/system-foundation-gate.md",
            ".spiral/system-foundation-gate.md",
            "system-foundation-gate.md",
        ],
        "docs/spiral/*foundation-gate*.md",
    )
    simplicity = first_existing(
        [
            "docs/spiral/simplicity-interrogation-record.md",
            "docs/architecture/simplicity-interrogation-record.md",
            ".spiral/simplicity-interrogation-record.md",
            "simplicity-interrogation-record.md",
        ],
        "docs/spiral/*simplicity*.md",
    )
    risk = first_existing(
        ["docs/spiral/risk-spike-register.md", ".spiral/risk-spike-register.md", "risk-spike-register.md"],
        "docs/spiral/*risk*.md",
    )

    adrs: list[Path] = []
    for adr_dir in ("docs/architecture/adr", "docs/adr", "adr"):
        dp = project_dir / adr_dir
        if dp.is_dir():
            adrs.extend(sorted(dp.glob("*.md")))

    arch_docs = [
        p
        for p in (
            list((project_dir / "docs/architecture").glob("*.md"))
            if (project_dir / "docs/architecture").is_dir()
            else []
        )
        + [project_dir / "architecture.md", project_dir / "docs/system-design.md"]
        if p.is_file()
    ]
    control_manifest = first_existing(
        ["docs/architecture/control-manifest.md", "control-manifest.md"]
    )
    data_models = [
        p
        for p in [
            project_dir / "docs/architecture/data-model.md",
            project_dir / "docs/data/data-model.md",
            project_dir / "prisma/schema.prisma",
            project_dir / "schema.sql",
            project_dir / "db/schema.sql",
        ]
        if p.is_file()
    ]
    contracts = [
        p
        for p in [
            project_dir / "docs/contracts/openapi.yaml",
            project_dir / "docs/contracts/openapi.json",
            project_dir / "openapi.yaml",
            project_dir / "openapi.json",
            project_dir / "schema.graphql",
            project_dir / "tokens.json",
            project_dir / "docs/design/tokens.json",
        ]
        if p.is_file()
    ]

    return {
        "charter": charter,
        "foundation": foundation,
        "simplicity": simplicity,
        "risk": risk,
        "adrs": adrs,
        "arch_docs": arch_docs,
        "control_manifest": control_manifest,
        "data_models": data_models,
        "contracts": contracts,
    }


def check_adr_dag(adr_paths: list[Path]) -> tuple[str, list[str], list[str]]:
    """Verify every ADR has Status: Accepted and Depends On forms a cycle-free DAG."""
    errors: list[str] = []
    warnings: list[str] = []
    if not adr_paths:
        return "NOT ASSESSED", errors, warnings

    graph: dict[str, list[str]] = {}
    id_map: dict[str, Path] = {}

    for p in adr_paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        m_id = re.search(r"\b(ADR-\d+)\b", text, re.IGNORECASE)
        adr_id = m_id.group(1).upper() if m_id else p.stem.upper()
        id_map[adr_id] = p

        # Status check (strip Markdown bold/italic/code formatting)
        st_m = re.search(r"(?:Status\*{0,2}\s*:\s*|##\s+Status\s*\n+\s*)([^\n]+)", text, re.IGNORECASE)
        if st_m:
            raw_st = re.sub(r"\s*\*\([^)]*\)\*\s*$", "", st_m.group(1)).strip()
            status_val = raw_st.strip("*_` ").strip()
        else:
            status_val = ""
        if not status_val or "[" in status_val:
            errors.append(f"{p.name}: UNFILLED ADR Status")
        elif status_val.lower() != "accepted":
            errors.append(f"{p.name}: PROPOSED_ADR — Status is '{status_val}', expected 'Accepted'")

        # Depends On check
        dep_m = re.search(r"Depends\s+On\*{0,2}\s*:\s*(.+)", text, re.IGNORECASE)
        if not dep_m:
            warnings.append(f"{p.name}: NO_DEPS_SECTION ('Depends On:' missing)")
            graph[adr_id] = []
        else:
            raw_deps = dep_m.group(1).strip()
            if "[" in raw_deps or "TBD" in raw_deps.upper():
                errors.append(f"{p.name}: UNFILLED_DEPS in Depends On: {raw_deps}")
                graph[adr_id] = []
            elif raw_deps.lower().strip("*_` ") in {"none", "n/a", "-"}:
                graph[adr_id] = []
            else:
                deps = [d.upper() for d in re.findall(r"ADR-\d+", raw_deps, re.IGNORECASE)]
                graph[adr_id] = deps

    # Dangling Depends On target detection
    for nid, deps in sorted(graph.items()):
        for dep in deps:
            if dep not in graph:
                src_name = id_map[nid].name if nid in id_map else nid
                errors.append(f"{src_name}: DANGLING_ADR_DEP — Depends On unknown '{dep}'")

    # Cycle detection (0=unvisited, 1=visiting, 2=visited)
    state: dict[str, int] = {}

    def dfs(node: str, stack: list[str]) -> None:
        state[node] = 1
        for nxt in graph.get(node, []):
            if state.get(nxt, 0) == 1:
                cycle = " -> ".join(stack[stack.index(nxt) :] + [nxt]) if nxt in stack else f"{node} -> {nxt}"
                errors.append(f"CYCLE: Circular ADR dependency detected ({cycle})")
            elif state.get(nxt, 0) == 0 and nxt in graph:
                dfs(nxt, stack + [nxt])
        state[node] = 2

    for nid in sorted(graph.keys()):
        if state.get(nid, 0) == 0:
            dfs(nid, [nid])

    verdict = "FAIL" if errors else ("CONCERNS" if warnings else "PASS")
    return verdict, errors, warnings


def check_charter(path: Path | None, strict: bool) -> dict[str, Any]:
    if not path or not path.is_file():
        return {"verdict": "NOT ASSESSED", "status": "ABSENT", "errors": ["Spiral Charter file missing"], "warnings": []}

    text = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_header_meta(text)
    errors: list[str] = []
    warnings: list[str] = []
    placeholders = find_placeholders(text)

    required_meta = ("spiral id", "primary surface", "lifecycle mode", "rigor tier", "status", "owner")
    for rm in required_meta:
        val = meta.get(rm, "")
        if not val or (val.startswith("[") and val.endswith("]")):
            (errors if strict else warnings).append(f"{path.name}: unfilled metadata '{rm}'")

    tier_raw = meta.get("rigor tier", "").lower().strip("[] ")
    detected_tier = TIER_ALIASES.get(tier_raw)

    headings = [ln.lower() for ln in text.splitlines() if re.match(r"^#{1,3}\s+", ln)]
    joined_h = "\n".join(headings)
    for label, kw in (
        ("Objectives & Non-Goals", r"objective|goal|non-goal|scope"),
        ("Constraints & Operating Mode", r"constraint|budget|mode"),
        ("Simplest High-Craft Option", r"simplest|alternative"),
        ("Gate Ledger / Exit", r"ledger|exit"),
    ):
        if not re.search(kw, joined_h):
            errors.append(f"{path.name}: missing Charter section '{label}'")

    verdict = "PASS"
    if errors:
        verdict = worse_verdict(verdict, "FAIL")
    if placeholders:
        warnings.append(f"{path.name}: unfilled placeholder(s): {', '.join(placeholders[:5])}")
        verdict = worse_verdict(verdict, "NOT ASSESSED")

    # Extract Spiral Exit Verdict from header (if present) and specifically from Section 4
    raw_hdr_ev = meta.get("spiral exit verdict")
    if raw_hdr_ev:
        s_ev = raw_hdr_ev.strip()
        if not (s_ev.startswith("[") and s_ev.endswith("]")):
            verdict = worse_verdict(verdict, extract_verdict_token(s_ev))

    sec4_m = re.search(r"(?im)^##\s*4\b[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.DOTALL)
    if sec4_m:
        sec4_meta = parse_meta_fields(sec4_m.group(1))
        raw_sec4_ev = sec4_meta.get("spiral exit verdict")
        if raw_sec4_ev:
            s_ev = raw_sec4_ev.strip()
            if not (s_ev.startswith("[") and s_ev.endswith("]")):
                verdict = worse_verdict(verdict, extract_verdict_token(s_ev))

    return {
        "verdict": verdict,
        "status": "PRESENT",
        "path": str(path),
        "tier_detected": detected_tier,
        "primary_surface": meta.get("primary surface", ""),
        "placeholders": placeholders,
        "errors": errors,
        "warnings": warnings,
    }


def extract_socratic_questions(text: str) -> dict[str, tuple[str, str]]:
    """Return {Qn: (inline_after_colon, sub_body_cleaned)} for Q1..Q4 in numbered or bulleted format."""
    cleaned = strip_fences_keep_lines(text)
    lines = cleaned.splitlines()
    q_re = re.compile(r"^[ \t]*(?:\d+\.|[-*])[ \t]+\*\*(Q[1-4])\b[^*]*\*\*(.*)$")
    stop_re = re.compile(r"^[ \t]*(?:---+|##\s)")
    found: dict[str, tuple[str, str]] = {}
    i = 0
    while i < len(lines):
        m = q_re.match(lines[i])
        if m:
            qn = m.group(1).upper()
            tail = m.group(2).strip()
            inline = tail.split(":", 1)[1].strip() if ":" in tail else tail
            j = i + 1
            sub_lines: list[str] = []
            while j < len(lines):
                if q_re.match(lines[j]) or stop_re.match(lines[j]):
                    break
                sub_lines.append(lines[j])
                j += 1
            sub_raw = "\n".join(sub_lines).strip()
            sub_clean = re.sub(r"^\s*[-*]\s+\*\*[^*]+\*\*\s*:\s*", "", sub_raw, flags=re.MULTILINE).strip()
            if qn not in found:
                found[qn] = (inline, sub_clean)
            i = j
            continue
        i += 1
    return found


def check_simplicity(path: Path | None, strict: bool) -> dict[str, Any]:
    if not path or not path.is_file():
        return {"verdict": "NOT ASSESSED", "status": "ABSENT", "errors": ["Simplicity Interrogation Record missing"], "warnings": []}

    text = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_header_meta(text)
    errors: list[str] = []
    warnings: list[str] = []
    placeholders = find_placeholders(text)
    declared_verdict = extract_verdict_token(meta.get("verdict"))

    # Verify all 4 Socratic Questions have real answers (not empty, <20 non-ws chars, or prompt echoes)
    questions = extract_socratic_questions(text)
    invalid_q_answer = False
    for qn in ("Q1", "Q2", "Q3", "Q4"):
        if qn not in questions:
            errors.append(f"{path.name}: missing Socratic question {qn}")
            continue
        inline, sub_ans = questions[qn]
        inline_is_prompt = bool(inline) and (
            inline.startswith('*"') or inline.startswith('"') or is_prompt_echo(inline, qn)
        )
        if sub_ans:
            ans = sub_ans if (inline_is_prompt or not inline) else f"{inline} {sub_ans}".strip()
            extra_prompt = inline if inline_is_prompt else ""
        else:
            ans = inline
            extra_prompt = ""

        ans_no_ws = re.sub(r"\s+", "", ans)
        reason: str | None = None
        if not ans or ans.startswith("["):
            reason = "missing or still placeholder"
        elif len(ans_no_ws) < 20:
            reason = f"too short ({len(ans_no_ws)} non-whitespace chars; need >= 20)"
        elif is_prompt_echo(ans, qn, extra_prompt=extra_prompt):
            reason = "echoes Socratic question prompt without project-specific explanation"

        if reason:
            invalid_q_answer = True
            msg = f"{path.name}: {qn} answer {reason}"
            if declared_verdict in {"PASS", "CONCERNS"}:
                errors.append(f"{msg} (cannot declare Verdict={declared_verdict})")
            else:
                warnings.append(msg)

    if not re.search(r"Option A\s*[—–-]\s*Simplest High-Craft", text, re.IGNORECASE):
        errors.append(f"{path.name}: missing 'Option A — Simplest High-Craft' baseline analysis")

    pass_stage = meta.get("pass stage", "").upper()
    if pass_stage in {"PRE-SHIP-CONDENSATION", "BOTH"}:
        cleaned_text = strip_fences_keep_lines(text)
        sec4_m = re.search(r"(?im)^##\s*4\b[^\n]*\n(.*?)(?=^##\s|\Z)", cleaned_text, re.DOTALL)
        sec4_unchecked = re.findall(r"^\s*[-*]\s+\[\s\]\s+(.+)$", sec4_m.group(1), re.MULTILINE) if sec4_m else []
        whole_unchecked = re.findall(r"^\s*[-*]\s+\[\s\]\s+(.+)$", cleaned_text, re.MULTILINE)
        unchecked = sec4_unchecked if sec4_unchecked else whole_unchecked
        if len(whole_unchecked) > len(unchecked):
            unchecked = whole_unchecked
        if unchecked:
            errors.append(
                f"{path.name}: Pass Stage '{pass_stage}' has {len(unchecked)} unchecked Pre-Ship Deletion item(s)"
            )
        sec4_checked = re.findall(r"^\s*[-*]\s+\[[xX]\]\s+(.+)$", sec4_m.group(1), re.MULTILINE) if sec4_m else []
        whole_checked = re.findall(r"^\s*[-*]\s+\[[xX]\]\s+(.+)$", cleaned_text, re.MULTILINE)
        checked = sec4_checked if sec4_m else whole_checked
        if not checked:
            errors.append(
                f"{path.name}: Pass Stage '{pass_stage}' requires >= 1 checked Pre-Ship Deletion item (- [x]), found 0"
            )

    verdict = "PASS"
    if errors:
        verdict = worse_verdict(verdict, "FAIL")
    if placeholders or invalid_q_answer:
        if placeholders:
            warnings.append(f"{path.name}: unfilled placeholder(s): {', '.join(placeholders[:5])}")
        verdict = worse_verdict(verdict, "NOT ASSESSED")
    verdict = worse_verdict(verdict, declared_verdict)

    return {
        "verdict": verdict,
        "status": "PRESENT",
        "path": str(path),
        "declared_verdict": declared_verdict,
        "placeholders": placeholders,
        "errors": errors,
        "warnings": warnings,
    }


def check_foundation(
    path: Path | None,
    adrs: list[Path],
    project_artifacts: dict[str, Any] | None,
    strict: bool,
    single_file_mode: bool = False,
    tier: str = "standard",
    enforce_tier: bool = False,
    charter_surface: str = "",
) -> dict[str, Any]:
    if not path or not path.is_file():
        errs = ["System Foundation Gate record missing"]
        warns: list[str] = []
        verdict = "NOT ASSESSED"
        adr_verdict = "NOT ASSESSED"
        if adrs:
            adr_verdict, adr_errs, adr_warns = check_adr_dag(adrs)
            errs.extend(adr_errs)
            warns.extend(adr_warns)
            if adr_verdict == "FAIL":
                verdict = "FAIL"
        return {
            "verdict": verdict,
            "status": "ABSENT",
            "downstream_lock": "LOCKED",
            "adr_dag_verdict": adr_verdict,
            "errors": errs,
            "warnings": warns,
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_header_meta(text)
    errors: list[str] = []
    warnings: list[str] = []
    placeholders = find_placeholders(text)

    lock_raw = meta.get("downstream lock", "")
    lock_state = "UNLOCKED" if "UNLOCKED" in lock_raw.upper() and "[" not in lock_raw else "LOCKED"

    # Inspect 6-pillar table rows
    pillar_statuses: list[str] = []
    pillar4_row_text = ""
    for line in text.splitlines():
        rm = re.match(r"^\|\s*([1-6])\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]*)\|", line)
        if rm:
            st_raw = rm.group(5).strip()
            st = extract_verdict_token(st_raw)
            pillar_statuses.append(st)
            if rm.group(1) == "4":
                pillar4_row_text = line
            if st == "FAIL":
                errors.append(f"{path.name}: Foundation Pillar {rm.group(1)} ({rm.group(2).strip()}) is FAIL")

    if len(pillar_statuses) < 6:
        errors.append(f"{path.name}: expected 6 Foundation Pillar rows, found {len(pillar_statuses)}")

    # Section 2 checkboxes (hardened against heading renames; whole-file fallback excluding Conditional Risk Waivers)
    cleaned_text = strip_fences_keep_lines(text)
    sec2_m = re.search(r"(?im)^##\s*2\b[^\n]*\n(.*?)(?=^##\s|\Z)", cleaned_text, re.DOTALL)
    sec2_unchecked = re.findall(r"^\s*[-*]\s+\[\s\]\s+(.+)$", sec2_m.group(1), re.MULTILINE) if sec2_m else []
    without_waivers = re.sub(
        r"(?ims)^#{2,3}\s+(?:3\.\s*)?Conditional\s+Risk\s+Waivers\b.*?(?=^##\s|\Z)",
        "",
        cleaned_text,
    )
    whole_unchecked = re.findall(r"^\s*[-*]\s+\[\s\]\s+(.+)$", without_waivers, re.MULTILINE)
    unchecked_sec2 = whole_unchecked if len(whole_unchecked) >= len(sec2_unchecked) else sec2_unchecked

    declared_verdict = extract_verdict_token(meta.get("verdict"))

    # Unlock invariant check
    if lock_state == "UNLOCKED":
        bad_pillars = [s for s in pillar_statuses if s in {"FAIL", "NOT ASSESSED"}]
        if declared_verdict in {"FAIL", "NOT ASSESSED"} or bad_pillars or unchecked_sec2:
            errors.append(
                f"{path.name}: ILLEGAL_UNLOCK — Downstream Lock=UNLOCKED while verdict={declared_verdict}, "
                f"incomplete_pillars={len(bad_pillars)}, unchecked_checklist={len(unchecked_sec2)}"
            )

    # ADR DAG check
    adr_verdict, adr_errs, adr_warns = check_adr_dag(adrs)
    errors.extend(adr_errs)
    warnings.extend(adr_warns)

    # Disk supporting evidence & --tier floor checks in project mode
    if not single_file_mode and project_artifacts is not None:
        surface_low = (meta.get("primary surface", "") + " " + charter_surface).lower()
        is_static_landing_na = (
            ("landing" in surface_low or "static" in surface_low)
            and bool(
                re.search(r"\bN/?A\b", pillar4_row_text, re.IGNORECASE)
                or re.search(r"(?:control-manifest|adrs?)\s*:\s*N/?A\b", text, re.IGNORECASE)
            )
        )
        if strict:
            if not project_artifacts.get("arch_docs"):
                errors.append("Phase 3A strict check: missing architecture doc (docs/architecture/*.md or architecture.md)")
            if not project_artifacts.get("adrs") and not is_static_landing_na:
                errors.append("Phase 3A strict check: missing Foundation ADRs (docs/architecture/adr/*.md or docs/adr/*.md)")
            if not project_artifacts.get("data_models") and not project_artifacts.get("contracts"):
                errors.append("Phase 3A strict check: missing data model or core contracts on disk")
        if strict or enforce_tier:
            if tier in {"standard", "full"} and not is_static_landing_na:
                if not project_artifacts.get("control_manifest"):
                    errors.append(
                        f"Phase 3A {tier} tier check: missing control-manifest.md (docs/architecture/control-manifest.md)"
                    )
                if len(adrs) < 3:
                    errors.append(
                        f"Phase 3A {tier} tier check: '{tier}' tier requires >= 3 Accepted ADRs, found {len(adrs)}"
                    )
            elif tier == "minimal" and not is_static_landing_na:
                if len(adrs) < 1:
                    errors.append(
                        f"Phase 3A minimal tier check: requires >= 1 Accepted ADR, found {len(adrs)}"
                    )

    verdict = "PASS"
    if errors:
        verdict = worse_verdict(verdict, "FAIL")
    for st in pillar_statuses:
        verdict = worse_verdict(verdict, st)
    if placeholders or unchecked_sec2:
        if placeholders:
            warnings.append(f"{path.name}: unfilled placeholder(s): {', '.join(placeholders[:5])}")
        verdict = worse_verdict(verdict, "NOT ASSESSED")
    verdict = worse_verdict(verdict, declared_verdict)
    if adr_verdict == "FAIL":
        verdict = worse_verdict(verdict, "FAIL")

    return {
        "verdict": verdict,
        "status": "PRESENT",
        "path": str(path),
        "declared_verdict": declared_verdict,
        "downstream_lock": lock_state,
        "pillars_found": len(pillar_statuses),
        "adr_dag_verdict": adr_verdict,
        "unchecked_checklist": len(unchecked_sec2),
        "placeholders": placeholders,
        "errors": errors,
        "warnings": warnings,
    }


SPIKE_LEAK_RE = re.compile(
    r"(?:import|from|require\s*\()\s*[^;\n]*(?:spikes|prototypes)[/\\]"
    r"|\b(?:import|from)\s+(?:\.{0,3})(?:[A-Za-z0-9_]+\.)*(?:spikes|prototypes)(?:\.|/|\s+import\b|\s+as\b|\s*,|\s*$|\s*#)"
    r"|\bfrom\s+[^\s;#]+\s+import\s+[^;\n#]*\b(?:spikes|prototypes)\b"
    r"|^\s*import\s+(?:[A-Za-z0-9_.]+\s*,\s*)*(?:[A-Za-z0-9_]+\.)*(?:spikes|prototypes)(?:\.[A-Za-z0-9_.]+)?(?=\s|,|$|#)",
    re.MULTILINE,
)


def check_risk_register(path: Path | None, project_dir: Path | None, strict: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    # Check prod code for spikes/ or prototypes/ leaks even if register is absent
    spike_leaks: list[str] = []
    if project_dir and project_dir.is_dir():
        for dname in CODE_DIRS:
            sub = project_dir / dname
            if not sub.is_dir():
                continue
            for cur_root, dirs, files in os.walk(sub):
                dirs[:] = [d for d in dirs if d not in SKIP_WALK_DIRS]
                for f in files:
                    fp = Path(cur_root) / f
                    if fp.suffix.lower() not in CODE_EXTS:
                        continue
                    try:
                        content = fp.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    if SPIKE_LEAK_RE.search(content):
                        spike_leaks.append(fp.relative_to(project_dir).as_posix())

    for leak in spike_leaks:
        errors.append(f"SPIKE_LEAK: production source '{leak}' imports from spikes/ or prototypes/")

    if not path or not path.is_file():
        verdict = "FAIL" if errors else "NOT ASSESSED"
        return {
            "verdict": verdict,
            "status": "ABSENT",
            "spike_leaks": spike_leaks,
            "errors": errors + ["Risk & Spike Register missing"],
            "warnings": warnings,
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    # Scope top-level metadata strictly to the header block (before first ## heading or ### Spike Card)
    header_text = re.split(r"(?m)^(?:##\s+|###\s+Spike Card\b)", text, maxsplit=1)[0]
    meta = parse_meta_fields(header_text)
    placeholders = find_placeholders(text)

    # Parse Section 1 Risk table rows
    open_high_crit = 0
    for line in text.splitlines():
        rm = re.match(r"^\|\s*(RSK-\d+|[^|\s]+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|", line)
        if rm:
            rid = rm.group(1).strip()
            if rid.lower() in {"risk id", "---"} or rid.startswith("---"):
                continue
            sev_raw = rm.group(5).strip()
            st_raw = rm.group(7).strip()
            # Ignore bracketed template placeholders such as [High] or [OPEN]
            if sev_raw.startswith("[") or st_raw.startswith("["):
                continue
            sev = sev_raw.lower()
            st = st_raw.upper()
            if sev in {"high", "critical"} and st == "OPEN":
                open_high_crit += 1
                errors.append(f"{path.name}: {rid} has Severity={sev.title()} and Status=OPEN (blocks Phase 3A)")

    # Parse Spike cards for 3-PIVOT-to-KILL invariant
    cards = re.split(r"^###\s+Spike Card:", text, flags=re.MULTILINE)[1:]
    for idx, card in enumerate(cards, start=1):
        pc_m = re.search(r"\*\*Pivot Count\*\*\s*:\s*([^\n]+)", card)
        vd_m = re.search(r"\*\*Verdict\*\*\s*:\s*([^\n]+)", card)
        if pc_m and vd_m:
            num_m = re.search(r"\d+", pc_m.group(1))
            pivots = int(num_m.group(0)) if num_m else 0
            vd = extract_verdict_token(vd_m.group(1))
            if pivots >= 3 and vd != "KILL":
                errors.append(
                    f"{path.name}: Spike Card #{idx} has Pivot Count={pivots} (>=3) but Verdict='{vd}' (MUST be KILL)"
                )

    verdict = "PASS"
    if errors:
        verdict = worse_verdict(verdict, "FAIL")
    if placeholders:
        warnings.append(f"{path.name}: unfilled placeholder(s): {', '.join(placeholders[:5])}")
        verdict = worse_verdict(verdict, "NOT ASSESSED")
    declared_verdict = extract_verdict_token(meta.get("verdict"))
    verdict = worse_verdict(verdict, declared_verdict)

    return {
        "verdict": verdict,
        "status": "PRESENT",
        "path": str(path),
        "declared_verdict": declared_verdict,
        "open_high_critical": open_high_crit,
        "spike_leaks": spike_leaks,
        "placeholders": placeholders,
        "errors": errors,
        "warnings": warnings,
    }


def detect_system_first_violation(
    project_dir: Path,
    foundation_res: dict[str, Any],
    simplicity_res: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Detect feature/UI code authored before Phase 3A Foundation & Simplicity Gates unlock."""
    feature_files: list[str] = []
    for dname in CODE_DIRS:
        sub = project_dir / dname
        if not sub.is_dir():
            continue
        for cur_root, dirs, files in os.walk(sub):
            dirs[:] = [d for d in dirs if d not in SKIP_WALK_DIRS]
            for f in files:
                fp = Path(cur_root) / f
                if fp.suffix.lower() not in CODE_EXTS:
                    continue
                if fp.stem.lower() in SKELETON_STEMS:
                    continue
                feature_files.append(fp.relative_to(project_dir).as_posix())

    if not feature_files:
        return [], []

    f_ok = foundation_res.get("verdict") in {"PASS", "CONCERNS"} and foundation_res.get("downstream_lock") == "UNLOCKED"
    s_ok = simplicity_res.get("verdict") in {"PASS", "CONCERNS"}
    if f_ok and s_ok:
        return [], feature_files

    reasons: list[str] = []
    if not f_ok:
        reasons.append(
            f"Phase 3A Foundation verdict={foundation_res.get('verdict')} lock={foundation_res.get('downstream_lock')}"
        )
    if not s_ok:
        reasons.append(f"Simplicity verdict={simplicity_res.get('verdict')}")
    sample = ", ".join(feature_files[:5])
    return [
        f"SYSTEM_FIRST_VIOLATION: Feature/UI code detected ({sample}) before Phase 3A & Simplicity Gates passed ({'; '.join(reasons)})"
    ], feature_files


def run_self_tests() -> tuple[bool, list[dict[str, Any]]]:
    """Run isolated self-test scenarios in TemporaryDirectory verifying gate invariants & anti-bypass rules."""
    results: list[dict[str, Any]] = []

    def _run_cli(ws: Path, extra: list[str] | None = None) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        argv = ["--project-dir", str(ws), "--json", *(extra or [])]
        with contextlib.redirect_stdout(buf):
            rc = main(argv)
        return rc, json.loads(buf.getvalue())

    def _write_clean_ws(ws: Path) -> None:
        ws.mkdir(parents=True, exist_ok=True)
        (ws / "spiral-charter.md").write_text(
            "# Spiral Charter (`SP-001`)\n\n"
            "- **Spiral ID**: SP-001\n- **Project / Product Name**: SelfTest\n"
            "- **Primary Surface**: Web App / SaaS\n- **Lifecycle Mode**: greenfield\n"
            "- **Rigor Tier**: standard\n- **Status**: ACTIVE\n- **Owner**: Lead\n\n"
            "## 1. Objectives & Non-Goals\n- Primary goal.\n\n"
            "## 2. Constraints & Operating Mode\n- 1 DB.\n\n"
            "## 3. Simplest High-Craft Option\n- Option A.\n\n"
            "## 4. Cross-Quadrant Gate Ledger & Q4 Spiral Exit\n"
            "- **Spiral Exit Verdict**: PASS\n",
            encoding="utf-8",
        )
        (ws / "simplicity-interrogation-record.md").write_text(
            "# Simplicity Interrogation Record (`SIR-001`)\n\n"
            "- **Record ID**: SIR-001\n- **Spiral ID**: SP-001\n- **Target Scope**: Full Spiral\n"
            "- **Pass Stage**: BOTH\n- **Verdict**: PASS\n\n"
            "## 1. Mandatory 4 Socratic Self-Interrogation Questions\n"
            "1. **Q1**: Replacing Redis and Celery with PostgreSQL SKIP LOCKED delivers lower latency and 0 extra services.\n"
            "2. **Q2**: Deleted ORM repository wrappers in favor of parameterized SQL queries and native HTML dialog elements.\n"
            "3. **Q3**: Verified peak load in PRD-02 is 500 req/min; multi-region sharding is explicitly deferred.\n"
            "4. **Q4**: Consolidated webhook handlers into 180 lines across two pure Python modules.\n\n"
            "## 2. Simplest High-Craft Option Analysis\n"
            "- **Option A — Simplest High-Craft Baseline**: Modular monolith with PostgreSQL 16.\n\n"
            "## 4. Complexity Budget & Pre-Ship Deletion / Condensation Pass\n"
            "- [x] Deleted unused wrappers and re-ran full test suite cleanly.\n",
            encoding="utf-8",
        )
        (ws / "system-foundation-gate.md").write_text(
            "# System-First Foundation Gate (`SFG-001`)\n\n"
            "- **Gate ID**: SFG-001\n- **Spiral ID**: SP-001\n- **Primary Surface**: Web App / SaaS\n"
            "- **Lifecycle Mode**: greenfield\n- **Rigor Tier**: standard\n- **Verdict**: PASS\n"
            "- **Downstream Lock**: UNLOCKED\n\n"
            "## 1. Mandatory Phase 3A Foundation Pillars\n"
            "| # | Pillar | Artifacts | Floor | Status | Evidence |\n"
            "|---|---|---|---|---|---|\n"
            "| 1 | Arch | arch.md | std | PASS | arch.md |\n"
            "| 2 | Data | data.md | std | PASS | data.md |\n"
            "| 3 | Contracts | openapi.yaml | std | PASS | openapi.yaml |\n"
            "| 4 | ADRs | adr-001.md | std | PASS | adr-001.md |\n"
            "| 5 | Skeleton | healthz | all | PASS | healthz |\n"
            "| 6 | Simplicity | SIR-001 | all | PASS | sir.md |\n\n"
            "## 2. Pre-Code Verification Checklist\n"
            "- [x] All 6 pillars verified.\n",
            encoding="utf-8",
        )
        (ws / "risk-spike-register.md").write_text(
            "# Risk & Spike Register (`RSK-SP-001`)\n\n"
            "- **Register ID**: RSK-SP-001\n- **Spiral ID**: SP-001\n"
            "- **Unmitigated High/Critical Risks**: 0\n- **Verdict**: PASS\n\n"
            "## 1. Risk & Threat Trigger Register\n"
            "| Risk ID | Domain | Trigger | Likelihood | Severity | Mitigation | Status |\n"
            "|---|---|---|---|---|---|---|\n"
            "| RSK-001 | Perf | Latency > 50ms | M | High | Indexed query | MITIGATED |\n\n"
            "## 2. Throwaway Spike & Concept Prototype Cards\n"
            "### Spike Card: `SPK-001`\n"
            "- **Pivot Count**: 1\n- **Verdict**: GO\n",
            encoding="utf-8",
        )

    with tempfile.TemporaryDirectory(prefix="spiral_gates_selftest_") as tmp:
        root = Path(tmp)

        # 1. Clean baseline with GO Spike Card
        w1 = root / "clean_baseline"
        _write_clean_ws(w1)
        rc, d = _run_cli(w1)
        ok1 = rc == 0 and d.get("verdict") == "PASS"
        results.append({"name": "clean_baseline_with_go_card", "passed": ok1, "rc": rc, "verdict": d.get("verdict")})

        # 2. Prompt echo + generic filler on Q1..Q4 (including Q3)
        w2 = root / "prompt_filler"
        _write_clean_ws(w2)
        (w2 / "simplicity-interrogation-record.md").write_text(
            "# Simplicity Interrogation Record (`SIR-001`)\n\n"
            "- **Record ID**: SIR-001\n- **Spiral ID**: SP-001\n"
            "- **Pass Stage**: PRE-DESIGN\n- **Verdict**: PASS\n\n"
            "## 1. Mandatory 4 Socratic Self-Interrogation Questions\n"
            "1. **Q1**: For this feature/requirement, is there a simpler approach that delivers equal or HIGHER quality, UX, reliability, and maintainability? Yes, we carefully evaluated this and confirmed our chosen approach is already minimal!\n"
            "2. **Q2**: What layers, dependencies, abstractions, or moving parts can be deleted or replaced with native platform/language/database/browser primitives? None, we checked all layers and confirmed everything is currently needed and appropriate.\n"
            "3. **Q3**: Are we solving a real, verified constraint right now or inventing complexity for hypothetical scale? Yes, we verified our current approach fits the actual constraints of this project today.\n"
            "4. **Q4**: How do we make the code and technical architecture as concise, dense, readable, and minimal as possible while maximizing craft? We reviewed the code and confirmed it remains concise, dense, readable, and minimal overall.\n\n"
            "## 2. Simplest High-Craft Option Analysis\n"
            "- **Option A — Simplest High-Craft Baseline**: Modular monolith.\n",
            encoding="utf-8",
        )
        rc, d = _run_cli(w2)
        errs = d.get("errors", [])
        ok2 = rc == 1 and d.get("verdict") == "FAIL" and all(f"{qn} answer echoes" in " ".join(errs) for qn in ("Q1", "Q2", "Q3", "Q4"))
        results.append({"name": "prompt_echo_plus_filler_all_q1_q4", "passed": ok2, "rc": rc, "verdict": d.get("verdict")})

        # 3. Synonym paraphrase evasion on Q1..Q4
        w3 = root / "synonym_paraphrase"
        _write_clean_ws(w3)
        (w3 / "simplicity-interrogation-record.md").write_text(
            "# Simplicity Interrogation Record (`SIR-001`)\n\n"
            "- **Record ID**: SIR-001\n- **Spiral ID**: SP-001\n"
            "- **Pass Stage**: PRE-DESIGN\n- **Verdict**: PASS\n\n"
            "## 1. Mandatory 4 Socratic Self-Interrogation Questions\n"
            "1. **Q1**: For this specific feature, is there an easier approach delivering equal or higher quality, UX, reliability, and maintainability in our app?\n"
            "2. **Q2**: What layers, packages, abstractions, or moving parts can we remove or swap with native platform, language, database, or browser primitives today?\n"
            "3. **Q3**: Are we solving a real, verified limitation right now or inventing extra complexity for future scale in this project?\n"
            "4. **Q4**: How do we keep the codebase and technical design as tight, dense, readable, and tiny as possible while maximizing craft here?\n\n"
            "## 2. Simplest High-Craft Option Analysis\n"
            "- **Option A — Simplest High-Craft Baseline**: Modular monolith.\n",
            encoding="utf-8",
        )
        rc, d = _run_cli(w3)
        errs = d.get("errors", [])
        ok3 = rc == 1 and d.get("verdict") == "FAIL" and all(f"{qn} answer echoes" in " ".join(errs) for qn in ("Q1", "Q2", "Q3", "Q4"))
        results.append({"name": "synonym_paraphrase_all_q1_q4", "passed": ok3, "rc": rc, "verdict": d.get("verdict")})

        # 4. Header FAIL + body PASS overwrite resistance (SIR + SFG + Charter)
        w4 = root / "hdr_fail_body_pass"
        _write_clean_ws(w4)
        for fn in ("simplicity-interrogation-record.md", "system-foundation-gate.md"):
            txt = (w4 / fn).read_text(encoding="utf-8")
            (w4 / fn).write_text(txt.replace("- **Verdict**: PASS", "- **Verdict**: FAIL", 1) + "\n## 5. Notes\n- **Verdict**: PASS\n", encoding="utf-8")
        rc, d = _run_cli(w4)
        s_decl = d.get("gates", {}).get("simplicity", {}).get("declared_verdict")
        f_decl = d.get("gates", {}).get("foundation", {}).get("declared_verdict")
        ok4 = rc == 1 and d.get("verdict") == "FAIL" and s_decl == "FAIL" and f_decl == "FAIL"
        results.append({"name": "header_meta_not_overwritten_by_body", "passed": ok4, "rc": rc, "s_decl": s_decl, "f_decl": f_decl})

        # 5. PRE-SHIP-CONDENSATION with zero checkboxes
        w5 = root / "preship_no_checkbox"
        _write_clean_ws(w5)
        sir_txt = (w5 / "simplicity-interrogation-record.md").read_text(encoding="utf-8")
        (w5 / "simplicity-interrogation-record.md").write_text(
            sir_txt.split("## 4.")[0] + "## 4. Complexity Budget\n- **Declared Complexity Budget**: 1 DB.\n",
            encoding="utf-8",
        )
        rc, d = _run_cli(w5)
        ok5 = rc == 1 and d.get("verdict") == "FAIL"
        results.append({"name": "preship_zero_checkboxes_rejected", "passed": ok5, "rc": rc, "verdict": d.get("verdict")})

        # 6. Nested pkg.spikes.* SPIKE_LEAK + non-leak false positive guard
        w6 = root / "nested_spike_leak"
        _write_clean_ws(w6)
        (w6 / "src").mkdir()
        (w6 / "src" / "svc.py").write_text("from pkg.spikes.foo import bar\n", encoding="utf-8")
        rc_leak, d_leak = _run_cli(w6)
        (w6 / "src" / "svc.py").write_text("from spikes_utils import ok\nspikes_count = 0\n", encoding="utf-8")
        rc_clean, d_clean = _run_cli(w6)
        ok6 = (
            rc_leak == 1
            and any("SPIKE_LEAK" in e for e in d_leak.get("errors", []))
            and rc_clean == 0
            and d_clean.get("verdict") == "PASS"
        )
        results.append({"name": "nested_spike_leak_and_nonleak_guard", "passed": ok6, "rc_leak": rc_leak, "rc_clean": rc_clean})

    all_passed = all(r["passed"] for r in results)
    return all_passed, results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Spiral Charter, Simplicity, Q2 Risk & Phase 3A System-First Foundation Gates."
    )
    parser.add_argument("--project-dir", "--root", dest="project_dir", default=".", help="Target project directory (default: .)")
    parser.add_argument(
        "--stage",
        "--phase",
        "--gate",
        dest="stage",
        default="auto",
        help="Gate stage: auto|all|charter|foundation|system-foundation|3a|simplicity|q2-risk|risk-spike|full",
    )
    parser.add_argument("--tier", default="auto", help="Rigor tier: auto|minimal|standard|full|micro|enterprise")
    parser.add_argument("--file", help="Validate a single gate/template file directly")
    parser.add_argument("--charter", help="Explicit path to spiral-charter.md")
    parser.add_argument("--foundation", help="Explicit path to system-foundation-gate.md")
    parser.add_argument("--simplicity", help="Explicit path to simplicity-interrogation-record.md")
    parser.add_argument("--risk", help="Explicit path to risk-spike-register.md")
    parser.add_argument("--strict", action="store_true", help="Treat missing supporting disk artifacts and unfilled metadata as hard failures")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run isolated self-tests verifying gate invariants and anti-bypass rules")
    args = parser.parse_args(argv)

    if args.self_test:
        passed, results = run_self_tests()
        if args.json:
            print(json.dumps({"self_test_passed": passed, "results": results}, indent=2))
        else:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] check_spiral_gates.py --self-test ({sum(1 for r in results if r['passed'])}/{len(results)} passed)")
            for r in results:
                mark = "PASS" if r["passed"] else "FAIL"
                print(f"  - [{mark}] {r['name']}")
        return 0 if passed else 1

    stage = args.stage.strip().lower()
    stage_norm_map = {
        "auto": "auto",
        "all": "all",
        "full": "all",
        "charter": "charter",
        "foundation": "foundation",
        "system-foundation": "foundation",
        "3a": "foundation",
        "simplicity": "simplicity",
        "q2-risk": "q2-risk",
        "risk-spike": "q2-risk",
    }
    if stage not in stage_norm_map:
        print(f"ERROR: Unsupported --stage '{args.stage}'", file=sys.stderr)
        return 2
    norm_stage = stage_norm_map[stage]

    if args.tier.lower() != "auto" and args.tier.lower() not in TIER_ALIASES:
        print(f"ERROR: Unsupported --tier '{args.tier}'", file=sys.stderr)
        return 2

    # Single-file direct validation mode
    if args.file:
        fp = Path(args.file)
        if not fp.is_file():
            msg = f"Target gate file not found: {args.file}"
            if args.json:
                print(json.dumps({"verdict": "FAIL", "errors": [msg]}))
            else:
                print(f"ERROR: {msg}", file=sys.stderr)
            return 2
        txt = fp.read_text(encoding="utf-8", errors="replace")
        ftype = norm_stage if norm_stage not in {"auto", "all"} else detect_file_type(txt, fp)
        if ftype == "charter":
            res = check_charter(fp, strict=args.strict)
        elif ftype == "simplicity":
            res = check_simplicity(fp, strict=args.strict)
        elif ftype == "foundation":
            res = check_foundation(fp, adrs=[], project_artifacts=None, strict=args.strict, single_file_mode=True)
        elif ftype == "q2-risk":
            res = check_risk_register(fp, project_dir=None, strict=args.strict)
        else:
            placeholders = find_placeholders(txt)
            res = {
                "verdict": "NOT ASSESSED" if placeholders else "PASS",
                "placeholders": placeholders,
                "errors": [],
                "warnings": [f"Unrecognized gate type; placeholders={len(placeholders)}"] if placeholders else [],
            }
        out = {
            "mode": "single_file",
            "file": str(fp),
            "detected_type": ftype,
            "verdict": res["verdict"],
            "result": res,
            "disclaimer": "Structural gate verification checks artifact presence, required sections, placeholders, and invariants; it cannot verify domain soundness.",
        }
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"[{res['verdict']}] {fp} (type={ftype})")
            for w in res.get("warnings", []):
                print(f"  WARN: {w}")
            for e in res.get("errors", []):
                print(f"  ERR:  {e}")
        return 0 if res["verdict"] in {"PASS", "CONCERNS"} else 1

    pdir = Path(args.project_dir)
    if not pdir.exists() or not pdir.is_dir():
        msg = f"Invalid project directory: {args.project_dir}"
        if args.json:
            print(json.dumps({"verdict": "FAIL", "errors": [msg]}))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    arts = discover_project_artifacts(pdir)
    charter_p = Path(args.charter) if args.charter else arts["charter"]
    foundation_p = Path(args.foundation) if args.foundation else arts["foundation"]
    simplicity_p = Path(args.simplicity) if args.simplicity else arts["simplicity"]
    risk_p = Path(args.risk) if args.risk else arts["risk"]

    gates: dict[str, Any] = {}
    errors: list[str] = []
    warnings: list[str] = []
    overall = "PASS"

    run_charter = norm_stage in {"auto", "all", "charter"}
    run_simplicity = norm_stage in {"auto", "all", "simplicity", "foundation"}
    run_foundation = norm_stage in {"auto", "all", "foundation"}
    run_risk = norm_stage in {"all", "q2-risk"} or (norm_stage in {"auto", "foundation"} and (risk_p is not None or args.strict))

    tier_explicit = args.tier.lower() != "auto"
    detected_tier: str | None = None
    charter_surface = ""

    if run_charter:
        c_res = check_charter(charter_p, strict=args.strict)
        gates["charter"] = c_res
        errors.extend(c_res["errors"])
        warnings.extend(c_res["warnings"])
        overall = worse_verdict(overall, c_res["verdict"])
        detected_tier = c_res.get("tier_detected")
        charter_surface = c_res.get("primary_surface", "")
    elif charter_p and charter_p.is_file():
        c_meta = parse_header_meta(charter_p.read_text(encoding="utf-8", errors="replace"))
        detected_tier = TIER_ALIASES.get(c_meta.get("rigor tier", "").lower().strip("[] "))
        charter_surface = c_meta.get("primary surface", "")

    if not detected_tier and foundation_p and foundation_p.is_file():
        f_meta = parse_header_meta(foundation_p.read_text(encoding="utf-8", errors="replace"))
        detected_tier = TIER_ALIASES.get(f_meta.get("rigor tier", "").lower().strip("[] "))

    tier_used = TIER_ALIASES[args.tier.lower()] if tier_explicit else (detected_tier or "standard")

    if run_simplicity:
        s_res = check_simplicity(simplicity_p, strict=args.strict)
        gates["simplicity"] = s_res
        errors.extend(s_res["errors"])
        warnings.extend(s_res["warnings"])
        overall = worse_verdict(overall, s_res["verdict"])
    else:
        s_res = {"verdict": "NOT ASSESSED"}

    if run_foundation:
        f_res = check_foundation(
            foundation_p,
            adrs=arts["adrs"],
            project_artifacts=arts,
            strict=args.strict,
            tier=tier_used,
            enforce_tier=tier_explicit,
            charter_surface=charter_surface,
        )
        gates["foundation"] = f_res
        errors.extend(f_res["errors"])
        warnings.extend(f_res["warnings"])
        overall = worse_verdict(overall, f_res["verdict"])
    else:
        f_res = {"verdict": "NOT ASSESSED", "downstream_lock": "LOCKED"}

    if run_risk:
        r_res = check_risk_register(risk_p, project_dir=pdir, strict=args.strict)
        gates["q2_risk"] = r_res
        errors.extend(r_res["errors"])
        warnings.extend(r_res["warnings"])
        overall = worse_verdict(overall, r_res["verdict"])

    # System-first violation scan
    if norm_stage in {"auto", "all", "foundation"}:
        sf_errs, feat_files = detect_system_first_violation(pdir, f_res, s_res)
        gates["system_first_order"] = {
            "verdict": "FAIL" if sf_errs else "PASS",
            "feature_files_found": len(feat_files),
            "errors": sf_errs,
        }
        if sf_errs:
            errors.extend(sf_errs)
            overall = worse_verdict(overall, "FAIL")

    report = {
        "project_dir": str(pdir.resolve()),
        "stage_evaluated": norm_stage,
        "tier": tier_used,
        "verdict": overall,
        "gates": gates,
        "observations": {
            "charter": str(charter_p) if charter_p else "ABSENT",
            "simplicity": str(simplicity_p) if simplicity_p else "ABSENT",
            "foundation": str(foundation_p) if foundation_p else "ABSENT",
            "risk_register": str(risk_p) if risk_p else "ABSENT",
            "adrs_found": len(arts["adrs"]),
            "arch_docs_found": len(arts["arch_docs"]),
            "data_models_found": len(arts["data_models"]),
            "contracts_found": len(arts["contracts"]),
        },
        "errors": errors,
        "warnings": warnings,
        "disclaimer": "Structural gate verification checks artifact presence, required sections, placeholders, ADR DAGs, and system-first ordering; it cannot judge architectural soundness.",
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"[{overall}] stage={norm_stage} tier={tier_used} project={pdir}")
        for gname, gval in gates.items():
            print(f"  - {gname}: {gval['verdict']}")
        for w in warnings:
            print(f"  WARN: {w}")
        for e in errors:
            print(f"  ERR:  {e}")

    return 0 if overall in {"PASS", "CONCERNS"} else 1


if __name__ == "__main__":
    sys.exit(main())
