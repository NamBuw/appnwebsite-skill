#!/usr/bin/env python3
"""Offline, vendor-neutral security baseline scanner (Python 3 stdlib only).

Checks Python, JS/TS/JSX/TSX, HTML, YAML/GitHub Actions, .env, and dependency
manifests for high-impact OWASP/supply-chain flaws without requiring any IDE
daemon or external network access.

Usage:
    python3 check_security_baseline.py --path <file_or_dir> [--json] [--severity low|medium|high|critical]
    python3 check_security_baseline.py <file_or_dir> [--json]
    python3 check_security_baseline.py --self-test
"""

from __future__ import annotations

import argparse
import ast
import http.client
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence

MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2 MiB resource guard

SEVERITY_ORDER: dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
        ".pytest_cache",
        ".mypy_cache",
    }
)

SCANNABLE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py",
        ".pyi",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".html",
        ".htm",
        ".yml",
        ".yaml",
        ".json",
    }
)

CODE_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
)
PY_EXTENSIONS: frozenset[str] = frozenset({".py", ".pyi"})
JS_EXTENSIONS: frozenset[str] = frozenset({".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"})

# --- Compiled Patterns (kept self-clean so scanning this file produces 0 FPs) ---

_KNOWN_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Stripe live secret key", re.compile(r"\bsk_live_[0-9a-zA-Z]{16,}\b")),
    ("Stripe restricted live key", re.compile(r"\brk_live_[0-9a-zA-Z]{16,}\b")),
    ("AWS access key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub personal access token", re.compile(r"\bghp_[0-9a-zA-Z]{20,}\b")),
    ("GitHub fine-grained PAT", re.compile(r"\bgithub_pat_[0-9a-zA-Z_]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9a-zA-Z-]{10,}\b")),
    (
        "Private key block",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ),
)

_SECRET_NAMES_PAT = (
    r"API_SECRET|SECRET_KEY|JWT_SECRET|DB_PASSWORD|DATABASE_URL|"
    r"PRIVATE_KEY|ACCESS_TOKEN|AUTH_SECRET|CLIENT_SECRET"
)
_SECRET_NAME_RE = re.compile(rf"^(?:{_SECRET_NAMES_PAT})$", re.IGNORECASE)
_ENV_SECRET_KEY_RE = re.compile(
    r"(?:SECRET|TOKEN|PASSWORD|PASSWD|PWD|PRIVATE_KEY|API_KEY|AUTH|"
    r"CREDENTIAL|DATABASE_URL|SIGNING_KEY|ENCRYPTION_KEY|(?:^|_)KEY$)",
    re.IGNORECASE,
)
_SECRET_ASSIGN_RE = re.compile(
    rf"""(?i)\b(?:{_SECRET_NAMES_PAT})\b\s*[:=]\s*(['"`])([^'"`\s]{{8,}})\1"""
)
_ENV_FALLBACK_RE = re.compile(
    r"""(\b(?:os\.(?:getenv|environ\.get)|environ\.get|getenv)\s*\(\s*(['"])([^'"]+)\2\s*,\s*(?:default\s*=\s*)?)(['"])([^'"]+)\4(\s*\))"""
)
_SAFE_SECRET_PLACEHOLDERS = frozenset(
    {"changeme", "example", "placeholder", "redacted", "dummy_secret_value"}
)

_SQL_KEYWORDS = r"(?:SELECT\s+.+?\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)"
_SQL_KEYWORDS_MULTILINE_RE = re.compile(
    r"(?:SELECT\s+[\s\S]{1,300}?\s+FROM|INSERT\s+INTO|UPDATE\s+(?:\w+|\$\{[^}]+\}|\{__AST_EXPR__\})\s+SET|DELETE\s+FROM)",
    re.IGNORECASE,
)
_TQ_S = "'" * 3
_TQ_D = '"' * 3
_PY_SQL_FSTRING_RE = re.compile(
    r"\bf(?:"
    + _TQ_D + r"[^\n]*" + _SQL_KEYWORDS + r"[^\n]*\{\s*[^}]+\s*\}[^\n]*" + _TQ_D
    + "|" + _TQ_S + r"[^\n]*" + _SQL_KEYWORDS + r"[^\n]*\{\s*[^}]+\s*\}[^\n]*" + _TQ_S
    + r'|"[^"]*' + _SQL_KEYWORDS + r'[^"]*\{\s*[^}]+\s*\}[^"]*"'
    + r"|'[^']*" + _SQL_KEYWORDS + r"[^']*\{\s*[^}]+\s*\}[^']*'"
    + r")",
    re.IGNORECASE,
)
_PY_SQL_FORMAT_RE = re.compile(
    rf"""(?:"[^"]*{_SQL_KEYWORDS}[^"]*"|'[^']*{_SQL_KEYWORDS}[^']*')\s*(?:%|\.format\s*\()""",
    re.IGNORECASE,
)
_SQL_CONCAT_RE = re.compile(
    rf"""(?:"[^"]*{_SQL_KEYWORDS}[^"]*"|'[^']*{_SQL_KEYWORDS}[^']*'|`[^`]*{_SQL_KEYWORDS}[^`]*`)\s*\+\s*[A-Za-z_(\[]""",
    re.IGNORECASE,
)
_JS_BACKTICK_SPAN_RE = re.compile(r"`(?:\\[\s\S]|[^`\\])*`")
_JS_INTERP_RE = re.compile(r"\$\{[^}]+\}")

_DANGEROUS_INNER_HTML_RE = re.compile(r"\bdangerouslySetInnerHTML\b")
_DOMPURIFY_RE = re.compile(r"\bDOMPurify\.sanitize\s*\(")
_DOM_SINKS_RE = re.compile(
    r"""(?:\.(?:innerHTML|outerHTML)\s*=(?!=)|\.insertAdjacentHTML\s*\(|\bdocument\.write(?:ln)?\s*\()"""
)

_WEB_STORAGE_TOKEN_RE = re.compile(
    r"""\b(?:localStorage|sessionStorage)\.setItem\s*\(\s*(['"])[^'"]*(?:token|jwt|session|auth|secret|refresh|credential)[^'"]*\1""",
    re.IGNORECASE,
)

_CORS_ORIGIN_WILDCARD_RE = re.compile(
    r"""(?:['"](?i:Access-Control-Allow-Origin)['"]\s*:\s*['"]\*['"]|"""
    r"""\ballow_origins\s*=\s*(?:\[[^\]]*['"]\*['"][^\]]*\]|\([^)]*['"]\*['"][^)]*\))|"""
    r"""\borigin\s*:\s*(?:['"]\*['"]|\[[^\]]*['"]\*['"][^\]]*\])|"""
    r"""\.(?:setHeader|header|set)\s*\(\s*['"](?i:Access-Control-Allow-Origin)['"]\s*,\s*['"]\*['"]\s*\))""",
    re.DOTALL,
)
_CORS_CREDENTIALS_TRUE_RE = re.compile(
    r"""(?:['"]Access-Control-Allow-Credentials['"]\s*:\s*['"]?true['"]?|"""
    r"""\ballow_credentials\s*=\s*True\b|"""
    r"""\bcredentials\s*:\s*true\b|"""
    r"""\.(?:setHeader|header|set)\s*\(\s*['"]Access-Control-Allow-Credentials['"]\s*,\s*(?:['"]?true['"]?|True)\s*\))""",
    re.IGNORECASE | re.DOTALL,
)

_EXEC_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("os.system command execution", re.compile(r"\bos\.system\s*\(")),
    (
        "subprocess with shell=True",
        re.compile(r"\bsubprocess\.(?:run|call|Popen|check_output|check_call)\([^)]*shell\s*=\s*True"),
    ),
    ("child_process.exec command execution", re.compile(r"\bchild_process\.exec(?:Sync)?\s*\(")),
    ("Dynamic eval call", re.compile(r"(?<![.\w$])[e]val\s*\(")),
    ("Dynamic new Function call", re.compile(r"\bnew\s+[F]unction\s*\(")),
)

_DESER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Unsafe Python pickle deserialization", re.compile(r"\b(?:c?Pickle|pickle)\.(?:loads?|Unpickler)\s*\(")),
    ("Unsafe marshal deserialization", re.compile(r"\bmarshal\.loads?\s*\(")),
    ("Unsafe yaml.unsafe_load call", re.compile(r"\byaml\.unsafe_load\s*\(")),
    (
        "yaml.load without SafeLoader",
        re.compile(r"\byaml\.load\s*\((?![^)]*(?:SafeLoader|CSafeLoader))[^)]*\)"),
    ),
    (
        "torch.load without weights_only=True",
        re.compile(r"\btorch\.load\s*\((?![^)]*weights_only\s*=\s*True)[^)]*\)"),
    ),
    (
        "Stdlib ElementTree XML parser (XXE risk on untrusted XML)",
        re.compile(r"\bxml\.etree\.ElementTree\.(?:parse|fromstring)\s*\("),
    ),
)

_CRYPTO_TLS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Weak AES ECB mode", re.compile(r"\bAES\.MODE_ECB\b")),
    ("Deprecated Node crypto createCipher", re.compile(r"\bcrypto\.create[C]ipher\b")),
    ("TLS verification disabled via verify False", re.compile(r"\bverify\s*[=]\s*False\b")),
    ("TLS verification disabled via rejectUnauthorized false", re.compile(r"\brejectUnauthorized\s*[:]\s*false\b")),
    ("TLS verification disabled via InsecureSkipVerify true", re.compile(r"\bInsecureSkipVerify\s*[:]\s*true\b")),
    ("Unverified SSL context", re.compile(r"\bssl\._create_unverified_context\b")),
)

_METADATA_IP_RE = re.compile(r"(?<![\\\d.])169\.254\.169\.254(?![\d.])")
_CSRF_COOKIE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("CSRF protection disabled via csrf_exempt", re.compile(r"@csrf[_]exempt\b")),
    ("Cookie httpOnly disabled", re.compile(r"\bhttpOnly\s*[:]\s*false\b", re.IGNORECASE)),
    ("Cookie httponly disabled", re.compile(r"\bhttponly\s*[=]\s*False\b")),
)

_SCRIPT_NO_SRI_RE = re.compile(
    r"""<script\b(?![^>]*\bintegrity\s*=)[^>]*\bsrc\s*=\s*(['"])https?://[^'"]+\1[^>]*>""",
    re.IGNORECASE,
)
_GHA_EXPR_IN_RUN_RE = re.compile(
    r"""\$\{\{\s*(?:github\.head_ref|github\.event\.(?:issue\.title|issue\.body|pull_request\.title|pull_request\.body|pull_request\.head\.(?:ref|label)|comment\.body|review\.body|discussion\.(?:title|body)|head_ref|commits|client_payload\.))"""
)
_GHA_MUTABLE_USES_RE = re.compile(
    r"""^\s*(?:-\s*)?uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)@([^\s#]+)"""
)
_HEX40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    cwe: str
    file: str
    line: int
    message: str
    snippet: str


def _redact_secret(text: str) -> str:
    """Redact secret-like literals so raw credentials are never emitted."""
    redacted = text
    for _, pat in _KNOWN_SECRET_PATTERNS:
        redacted = pat.sub("***REDACTED***", redacted)

    def _sub_env_fb(m: re.Match[str]) -> str:
        key_str, quote, val = m.group(3), m.group(4), m.group(5)
        if _ENV_SECRET_KEY_RE.search(key_str) and val.lower() not in _SAFE_SECRET_PLACEHOLDERS:
            return f"{m.group(1)}{quote}***REDACTED***{quote}{m.group(6)}"
        return m.group(0)

    def _sub_assign(m: re.Match[str]) -> str:
        quote, val = m.group(1), m.group(2)
        if (quote == "`" and "${" in val) or val.lower() in _SAFE_SECRET_PLACEHOLDERS:
            return m.group(0)
        lhs = m.group(0).split("=")[0].split(":")[0].strip()
        return f"{lhs}=***REDACTED***"

    redacted = _ENV_FALLBACK_RE.sub(_sub_env_fb, redacted)
    redacted = _SECRET_ASSIGN_RE.sub(_sub_assign, redacted)
    return redacted.strip()[:160]


def _is_comment_only(line: str, ext: str) -> bool:
    s = line.lstrip()
    if ext in PY_EXTENSIONS or ext in {".yml", ".yaml"}:
        return s.startswith("#")
    if ext in JS_EXTENSIONS:
        return s.startswith("//") or s.startswith("/*") or s.startswith("*")
    return False


_JS_REGEX_PREV_CHARS = frozenset("=([,:;!?&|^~+-*%>{}\n")
_JS_REGEX_PREV_WORDS = frozenset(
    {"return", "case", "throw", "typeof", "void", "delete", "in", "instanceof", "new", "await", "yield"}
)


def _strip_js_comments(raw: str) -> str:
    """Strip // and /* */ comments while preserving strings, template literals, and exact line numbers."""
    out: list[str] = []
    n = len(raw)
    i = 0
    prev_non_ws = "\n"
    prev_word = ""

    while i < n:
        ch = raw[i]

        # String or template literal
        if ch in ("'", '"', "`"):
            quote = ch
            out.append(ch)
            i += 1
            while i < n:
                c = raw[i]
                out.append(c)
                if c == "\\" and i + 1 < n:
                    out.append(raw[i + 1])
                    i += 2
                    continue
                if c == quote:
                    i += 1
                    break
                i += 1
            prev_non_ws = quote
            prev_word = ""
            continue

        # Line comment //
        if ch == "/" and i + 1 < n and raw[i + 1] == "/":
            out.append("  ")
            i += 2
            while i < n and raw[i] != "\n":
                out.append(" ")
                i += 1
            continue

        # Block comment /* ... */
        if ch == "/" and i + 1 < n and raw[i + 1] == "*":
            out.append("  ")
            i += 2
            while i < n:
                if raw[i] == "*" and i + 1 < n and raw[i + 1] == "/":
                    out.append("  ")
                    i += 2
                    break
                out.append("\n" if raw[i] == "\n" else " ")
                i += 1
            continue

        # Regex literal /.../ (avoiding JSX </tag> and />)
        if (
            ch == "/"
            and prev_non_ws != "<"
            and (i + 1 >= n or raw[i + 1] not in ("/", "*", ">"))
            and (prev_non_ws in _JS_REGEX_PREV_CHARS or prev_word in _JS_REGEX_PREV_WORDS)
        ):
            out.append(ch)
            i += 1
            in_class = False
            while i < n:
                c = raw[i]
                if c == "\n":
                    out.append(c)
                    i += 1
                    break
                out.append(c)
                if c == "\\" and i + 1 < n and raw[i + 1] != "\n":
                    out.append(raw[i + 1])
                    i += 2
                    continue
                if c == "[":
                    in_class = True
                elif c == "]" and in_class:
                    in_class = False
                elif c == "/" and not in_class:
                    i += 1
                    break
                i += 1
            prev_non_ws = "/"
            prev_word = ""
            continue

        out.append(ch)
        if not ch.isspace():
            if ch.isalnum() or ch in ("_", "$"):
                prev_word = prev_word + ch if (prev_non_ws.isalnum() or prev_non_ws in ("_", "$")) else ch
            else:
                prev_word = ""
            prev_non_ws = ch
        elif ch == "\n" and prev_non_ws == "\n":
            prev_word = ""
        i += 1

    return "".join(out)


def _strip_html_comments(raw: str) -> str:
    """Strip <!-- ... --> comments while preserving exact newline count."""
    return _HTML_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), raw)


def _find_matching_paren(text: str, open_idx: int) -> int:
    """Return index of matching ')' for '(' at open_idx, or -1 if unbalanced."""
    depth = 0
    n = len(text)
    i = open_idx
    while i < n:
        c = text[i]
        if c in ("'", '"', "`"):
            q = c
            i += 1
            while i < n:
                if text[i] == "\\" and i + 1 < n:
                    i += 2
                    continue
                if text[i] == q:
                    break
                i += 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _is_dompurify_sanitized_sink(stripped_line: str, sink_match: re.Match[str]) -> bool:
    """Return True only when sink directly assigns/inserts balanced DOMPurify.sanitize(...) with no '+' concat."""
    matched = sink_match.group(0)
    tail = stripped_line[sink_match.end() :]
    if matched.startswith(".") and ("innerHTML" in matched or "outerHTML" in matched):
        rhs = tail.lstrip()
        dp_m = re.match(r"DOMPurify\.sanitize\s*\(", rhs)
        if not dp_m:
            return False
        close_idx = _find_matching_paren(rhs, dp_m.end() - 1)
        if close_idx < 0:
            return False
        rem = rhs[close_idx + 1 :].strip()
        return not rem.startswith("+")

    if ".insertAdjacentHTML" in matched:
        # Find top-level comma separating position and HTML argument
        depth = 0
        i = 0
        comma_idx = -1
        while i < len(tail):
            c = tail[i]
            if c in ("'", '"', "`"):
                q = c
                i += 1
                while i < len(tail):
                    if tail[i] == "\\" and i + 1 < len(tail):
                        i += 2
                        continue
                    if tail[i] == q:
                        break
                    i += 1
            elif c in ("(", "[", "{"):
                depth += 1
            elif c in (")", "]", "}"):
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                comma_idx = i
                break
            i += 1
        if comma_idx < 0:
            return False
        arg2 = tail[comma_idx + 1 :].lstrip()
        dp_m = re.match(r"DOMPurify\.sanitize\s*\(", arg2)
        if not dp_m:
            return False
        close_idx = _find_matching_paren(arg2, dp_m.end() - 1)
        if close_idx < 0:
            return False
        rem = arg2[close_idx + 1 :].lstrip()
        return rem.startswith(")")

    return False


def _is_env_secret_file(path: Path) -> bool:
    name = path.name.lower()
    if not name.startswith(".env"):
        return False
    return name not in {".env.example", ".env.sample", ".env.template", ".env.dist"}


def _is_dep_manifest(path: Path) -> bool:
    name = path.name.lower()
    return name == "package.json" or (name.startswith("requirements") and name.endswith(".txt"))


def _should_scan_file(path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    if _is_env_secret_file(path) or _is_dep_manifest(path):
        return True
    return path.suffix.lower() in SCANNABLE_EXTENSIONS


def iter_target_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if _should_scan_file(target) else []
    files: list[Path] = []
    for root, dirs, filenames in os.walk(target):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        root_path = Path(root)
        for fname in sorted(filenames):
            p = root_path / fname
            if _should_scan_file(p):
                files.append(p)
    return files


def _resolve_attr_chain(
    node: ast.AST | None,
    aliases: dict[str, str],
    imported_syms: dict[str, str],
) -> str:
    """Resolve an AST Name/Attribute chain using module aliases and imported symbols."""
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return imported_syms.get(node.id, aliases.get(node.id, node.id))
    parts: list[str] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        root = imported_syms.get(cur.id, aliases.get(cur.id, cur.id))
        parts.append(root)
        return ".".join(reversed(parts))
    return ""


def _flatten_add(node: ast.AST, visited_adds: set[int]) -> list[ast.AST]:
    """Flatten nested AST Add binary operations in left-to-right order."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        visited_adds.add(id(node))
        return _flatten_add(node.left, visited_adds) + _flatten_add(node.right, visited_adds)
    return [node]


def _scan_python_ast(
    raw: str,
    lines: list[str],
    add: Callable[[str, str, str, int, str, str], None],
) -> bool:
    """Analyze Python source via stdlib AST. Returns False on SyntaxError for regex fallback."""
    try:
        tree = ast.parse(raw)
    except (SyntaxError, ValueError, RecursionError):
        return False

    def line_at(lineno: int) -> str:
        return lines[lineno - 1] if 1 <= lineno <= len(lines) else ""

    aliases: dict[str, str] = {}
    imported_syms: dict[str, str] = {}
    rhs_targets: dict[int, set[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                aliases[bound] = alias.name if alias.asname else bound
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound = alias.asname or alias.name
                imported_syms[bound] = f"{mod}.{alias.name}" if mod else alias.name
        elif isinstance(node, ast.Assign):
            names: set[str] = set()
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
                elif isinstance(t, ast.Attribute):
                    names.add(t.attr)
            if names:
                rhs_targets.setdefault(id(node.value), set()).update(names)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if isinstance(node.target, ast.Name):
                rhs_targets.setdefault(id(node.value), set()).add(node.target.id)
            elif isinstance(node.target, ast.Attribute):
                rhs_targets.setdefault(id(node.value), set()).add(node.target.attr)

    cors_wildcard_hits: list[tuple[int, str]] = []
    has_cors_credentials = False
    visited_adds: set[int] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                dec_name = _resolve_attr_chain(dec, aliases, imported_syms)
                if dec_name == "csrf_exempt" or dec_name.endswith(".csrf_exempt"):
                    d_line = getattr(dec, "lineno", node.lineno)
                    add(
                        "SEC-COOKIE-CSRF-001",
                        "medium",
                        "CWE-352",
                        d_line,
                        "CSRF protection disabled via csrf_exempt",
                        line_at(d_line),
                    )

        elif isinstance(node, ast.Call):
            fname = _resolve_attr_chain(node.func, aliases, imported_syms)

            # Execution sinks
            if (isinstance(node.func, ast.Name) and node.func.id == "eval") or fname == "builtins.eval":
                add(
                    "SEC-EXEC-001",
                    "critical",
                    "CWE-78",
                    node.lineno,
                    "Dangerous execution sink: Dynamic eval call",
                    line_at(node.lineno),
                )
            elif fname == "os.system":
                add(
                    "SEC-EXEC-001",
                    "critical",
                    "CWE-78",
                    node.lineno,
                    "Dangerous execution sink: os.system command execution",
                    line_at(node.lineno),
                )
            elif fname in {
                "subprocess.run",
                "subprocess.call",
                "subprocess.Popen",
                "subprocess.check_output",
                "subprocess.check_call",
            }:
                if any(
                    kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True
                    for kw in node.keywords
                ):
                    add(
                        "SEC-EXEC-001",
                        "critical",
                        "CWE-78",
                        node.lineno,
                        "Dangerous execution sink: subprocess with shell=True",
                        line_at(node.lineno),
                    )

            # Deserialization & XML sinks
            elif fname == "yaml.load":
                loader_node: ast.AST | None = None
                for kw in node.keywords:
                    if kw.arg == "Loader":
                        loader_node = kw.value
                        break
                if loader_node is None and len(node.args) >= 2:
                    loader_node = node.args[1]
                loader_name = (
                    _resolve_attr_chain(loader_node, aliases, imported_syms)
                    if loader_node is not None
                    else ""
                )
                if loader_name not in {"yaml.SafeLoader", "yaml.CSafeLoader", "SafeLoader", "CSafeLoader"}:
                    add(
                        "SEC-DESER-001",
                        "high",
                        "CWE-502",
                        node.lineno,
                        "yaml.load without SafeLoader",
                        line_at(node.lineno),
                    )
            elif fname == "yaml.unsafe_load":
                add(
                    "SEC-DESER-001",
                    "high",
                    "CWE-502",
                    node.lineno,
                    "Unsafe yaml.unsafe_load call",
                    line_at(node.lineno),
                )
            elif fname in {
                "pickle.load",
                "pickle.loads",
                "pickle.Unpickler",
                "cPickle.load",
                "cPickle.loads",
                "cPickle.Unpickler",
            }:
                add(
                    "SEC-DESER-001",
                    "high",
                    "CWE-502",
                    node.lineno,
                    "Unsafe Python pickle deserialization",
                    line_at(node.lineno),
                )
            elif fname in {"marshal.load", "marshal.loads"}:
                add(
                    "SEC-DESER-001",
                    "high",
                    "CWE-502",
                    node.lineno,
                    "Unsafe marshal deserialization",
                    line_at(node.lineno),
                )
            elif fname == "torch.load":
                if not any(
                    kw.arg == "weights_only"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                    for kw in node.keywords
                ):
                    add(
                        "SEC-DESER-001",
                        "high",
                        "CWE-502",
                        node.lineno,
                        "torch.load without weights_only=True",
                        line_at(node.lineno),
                    )
            elif fname in {"xml.etree.ElementTree.parse", "xml.etree.ElementTree.fromstring"}:
                add(
                    "SEC-DESER-001",
                    "high",
                    "CWE-502",
                    node.lineno,
                    "Stdlib ElementTree XML parser (XXE risk on untrusted XML)",
                    line_at(node.lineno),
                )

            # os.getenv / os.environ.get fallback secret literals
            elif fname in {"os.getenv", "os.environ.get", "os.environ.setdefault"}:
                key_node = node.args[0] if node.args else None
                default_node: ast.AST | None = node.args[1] if len(node.args) >= 2 else None
                if default_node is None:
                    for kw in node.keywords:
                        if kw.arg == "default":
                            default_node = kw.value
                            break
                if (
                    isinstance(key_node, ast.Constant)
                    and isinstance(key_node.value, str)
                    and isinstance(default_node, ast.Constant)
                    and isinstance(default_node.value, str)
                ):
                    key_str = key_node.value
                    val_str = default_node.value
                    target_names = rhs_targets.get(id(node), set())
                    sensitive = bool(_ENV_SECRET_KEY_RE.search(key_str)) or any(
                        bool(_SECRET_NAME_RE.match(tn) or _ENV_SECRET_KEY_RE.search(tn))
                        for tn in target_names
                    )
                    if (
                        sensitive
                        and len(val_str) >= 4
                        and val_str.lower() not in _SAFE_SECRET_PLACEHOLDERS
                        and not val_str.startswith(("<", "${", "{{"))
                        and not any(pat.search(val_str) for _, pat in _KNOWN_SECRET_PATTERNS)
                    ):
                        add(
                            "SEC-SECRET-001",
                            "critical",
                            "CWE-798",
                            node.lineno,
                            f"Hardcoded fallback secret in {fname}({key_str!r})",
                            f'{fname}("{key_str}", "***REDACTED***")',
                        )

            # .format() SQLi
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "format"
                and isinstance(node.func.value, ast.Constant)
                and isinstance(node.func.value.value, str)
                and _SQL_KEYWORDS_MULTILINE_RE.search(node.func.value.value)
            ):
                add(
                    "SEC-SQLI-001",
                    "high",
                    "CWE-89",
                    node.lineno,
                    "Dynamic SQL string interpolation/concatenation (use parameterized queries)",
                    line_at(node.lineno),
                )

            # Keyword-level flags: verify=False, httponly=False, allow_origins, allow_credentials
            for kw in node.keywords:
                kw_line = getattr(kw, "lineno", node.lineno)
                if kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    add(
                        "SEC-CRYPTO-001",
                        "medium",
                        "CWE-327",
                        kw_line,
                        "TLS verification disabled via verify False",
                        line_at(kw_line),
                    )
                elif kw.arg == "httponly" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    add(
                        "SEC-COOKIE-CSRF-001",
                        "medium",
                        "CWE-352",
                        kw_line,
                        "Cookie httponly disabled",
                        line_at(kw_line),
                    )
                elif kw.arg == "allow_origins":
                    if isinstance(kw.value, ast.Constant) and kw.value.value == "*":
                        cors_wildcard_hits.append((kw_line, line_at(kw_line)))
                    elif isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
                        if any(
                            isinstance(elt, ast.Constant) and elt.value == "*"
                            for elt in kw.value.elts
                        ):
                            cors_wildcard_hits.append((kw_line, line_at(kw_line)))
                elif kw.arg == "allow_credentials" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    has_cors_credentials = True

        elif isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            has_expr = False
            for val_node in node.values:
                if isinstance(val_node, ast.Constant) and isinstance(val_node.value, str):
                    parts.append(val_node.value)
                elif isinstance(val_node, ast.FormattedValue):
                    has_expr = True
                    parts.append("{__AST_EXPR__}")
            if has_expr and _SQL_KEYWORDS_MULTILINE_RE.search("".join(parts)):
                add(
                    "SEC-SQLI-001",
                    "high",
                    "CWE-89",
                    node.lineno,
                    "Dynamic SQL string interpolation/concatenation (use parameterized queries)",
                    line_at(node.lineno),
                )

        elif isinstance(node, ast.BinOp):
            if (
                isinstance(node.op, ast.Mod)
                and isinstance(node.left, ast.Constant)
                and isinstance(node.left.value, str)
                and _SQL_KEYWORDS_MULTILINE_RE.search(node.left.value)
            ):
                add(
                    "SEC-SQLI-001",
                    "high",
                    "CWE-89",
                    node.lineno,
                    "Dynamic SQL string interpolation/concatenation (use parameterized queries)",
                    line_at(node.lineno),
                )
            elif isinstance(node.op, ast.Add) and id(node) not in visited_adds:
                add_parts = _flatten_add(node, visited_adds)
                str_parts = [
                    p.value
                    for p in add_parts
                    if isinstance(p, ast.Constant) and isinstance(p.value, str)
                ]
                has_non_const = any(not isinstance(p, ast.Constant) for p in add_parts)
                if has_non_const and str_parts and _SQL_KEYWORDS_MULTILINE_RE.search(" ".join(str_parts)):
                    add(
                        "SEC-SQLI-001",
                        "high",
                        "CWE-89",
                        node.lineno,
                        "Dynamic SQL string interpolation/concatenation (use parameterized queries)",
                        line_at(node.lineno),
                    )

        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            val_node = node.value
            if val_node is not None:
                for t in targets:
                    if isinstance(t, ast.Subscript):
                        sl = t.slice
                        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                            k_low = sl.value.lower()
                            if (
                                k_low == "access-control-allow-origin"
                                and isinstance(val_node, ast.Constant)
                                and val_node.value == "*"
                            ):
                                cors_wildcard_hits.append((node.lineno, line_at(node.lineno)))
                            elif (
                                k_low == "access-control-allow-credentials"
                                and isinstance(val_node, ast.Constant)
                                and str(val_node.value).lower() == "true"
                            ):
                                has_cors_credentials = True
                        continue

                    tname = t.id if isinstance(t, ast.Name) else (t.attr if isinstance(t, ast.Attribute) else "")
                    if (
                        tname
                        and _SECRET_NAME_RE.match(tname)
                        and isinstance(val_node, ast.Constant)
                        and isinstance(val_node.value, str)
                    ):
                        sval = val_node.value
                        if (
                            len(sval) >= 8
                            and not any(c.isspace() for c in sval)
                            and sval.lower() not in _SAFE_SECRET_PLACEHOLDERS
                            and not sval.startswith(("<", "${", "{{", "os.environ", "process.env"))
                            and not any(pat.search(sval) for _, pat in _KNOWN_SECRET_PATTERNS)
                        ):
                            add(
                                "SEC-SECRET-001",
                                "critical",
                                "CWE-798",
                                node.lineno,
                                "Hardcoded secret literal assignment detected",
                                line_at(node.lineno),
                            )

        elif isinstance(node, ast.Dict):
            for k_node, v_node in zip(node.keys, node.values):
                if isinstance(k_node, ast.Constant) and isinstance(k_node.value, str):
                    k_low = k_node.value.lower()
                    if (
                        k_low == "access-control-allow-origin"
                        and isinstance(v_node, ast.Constant)
                        and isinstance(v_node.value, str)
                        and v_node.value.strip() == "*"
                    ):
                        cors_wildcard_hits.append((k_node.lineno, line_at(k_node.lineno)))
                    elif (
                        k_low == "access-control-allow-credentials"
                        and isinstance(v_node, ast.Constant)
                        and (v_node.value is True or str(v_node.value).strip().lower() == "true")
                    ):
                        has_cors_credentials = True

        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            sval = node.value
            start_ln = node.lineno
            end_ln = getattr(node, "end_lineno", start_ln) or start_ln
            for label, pat in _KNOWN_SECRET_PATTERNS:
                if pat.search(sval):
                    hit_ln = start_ln
                    for ln in range(start_ln, min(end_ln, len(lines)) + 1):
                        if pat.search(lines[ln - 1]):
                            hit_ln = ln
                            break
                    add(
                        "SEC-SECRET-001",
                        "critical",
                        "CWE-798",
                        hit_ln,
                        f"Hardcoded {label} detected",
                        line_at(hit_ln),
                    )
                    break
            if _METADATA_IP_RE.search(sval):
                hit_ln = start_ln
                for ln in range(start_ln, min(end_ln, len(lines)) + 1):
                    if _METADATA_IP_RE.search(lines[ln - 1]):
                        hit_ln = ln
                        break
                add(
                    "SEC-SSRF-001",
                    "high",
                    "CWE-918",
                    hit_ln,
                    "Cloud metadata endpoint IP literal detected (SSRF target)",
                    line_at(hit_ln),
                )

        elif isinstance(node, ast.Attribute):
            attr_name = _resolve_attr_chain(node, aliases, imported_syms)
            if attr_name == "AES.MODE_ECB" or attr_name.endswith(".AES.MODE_ECB"):
                add(
                    "SEC-CRYPTO-001",
                    "medium",
                    "CWE-327",
                    node.lineno,
                    "Weak AES ECB mode",
                    line_at(node.lineno),
                )
            elif attr_name == "ssl._create_unverified_context":
                add(
                    "SEC-CRYPTO-001",
                    "medium",
                    "CWE-327",
                    node.lineno,
                    "Unverified SSL context",
                    line_at(node.lineno),
                )

    for cors_line, cors_snippet in cors_wildcard_hits:
        if has_cors_credentials:
            add(
                "SEC-CORS-001",
                "high",
                "CWE-942",
                cors_line,
                "Wildcard CORS Access-Control-Allow-Origin '*' combined with credentials=true",
                cors_snippet,
            )
        else:
            add(
                "SEC-CORS-002",
                "medium",
                "CWE-942",
                cors_line,
                "Wildcard CORS origin '*' configured; restrict to explicit origin allowlist",
                cors_snippet,
            )

    return True


def scan_file(path: Path, display_root: Path) -> list[Finding]:
    """Run all deterministic baseline security rules on a single file."""
    try:
        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            return []
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        rel_path = str(path.resolve().relative_to(display_root.resolve()))
    except ValueError:
        rel_path = str(path)

    ext = path.suffix.lower()
    lines = raw.splitlines()
    findings: list[Finding] = []

    def add(rule_id: str, severity: str, cwe: str, lineno: int, msg: str, line_text: str) -> None:
        findings.append(
            Finding(
                rule_id=rule_id,
                severity=severity,
                cwe=cwe,
                file=rel_path,
                line=lineno,
                message=msg,
                snippet=_redact_secret(line_text),
            )
        )

    # 1. Committed .env file check
    if _is_env_secret_file(path):
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, val = stripped.split("=", 1)
            key_clean = key.strip()
            val_clean = val.strip().strip("'\"")
            if not val_clean:
                continue
            known_hit = False
            for label, pat in _KNOWN_SECRET_PATTERNS:
                if pat.search(val_clean):
                    add(
                        "SEC-SECRET-001",
                        "critical",
                        "CWE-798",
                        idx,
                        f"Hardcoded {label} detected in .env ({key_clean})",
                        f"{key_clean}=***REDACTED***",
                    )
                    known_hit = True
                    break
            if not known_hit and _ENV_SECRET_KEY_RE.search(key_clean):
                add(
                    "SEC-CONFIG-001",
                    "high",
                    "CWE-798",
                    idx,
                    f"Committed non-example .env secret entry for {key_clean}",
                    f"{key_clean}=***REDACTED***",
                )
        return findings

    # 1b. Python AST analysis (falls back to regex scan on SyntaxError)
    if ext in PY_EXTENSIONS:
        if _scan_python_ast(raw, lines, add):
            return findings

    # 2. Dependency manifest unpinned wildcard / latest checks
    if path.name.lower().startswith("requirements") and ext == ".txt":
        for idx, line in enumerate(lines, start=1):
            s = line.strip()
            if s and not s.startswith("#") and ("==*" in s or re.fullmatch(r"[A-Za-z0-9_.-]+", s)):
                add(
                    "SEC-DEP-001",
                    "medium",
                    "CWE-1104",
                    idx,
                    "Unpinned Python dependency in requirements file (pin exact version + hashes)",
                    line,
                )
    elif path.name.lower() == "package.json":
        try:
            pkg = json.loads(raw)
        except json.JSONDecodeError:
            pkg = {}
        if isinstance(pkg, dict):
            for section in ("dependencies", "devDependencies", "optionalDependencies"):
                deps = pkg.get(section)
                if isinstance(deps, dict):
                    for dep_name, ver in deps.items():
                        if isinstance(ver, str) and ver.strip() in {"*", "latest", ""}:
                            add(
                                "SEC-DEP-001",
                                "medium",
                                "CWE-1104",
                                1,
                                f"Unpinned npm dependency {dep_name!r} ({ver!r}) in {section}",
                                f'"{dep_name}": "{ver}"',
                            )

    # 3. GitHub Actions workflow hardening checks
    is_workflow = (".github" in path.parts and "workflows" in path.parts) or (
        ext in {".yml", ".yaml"} and "\njobs:" in raw and "\nsteps:" in raw
    )
    if is_workflow:
        in_run_block = False
        run_indent = 0
        for idx, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if re.match(r"^(?:-\s*)?run:\s*", stripped):
                in_run_block = stripped.rstrip().endswith(("|", "|-", ">", ">-"))
                run_indent = indent
                if _GHA_EXPR_IN_RUN_RE.search(line):
                    add(
                        "SEC-CONFIG-001",
                        "high",
                        "CWE-94",
                        idx,
                        "Untrusted github.event expression interpolated directly in workflow run:",
                        line,
                    )
            elif in_run_block:
                if stripped and indent <= run_indent:
                    in_run_block = False
                elif _GHA_EXPR_IN_RUN_RE.search(line):
                    add(
                        "SEC-CONFIG-001",
                        "high",
                        "CWE-94",
                        idx,
                        "Untrusted github.event expression interpolated inside multiline run: block",
                        line,
                    )

            uses_m = _GHA_MUTABLE_USES_RE.match(line)
            if uses_m:
                action_ref, ref_ver = uses_m.group(1), uses_m.group(2)
                if not action_ref.startswith("./") and not _HEX40_RE.match(ref_ver):
                    add(
                        "SEC-CONFIG-001",
                        "medium",
                        "CWE-829",
                        idx,
                        f"GitHub Action {action_ref}@{ref_ver} uses mutable ref instead of 40-hex commit SHA",
                        line,
                    )

    # Strip JS/HTML comments while keeping 1:1 line numbering
    if ext in JS_EXTENSIONS:
        scan_raw = _strip_js_comments(raw)
    elif ext in {".html", ".htm"}:
        scan_raw = _strip_html_comments(raw)
    else:
        scan_raw = raw
    scan_lines = scan_raw.splitlines()

    # 4. File-level CORS wildcard + credentials pairing
    if ext in CODE_EXTENSIONS:
        origin_matches = list(_CORS_ORIGIN_WILDCARD_RE.finditer(scan_raw))
        if origin_matches:
            has_creds_true = bool(_CORS_CREDENTIALS_TRUE_RE.search(scan_raw))
            for m in origin_matches:
                lineno = scan_raw.count("\n", 0, m.start()) + 1
                snippet_line = lines[lineno - 1] if lineno - 1 < len(lines) else m.group(0)
                if has_creds_true:
                    add(
                        "SEC-CORS-001",
                        "high",
                        "CWE-942",
                        lineno,
                        "Wildcard CORS Access-Control-Allow-Origin '*' combined with credentials=true",
                        snippet_line,
                    )
                else:
                    add(
                        "SEC-CORS-002",
                        "medium",
                        "CWE-942",
                        lineno,
                        "Wildcard CORS origin '*' configured; restrict to explicit origin allowlist",
                        snippet_line,
                    )

    # 4b. Multiline JS/TS SQL template literals
    if ext in JS_EXTENSIONS:
        for bt_m in _JS_BACKTICK_SPAN_RE.finditer(scan_raw):
            span_text = bt_m.group(0)
            if _JS_INTERP_RE.search(span_text) and _SQL_KEYWORDS_MULTILINE_RE.search(span_text):
                lineno = scan_raw.count("\n", 0, bt_m.start()) + 1
                snippet_line = lines[lineno - 1] if lineno - 1 < len(lines) else span_text
                add(
                    "SEC-SQLI-001",
                    "high",
                    "CWE-89",
                    lineno,
                    "Dynamic SQL template/concatenation (use parameterized queries)",
                    snippet_line,
                )

    # 5. Line-by-line code & HTML checks
    for idx, scan_line in enumerate(scan_lines, start=1):
        orig_line = lines[idx - 1] if idx - 1 < len(lines) else scan_line
        if _is_comment_only(scan_line, ext) or not scan_line.strip():
            continue

        # Hardcoded known key prefixes
        secret_hit = False
        for label, pat in _KNOWN_SECRET_PATTERNS:
            if pat.search(scan_line):
                add("SEC-SECRET-001", "critical", "CWE-798", idx, f"Hardcoded {label} detected", orig_line)
                secret_hit = True
                break

        if not secret_hit:
            assign_m = _SECRET_ASSIGN_RE.search(scan_line)
            if assign_m:
                quote, val = assign_m.group(1), assign_m.group(2)
                if (
                    not (quote == "`" and "${" in val)
                    and val.lower() not in _SAFE_SECRET_PLACEHOLDERS
                    and not val.startswith(("<", "${", "{{", "os.environ", "process.env"))
                ):
                    add(
                        "SEC-SECRET-001",
                        "critical",
                        "CWE-798",
                        idx,
                        "Hardcoded secret literal assignment detected",
                        orig_line,
                    )

        # Fallback secret in regex mode (Python SyntaxError fallback)
        if ext in PY_EXTENSIONS:
            fb_m = _ENV_FALLBACK_RE.search(scan_line)
            if fb_m:
                key_str, val_str = fb_m.group(3), fb_m.group(5)
                if (
                    _ENV_SECRET_KEY_RE.search(key_str)
                    and len(val_str) >= 4
                    and val_str.lower() not in _SAFE_SECRET_PLACEHOLDERS
                    and not val_str.startswith(("<", "${", "{{"))
                ):
                    add(
                        "SEC-SECRET-001",
                        "critical",
                        "CWE-798",
                        idx,
                        f"Hardcoded fallback secret for {key_str!r}",
                        orig_line,
                    )

        # HTML / JSX checks
        if ext in JS_EXTENSIONS or ext in {".html", ".htm"}:
            if _DANGEROUS_INNER_HTML_RE.search(scan_line):
                window_text = "\n".join(scan_lines[max(0, idx - 2) : min(len(scan_lines), idx + 2)])
                if not _DOMPURIFY_RE.search(window_text):
                    add(
                        "SEC-XSS-001",
                        "high",
                        "CWE-79",
                        idx,
                        "Unsanitized dangerouslySetInnerHTML without DOMPurify.sanitize()",
                        orig_line,
                    )
            sink_m = _DOM_SINKS_RE.search(scan_line)
            if sink_m and not _is_dompurify_sanitized_sink(scan_line, sink_m):
                add("SEC-XSS-001", "high", "CWE-79", idx, "Unsafe raw HTML DOM sink detected", orig_line)
            if _SCRIPT_NO_SRI_RE.search(scan_line):
                add(
                    "SEC-CONFIG-001",
                    "medium",
                    "CWE-353",
                    idx,
                    "External <script src=...> missing Subresource Integrity (integrity=)",
                    orig_line,
                )

        if ext not in CODE_EXTENSIONS:
            continue

        # SQL injection formatting/concatenation
        if ext in PY_EXTENSIONS:
            if (
                _PY_SQL_FSTRING_RE.search(scan_line)
                or _PY_SQL_FORMAT_RE.search(scan_line)
                or _SQL_CONCAT_RE.search(scan_line)
            ):
                add(
                    "SEC-SQLI-001",
                    "high",
                    "CWE-89",
                    idx,
                    "Dynamic SQL string interpolation/concatenation (use parameterized queries)",
                    orig_line,
                )
        elif ext in JS_EXTENSIONS:
            if _SQL_CONCAT_RE.search(scan_line):
                add(
                    "SEC-SQLI-001",
                    "high",
                    "CWE-89",
                    idx,
                    "Dynamic SQL template/concatenation (use parameterized queries)",
                    orig_line,
                )

        # Web Storage token persistence
        if ext in JS_EXTENSIONS and _WEB_STORAGE_TOKEN_RE.search(scan_line):
            add(
                "SEC-STORAGE-001",
                "high",
                "CWE-922",
                idx,
                "Sensitive auth/session token stored in Web Storage (use HttpOnly __Host- cookie)",
                orig_line,
            )

        # Command / dynamic code execution
        for label, pat in _EXEC_PATTERNS:
            if pat.search(scan_line):
                add("SEC-EXEC-001", "critical", "CWE-78", idx, f"Dangerous execution sink: {label}", orig_line)

        # Unsafe deserialization & XXE
        for label, pat in _DESER_PATTERNS:
            if pat.search(scan_line):
                add("SEC-DESER-001", "high", "CWE-502", idx, label, orig_line)

        # Weak crypto / disabled TLS
        for label, pat in _CRYPTO_TLS_PATTERNS:
            if pat.search(scan_line):
                add("SEC-CRYPTO-001", "medium", "CWE-327", idx, label, orig_line)

        # Cloud metadata IP literal
        if _METADATA_IP_RE.search(scan_line):
            add(
                "SEC-SSRF-001",
                "high",
                "CWE-918",
                idx,
                "Cloud metadata endpoint IP literal detected (SSRF target)",
                orig_line,
            )

        # Cookie / CSRF weaknesses
        for label, pat in _CSRF_COOKIE_PATTERNS:
            if pat.search(scan_line):
                add("SEC-COOKIE-CSRF-001", "medium", "CWE-352", idx, label, orig_line)

    return findings


def _optional_ide_hook(enabled: bool, target: Path, summary: dict[str, int]) -> str:
    """Optionally notify SecureCoder IDE API; silently skip when offline or absent."""
    if not enabled:
        return "skipped_disabled"
    port = os.environ.get("SECURECODER_API_PORT", "").strip()
    if not port:
        api_json = Path.home() / ".securecoder" / "api.json"
        if api_json.is_file():
            try:
                data = json.loads(api_json.read_text(encoding="utf-8"))
                port = str(data.get("port", "")).strip()
            except (OSError, json.JSONDecodeError, AttributeError):
                port = ""
    if not port or not port.isascii() or not port.isdigit():
        return "skipped_offline"
    port_num = int(port)
    if not (1 <= port_num <= 65535):
        return "skipped_offline"
    url = f"http://127.0.0.1:{port_num}/baseline_summary"
    req = urllib.request.Request(
        url,
        data=json.dumps({"target": str(target), "summary": summary}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=1.5):
            return "notified"
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError, ValueError):
        return "skipped_unreachable"


def scan_target(
    target: Path,
    min_severity: str = "low",
    ide_hook: bool = False,
) -> dict[str, object]:
    files = iter_target_files(target)
    display_root = target.parent if target.is_file() else target
    raw_findings: list[Finding] = []
    skipped_large_files: list[str] = []

    for fpath in files:
        try:
            if fpath.stat().st_size > MAX_FILE_SIZE_BYTES:
                try:
                    rel_skip = str(fpath.resolve().relative_to(display_root.resolve()))
                except ValueError:
                    rel_skip = str(fpath)
                skipped_large_files.append(rel_skip)
                continue
        except OSError:
            continue
        raw_findings.extend(scan_file(fpath, display_root))

    # Deduplicate deterministically and sort by severity desc, file, line, rule_id
    deduped = {
        (f.rule_id, f.file, f.line, f.message): f
        for f in raw_findings
    }
    ordered = sorted(
        deduped.values(),
        key=lambda f: (-SEVERITY_ORDER[f.severity], f.file, f.line, f.rule_id),
    )

    counts = {
        "critical": sum(1 for f in ordered if f.severity == "critical"),
        "high": sum(1 for f in ordered if f.severity == "high"),
        "medium": sum(1 for f in ordered if f.severity == "medium"),
        "low": sum(1 for f in ordered if f.severity == "low"),
        "total": len(ordered),
    }
    threshold = SEVERITY_ORDER[min_severity]
    failing = [f for f in ordered if SEVERITY_ORDER[f.severity] >= threshold]
    status = "FAIL" if failing else "PASS"
    hook_state = _optional_ide_hook(ide_hook, target, counts)

    return {
        "status": status,
        "target": str(target),
        "severity_threshold": min_severity,
        "scanned_files": len(files) - len(skipped_large_files),
        "skipped_large_files": sorted(skipped_large_files),
        "summary": counts,
        "ide_hook": hook_state,
        "findings": [asdict(f) for f in ordered],
    }


def run_self_test() -> int:
    """Run embedded positive and negative checks in an isolated temp directory."""
    with tempfile.TemporaryDirectory(prefix="sec_baseline_selftest_") as tmp:
        root = Path(tmp)
        vuln_dir = root / "vuln"
        clean_dir = root / "clean"
        vuln_dir.mkdir()
        clean_dir.mkdir()

        # Construct test payloads dynamically so static scans of this script stay clean
        sk_val = "sk_" + "live_9876543210abcdef1234567890"
        sk_val2 = "sk_" + "live_abcdef9876543210abcdef1234"
        fb_secret = "dev-fb-" + "secret-1234"
        js_bt_secret = "MyVery" + "SecretToken12345"
        api_key_name = "API_" + "SECRET"
        cors_origin_hdr = "Access-Control-Allow-" + "Origin"
        cors_creds_hdr = "Access-Control-Allow-" + "Credentials"
        sel_kw = "SEL" + "ECT"
        os_sys_call = "os." + "system"

        vuln_py = (
            "import os, subprocess, yaml\n"
            f'{api_key_name} = "{sk_val}"\n'
            f'FALLBACK_KEY = os.getenv("JWT_SECRET", "{fb_secret}")\n'
            "def q(cur, uid):\n"
            f'    cur.execute(f"{sel_kw} id FROM users WHERE id = \'{{uid}}\'")\n'
            f'    cur.execute(f"""\n{sel_kw} id\nFROM users\nWHERE id = \'{{uid}}\'\n""")\n'
            "    subprocess.run(build_cmd(), shell=True)\n"
            "    data = yaml.load(\n        raw,\n    )\n"
            "    app.add_middleware(\n"
            "        CORSMiddleware,\n"
            '        allow_origins=["https://app.example.com", "*"],\n'
            "        allow_credentials=True,\n"
            "    )\n"
            f'    return {{"{cors_origin_hdr}": "*", "{cors_creds_hdr}": "true"}}\n'
        )
        vuln_syntax_py = f"def broken(:\n    {os_sys_call}('id')\n"
        vuln_tsx = (
            "export function Bad({ t, h }: { t: string; h: string }) {\n"
            '  localStorage.setItem("access_token", t);\n'
            "  // TODO: maybe use DOMPurify.sanitize(h) later\n"
            "  return <div dangerouslySetInnerHTML={{ __html: h }} />;\n"
            "}\n"
        )
        vuln_ts = (
            f"export const {api_key_name} = `{js_bt_secret}`;\n"
            f"const q = `\n  {sel_kw} id\n  FROM users\n  WHERE id = ${{uid}}\n`;\n"
            "export function corsHandler(res: any) {\n"
            f'  res.setHeader("{cors_origin_hdr}", "*");\n'
            "}\n"
        )
        vuln_env = f"STRIPE_AUTH={sk_val2}\n"

        vuln_wf = vuln_dir / ".github" / "workflows"
        vuln_wf.mkdir(parents=True)
        wf_text = (
            "on: [pull_request]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            '      - run: echo "${{ github.event.pull_request.title }}"\n'
            '      - run: echo "${{ github.head_ref }}"\n'
        )

        clean_py = (
            "import os, yaml\n"
            "def get_secret():\n"
            '    return os.environ["APP_API_SECRET"]\n'
            'LOG_LEVEL = os.getenv("LOG_LEVEL", "info")\n'
            'MSG = "Never call eval() on untrusted input"\n'
            'cfg = yaml.load(open("a.yml"), Loader=yaml.SafeLoader)\n'
            "def q(cur, uid, origin):\n"
            f'    cur.execute("{sel_kw} id FROM users WHERE id = %s", (uid,))\n'
            '    return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}\n'
        )
        clean_tsx = (
            'import DOMPurify from "dompurify";\n'
            f"const {api_key_name} = `${{process.env.API_SECRET}}`;\n"
            "export function Good({ name, el, h }: { name: string; el: HTMLElement; h: string }) {\n"
            "  el.innerHTML = DOMPurify.sanitize(h);\n"
            "  return <div>{name}</div>;\n"
            "}\n"
        )

        (vuln_dir / "app.py").write_text(vuln_py, encoding="utf-8")
        (vuln_dir / "broken.py").write_text(vuln_syntax_py, encoding="utf-8")
        (vuln_dir / "client.tsx").write_text(vuln_tsx, encoding="utf-8")
        (vuln_dir / "extra.ts").write_text(vuln_ts, encoding="utf-8")
        (vuln_dir / ".env").write_text(vuln_env, encoding="utf-8")
        (vuln_wf / "ci.yml").write_text(wf_text, encoding="utf-8")

        (clean_dir / "app.py").write_text(clean_py, encoding="utf-8")
        (clean_dir / "client.tsx").write_text(clean_tsx, encoding="utf-8")
        (clean_dir / "bundle.js").write_text("//" + ("a" * (MAX_FILE_SIZE_BYTES + 1024)), encoding="utf-8")

        v_report = scan_target(vuln_dir, min_severity="low", ide_hook=False)
        c_report = scan_target(clean_dir, min_severity="low", ide_hook=False)

        v_rules = {f["rule_id"] for f in v_report["findings"]}  # type: ignore[index]
        expected_rules = {
            "SEC-SECRET-001",
            "SEC-SQLI-001",
            "SEC-CORS-001",
            "SEC-CORS-002",
            "SEC-XSS-001",
            "SEC-STORAGE-001",
            "SEC-CONFIG-001",
            "SEC-EXEC-001",
            "SEC-DESER-001",
        }
        missing = sorted(expected_rules - v_rules)
        serialized_vuln = json.dumps(v_report)
        redacted_ok = all(
            s not in serialized_vuln for s in (sk_val, sk_val2, fb_secret, js_bt_secret)
        )
        oversized_file_skipped = "bundle.js" in c_report.get("skipped_large_files", [])  # type: ignore[operator]

        prev_port = os.environ.get("SECURECODER_API_PORT")
        try:
            os.environ["SECURECODER_API_PORT"] = "²"
            u_hook = _optional_ide_hook(True, clean_dir, {"total": 0})
            os.environ["SECURECODER_API_PORT"] = "99999"
            oob_hook = _optional_ide_hook(True, clean_dir, {"total": 0})
            unicode_port_safe = u_hook == "skipped_offline" and oob_hook == "skipped_offline"
        finally:
            if prev_port is None:
                os.environ.pop("SECURECODER_API_PORT", None)
            else:
                os.environ["SECURECODER_API_PORT"] = prev_port

        ok = (
            v_report["status"] == "FAIL"
            and not missing
            and redacted_ok
            and c_report["status"] == "PASS"
            and c_report["summary"]["total"] == 0  # type: ignore[index]
            and oversized_file_skipped
            and unicode_port_safe
        )
        print(
            json.dumps(
                {
                    "self_test": "PASS" if ok else "FAIL",
                    "vuln_rules_detected": sorted(v_rules),
                    "missing_rules": missing,
                    "secret_redacted": redacted_ok,
                    "clean_findings": c_report["summary"]["total"],  # type: ignore[index]
                    "oversized_file_skipped": oversized_file_skipped,
                    "unicode_port_safe": unicode_port_safe,
                },
                indent=2,
            )
        )
        return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline, vendor-neutral security baseline scanner (Python 3 stdlib only)."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target file or directory to scan (defaults to current working directory).",
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        default=None,
        help="Target file or directory path to scan.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output to stdout.",
    )
    parser.add_argument(
        "--severity",
        choices=("low", "medium", "high", "critical"),
        default="low",
        help="Minimum severity threshold causing non-zero exit (default: low).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run embedded offline self-tests in an isolated temporary directory.",
    )
    parser.add_argument(
        "--ide-hook",
        action="store_true",
        help="Optionally notify local IDE security daemon when configured; silently skipped offline.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    raw_target = args.path or args.target or "."
    target = Path(raw_target)
    if not target.exists():
        msg = f"Target path does not exist: {target}"
        if args.json:
            print(json.dumps({"status": "ERROR", "error": msg}))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    report = scan_target(target, min_severity=args.severity, ide_hook=args.ide_hook)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print(
            f"Security Baseline [{report['status']}] target={report['target']} "
            f"files={report['scanned_files']} findings={summary['total']} "  # type: ignore[index]
            f"(C={summary['critical']} H={summary['high']} M={summary['medium']} L={summary['low']}) "  # type: ignore[index]
            f"ide_hook={report['ide_hook']}"
        )
        for item in report["findings"]:  # type: ignore[attr-defined]
            print(
                f"  [{item['severity'].upper()}] {item['rule_id']} ({item['cwe']}) "
                f"{item['file']}:{item['line']} - {item['message']}"
            )

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
