"""Shared evidence cap. Every arm's search and list output goes through this.

The cap is part of the independent-variable control: the same limit and the
same character budget, applied in rank order. A unit that does not fit is
truncated. A later, shorter unit is not substituted for it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    id: str
    title: str
    text: str
    score: float | None = None
    truncated_chars: int = 0


def cap_evidence(
    units: list[Evidence],
    *,
    limit: int,
    budget_chars: int,
) -> tuple[list[Evidence], int]:
    """Return units in the given order, plus total characters cut off.

    ``limit`` is the maximum number of evidence units. ``budget_chars`` is
    the shared injection / return budget. Both are required; callers must
    not invent a default inside an arm.
    """
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if budget_chars < 1:
        raise ValueError("budget_chars must be >= 1")
    chosen: list[Evidence] = []
    cut = 0
    remaining = budget_chars
    for unit in units[:limit]:
        if remaining <= 0:
            break
        if len(unit.text) <= remaining:
            chosen.append(unit)
            remaining -= len(unit.text)
            continue
        cut += len(unit.text) - remaining
        chosen.append(
            Evidence(
                id=unit.id,
                title=unit.title,
                text=unit.text[:remaining],
                score=unit.score,
                truncated_chars=unit.truncated_chars + (len(unit.text) - remaining),
            )
        )
        break
    return chosen, cut
