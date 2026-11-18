"""One-task and batch runner. Gold files are never copied into the work directory."""

from __future__ import annotations

import json
import time
from pathlib import Path

from kbbench.arms import open_store
from kbbench.prompts import HANDOFF_INSTRUCTIONS, WRITE_INSTRUCTIONS
from kbbench.session import Session, StubModel


def _write_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_task(
    *,
    task_id: str,
    arm: str,
    repeat: int,
    source_dir: Path,
    run_root: Path,
    limit: int,
    budget_chars: int,
    embedder_name: str | None,
    model_name: str,
) -> dict:
    """Run write then handoff. ``source_dir`` must already be sanitized."""
    if model_name != StubModel.name:
        raise RuntimeError(
            "no live model client is configured; set a model only after "
            "docs/paper/design-decisions.md checklist items 1-10 are filled"
        )
    work = run_root / task_id / arm / f"r{repeat}"
    write_dir = work / "write_src"
    handoff_dir = work / "handoff"
    write_dir.mkdir(parents=True, exist_ok=True)
    handoff_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(source_dir.iterdir()):
        if src.is_file():
            (write_dir / src.name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    store = open_store(arm, work / "kb", embedder_name)
    trace = work / "trace.jsonl"
    started = time.perf_counter()
    _write_jsonl(
        trace,
        {
            "event": "start",
            "task_id": task_id,
            "arm": arm,
            "repeat": repeat,
            "model": model_name,
            "limit": limit,
            "b_inject_chars": budget_chars,
            "embedder": embedder_name,
            "token_count_source": "unset_tokenizer_char_proxy",
        },
    )
    model = StubModel()
    write_session = Session(
        store,
        limit=limit,
        budget_chars=budget_chars,
        source_root=write_dir,
        allow_files=True,
    )
    t0 = time.perf_counter()
    model.run_write(write_session)
    _write_jsonl(
        trace,
        {
            "event": "write_session",
            "prompt": WRITE_INSTRUCTIONS,
            "tools": write_session.tool_names(),
            "tool_events": write_session.events,
            "latency_ms": int((time.perf_counter() - t0) * 1000),
        },
    )
    handoff_session = Session(
        store,
        limit=limit,
        budget_chars=budget_chars,
        source_root=None,
        allow_files=False,
    )
    t1 = time.perf_counter()
    answer_text = model.run_handoff(handoff_session)
    try:
        answer = json.loads(answer_text)
    except json.JSONDecodeError:
        answer = None
    _write_jsonl(
        trace,
        {
            "event": "handoff_session",
            "prompt": HANDOFF_INSTRUCTIONS,
            "tools": handoff_session.tool_names(),
            "tool_events": handoff_session.events,
            "answer": answer,
            "answer_ok": answer is not None,
            "latency_ms": int((time.perf_counter() - t1) * 1000),
        },
    )
    (work / "kb_snapshot.json").write_text(
        json.dumps(store.snapshot(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_jsonl(
        trace,
        {
            "event": "end",
            "wall_ms": int((time.perf_counter() - started) * 1000),
            "source_chars": sum(len(p.read_text(encoding="utf-8")) for p in write_dir.iterdir() if p.is_file()),
        },
    )
    return {
        "task_id": task_id,
        "arm": arm,
        "repeat": repeat,
        "answer": answer,
        "trace": str(trace),
        "handoff_tools": handoff_session.tool_names(),
        "write_files": sorted(p.name for p in write_dir.iterdir()),
        "handoff_files": sorted(p.name for p in handoff_dir.iterdir()),
    }
