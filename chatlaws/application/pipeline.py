"""Live loop for one sentence: compile -> red -> patch -> green -> rulebook -> state.json (what the screen shows)."""
import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from .ingest import Ingest
from ..domain.law import LawBook

MAX_EVENTS = 8


@dataclass
class Result:
    status: str
    reason: Optional[str] = None
    number: Optional[int] = None
    session: Optional[str] = None
    timings: Dict[str, float] = field(default_factory=dict)


class Pipeline:
    """Rejected text is never stored, shown or logged: only counters and in-grammar sentences leave here."""

    def __init__(self, book: LawBook, state_path: str, ports, log: Callable[[str], None] = print,
                 clock: Callable[[], float] = time.monotonic):
        self.book, self.state_path, self.ports, self.log, self.clock = book, state_path, ports, log, clock
        self.ingest = Ingest(book)
        self.events, self.dropped = [], 0
        self._lock = threading.RLock()
        self._write()

    # -- state.json (the only thing the screen reads) --
    def _write(self):
        with self._lock:
            laws = [{"n": i + 1, "subject": l.subject, "obj": l.obj, "color": l.color,
                     "author": l.author, "sentence": l.sentence} for i, l in enumerate(self.book.laws)]
            doc = {"laws": laws, "events": self.events[-MAX_EVENTS:], "dropped": self.dropped,
                   "updated": time.time()}
            tmp = self.state_path + ".tmp"
            with open(tmp, "w", encoding="utf8") as f:
                json.dump(doc, f)
            os.replace(tmp, self.state_path)

    def note_dropped(self):
        with self._lock:
            self.dropped += 1
            self._write()

    def _event(self, kind, sentence, author):
        self.events.append({"kind": kind, "sentence": sentence, "author": author})

    # -- one sentence --
    def process(self, author: str, text: str) -> Result:
        t0 = self.clock()
        out = self.ingest.submit(author, text)
        if out.status != "accepted":
            if out.reason in ("conflict", "duplicate"):
                # in-grammar, so the sentence is rebuilt from parsed fields, never echoed from the raw text
                with self._lock:
                    self._event(out.reason, _rebuild(text), author)
                    self._write()
            else:
                self.note_dropped()
                self.log("dropped (outside grammar)")
            return Result("rejected", out.reason)
        n, name, p = out.number, out.test_name, self.ports
        tm = {}
        p.write_test(name, out.test_source)
        t1 = self.clock(); tm["compile"] = t1 - t0
        rc, _ = p.run_tests(name)
        t2 = self.clock(); tm["red"] = t2 - t1
        session = None
        if rc != 0:
            prc, session = p.patch(name)
            t3 = self.clock(); tm["patch"] = t3 - t2
            ok = prc == 0 and p.run_tests(name)[0] == 0 and p.run_all()[0] == 0
        else:
            t3 = self.clock(); tm["patch"] = 0.0
            ok = True
        t4 = self.clock(); tm["green"] = t4 - t3
        if not ok:
            p.remove_test(name)
            p.restore()
            self.book.pop_last()
            self.log("law %03d patch failed, rolled back" % n)
            return Result("rejected", "patch", n, session, tm)
        p.persist(self.book.laws)
        p.rule(n, out.law.sentence, out.law.author)
        if session:
            p.note_session(n, session)
        with self._lock:
            self._event("accepted", out.law.sentence, out.law.author)
            self._write()
        tm["total"] = self.clock() - t0
        self.log("law %03d accepted by @%s in %.1fs" % (n, author, tm["total"]))
        return Result("accepted", None, n, session, tm)


def _rebuild(text):
    from ..domain.grammar import parse_sentence
    p = parse_sentence(text)
    return "when %s hits %s it turns %s" % (p.subject, p.obj, p.color)
