import unittest
from chatlaws.engine import World
from chatlaws.lawtable import LAW_TABLE


class Law003(unittest.TestCase):
    """when crate hits wall it turns green"""

    def test_crate_hits_wall_turns_green(self):
        w = World({"crate": "white", "wall": "gray"}, laws=LAW_TABLE)
        w.collide("crate", "wall")
        self.assertEqual(w.color("crate"), "green")

    def test_unrelated_pair_unchanged(self):
        w = World({"crate": "white", "wall": "gray"}, laws=LAW_TABLE)
        w.collide("wall", "crate")
        self.assertEqual(w.color("crate"), "white")


if __name__ == "__main__":
    unittest.main()
