"""Chat intake. Grammar is the filter: only in-grammar sentences are queued; the rest only bump a counter."""
import collections
import threading
from typing import Callable, Optional, Tuple

from ..domain.grammar import parse_sentence, GrammarError
from ..domain.irc import parse_line


class Watcher:
    def __init__(self, on_drop: Callable[[], None], log: Callable[[str], None] = print):
        self._q, self._lock, self.on_drop, self.log = collections.deque(), threading.Lock(), on_drop, log

    def feed(self, user: str, text: str) -> bool:
        try:
            parse_sentence(text)
        except GrammarError:
            self.on_drop()
            return False
        with self._lock:
            self._q.append((user, text))
        self.log("queued (in grammar)")
        return True

    def feed_irc(self, line: str) -> bool:
        r = parse_line(line)
        return self.feed(r[0], r[2]) if r else False

    def pending(self) -> int:
        with self._lock:
            return len(self._q)

    def take(self) -> Optional[Tuple[str, str]]:
        with self._lock:
            return self._q.popleft() if self._q else None
