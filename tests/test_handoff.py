import json
import tempfile
import unittest
from pathlib import Path

from kbbench.arms import NotesStore
from kbbench.runner import run_task
from kbbench.sanitize import sanitize_source, write_agent_bundle
from kbbench.session import Session, StubModel, ToolError


class HandoffTest(unittest.TestCase):
    def test_handoff_session_has_no_file_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = NotesStore(Path(tmp))
            session = Session(
                store, limit=2, budget_chars=100, source_root=None, allow_files=False
            )
            self.assertNotIn("read_file", session.tool_names())
            with self.assertRaises(ToolError):
                session.call("read_file", {"path": "file_1.c"})

    def test_run_does_not_place_source_or_gold_in_handoff_dir(self):
        raw = (Path(__file__).parent / "fixtures" / "leak_pattern.c").read_text(
            encoding="utf-8"
        )
        result = sanitize_source(raw, source_name="leak_pattern.c")
        self.assertTrue(result.agent_ready)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            write_agent_bundle(result, src / "file_1.c")
            gold = root / "gold" / "synthetic-1.json"
            gold.parent.mkdir()
            gold.write_text(
                json.dumps({"vulnerable": "yes", "cwe": "999"}) + "\n",
                encoding="utf-8",
            )
            row = run_task(
                task_id="synthetic-1",
                arm="notes",
                repeat=0,
                source_dir=src,
                run_root=root / "runs",
                limit=3,
                budget_chars=800,
                embedder_name=None,
                model_name=StubModel.name,
            )
            handoff = root / "runs" / "synthetic-1" / "notes" / "r0" / "handoff"
            self.assertEqual([p.name for p in handoff.iterdir()], [])
            self.assertNotIn("read_file", row["handoff_tools"])
            trace = Path(row["trace"]).read_text(encoding="utf-8")
            self.assertNotIn("CWE999", trace)
            self.assertNotIn('"cwe": "999"', trace)


if __name__ == "__main__":
    unittest.main()
