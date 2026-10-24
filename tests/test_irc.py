import unittest
from chatlaws.infrastructure.twitch_irc import parse_line

class IrcTest(unittest.TestCase):
    def test_privmsg(self):
        r = parse_line(":imprabs!imprabs@imprabs.tmi.twitch.tv PRIVMSG #xqc :hello there")
        self.assertEqual(r, ("imprabs", "xqc", "hello there"))

    def test_privmsg_with_colon_in_text(self):
        r = parse_line(":a_b1!a_b1@a_b1.tmi.twitch.tv PRIVMSG #c :when x: y")
        self.assertEqual(r[2], "when x: y")

    def test_non_privmsg_ignored(self):
        for l in [":tmi.twitch.tv 001 justinfan1 :Welcome, GLHF!",
                  ":justinfan1!justinfan1@justinfan1.tmi.twitch.tv JOIN #xqc",
                  "PING :tmi.twitch.tv"]:
            self.assertIsNone(parse_line(l))

    def test_tagged_privmsg(self):
        r = parse_line("@badge-info=;color=#FF0000 :bob_2!bob_2@bob_2.tmi.twitch.tv PRIVMSG #chan :hi")
        self.assertEqual(r, ("bob_2", "chan", "hi"))
