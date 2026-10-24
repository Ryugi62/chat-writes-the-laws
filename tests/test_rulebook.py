import unittest, tempfile, os
from chatlaws.infrastructure.rulebook import append_rule

class RulebookTest(unittest.TestCase):
    def test_append_writes_author_line(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "RULEBOOK.md")
            append_rule(p, 1, "when ball hits wall it turns red", "alice_01")
            append_rule(p, 2, "when crate hits floor it turns blue", "bob_02")
            t = open(p).read()
            self.assertIn("alice_01", t); self.assertIn("bob_02", t)
            self.assertEqual(t.count("\n- "), 2)

    def test_header_written_once(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "RULEBOOK.md")
            append_rule(p, 1, "x", "a_b1"); append_rule(p, 2, "y", "c_d2")
            self.assertEqual(open(p).read().count("# Rulebook"), 1)
