import json
import os
import tempfile
import unittest
from chatlaws.application.pipeline import Pipeline
from chatlaws.domain.law import LawBook

MARK = "ZZINJECTZZ"


class Fake:
    """Ports with no subprocess: tests go red until patch() ran."""

    def __init__(self, patch_ok=True):
        self.files, self.patched, self.prompts, self.patch_ok, self.removed = {}, set(), [], patch_ok, []
        self.rules = []

    def write_test(self, name, src):
        self.files[name] = src

    def remove_test(self, name):
        self.removed.append(name)
        self.files.pop(name, None)

    def run_tests(self, name):
        return (0, "ok") if name in self.patched else (1, "AssertionError")

    def run_all(self):
        return (0, "ok") if self.patch_ok else (1, "FAILED")

    def patch(self, name):
        self.prompts.append(name)
        if self.patch_ok:
            self.patched.add(name)
        return (0 if self.patch_ok else 1), "sess-%d" % len(self.prompts)

    def rule(self, number, sentence, author):
        self.rules.append((number, sentence, author))

    def restore(self):
        self.restored = getattr(self, "restored", 0) + 1

    def note_session(self, number, session):
        self.sessions = getattr(self, "sessions", []) + [(number, session)]

    def persist(self, laws):
        self.persisted = list(laws)


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.state = os.path.join(self.d, "state.json")
        self.f = Fake()
        self.logs = []
        t = iter(x * 0.5 for x in range(1, 200))
        self.p = Pipeline(LawBook(), self.state, self.f, log=self.logs.append, clock=lambda: next(t))

    def st(self):
        return json.load(open(self.state))

    def test_accept_goes_red_patch_green_and_state_has_author(self):
        r = self.p.process("alice_01", "when ball hits wall it turns red")
        self.assertEqual((r.status, r.number, r.session), ("accepted", 1, "sess-1"))
        self.assertEqual(self.f.rules, [(1, "when ball hits wall it turns red", "alice_01")])
        s = self.st()
        self.assertEqual(s["laws"][0]["author"], "alice_01")
        self.assertEqual(s["laws"][0]["color"], "red")
        self.assertEqual(s["events"][-1]["kind"], "accepted")
        for k in ("compile", "red", "patch", "green", "total"):
            self.assertIn(k, r.timings)
        self.assertGreater(r.timings["total"], 0)
        self.assertEqual(self.f.sessions, [(1, "sess-1")])
        self.assertEqual(len(self.f.persisted), 1)

    def test_grammar_reject_only_counts(self):
        r = self.p.process("alice_01", "when ball hits wall it turns red; %s" % MARK)
        self.assertEqual((r.status, r.reason), ("rejected", "grammar"))
        self.assertEqual(self.f.files, {})
        self.assertEqual(self.f.prompts, [])
        raw = open(self.state).read()
        self.assertNotIn(MARK, raw)
        self.assertNotIn("alice_01", raw)
        self.assertEqual(self.st()["dropped"], 1)
        self.assertNotIn(MARK, "\n".join(self.logs))
        self.assertNotIn("alice_01", "\n".join(self.logs))

    def test_conflict_shows_toast_and_changes_nothing(self):
        self.p.process("alice_01", "when ball hits wall it turns red")
        r = self.p.process("bob_02", "when ball hits wall it turns blue")
        self.assertEqual((r.status, r.reason), ("rejected", "conflict"))
        s = self.st()
        self.assertEqual(len(s["laws"]), 1)
        self.assertEqual(s["events"][-1]["kind"], "conflict")
        self.assertEqual(s["events"][-1]["sentence"], "when ball hits wall it turns blue")
        self.assertEqual(len(self.f.prompts), 1)

    def test_failed_patch_rolls_back(self):
        f = Fake(patch_ok=False)
        p = Pipeline(LawBook(), self.state, f, log=lambda m: None)
        r = p.process("alice_01", "when ball hits wall it turns red")
        self.assertEqual((r.status, r.reason), ("rejected", "patch"))
        self.assertEqual(len(f.removed), 1)
        self.assertEqual(f.restored, 1)
        self.assertEqual(self.st()["laws"], [])
        self.assertEqual(p.book.laws, [])
        p2 = p.process("bob_02", "when ball hits wall it turns blue")
        self.assertEqual(p2.reason, "patch")  # book was rolled back: not a conflict

    def test_note_dropped(self):
        self.p.note_dropped()
        self.p.note_dropped()
        self.assertEqual(self.st()["dropped"], 2)
