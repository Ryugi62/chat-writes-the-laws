"""Local core loop: sentence -> compile -> red -> codex fixes engine -> green -> rulebook."""
import argparse
import json
import os
import subprocess
import sys
import time

from .application.ingest import Ingest
from .application.agent_prompt import build_prompt
from .domain.grammar import parse_sentence, GrammarError
from .domain.law import LawBook, Law
from .infrastructure.codex_runner import run_codex
from .infrastructure.rulebook import append_rule

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "laws.json")


def _tests(*extra):
    p = subprocess.run([sys.executable, "-m", "unittest"] + list(extra), cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def _load_book():
    b = LawBook()
    if os.path.exists(STATE):
        for d in json.load(open(STATE)):
            b.add(Law(**d))
    return b


def apply(author, text):
    t0 = time.time()
    book = _load_book()
    out = Ingest(book).submit(author, text)
    if out.status != "accepted":
        print("REJECTED reason=%s (text not shown, not stored, not sent to the agent)" % out.reason)
        return 2
    print("COMPILED law %03d -> tests/laws/%s" % (out.number, out.test_name))
    path = os.path.join(ROOT, "tests", "laws", out.test_name)
    open(path, "w").write(out.test_source)
    rc, log = _tests("tests.laws." + out.test_name[:-3])
    print("RED run (expected failure), exit=%d\n%s" % (rc, "\n".join(log.strip().splitlines()[-6:])))
    session = None
    if rc == 0:
        print("test already green: engine needs no fix")
    else:
        rc2, session, _ = run_codex(ROOT, build_prompt(out.test_name))
        print("CODEX exit=%d session_id=%s" % (rc2, session))
        rc, log = _tests("discover", "-s", "tests", "-t", ".")
        print("GREEN run exit=%d\n%s" % (rc, "\n".join(log.strip().splitlines()[-4:])))
        if rc != 0:
            os.remove(path)
            return 3
    json.dump([l.__dict__ for l in book.laws], open(STATE, "w"), indent=1)
    append_rule(os.path.join(ROOT, "RULEBOOK.md"), out.number, out.law.sentence, out.law.author)
    print("RULEBOOK +1: Law %03d by @%s  (%.0fs total)" % (out.number, out.law.author, time.time() - t0))
    if session:
        open(os.path.join(ROOT, "SESSIONS.log"), "a").write("law %03d %s\n" % (out.number, session))
    return 0


def watch(channel, seconds):
    from .infrastructure.twitch_irc import read_chat
    for user, _ch, text in read_chat(channel, seconds):
        try:
            parse_sentence(text)
            print("IN-GRAMMAR from @%s" % user)
        except GrammarError:
            print("dropped (outside grammar) from @%s" % user)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="chatlaws")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--author", required=True)
    a.add_argument("--text", required=True)
    w = sub.add_parser("watch")
    w.add_argument("channel")
    w.add_argument("--seconds", type=float, default=30)
    args = ap.parse_args(argv)
    return apply(args.author, args.text) if args.cmd == "apply" else watch(args.channel, args.seconds)


if __name__ == "__main__":
    sys.exit(main())
