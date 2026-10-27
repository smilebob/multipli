"""
Tests unitaires pour la génération des questions et des options QCM.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multipli.game_view import Question


class TestQuestions(unittest.TestCase):
    def test_direct_question(self):
        q = Question(6, 7, "direct")
        self.assertEqual(q.correct_answer, 42)
        self.assertEqual(q.display_text, "6 × 7 = ?")
        self.assertEqual(q.full_equation, "6 × 7 = 42")

        opts = q.generate_options()
        self.assertEqual(len(opts), 4)
        self.assertEqual(len(set(opts)), 4)
        self.assertIn(42, opts)
        self.assertTrue(all(x > 0 for x in opts))

    def test_missing_factor_a(self):
        q = Question(8, 4, "missing_factor_a")
        self.assertEqual(q.correct_answer, 8)
        self.assertEqual(q.display_text, "? × 4 = 32")
        self.assertEqual(q.full_equation, "8 × 4 = 32")

        opts = q.generate_options()
        self.assertEqual(len(opts), 4)
        self.assertEqual(len(set(opts)), 4)
        self.assertIn(8, opts)
        self.assertTrue(all(x > 0 for x in opts))

    def test_missing_factor_b(self):
        q = Question(9, 5, "missing_factor_b")
        self.assertEqual(q.correct_answer, 5)
        self.assertEqual(q.display_text, "9 × ? = 45")
        self.assertEqual(q.full_equation, "9 × 5 = 45")

        opts = q.generate_options()
        self.assertEqual(len(opts), 4)
        self.assertEqual(len(set(opts)), 4)
        self.assertIn(5, opts)
        self.assertTrue(all(x > 0 for x in opts))

    def test_multiple_iterations_always_valid(self):
        for _ in range(50):
            for q_type in ["direct", "missing_factor_a", "missing_factor_b"]:
                t = 7
                m = 8
                q = Question(t, m, q_type)
                opts = q.generate_options()
                self.assertEqual(len(opts), 4)
                self.assertEqual(len(set(opts)), 4)
                self.assertIn(q.correct_answer, opts)


if __name__ == "__main__":
    unittest.main()
