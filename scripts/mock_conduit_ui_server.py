"""Minimal Conduit-compatible UI stub for CI and local runs without a frontend container."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Final

_HOST: Final[str] = "0.0.0.0"
_PORT: Final[int] = 4200
_UI_DIR = Path(__file__).resolve().parent / "mock_conduit_ui"


class ConduitUiMockHandler(BaseHTTPRequestHandler):
    """Serve static pages that match Conduit UI page object selectors."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default stdout logging during automated runs."""
        return

    def do_GET(self) -> None:
        """Route supported UI paths to static HTML fixtures."""
        route = self.path.split("?", maxsplit=1)[0]
        if route in {"/", "/index.html"}:
            content = (_UI_DIR / "index.html").read_text(encoding="utf-8")
        elif route == "/login":
            content = (_UI_DIR / "login.html").read_text(encoding="utf-8")
        else:
            self.send_error(404, "Not Found")
            return

        body = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    """Start the mock Conduit UI server."""
    server = ThreadingHTTPServer((_HOST, _PORT), ConduitUiMockHandler)
    print(f"Mock Conduit UI listening on http://localhost:{_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
