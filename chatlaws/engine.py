"""World simulation. Baseline: laws are accepted but collisions change nothing."""


class World:
    def __init__(self, colors, laws=()):
        self._colors = dict(colors)
        self._laws = list(laws)

    def color(self, name):
        return self._colors[name]

    def collide(self, a, b):
        return None
