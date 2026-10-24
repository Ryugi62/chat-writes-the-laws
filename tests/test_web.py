import json
import os
import re
import tempfile
import threading
import unittest
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "web", "index.html")


class WebTest(unittest.TestCase):
    def test_page_is_self_contained(self):
        src = open(HTML, encoding="utf8").read()
        self.assertIsNone(re.search(r"(https?:)?//[a-z0-9.-]+\.[a-z]{2,}", src, re.I), "external URL found")
        self.assertIn("state.json", src)
        self.assertIn("conflict", src)
        self.assertIn("<canvas", src)

    def test_server_serves_page_and_state_on_loopback(self):
        from chatlaws.infrastructure.webserver import make_server
        d = tempfile.mkdtemp()
        sp = os.path.join(d, "state.json")
        json.dump({"laws": [], "events": [], "dropped": 0}, open(sp, "w"))
        srv = make_server(ROOT, sp, 0)
        self.assertEqual(srv.server_address[0], "127.0.0.1")
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            base = "http://127.0.0.1:%d" % srv.server_address[1]
            self.assertIn(b"<canvas", urllib.request.urlopen(base + "/").read())
            self.assertEqual(json.load(urllib.request.urlopen(base + "/state.json"))["dropped"], 0)
        finally:
            srv.shutdown()
            srv.server_close()
