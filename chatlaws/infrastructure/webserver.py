"""Loopback-only static server: the page and state.json. Usable as an OBS browser source."""
import http.server
import os


def make_server(root: str, state_path: str, port: int = 8765) -> http.server.ThreadingHTTPServer:
    page = os.path.join(root, "web", "index.html")

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                f, ctype = page, "text/html; charset=utf-8"
            elif path == "/state.json":
                f, ctype = state_path, "application/json"
            else:
                self.send_error(404)
                return
            try:
                body = open(f, "rb").read()
            except OSError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
