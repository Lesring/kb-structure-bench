import unittest
from pathlib import Path

from kbbench.sanitize import sanitize_source

FIXTURE = Path(__file__).parent / "fixtures" / "leak_pattern.c"


class SanitizeTest(unittest.TestCase):
    def test_leak_markers_leave_residuals_until_a_literal_decision(self):
        raw = FIXTURE.read_text(encoding="utf-8")
        result = sanitize_source(raw, source_name=FIXTURE.name)
        self.assertNotIn("CWE999", result.code)
        self.assertNotIn("goodG2B", result.code)
        self.assertNotIn("POTENTIAL FLAW", result.code)
        self.assertNotIn("INCLUDEMAIN", result.code)
        self.assertNotIn("Calling good", result.code)
        self.assertNotIn("Calling bad", result.code)
        self.assertNotIn("_bad", result.code)
        self.assertEqual(result.residuals, [])
        self.assertTrue(result.agent_ready)
        self.assertTrue(result.flawed_sanitized)

    def test_string_literal_good_blocks_the_bundle(self):
        src = 'void CWE1_x_bad(void) { const char *s = "Good"; }\n'
        result = sanitize_source(src, source_name="t.c")
        self.assertFalse(result.agent_ready)
        self.assertTrue(any(item["kind"] == "string" and item["token"] == "good" for item in result.residuals))
        rewritten = sanitize_source(src, source_name="t.c", literal_rewrites={"Good": "set"})
        self.assertTrue(rewritten.agent_ready)
        self.assertIn("set", rewritten.code)
        self.assertNotIn("Good", rewritten.code)
        self.assertNotIn("CWE1", rewritten.code)


if __name__ == "__main__":
    unittest.main()
