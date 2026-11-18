import tempfile
import unittest
from pathlib import Path

from kbbench.arms import GraphStore, NotesStore, VectorStore
from kbbench.session import Session


class ArmTest(unittest.TestCase):
    def test_graph_list_hides_doc_and_search_uses_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = GraphStore(Path(tmp))
            store.write("alpha widget", "short summary\nDOC_TOKEN_SHOULD_STAY_HIDDEN", None)
            listed = "\n".join(item.text for item in store.list_records())
            self.assertNotIn("DOC_TOKEN_SHOULD_STAY_HIDDEN", listed)
            self.assertIn("short summary", listed)
            found = store.search("alpha widget")
            self.assertTrue(found)
            self.assertNotIn("DOC_TOKEN", found[0].text)
            full = store.read(found[0].id)
            self.assertIn("DOC_TOKEN_SHOULD_STAY_HIDDEN", full.text)

    def test_notes_search_is_substring_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = NotesStore(Path(tmp))
            store.write("one", "aaa keep", None)
            store.write("two", "bbb keep", None)
            hits = store.search("keep")
            self.assertEqual([h.id for h in hits], ["n001", "n002"])

    def test_vector_and_graph_share_session_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            graph = GraphStore(root / "g")
            vector = VectorStore(root / "v", "stub-hash-v0")
            body = "token " * 80
            graph.write("same", body, None)
            vector.write("same", body, None)
            for store in (graph, vector):
                session = Session(store, limit=1, budget_chars=30, source_root=None, allow_files=False)
                text = session.call("kb_search", {"query": "same token"})
                self.assertLessEqual(len(text.splitlines()[-1]), 30)
                self.assertEqual(session.events[-1]["returned"], 1)

    def test_depends_on_is_an_edge_only_for_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            graph = GraphStore(root / "g")
            notes = NotesStore(root / "n")
            a = graph.write("a", "first fact", None)
            graph.write("b", "second fact", [a])
            snap = graph.snapshot()
            self.assertEqual(snap["intents"][0]["from"], [a])
            self.assertEqual(snap["intents"][0]["to"], "f002")
            notes.write("a", "first", None)
            notes.write("b", "second", ["n001"])
            self.assertIn("depends_on: n001", notes.read("n002").text)
            self.assertEqual(notes.snapshot()["sections"][0]["id"], "n001")


if __name__ == "__main__":
    unittest.main()
