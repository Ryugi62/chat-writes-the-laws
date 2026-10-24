"""Law -> executable test source. Contains no author name and no raw chat text."""
from .law import Law

_TEMPLATE = '''import unittest
from chatlaws.engine import World


class Law{num:03d}(unittest.TestCase):
    """{sentence}"""

    def test_{subject}_hits_{obj}_turns_{color}(self):
        w = World({{"{subject}": "white", "{obj}": "gray"}}, laws=[("{subject}", "{obj}", "{color}")])
        w.collide("{subject}", "{obj}")
        self.assertEqual(w.color("{subject}"), "{color}")

    def test_unrelated_pair_unchanged(self):
        w = World({{"{subject}": "white", "{obj}": "gray"}}, laws=[("{subject}", "{obj}", "{color}")])
        w.collide("{obj}", "{subject}")
        self.assertEqual(w.color("{subject}"), "white")


if __name__ == "__main__":
    unittest.main()
'''


def test_file_name(law: Law, num: int) -> str:
    return "test_law_%03d_%s_%s.py" % (num, law.subject, law.obj)


def render_test(law: Law, num: int) -> str:
    return _TEMPLATE.format(num=num, sentence=law.sentence, subject=law.subject, obj=law.obj, color=law.color)
