"""The only text that reaches Codex. Built from a compiled test file name, never from chat."""
import re

_NAME = re.compile(r"^test_law_\d{3}_[a-z]+_[a-z]+\.py$")


def build_prompt(test_name: str) -> str:
    if not _NAME.match(test_name):
        raise ValueError("not a compiled law test")
    return (
        "The new compiled test tests/laws/%s fails because the law table lacks its entry. "
        "Edit ONLY chatlaws/lawtable.py: add the one (subject, object, color) tuple that test expects to "
        "LAW_TABLE, in the same style as the existing entries, with a '# Law NNN' comment. "
        "Do not edit anything else, do not run the test suite (the caller runs it). Stdlib only." % test_name
    )
