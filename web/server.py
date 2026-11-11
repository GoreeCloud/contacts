#!/usr/bin/env python3
"""Development-only static Contacts web server; binds loopback, no APIs.

Never use this server to expose private contacts or provide production auth.
No personal data is accepted, logged, or stored on the server.
"""
from __future__ import annotations

from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PUBLIC = frozenset({"/", "/index.html", "/style.css", "/main.mjs",
                    "/model.mjs", "/store.mjs", "/vcard.mjs", "/gc-ui/tokens.css",
                    "/assets/goreecloud-logo.svg"})
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; "
       "img-src 'self'; connect-src 'none'; font-src 'none'; "
       "base-uri 'none'; form-action 'none'; object-src 'none'; frame-src 'none'")

class ContactsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _allowed(self):
        url = self.path.split("?", 1)[0].split("#", 1)[0]
        if url not in PUBLIC:
            self.send_error(404, "Not found")
            return False
        self.path = "/index.html" if url == "/" else url
        return True

    def do_GET(self):
        if self._allowed():
            super().do_GET()

    def do_HEAD(self):
        if self._allowed():
            super().do_HEAD()

    def do_POST(self):
        self.send_error(405, "Read-only static server")

    def list_directory(self, path):
        self.send_error(404, "Directory listing disabled")
        return None

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # Prevent URL paths or query strings from entering shared logs.
        pass


def main(argv=None):
    p = ArgumentParser(description="Run GoreeCloud Contacts development web preview on loopback")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args(argv)
    if not 0 <= args.port <= 65535:
        p.error("Port must be between 0 and 65535")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), ContactsHandler)
    try:
        print("Contacts static preview on http://127.0.0.1:" + str(server.server_port), flush=True)
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
