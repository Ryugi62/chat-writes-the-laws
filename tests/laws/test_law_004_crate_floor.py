import unittest
from chatlaws.engine import World
from chatlaws.lawtable import LAW_TABLE


class Law004(unittest.TestCase):
    """when crate hits floor it turns orange"""

    def test_crate_hits_floor_turns_orange(self):
        w = World({"crate": "white", "floor": "gray"}, laws=LAW_TABLE)
        w.collide("crate", "floor")
        self.assertEqual(w.color("crate"), "orange")

    def test_unrelated_pair_unchanged(self):
        w = World({"crate": "white", "floor": "gray"}, laws=LAW_TABLE)
        w.collide("floor", "crate")
        self.assertEqual(w.color("crate"), "white")


if __name__ == "__main__":
    unittest.main()
