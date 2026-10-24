from dataclasses import dataclass, field
from typing import List


class Conflict(Exception):
    pass


class Duplicate(Exception):
    pass


@dataclass(frozen=True)
class Law:
    subject: str
    obj: str
    color: str
    author: str

    @property
    def sentence(self) -> str:
        return "when %s hits %s it turns %s" % (self.subject, self.obj, self.color)


@dataclass
class LawBook:
    laws: List[Law] = field(default_factory=list)

    def add(self, law: Law) -> int:
        for old in self.laws:
            if (old.subject, old.obj) == (law.subject, law.obj):
                if old.color == law.color:
                    raise Duplicate()
                raise Conflict()
        self.laws.append(law)
        return len(self.laws)
