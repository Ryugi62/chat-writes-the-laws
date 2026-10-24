"""World simulation with directional collision laws that recolor the subject."""


class World:
    def __init__(self, colors, laws=()):
        self._colors = dict(colors)
        self._laws = list(laws)

    def color(self, name):
        return self._colors[name]

    def collide(self, a, b):
        for subject, obj, color in self._laws:
            if (subject, obj) == (a, b):
                self._colors[subject] = color
