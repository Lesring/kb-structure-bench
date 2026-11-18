"""Tool execution and a stub model used for the pipeline check.

The stub model is not a research baseline. It only proves that write and
handoff sessions call the shared interface and that handoff has no file tools.
"""

from __future__ import annotations

import json
from pathlib import Path

from kbbench.budget import Evidence, cap_evidence
from kbbench.arms import KnowledgeBase


class ToolError(Exception):
    pass


def render_evidence(units: list[Evidence]) -> str:
    if not units:
        return "(empty)"
    lines = []
    for unit in units:
        score = "" if unit.score is None else f" score={unit.score:.3f}"
        lines.append(f"{unit.id}\t{unit.title}{score}\n{unit.text}")
    return "\n".join(lines)


class Session:
    def __init__(
        self,
        store: KnowledgeBase,
        *,
        limit: int,
        budget_chars: int,
        source_root: Path | None,
        allow_files: bool,
    ):
        self.store = store
        self.limit = limit
        self.budget_chars = budget_chars
        self.source_root = source_root
        self.allow_files = allow_files
        self.events: list[dict] = []

    def tool_names(self) -> list[str]:
        names = ["kb_write", "kb_search", "kb_read", "kb_list"]
        if self.allow_files:
            names.extend(["list_dir", "read_file", "search_file"])
        return names

    def call(self, name: str, args: dict) -> str:
        if name not in self.tool_names():
            raise ToolError(f"tool {name} is not available in this session")
        if name == "kb_write":
            depends = args.get("depends_on") or []
            if isinstance(depends, str):
                depends = [part for part in depends.split(",") if part]
            node_id = self.store.write(
                str(args.get("title") or ""),
                str(args.get("body") or ""),
                list(depends),
            )
            self.events.append({"tool": name, "id": node_id, "chars": len(str(args.get("body") or ""))})
            return node_id
        if name == "kb_search":
            ranked = self.store.search(str(args.get("query") or ""))
            capped, cut = cap_evidence(ranked, limit=self.limit, budget_chars=self.budget_chars)
            self.events.append(
                {
                    "tool": name,
                    "returned": len(capped),
                    "truncated_chars": cut,
                    "chars": sum(len(item.text) for item in capped),
                }
            )
            return render_evidence(capped)
        if name == "kb_read":
            try:
                item = self.store.read(str(args["id"]))
            except KeyError as exc:
                raise ToolError(f"unknown id {args.get('id')}") from exc
            capped, cut = cap_evidence([item], limit=1, budget_chars=self.budget_chars)
            self.events.append({"tool": name, "truncated_chars": cut, "chars": len(capped[0].text)})
            return render_evidence(capped)
        if name == "kb_list":
            listed = self.store.list_records()
            capped, cut = cap_evidence(listed, limit=self.limit, budget_chars=self.budget_chars)
            blob = render_evidence(capped)
            self.events.append(
                {
                    "tool": name,
                    "returned": len(capped),
                    "truncated_chars": cut,
                    "chars": len(blob),
                }
            )
            return blob
        if name == "list_dir":
            assert self.source_root is not None
            names = sorted(p.name for p in self.source_root.iterdir() if p.is_file())
            self.events.append({"tool": name, "count": len(names)})
            return "\n".join(names)
        if name == "read_file":
            text = self._read_source(str(args.get("path") or ""))
            self.events.append({"tool": name, "path": args.get("path"), "chars": len(text)})
            return text
        if name == "search_file":
            text = self._read_source(str(args.get("path") or ""))
            query = str(args.get("query") or "")
            hits = [line for line in text.splitlines() if query and query in line]
            blob = "\n".join(hits)
            self.events.append({"tool": name, "hits": len(hits), "chars": len(blob)})
            return blob
        raise ToolError(name)

    def _read_source(self, rel: str) -> str:
        if self.source_root is None:
            raise ToolError("no source root")
        path = (self.source_root / rel).resolve()
        root = self.source_root.resolve()
        if root not in path.parents and path != root:
            raise ToolError("path escapes the task directory")
        if not path.is_file():
            raise ToolError("file not in the task directory")
        return path.read_text(encoding="utf-8", errors="replace")


class StubModel:
    """Scripted model. name is stub-model, not a paper system."""

    name = "stub-model"

    def run_write(self, session: Session) -> None:
        listing = session.call("list_dir", {})
        first = listing.splitlines()[0]
        text = session.call("read_file", {"path": first})
        excerpt = " ".join(text.split())[:80]
        session.call(
            "kb_write",
            {
                "title": "note",
                "body": excerpt + "\nCLAIM vulnerable=unknown",
            },
        )

    def run_handoff(self, session: Session) -> str:
        session.call("kb_list", {})
        session.call("kb_search", {"query": "note"})
        answer = {
            "vulnerable": "unknown",
            "category": "unknown",
            "location": "unknown",
            "evidence_ids": [],
            "notes": "stub handoff",
        }
        return json.dumps(answer, ensure_ascii=False)
