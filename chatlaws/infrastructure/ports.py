"""Real ports for the pipeline: files, unittest subprocesses, codex exec."""
import json
import os
import subprocess
import sys

from .codex_runner import run_codex
from .rulebook import append_rule
from ..application.agent_prompt import build_prompt


class LocalPorts:
    def __init__(self, root: str, patcher: str = "codex", codex_effort: str = "low"):
        self.root, self.patcher, self.effort = root, patcher, codex_effort
        self.table = os.path.join(root, "chatlaws", "lawtable.py")
        self._snapshot = None

    def _unittest(self, *args):
        p = subprocess.run([sys.executable, "-m", "unittest"] + list(args), cwd=self.root,
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def write_test(self, name, src):
        with open(os.path.join(self.root, "tests", "laws", name), "w") as f:
            f.write(src)

    def remove_test(self, name):
        try:
            os.remove(os.path.join(self.root, "tests", "laws", name))
        except OSError:
            pass

    def run_tests(self, name):
        return self._unittest("tests.laws." + name[:-3])

    def run_all(self):
        return self._unittest("discover", "-s", "tests", "-t", ".")

    def patch(self, name):
        self._snapshot = open(self.table).read()
        rc, session, _ = run_codex(self.root, build_prompt(name), effort=self.effort)
        return rc, session

    def restore(self):
        if self._snapshot is not None:
            open(self.table, "w").write(self._snapshot)

    def persist(self, laws):
        with open(os.path.join(self.root, "laws.json"), "w") as f:
            json.dump([l.__dict__ for l in laws], f, indent=1)

    def rule(self, number, sentence, author):
        append_rule(os.path.join(self.root, "RULEBOOK.md"), number, sentence, author)

    def note_session(self, number, session):
        with open(os.path.join(self.root, "SESSIONS.log"), "a") as f:
            f.write("law %03d %s\n" % (number, session))
