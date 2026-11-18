import unittest

from kbbench.budget import Evidence, cap_evidence


class BudgetTest(unittest.TestCase):
    def test_does_not_replace_long_unit_with_shorter_later_unit(self):
        units = [
            Evidence(id="a", title="long", text="x" * 100, score=0.9),
            Evidence(id="b", title="short", text="y" * 10, score=0.1),
            Evidence(id="c", title="short2", text="z" * 10, score=0.1),
        ]
        chosen, cut = cap_evidence(units, limit=3, budget_chars=50)
        self.assertEqual([item.id for item in chosen], ["a"])
        self.assertEqual(len(chosen[0].text), 50)
        self.assertEqual(cut, 50)
        self.assertEqual(chosen[0].truncated_chars, 50)

    def test_limit_counts_units_not_only_chars(self):
        units = [Evidence(id=str(i), title="", text="ab", score=None) for i in range(5)]
        chosen, cut = cap_evidence(units, limit=2, budget_chars=100)
        self.assertEqual([item.id for item in chosen], ["0", "1"])
        self.assertEqual(cut, 0)


if __name__ == "__main__":
    unittest.main()
