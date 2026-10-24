"""Pure IRC line parsing (no I/O)."""
import re
from typing import Optional, Tuple

_PRIV = re.compile(r"^(?:@\S+ )?:([A-Za-z0-9_]+)![^ ]+ PRIVMSG #([A-Za-z0-9_]+) :(.*)$")


def parse_line(line: str) -> Optional[Tuple[str, str, str]]:
    m = _PRIV.match(line)
    if not m:
        return None
    return m.group(1).lower(), m.group(2).lower(), m.group(3)
