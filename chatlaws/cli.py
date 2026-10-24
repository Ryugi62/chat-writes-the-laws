"""CLI: apply one sentence, or run the live loop (IRC -> grammar -> queue -> test -> patch -> screen)."""
import argparse
import json
import os
import sys
import threading
import time

from .application.pipeline import Pipeline
from .application.watch import Watcher
from .domain.law import LawBook, Law
from .infrastructure.ports import LocalPorts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "laws.json")
STATE_JSON = os.path.join(ROOT, "state.json")


def _load_book():
    b = LawBook()
    if os.path.exists(STATE):
        for d in json.load(open(STATE)):
            b.add(Law(**d))
    return b


def _pipeline(patcher_effort):
    return Pipeline(_load_book(), STATE_JSON, LocalPorts(ROOT, codex_effort=patcher_effort))


def _report(r):
    t = " ".join("%s=%.1fs" % (k, v) for k, v in r.timings.items())
    print("RESULT %s%s session=%s | %s" % (r.status, " reason=" + r.reason if r.reason else "", r.session, t))


def apply(author, text, effort):
    r = _pipeline(effort).process(author, text)
    _report(r)
    return 0 if r.status == "accepted" else 2


def live(channel, seconds, port, effort, inject):
    from .infrastructure.twitch_irc import read_chat
    from .infrastructure.webserver import make_server
    pipe = _pipeline(effort)
    w = Watcher(on_drop=pipe.note_dropped, log=lambda m: print(m, flush=True))
    srv = make_server(ROOT, STATE_JSON, port)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("screen: http://127.0.0.1:%d/  (OBS browser source)" % srv.server_address[1], flush=True)
    end = time.time() + seconds

    def reader():
        if not channel:
            return
        try:
            for user, _ch, text in read_chat(channel, seconds):
                w.feed(user, text)
        except OSError as e:
            print("irc stopped: %s" % type(e).__name__, flush=True)

    threading.Thread(target=reader, daemon=True).start()
    for s in inject:  # developer input, labelled local_dev, never a viewer
        w.feed("local_dev", s)
    while time.time() < end or w.pending():
        item = w.take()
        if item:
            _report(pipe.process(*item))
        else:
            time.sleep(0.05)
    srv.shutdown()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="chatlaws")
    ap.add_argument("--effort", default="low", help="codex reasoning effort for the patch")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--author", required=True)
    a.add_argument("--text", required=True)
    w = sub.add_parser("live")
    w.add_argument("channel", nargs="?", default="")
    w.add_argument("--seconds", type=float, default=60)
    w.add_argument("--port", type=int, default=8765)
    w.add_argument("--inject", action="append", default=[], help="dev sentence, author local_dev")
    args = ap.parse_args(argv)
    if args.cmd == "apply":
        return apply(args.author, args.text, args.effort)
    return live(args.channel, args.seconds, args.port, args.effort, args.inject)


if __name__ == "__main__":
    sys.exit(main())
