import unittest
from chatlaws.engine import World
from chatlaws.lawtable import LAW_TABLE


class Law005(unittest.TestCase):
    """when ball hits crate it turns yellow"""

    def test_ball_hits_crate_turns_yellow(self):
        w = World({"ball": "white", "crate": "gray"}, laws=LAW_TABLE)
        w.collide("ball", "crate")
        self.assertEqual(w.color("ball"), "yellow")

    def test_unrelated_pair_unchanged(self):
        w = World({"ball": "white", "crate": "gray"}, laws=LAW_TABLE)
        w.collide("crate", "ball")
        self.assertEqual(w.color("ball"), "white")


if __name__ == "__main__":
    unittest.main()
