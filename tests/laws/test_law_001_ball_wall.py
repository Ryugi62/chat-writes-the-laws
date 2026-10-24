import unittest
from chatlaws.engine import World


class Law001(unittest.TestCase):
    """when ball hits wall it turns red"""

    def test_ball_hits_wall_turns_red(self):
        w = World({"ball": "white", "wall": "gray"}, laws=[("ball", "wall", "red")])
        w.collide("ball", "wall")
        self.assertEqual(w.color("ball"), "red")

    def test_unrelated_pair_unchanged(self):
        w = World({"ball": "white", "wall": "gray"}, laws=[("ball", "wall", "red")])
        w.collide("wall", "ball")
        self.assertEqual(w.color("ball"), "white")


if __name__ == "__main__":
    unittest.main()
