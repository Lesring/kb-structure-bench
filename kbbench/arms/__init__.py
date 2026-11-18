"""Knowledge-base arms. Structure differs; the Evidence objects do not."""

from __future__ import annotations

import hashlib
import json
import math
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

from kbbench.arms.recall import recall_score
from kbbench.budget import Evidence

NVWABASE_COMMIT = "c9ec790a99c01641d566e38d8d7d7e6c63a24bcc"
STUB_EMBEDDER_NAME = "stub-hash-v0"
STUB_EMBEDDER_DIM = 32


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_line(body: str) -> str:
    line = body.strip().splitlines()[0] if body.strip() else ""
    return line.strip()


class KnowledgeBase(ABC):
    arm: str

    @abstractmethod
    def write(self, title: str, body: str, depends_on: list[str] | None = None) -> str:
        """Persist one observation. Return its id."""

    @abstractmethod
    def search(self, query: str) -> list[Evidence]:
        """Ranked evidence units, before the shared cap."""

    @abstractmethod
    def read(self, node_id: str) -> Evidence:
        """Full record. Graph arm returns doc, or description if doc is empty."""

    @abstractmethod
    def list_records(self) -> list[Evidence]:
        """Summary units for injection. Graph arm must not include doc."""

    def snapshot(self) -> dict:
        return {"arm": self.arm}


class GraphStore(KnowledgeBase):
    """Frozen fact/intent adapter. One JSON file per node, no fgc dispatch."""

    arm = "graph"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.facts = self.root / "facts"
        self.intents = self.root / "intents"
        self.facts.mkdir(parents=True, exist_ok=True)
        self.intents.mkdir(parents=True, exist_ok=True)
        self._fact_n = self._max_id(self.facts, "f")
        self._intent_n = self._max_id(self.intents, "i")
        meta = {
            "nvwabase_commit": NVWABASE_COMMIT,
            "fields": ["title", "description", "doc", "from", "to"],
            "typed_facts": False,
        }
        (self.root / "PIN.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )

    @staticmethod
    def _max_id(directory: Path, prefix: str) -> int:
        best = 0
        for path in directory.glob(f"{prefix}*.json"):
            stem = path.stem[len(prefix) :]
            if stem.isdigit():
                best = max(best, int(stem))
        return best

    def write(self, title: str, body: str, depends_on: list[str] | None = None) -> str:
        self._fact_n += 1
        fid = f"f{self._fact_n:03d}"
        fact = {
            "id": fid,
            "title": title.strip() or None,
            "description": _first_line(body),
            "doc": body,
            "created_at": _now(),
            "creator": "agent",
            "source_intent": None,
        }
        deps = [d for d in (depends_on or []) if d]
        if deps:
            self._intent_n += 1
            iid = f"i{self._intent_n:03d}"
            intent = {
                "id": iid,
                "title": None,
                "from": deps,
                "to": fid,
                "description": f"depends on {', '.join(deps)}",
                "doc": None,
                "creator": "agent",
                "status": "done",
                "created_at": _now(),
                "concluded_at": _now(),
            }
            fact["source_intent"] = iid
            self._dump(self.intents / f"{iid}.json", intent)
        self._dump(self.facts / f"{fid}.json", fact)
        return fid

    def search(self, query: str) -> list[Evidence]:
        ranked: list[Evidence] = []
        for fact in self._load_all(self.facts):
            if fact.get("id") == "goal":
                continue
            score = recall_score(query, fact.get("title"), fact.get("description"))
            if score <= 0:
                continue
            desc = fact.get("description") or ""
            ranked.append(
                Evidence(
                    id=fact["id"],
                    title=fact.get("title") or "",
                    text=desc,
                    score=score,
                )
            )
        ranked.sort(key=lambda item: (-(item.score or 0), item.id))
        return ranked

    def read(self, node_id: str) -> Evidence:
        fact = self._load(self.facts / f"{node_id}.json")
        if fact is None:
            raise KeyError(node_id)
        body = fact.get("doc") or fact.get("description") or ""
        return Evidence(id=fact["id"], title=fact.get("title") or "", text=body)

    def list_records(self) -> list[Evidence]:
        facts = [f for f in self._load_all(self.facts) if f.get("id") != "goal"]
        facts.sort(key=lambda f: f.get("created_at") or "", reverse=True)
        out: list[Evidence] = []
        for fact in facts:
            desc = fact.get("description") or ""
            out.append(
                Evidence(id=fact["id"], title=fact.get("title") or "", text=desc)
            )
        return out

    def snapshot(self) -> dict:
        return {
            "arm": self.arm,
            "nvwabase_commit": NVWABASE_COMMIT,
            "facts": self._load_all(self.facts),
            "intents": self._load_all(self.intents),
        }

    @staticmethod
    def _dump(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _load(path: Path) -> dict | None:
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_all(self, directory: Path) -> list[dict]:
        rows = []
        for path in sorted(directory.glob("*.json")):
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        return rows


def stub_hash_embed(text: str, dim: int = STUB_EMBEDDER_DIM) -> list[float]:
    """Deterministic bag-of-tokens vector. Not a scientific embedding model."""
    vec = [0.0] * dim
    for tok in re.findall(r"[\w一-鿿]+", text.lower()):
        digest = hashlib.sha256(tok.encode("utf-8")).digest()
        idx = digest[0] % dim
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class VectorStore(KnowledgeBase):
    """Session-writable chunks. Ranking uses cosine; the cap is applied outside."""

    arm = "vector"

    def __init__(self, root: Path, embedder_name: str | None):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "chunks.jsonl"
        self.embedder_name = embedder_name or STUB_EMBEDDER_NAME
        if self.embedder_name != STUB_EMBEDDER_NAME:
            raise ValueError(
                "only the labeled stub embedder is implemented; "
                f"refusing to pretend {self.embedder_name!r} is configured"
            )
        self._n = 0
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._n = max(self._n, int(json.loads(line)["id"][1:]))

    def write(self, title: str, body: str, depends_on: list[str] | None = None) -> str:
        self._n += 1
        cid = f"c{self._n:03d}"
        text = body
        if depends_on:
            text = body.rstrip() + "\ndepends_on: " + ", ".join(depends_on)
        row = {
            "id": cid,
            "title": title.strip(),
            "text": text,
            "embedder": self.embedder_name,
            "dim": STUB_EMBEDDER_DIM,
            "vector": stub_hash_embed(f"{title}\n{text}"),
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return cid

    def _rows(self) -> list[dict]:
        if not self.path.is_file():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def search(self, query: str) -> list[Evidence]:
        qv = stub_hash_embed(query)
        ranked: list[Evidence] = []
        for row in self._rows():
            score = cosine(qv, row["vector"])
            ranked.append(
                Evidence(id=row["id"], title=row["title"], text=row["text"], score=score)
            )
        ranked.sort(key=lambda item: (-(item.score or 0), item.id))
        return ranked

    def read(self, node_id: str) -> Evidence:
        for row in self._rows():
            if row["id"] == node_id:
                return Evidence(id=row["id"], title=row["title"], text=row["text"])
        raise KeyError(node_id)

    def list_records(self) -> list[Evidence]:
        rows = self._rows()
        return [
            Evidence(id=row["id"], title=row["title"], text=_first_line(row["text"]))
            for row in reversed(rows)
        ]

    def snapshot(self) -> dict:
        rows = self._rows()
        public = []
        for row in rows:
            public.append({k: v for k, v in row.items() if k != "vector"})
        return {
            "arm": self.arm,
            "embedder": self.embedder_name,
            "dim": STUB_EMBEDDER_DIM,
            "chunks": public,
        }


class NotesStore(KnowledgeBase):
    """One markdown file. Search is a case-insensitive substring scan, in order."""

    arm = "notes"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "NOTES.md"
        self._sections: list[dict] = []
        if self.path.is_file():
            self._parse(self.path.read_text(encoding="utf-8"))

    def _parse(self, text: str) -> None:
        current: dict | None = None
        buf: list[str] = []
        for line in text.splitlines():
            if line.startswith("## "):
                if current is not None:
                    current["text"] = "\n".join(buf).strip("\n")
                    self._sections.append(current)
                parts = line[3:].split(" ", 1)
                current = {"id": parts[0], "title": parts[1] if len(parts) > 1 else ""}
                buf = []
            elif current is not None:
                buf.append(line)
        if current is not None:
            current["text"] = "\n".join(buf).strip("\n")
            self._sections.append(current)

    def _flush(self) -> None:
        chunks = []
        for sec in self._sections:
            chunks.append(f"## {sec['id']} {sec['title']}\n{sec['text']}\n")
        self.path.write_text("\n".join(chunks), encoding="utf-8")

    def write(self, title: str, body: str, depends_on: list[str] | None = None) -> str:
        nid = f"n{len(self._sections) + 1:03d}"
        text = body
        if depends_on:
            text = body.rstrip() + "\ndepends_on: " + ", ".join(depends_on)
        self._sections.append({"id": nid, "title": title.strip(), "text": text})
        self._flush()
        return nid

    def search(self, query: str) -> list[Evidence]:
        needle = query.lower()
        hits: list[Evidence] = []
        for sec in self._sections:
            hay = f"{sec['title']}\n{sec['text']}".lower()
            if needle and needle not in hay:
                continue
            hits.append(Evidence(id=sec["id"], title=sec["title"], text=sec["text"], score=None))
        return hits

    def read(self, node_id: str) -> Evidence:
        for sec in self._sections:
            if sec["id"] == node_id:
                return Evidence(id=sec["id"], title=sec["title"], text=sec["text"])
        raise KeyError(node_id)

    def list_records(self) -> list[Evidence]:
        return [
            Evidence(id=sec["id"], title=sec["title"], text=_first_line(sec["text"]))
            for sec in reversed(self._sections)
        ]

    def snapshot(self) -> dict:
        return {"arm": self.arm, "sections": list(self._sections)}


def open_store(arm: str, root: Path, embedder_name: str | None) -> KnowledgeBase:
    root.mkdir(parents=True, exist_ok=True)
    if arm == "graph":
        return GraphStore(root / "graph")
    if arm == "vector":
        return VectorStore(root / "vector", embedder_name)
    if arm == "notes":
        return NotesStore(root / "notes")
    raise ValueError(f"unknown arm {arm!r}")
