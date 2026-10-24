import unittest
from chatlaws.infrastructure.codex_runner import extract_thread_id

class RunnerTest(unittest.TestCase):
    def test_extract(self):
        out = '{"type":"thread.started","thread_id":"abc-123"}\n{"type":"turn.started"}\n'
        self.assertEqual(extract_thread_id(out), "abc-123")

    def test_missing(self):
        self.assertIsNone(extract_thread_id('{"type":"turn.started"}\nnot json\n'))
