import unittest
from chatlaws.engine import World
from chatlaws.lawtable import LAW_TABLE


class Law002(unittest.TestCase):
    """when ball hits floor it turns blue"""

    def test_ball_hits_floor_turns_blue(self):
        w = World({"ball": "white", "floor": "gray"}, laws=LAW_TABLE)
        w.collide("ball", "floor")
        self.assertEqual(w.color("ball"), "blue")

    def test_unrelated_pair_unchanged(self):
        w = World({"ball": "white", "floor": "gray"}, laws=LAW_TABLE)
        w.collide("floor", "ball")
        self.assertEqual(w.color("ball"), "white")


if __name__ == "__main__":
    unittest.main()
