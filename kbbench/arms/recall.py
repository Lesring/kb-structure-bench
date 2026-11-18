"""Title-weighted token overlap used by the graph arm.

Adapted from N1nEmAn/nvwabase ``lib/fg.py`` at commit
c9ec790a99c01641d566e38d8d7d7e6c63a24bcc (MIT License, Copyright 2026
N1nEmAn). ``_recall_tokenize`` and ``_recall_score`` are copied so this
harness does not call ``fgc`` or ``fgc dispatch``. Upstream ``master``
after that commit is intentionally not followed.
"""

from __future__ import annotations

import difflib
import re

_RECALL_TOKEN_RE = re.compile(r"[\w一-鿿]+", re.UNICODE)


def recall_tokenize(text: str) -> list[str]:
    """Lowercase + Unicode-word/CJK tokenization.

    CJK runs are split into individual characters, matching nvwabase.
    """
    if not text:
        return []
    out: list[str] = []
    for tok in _RECALL_TOKEN_RE.findall(text.lower()):
        if any("一" <= ch <= "鿿" for ch in tok):
            out.extend(list(tok))
        else:
            out.append(tok)
    return [t for t in out if t]


def recall_score(query: str, title: str | None, description: str | None) -> float:
    """Score title (counted twice) and description. No embeddings."""
    title_l = (title or "").lower()
    desc_l = (description or "").lower()
    haystack = f"{title_l} {title_l} {desc_l}".strip()
    if not haystack:
        return 0.0
    q_tokens = set(recall_tokenize(query))
    if not q_tokens:
        return 0.0
    h_tokens = set(recall_tokenize(haystack))
    if not h_tokens:
        return 0.0
    overlap = len(q_tokens & h_tokens)
    if overlap == 0:
        ratio = difflib.SequenceMatcher(None, query.lower(), haystack).ratio()
        return ratio if ratio >= 0.45 else 0.0
    overlap_score = overlap / max(1, len(q_tokens))
    ratio_bonus = 0.2 * difflib.SequenceMatcher(None, query.lower(), haystack).ratio()
    return overlap_score + ratio_bonus
