"""Anonymous read-only Twitch IRC (justinfan). No login, no developer app."""
import re
import socket
import ssl
import time
from typing import Iterator, Tuple

from ..domain.irc import parse_line

def read_chat(channel: str, seconds: float = 30.0) -> Iterator[Tuple[str, str, str]]:
    ctx = ssl.create_default_context()
    raw = socket.create_connection(("irc.chat.twitch.tv", 6697), timeout=10)
    s = ctx.wrap_socket(raw, server_hostname="irc.chat.twitch.tv")
    s.settimeout(5)
    for cmd in ("PASS SCHMOOPIIE", "NICK justinfan48213", "JOIN #" + channel.lower()):
        s.sendall((cmd + "\r\n").encode())
    buf, end = "", time.time() + seconds
    try:
        while time.time() < end:
            try:
                buf += s.recv(4096).decode("utf8", "replace")
            except socket.timeout:
                continue
            while "\r\n" in buf:
                line, buf = buf.split("\r\n", 1)
                if line.startswith("PING"):
                    s.sendall(b"PONG :tmi.twitch.tv\r\n")
                    continue
                r = parse_line(line)
                if r:
                    yield r
    finally:
        s.close()
