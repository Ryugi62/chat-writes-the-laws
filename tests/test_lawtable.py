import unittest
from chatlaws.domain.law import Law
from chatlaws.domain.testgen import PRECOMPILED, render_test, test_file_name
from chatlaws.application.agent_prompt import build_prompt


class LawTableTest(unittest.TestCase):
    def test_table_is_the_single_patch_target(self):
        from chatlaws import lawtable
        self.assertIsInstance(lawtable.LAW_TABLE, list)

    def test_precompiled_covers_every_grammar_combination(self):
        self.assertEqual(len(PRECOMPILED), 4 * 4 * 7)

    def test_render_uses_precompiled_and_reads_the_table(self):
        src = render_test(Law("crate", "floor", "green", "alice_01"), 7)
        self.assertIn("from chatlaws.lawtable import LAW_TABLE", src)
        self.assertIn("class Law007", src)
        self.assertNotIn("alice_01", src)
        compile(src, "x", "exec")

    def test_generated_test_is_red_on_an_empty_table(self):
        import types
        from chatlaws import lawtable
        src = render_test(Law("ball", "floor", "blue", "x_yz"), 1)
        mod = types.ModuleType("gen")
        old = list(lawtable.LAW_TABLE)
        lawtable.LAW_TABLE[:] = []
        try:
            exec(compile(src, "gen", "exec"), mod.__dict__)
            import unittest as u
            r = u.TextTestRunner(stream=open("/dev/null", "w")).run(u.defaultTestLoader.loadTestsFromModule(mod))
            self.assertFalse(r.wasSuccessful())
            lawtable.LAW_TABLE[:] = [("ball", "floor", "blue")]
            r = u.TextTestRunner(stream=open("/dev/null", "w")).run(u.defaultTestLoader.loadTestsFromModule(mod))
            self.assertTrue(r.wasSuccessful())
        finally:
            lawtable.LAW_TABLE[:] = old

    def test_prompt_scope_is_the_table_only(self):
        p = build_prompt(test_file_name(Law("ball", "floor", "blue", "a_b"), 2))
        self.assertIn("chatlaws/lawtable.py", p)
        self.assertNotIn("engine.py", p)
        self.assertNotIn("a_b", p)
