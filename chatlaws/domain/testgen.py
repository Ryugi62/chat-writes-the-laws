"""Law -> executable test source. Contains no author name and no raw chat text."""
from itertools import product

from .grammar import THINGS, COLORS
from .law import Law

_TEMPLATE = '''import unittest
from chatlaws.engine import World
from chatlaws.lawtable import LAW_TABLE


class Law@NUM@(unittest.TestCase):
    """{sentence}"""

    def test_{subject}_hits_{obj}_turns_{color}(self):
        w = World({{"{subject}": "white", "{obj}": "gray"}}, laws=LAW_TABLE)
        w.collide("{subject}", "{obj}")
        self.assertEqual(w.color("{subject}"), "{color}")
{unrelated}

if __name__ == "__main__":
    unittest.main()
'''


_UNRELATED = '''
    def test_unrelated_pair_unchanged(self):
        w = World({{"{subject}": "white", "{obj}": "gray"}}, laws=LAW_TABLE)
        w.collide("{obj}", "{subject}")
        self.assertEqual(w.color("{subject}"), "white")
'''


def _compile(subject: str, obj: str, color: str) -> str:
    law = Law(subject, obj, color, "-")
    extra = _UNRELATED.format(subject=subject, obj=obj) if subject != obj else ""
    return _TEMPLATE.format(sentence=law.sentence, subject=subject, obj=obj, color=color, unrelated=extra)


# Precompiled once at import: 4 x 4 x 7 = 112 grammar combinations. Only the law number is filled in later.
PRECOMPILED = {(s, o, c): _compile(s, o, c) for s, o, c in product(THINGS, THINGS, COLORS)}


def test_file_name(law: Law, num: int) -> str:
    return "test_law_%03d_%s_%s.py" % (num, law.subject, law.obj)


def render_test(law: Law, num: int) -> str:
    return PRECOMPILED[(law.subject, law.obj, law.color)].replace("@NUM@", "%03d" % num)
