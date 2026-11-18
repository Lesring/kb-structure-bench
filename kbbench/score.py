"""Score a handoff answer against a gold file that the agent never saw.

Numbers produced here are only as meaningful as the run that created the
answer. The stub model is not a measurement of any knowledge-base structure.
"""

from __future__ import annotations


def score_answer(answer: dict | None, gold: dict, *, evidence_min_chars: int, kb_text: str, source_text: str) -> dict:
    if not answer:
        return {
            "failed": True,
            "vulnerable_correct": False,
            "category_correct": False,
            "location_hit": False,
            "faithful_evidence": 0,
            "evidence_total": 0,
        }
    vulnerable = str(answer.get("vulnerable") or "")
    gold_vuln = str(gold.get("vulnerable") or "")
    category = str(answer.get("category") or "")
    gold_cwe = str(gold.get("cwe") or "")
    location = str(answer.get("location") or "")
    flawed = gold.get("flawed_functions") or []
    location_hit = any(name and name in location for name in flawed)
    ids = answer.get("evidence_ids") or []
    faithful = 0
    for node_id in ids:
        if node_id not in kb_text:
            continue
        # faithfulness needs a long shared span; the stub usually has none
        if _shares_span(kb_text, source_text, evidence_min_chars):
            faithful += 1
    return {
        "failed": False,
        "vulnerable_correct": vulnerable == gold_vuln and vulnerable != "unknown",
        "unknown": vulnerable == "unknown",
        "category_correct": bool(gold_cwe) and category == gold_cwe and gold_vuln == "yes",
        "location_hit": location_hit,
        "faithful_evidence": faithful,
        "evidence_total": len(ids),
    }


def _shares_span(kb_text: str, source_text: str, min_chars: int) -> bool:
    compact_src = "".join(source_text.split())
    compact_kb = "".join(kb_text.split())
    if min_chars < 1 or len(compact_src) < min_chars:
        return False
    for i in range(0, len(compact_src) - min_chars + 1, max(1, min_chars // 2)):
        span = compact_src[i : i + min_chars]
        if span and span in compact_kb:
            return True
    return False
