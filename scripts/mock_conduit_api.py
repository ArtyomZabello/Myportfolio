"""Minimal Conduit-compatible API stub for local runs without Docker."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Final

_HOST: Final[str] = "0.0.0.0"
_PORT: Final[int] = 8000


class ConduitMockHandler(BaseHTTPRequestHandler):
    """Serve the public endpoints required by API, load, and security checks."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default stdout logging during automated runs."""
        return

    def do_GET(self) -> None:
        """Handle supported Conduit GET routes."""
        payload: dict[str, Any]
        if self.path == "/api/tags":
            payload = {"tags": ["testing", "automation", "conduit"]}
        elif self.path.startswith("/api/articles"):
            payload = {
                "articles": [],
                "articlesCount": 0,
            }
        else:
            self.send_error(404, "Not Found")
            return

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    """Start the mock Conduit API server."""
    server = ThreadingHTTPServer((_HOST, _PORT), ConduitMockHandler)
    print(f"Mock Conduit API listening on http://localhost:{_PORT}/api")
    server.serve_forever()


if __name__ == "__main__":
    main()
