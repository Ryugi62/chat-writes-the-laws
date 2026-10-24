"""Constraint-sentence grammar: the only door from chat text to a Law."""
import re
from dataclasses import dataclass

THINGS = ("ball", "wall", "floor", "crate")
COLORS = ("red", "green", "blue", "yellow", "purple", "orange", "white")
MAX_LEN = 60

_RE = re.compile(r"^when (%s) hits (%s) it turns (%s)$" % ("|".join(THINGS), "|".join(THINGS), "|".join(COLORS)))


class GrammarError(ValueError):
    """Raised without echoing the offending text."""


@dataclass(frozen=True)
class Parsed:
    subject: str
    obj: str
    color: str


def parse_sentence(text: str) -> Parsed:
    if not isinstance(text, str) or not text.isascii():
        raise GrammarError("grammar")
    t = text.strip().lower().rstrip(".!")
    t = re.sub(r"\s+", " ", t)
    if not t or len(t) > MAX_LEN:
        raise GrammarError("grammar")
    m = _RE.match(t)
    if not m:
        raise GrammarError("grammar")
    return Parsed(*m.groups())
