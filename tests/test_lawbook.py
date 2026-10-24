import unittest
from chatlaws.domain.law import Law, LawBook, Conflict, Duplicate
from chatlaws.domain.testgen import render_test

def L(c="red", a="alice_01"): return Law("ball", "wall", c, a)

class LawBookTest(unittest.TestCase):
    def test_accepts_first_and_numbers_it(self):
        b = LawBook(); n = b.add(L())
        self.assertEqual(n, 1)
        self.assertEqual(len(b.laws), 1)

    def test_conflict_rejected(self):
        b = LawBook(); b.add(L("red"))
        with self.assertRaises(Conflict):
            b.add(L("blue", "bob_02"))
        self.assertEqual(len(b.laws), 1)

    def test_duplicate_rejected(self):
        b = LawBook(); b.add(L())
        with self.assertRaises(Duplicate):
            b.add(L(a="carol_03"))

    def test_reverse_pair_is_distinct(self):
        b = LawBook(); b.add(L())
        b.add(Law("wall", "ball", "blue", "bob_02"))
        self.assertEqual(len(b.laws), 2)

class TestGenTest(unittest.TestCase):
    def test_render_is_valid_python_and_names_the_law(self):
        src = render_test(L(), 1)
        compile(src, "t.py", "exec")
        self.assertIn("ball", src); self.assertIn("red", src)
        self.assertIn("class Law001", src)

    def test_render_contains_no_author(self):
        self.assertNotIn("alice_01", render_test(L(), 1))


class PopTest(unittest.TestCase):
    def test_pop_last_rolls_back(self):
        b = LawBook(); b.add(L("red"))
        b.pop_last()
        self.assertEqual(b.laws, [])
        self.assertEqual(b.add(L("blue")), 1)
