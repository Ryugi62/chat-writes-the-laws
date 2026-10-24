import re
from dataclasses import dataclass
from typing import Optional

from ..domain.grammar import parse_sentence, GrammarError
from ..domain.law import Law, LawBook, Conflict, Duplicate
from ..domain.testgen import render_test, test_file_name

_LOGIN = re.compile(r"^[a-z0-9_]{3,25}$")


@dataclass(frozen=True)
class Outcome:
    status: str                      # accepted | rejected
    reason: Optional[str] = None     # grammar | conflict | duplicate | author
    law: Optional[Law] = None
    number: Optional[int] = None
    test_name: Optional[str] = None
    test_source: Optional[str] = None


class Ingest:
    """Chat sentence in, test source out. Rejected text is never stored or echoed."""

    def __init__(self, book: Optional[LawBook] = None):
        self.book = book or LawBook()

    def submit(self, author: str, text: str) -> Outcome:
        if not isinstance(author, str) or not _LOGIN.match(author):
            return Outcome("rejected", "author")
        try:
            p = parse_sentence(text)
        except GrammarError:
            return Outcome("rejected", "grammar")
        law = Law(p.subject, p.obj, p.color, author)
        try:
            n = self.book.add(law)
        except Conflict:
            return Outcome("rejected", "conflict")
        except Duplicate:
            return Outcome("rejected", "duplicate")
        return Outcome("accepted", None, law, n, test_file_name(law, n), render_test(law, n))
