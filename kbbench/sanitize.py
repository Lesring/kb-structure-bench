"""Juliet-oriented sanitizer.

Removes path names, renames guide-pattern identifiers, and drops comments
that carry CWE or good/bad labels. String literals are not rewritten unless
an explicit exact-content rewrite is passed in. Residuals block agent_ready.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

LEAK_COMMENT = re.compile(
    r"cwe|badsource|goodsource|badsink|goodsink|potential flaw|fix:|flaw|omitbad|omitgood",
    re.IGNORECASE,
)
LEAK_SCAN = ("cwe", "good", "bad", "sink", "flaw", "vuln")

_IDENT = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_RENAME_PATTERNS = [
    re.compile(r"^CWE\d+.*", re.IGNORECASE),
    re.compile(r"^(CWE.*_)?bad$", re.IGNORECASE),
    re.compile(r"^(CWE.*_)?good$", re.IGNORECASE),
    re.compile(r"^good(\d+|G2B\d*|B2G\d*)$"),
    re.compile(r"^good(G2B\d*|B2G\d*)?(Source|Sink)(_[a-z])?$"),
    re.compile(r"^helper(Bad|Good(G2B|B2G)?\d*)$"),
    re.compile(r"^(bad|good)(G2B|B2G)?\d*VaSink[BG]?$"),
    re.compile(r"^(Bad|Good)(Base|Derived)?Class$"),
    re.compile(r"^(Bad|Good)Source$"),
    re.compile(r"^(Bad|Good)Sink$"),
    re.compile(r".*_(bad|good\d*)$", re.IGNORECASE),
]


@dataclass
class SanitizeResult:
    source_name: str
    code: str
    rename_map: dict[str, str]
    residuals: list[dict]
    agent_ready: bool
    flawed_original: list[str] = field(default_factory=list)

    @property
    def flawed_sanitized(self) -> list[str]:
        return [self.rename_map[name] for name in self.flawed_original if name in self.rename_map]


def _should_rename(name: str) -> bool:
    return any(pat.match(name) for pat in _RENAME_PATTERNS)


def _is_flawed_name(name: str) -> bool:
    if re.fullmatch(r"(CWE.*_)?bad", name, flags=re.IGNORECASE):
        return True
    if name.endswith("_bad") or name.endswith("_bad()"):
        return True
    if name in {"BadClass", "BadBaseClass", "BadDerivedClass", "BadSource", "BadSink", "helperBad"}:
        return True
    return False


def _lex(src: str) -> list[tuple[str, str]]:
    """Split into code / comment / string segments. Strings keep their quotes."""
    parts: list[tuple[str, str]] = []
    i = 0
    n = len(src)
    buf: list[str] = []

    def flush() -> None:
        if buf:
            parts.append(("code", "".join(buf)))
            buf.clear()

    while i < n:
        if src.startswith("//", i):
            flush()
            j = src.find("\n", i)
            if j < 0:
                parts.append(("comment", src[i:]))
                i = n
            else:
                parts.append(("comment", src[i:j]))
                i = j
            continue
        if src.startswith("/*", i):
            flush()
            j = src.find("*/", i + 2)
            if j < 0:
                parts.append(("comment", src[i:]))
                i = n
            else:
                parts.append(("comment", src[i : j + 2]))
                i = j + 2
            continue
        if src[i] in {'"', "'"}:
            flush()
            quote = src[i]
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == quote:
                    j += 1
                    break
                j += 1
            parts.append(("string", src[i:j]))
            i = j
            continue
        buf.append(src[i])
        i += 1
    flush()
    return parts


def _strip_preprocessor(src: str) -> str:
    """Drop Juliet's OMIT* and INCLUDEMAIN guards while those words are still present."""
    lines = src.splitlines(keepends=True)
    out: list[str] = []
    skipping = False
    depth = 0
    for line in lines:
        stripped = line.strip()
        if not skipping and re.match(r"#\s*ifdef\s+INCLUDEMAIN\b", stripped):
            skipping = True
            depth = 1
            continue
        if skipping:
            if re.match(r"#\s*if", stripped):
                depth += 1
            elif re.match(r"#\s*endif\b", stripped):
                depth -= 1
                if depth == 0:
                    skipping = False
            continue
        if re.search(r"\b(OMITBAD|OMITGOOD)\b", line):
            continue
        out.append(line)
    return "".join(out)


def sanitize_source(
    src: str,
    *,
    source_name: str = "input.c",
    literal_rewrites: dict[str, str] | None = None,
) -> SanitizeResult:
    """Sanitize one translation unit. ``literal_rewrites`` maps exact contents."""
    rewrites = literal_rewrites or {}
    src = _strip_preprocessor(src)
    parts = _lex(src)
    names: list[str] = []
    for kind, text in parts:
        if kind != "code":
            continue
        names.extend(m.group(0) for m in _IDENT.finditer(text) if _should_rename(m.group(0)))
    ordered: list[str] = []
    for name in names:
        if name not in ordered:
            ordered.append(name)
    rename = {name: f"fn_{i}" for i, name in enumerate(ordered, start=1)}
    flawed = [name for name in ordered if _is_flawed_name(name)]

    rebuilt: list[str] = []
    for kind, text in parts:
        if kind == "comment":
            body = text
            if LEAK_COMMENT.search(body):
                if body.startswith("//"):
                    rebuilt.append("")
                else:
                    rebuilt.append(" ")
                continue
            rebuilt.append(text)
            continue
        if kind == "string":
            quote = text[0]
            inner = text[1:-1] if len(text) >= 2 and text[-1] == quote else text
            if inner in rewrites:
                rebuilt.append(quote + rewrites[inner] + quote)
            else:
                rebuilt.append(text)
            continue
        def repl(match: re.Match[str]) -> str:
            word = match.group(0)
            return rename.get(word, word)

        rebuilt.append(_IDENT.sub(repl, text))
    code = "".join(rebuilt)
    residuals: list[dict] = []
    for kind, text in _lex(code):
        if kind == "code":
            for match in _IDENT.finditer(text):
                word = match.group(0)
                low = word.lower()
                if any(tok in low for tok in LEAK_SCAN):
                    residuals.append({"kind": "identifier", "token": word, "text": word})
        elif kind == "string":
            quote = text[0]
            inner = text[1:-1] if len(text) >= 2 and text[-1] == quote else text
            low = inner.lower()
            for token in LEAK_SCAN:
                if token in low:
                    residuals.append({"kind": "string", "token": token, "text": inner})
                    break
        elif kind == "comment" and LEAK_COMMENT.search(text):
            residuals.append({"kind": "comment", "token": "leak-comment", "text": text[:80]})
    agent_ready = not residuals
    return SanitizeResult(
        source_name=source_name,
        code=code,
        rename_map=rename,
        residuals=residuals,
        agent_ready=agent_ready,
        flawed_original=flawed,
    )


def cwe_from_path(path: str) -> str | None:
    match = re.search(r"CWE(\d+)", path, flags=re.IGNORECASE)
    return match.group(1) if match else None


def write_agent_bundle(result: SanitizeResult, dest: Path) -> None:
    """Write only sanitized code. Caller must keep gold elsewhere."""
    if not result.agent_ready:
        raise RuntimeError(f"{result.source_name} is not agent-ready")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result.code, encoding="utf-8")


def bundle_digest(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def gold_record(task_id: str, archive_member: str, result: SanitizeResult) -> dict:
    return {
        "task_id": task_id,
        "archive_member": archive_member,
        "cwe": cwe_from_path(archive_member),
        "vulnerable": "yes" if result.flawed_sanitized else "no",
        "flawed_functions": result.flawed_sanitized,
        "rename_map": result.rename_map,
        "agent_bundle_sha256": bundle_digest(result.code),
    }


def dump_gold(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
