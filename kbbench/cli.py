"""Command line. Live model runs are refused until the design checklist is filled."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path

from kbbench import __version__
from kbbench.runner import run_task
from kbbench.sanitize import dump_gold, gold_record, sanitize_source, write_agent_bundle
from kbbench.session import StubModel

# Digest printed on the SARD suite 112 page opened 2026-11-18.
# It is a published string, not a hash this repository has computed.
SARD_PAGE_SHA256 = "ada9d7e1c323d283446df3f55bdee0d00bda1fed786785fe98764d58688f38eb"
ZENODO_URL = (
    "https://zenodo.org/records/4701387/files/"
    "Juliet_Test_Suite_v1.3_for_C_Cpp.zip?download=1"
)
ZENODO_RECORD = "https://zenodo.org/records/4701387"


def _load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pipeline_params(cfg: dict) -> dict:
    profile = cfg.get("pipeline_check_placeholders") or {}
    required = ("b_inject_chars", "n_steps", "search_limit")
    missing = [key for key in required if profile.get(key) in (None, "")]
    if missing:
        raise SystemExit(
            "pipeline-check placeholders missing "
            + ", ".join(missing)
            + ". These are not tuned defaults; put them under pipeline_check_placeholders."
        )
    return profile


def cmd_pipeline_check(args: argparse.Namespace) -> int:
    cfg = _load_config(Path(args.config))
    params = _pipeline_params(cfg)
    fixture = Path(args.fixture)
    raw = fixture.read_text(encoding="utf-8")
    result = sanitize_source(raw, source_name=fixture.name, literal_rewrites={"Good": "set"})
    if not result.agent_ready:
        print(json.dumps({"agent_ready": False, "residuals": result.residuals}, ensure_ascii=False))
        return 2
    run_root = Path(args.out)
    src_dir = run_root / "sanitized"
    write_agent_bundle(result, src_dir / "file_1.c")
    gold = gold_record("synthetic-1", fixture.name, result)
    dump_gold(run_root / "gold" / "synthetic-1.json", gold)
    summary = []
    for arm in ("graph", "vector", "notes"):
        row = run_task(
            task_id="synthetic-1",
            arm=arm,
            repeat=0,
            source_dir=src_dir,
            run_root=run_root / "runs",
            limit=int(params["search_limit"]),
            budget_chars=int(params["b_inject_chars"]),
            embedder_name="stub-hash-v0" if arm == "vector" else None,
            model_name=StubModel.name,
        )
        handoff = run_root / "runs" / "synthetic-1" / arm / "r0" / "handoff"
        write_src = run_root / "runs" / "synthetic-1" / arm / "r0" / "write_src"
        summary.append(
            {
                "arm": arm,
                "handoff_tools": row["handoff_tools"],
                "handoff_dir_empty": handoff.is_dir() and not any(handoff.iterdir()),
                "write_has_source": any(write_src.glob("file_1.c")),
                "answer": row["answer"],
                "model": StubModel.name,
            }
        )
    report = {
        "kind": "pipeline_check",
        "not_a_paper_result": True,
        "model": StubModel.name,
        "placeholders": params,
        "arms": summary,
        "gold_path_not_in_handoff": True,
    }
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


def cmd_sanitize_file(args: argparse.Namespace) -> int:
    src = Path(args.src).read_text(encoding="utf-8")
    rewrites = {}
    if args.rewrites:
        rewrites = json.loads(Path(args.rewrites).read_text(encoding="utf-8"))
    result = sanitize_source(src, source_name=Path(args.src).name, literal_rewrites=rewrites)
    report = {
        "agent_ready": result.agent_ready,
        "rename_map": result.rename_map,
        "residuals": result.residuals,
        "flawed_sanitized": result.flawed_sanitized,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.out and result.agent_ready:
        write_agent_bundle(result, Path(args.out))
    return 0 if result.agent_ready else 2


def cmd_hash_zip(args: argparse.Namespace) -> int:
    path = Path(args.zip)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    record = {
        "path": str(path),
        "sha256": digest,
        "size": path.stat().st_size,
        "sard_page_sha256": SARD_PAGE_SHA256,
        "matches_sard_page": digest == SARD_PAGE_SHA256,
    }
    print(json.dumps(record, indent=2))
    return 0 if record["matches_sard_page"] else 3


def cmd_prepare_tasks(args: argparse.Namespace) -> int:
    """Sanitize selected archive members. Gold is written beside the bundle, not inside it."""
    spec = json.loads(Path(args.tasks).read_text(encoding="utf-8"))
    rewrites = {}
    if args.rewrites:
        rewrites = json.loads(Path(args.rewrites).read_text(encoding="utf-8"))
    archive = zipfile.ZipFile(args.zip)
    out_root = Path(args.out)
    prepared = []
    for task in spec["tasks"]:
        member = task["archive_member"]
        raw = archive.read(member).decode("utf-8", errors="replace")
        result = sanitize_source(raw, source_name=member, literal_rewrites=rewrites)
        entry = {
            "task_id": task["task_id"],
            "archive_member": member,
            "agent_ready": result.agent_ready,
            "residuals": result.residuals,
            "rationale": task.get("rationale", ""),
        }
        if result.agent_ready:
            bundle = out_root / "agent" / task["task_id"]
            write_agent_bundle(result, bundle / "file_1.c")
            dump_gold(out_root / "gold" / f"{task['task_id']}.json", gold_record(task["task_id"], member, result))
        prepared.append(entry)
    report_path = out_root / "prepare-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(prepared, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    blocked = [row["task_id"] for row in prepared if not row["agent_ready"]]
    return 0 if not blocked else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kbbench", description="v0.1 KB-structure harness")
    parser.add_argument("--version", action="version", version=f"kbbench {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pipe = sub.add_parser("pipeline-check", help="stub-model run on one synthetic fixture")
    pipe.add_argument("--config", default="config/v0.1.json")
    pipe.add_argument("--fixture", default="tests/fixtures/leak_pattern.c")
    pipe.add_argument("--out", default="runs/pipeline-check")
    pipe.add_argument("--report", default="runs/pipeline-check/report.json")
    pipe.set_defaults(func=cmd_pipeline_check)

    san = sub.add_parser("sanitize-file", help="sanitize one source file and print residuals")
    san.add_argument("--src", required=True)
    san.add_argument("--out")
    san.add_argument("--rewrites")
    san.set_defaults(func=cmd_sanitize_file)

    digest = sub.add_parser("hash-zip", help="sha256 a local Juliet zip and compare to the SARD page")
    digest.add_argument("--zip", required=True)
    digest.set_defaults(func=cmd_hash_zip)

    prep = sub.add_parser("prepare-tasks", help="sanitize archive members listed in a task file")
    prep.add_argument("--zip", required=True)
    prep.add_argument("--tasks", required=True)
    prep.add_argument("--out", required=True)
    prep.add_argument("--rewrites")
    prep.set_defaults(func=cmd_prepare_tasks)

    run = sub.add_parser("run", help="one sanitized task, one arm, stub or refused live model")
    run.add_argument("--task-id", required=True)
    run.add_argument("--arm", required=True, choices=["graph", "vector", "notes"])
    run.add_argument("--source-dir", required=True)
    run.add_argument("--config", default="config/v0.1.json")
    run.add_argument("--out", default="runs/manual")
    run.add_argument("--repeat", type=int, default=0)
    run.set_defaults(func=cmd_run)

    batch = sub.add_parser("batch", help="run every prepared task directory with the stub model")
    batch.add_argument("--manifest", required=True)
    batch.add_argument("--config", default="config/v0.1.json")
    batch.add_argument("--out", default="runs/batch")
    batch.set_defaults(func=cmd_batch)
    return parser


def cmd_batch(args: argparse.Namespace) -> int:
    cfg = _load_config(Path(args.config))
    if os.environ.get("KBBENCH_MODEL"):
        raise SystemExit("KBBENCH_MODEL is set; refusing a live-model batch")
    params = _pipeline_params(cfg)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    rows = []
    for task in manifest["tasks"]:
        for arm in ("graph", "vector", "notes"):
            for repeat in range(int(task.get("repeats", 1))):
                row = run_task(
                    task_id=task["task_id"],
                    arm=arm,
                    repeat=repeat,
                    source_dir=Path(task["source_dir"]),
                    run_root=Path(args.out),
                    limit=int(params["search_limit"]),
                    budget_chars=int(params["b_inject_chars"]),
                    embedder_name="stub-hash-v0" if arm == "vector" else None,
                    model_name=StubModel.name,
                )
                rows.append({"task_id": task["task_id"], "arm": arm, "repeat": repeat, "trace": row["trace"]})
    print(json.dumps({"model": StubModel.name, "not_a_paper_result": True, "runs": rows}, ensure_ascii=False, indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    cfg = _load_config(Path(args.config))
    if os.environ.get("KBBENCH_MODEL"):
        raise SystemExit(
            "KBBENCH_MODEL is set but this harness has no live client yet. "
            "Refusing to run a real model."
        )
    params = _pipeline_params(cfg)
    row = run_task(
        task_id=args.task_id,
        arm=args.arm,
        repeat=args.repeat,
        source_dir=Path(args.source_dir),
        run_root=Path(args.out),
        limit=int(params["search_limit"]),
        budget_chars=int(params["b_inject_chars"]),
        embedder_name="stub-hash-v0" if args.arm == "vector" else None,
        model_name=StubModel.name,
    )
    print(json.dumps({"arm": row["arm"], "answer": row["answer"], "trace": row["trace"]}, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
