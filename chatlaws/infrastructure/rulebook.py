import os


def append_rule(path: str, number: int, sentence: str, author: str) -> None:
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf8") as f:
        if new:
            f.write("# Rulebook\n\nLaws written by chat. Each one passed the grammar compiler and an executable test.\n")
        f.write("\n- Law %03d: `%s` - written by @%s" % (number, sentence, author))
        f.write("\n")
