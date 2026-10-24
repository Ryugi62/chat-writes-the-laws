"""The only text that reaches Codex. Built from a compiled test file name, never from chat."""
import re

_NAME = re.compile(r"^test_law_\d{3}_[a-z]+_[a-z]+\.py$")


def build_prompt(test_name: str) -> str:
    if not _NAME.match(test_name):
        raise ValueError("not a compiled law test")
    return (
        "The new compiled test tests/laws/%s fails. Edit ONLY chatlaws/engine.py so that every test under "
        "tests/ passes (python3 -m unittest discover -s tests -t .). Do not edit anything under tests/. "
        "Implement the World laws generically (any law tuple of subject, object, color), not as a special "
        "case for this one test. Keep it stdlib-only." % test_name
    )
