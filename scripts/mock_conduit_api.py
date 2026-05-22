"""In-memory Conduit-compatible API stub for local runs without Docker."""

from __future__ import annotations

import json
import re
import secrets
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Final
from urllib.parse import parse_qs, urlparse

_HOST: Final[str] = "0.0.0.0"
_PORT: Final[int] = 8000
_API_PREFIX: Final[str] = "/api"
_EMAIL_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slugify(title: str) -> str:
    """Convert an article title into a URL-friendly slug."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-") or "article"


def _author_profile(username: str, *, following: bool = False) -> dict[str, Any]:
    """Build a RealWorld-compatible embedded author/profile payload."""
    return {
        "username": username,
        "bio": None,
        "image": None,
        "following": following,
    }


@dataclass
class MockState:
    """Thread-safe in-memory storage backing the Conduit mock API."""

    users_by_email: dict[str, dict[str, str]] = field(default_factory=dict)
    tokens_by_value: dict[str, str] = field(default_factory=dict)
    articles_by_slug: dict[str, dict[str, Any]] = field(default_factory=dict)
    comments_by_slug: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    follows: set[tuple[str, str]] = field(default_factory=set)
    seeded_profiles: set[str] = field(
        default_factory=lambda: {"jake", "john", "alice", "bob"},
    )
    next_comment_id: int = 1
    slug_counts: dict[str, int] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def register_user(self, user_data: dict[str, str]) -> dict[str, Any]:
        """Register a user and return the RealWorld user response payload."""
        email = user_data["email"]
        username = user_data["username"]
        password = user_data["password"]

        if email in self.users_by_email:
            raise ValueError("duplicate_email")
        if "@" not in email or not _EMAIL_PATTERN.match(email):
            raise ValueError("invalid_email")

        self.users_by_email[email] = {
            "email": email,
            "username": username,
            "password": password,
            "bio": "",
            "image": "",
        }
        token = secrets.token_urlsafe(24)
        self.tokens_by_value[token] = email
        return {
            "user": {
                "email": email,
                "token": token,
                "username": username,
                "bio": None,
                "image": None,
            }
        }

    def login_user(self, credentials: dict[str, str]) -> dict[str, Any]:
        """Authenticate a user and return the RealWorld user response payload."""
        email = credentials.get("email", "")
        password = credentials.get("password", "")

        if not email or not password or "@" not in email:
            raise ValueError("invalid_credentials")
        stored = self.users_by_email.get(email)
        if stored is None or stored["password"] != password:
            raise LookupError("unknown_credentials")

        token = secrets.token_urlsafe(24)
        self.tokens_by_value[token] = email
        return {
            "user": {
                "email": stored["email"],
                "token": token,
                "username": stored["username"],
                "bio": None,
                "image": None,
            }
        }

    def resolve_user(self, token: str | None) -> dict[str, str] | None:
        """Resolve the authenticated user record from a bearer token."""
        if token is None:
            return None
        email = self.tokens_by_value.get(token)
        if email is None:
            return None
        return self.users_by_email.get(email)

    def unique_slug(self, title: str) -> str:
        """Generate a unique slug for a newly created article."""
        base_slug = _slugify(title)
        count = self.slug_counts.get(base_slug, 0)
        self.slug_counts[base_slug] = count + 1
        if count == 0:
            return base_slug
        return f"{base_slug}-{count + 1}"

    def create_article(
        self,
        author: dict[str, str],
        article_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create and persist an article owned by the authenticated author."""
        slug = self.unique_slug(str(article_data["title"]))
        timestamp = _utc_now_iso()
        article = {
            "slug": slug,
            "title": article_data["title"],
            "description": article_data["description"],
            "body": article_data["body"],
            "tagList": article_data.get("tagList", []),
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "favorited": False,
            "favoritesCount": 0,
            "author": _author_profile(author["username"]),
        }
        self.articles_by_slug[slug] = article
        self.comments_by_slug.setdefault(slug, [])
        return {"article": article}

    def list_articles(self, *, limit: int, offset: int) -> dict[str, Any]:
        """Return a paginated global feed sorted by creation time descending."""
        articles = sorted(
            self.articles_by_slug.values(),
            key=lambda item: item["createdAt"],
            reverse=True,
        )
        paginated = articles[offset : offset + limit]
        return {"articles": paginated, "articlesCount": len(articles)}

    def get_article(self, slug: str) -> dict[str, Any] | None:
        """Return a single article payload by slug."""
        article = self.articles_by_slug.get(slug)
        if article is None:
            return None
        return {"article": article}

    def update_article(
        self,
        slug: str,
        author: dict[str, str],
        article_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update an article when the authenticated user is the owner."""
        article = self.articles_by_slug.get(slug)
        if article is None:
            return None
        if article["author"]["username"] != author["username"]:
            raise PermissionError("forbidden")

        article.update(
            {
                "title": article_data["title"],
                "description": article_data["description"],
                "body": article_data["body"],
                "tagList": article_data.get("tagList", []),
                "updatedAt": _utc_now_iso(),
            },
        )
        return {"article": article}

    def delete_article(self, slug: str, author: dict[str, str]) -> bool:
        """Delete an article when the authenticated user is the owner."""
        article = self.articles_by_slug.get(slug)
        if article is None:
            return False
        if article["author"]["username"] != author["username"]:
            raise PermissionError("forbidden")
        del self.articles_by_slug[slug]
        self.comments_by_slug.pop(slug, None)
        return True

    def add_comment(
        self,
        slug: str,
        author: dict[str, str],
        body: str,
    ) -> dict[str, Any] | None:
        """Add a comment to an article as the authenticated user."""
        if slug not in self.articles_by_slug:
            return None
        timestamp = _utc_now_iso()
        comment = {
            "id": self.next_comment_id,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "body": body,
            "author": _author_profile(author["username"]),
        }
        self.next_comment_id += 1
        self.comments_by_slug.setdefault(slug, []).append(comment)
        return {"comment": comment}

    def list_comments(self, slug: str) -> dict[str, Any] | None:
        """Return all comments attached to an article."""
        if slug not in self.articles_by_slug:
            return None
        return {"comments": list(self.comments_by_slug.get(slug, []))}

    def delete_comment(self, slug: str, comment_id: int, author: dict[str, str]) -> bool:
        """Delete a comment when the authenticated user is the comment author."""
        comments = self.comments_by_slug.get(slug)
        if comments is None:
            return False
        for index, comment in enumerate(comments):
            if comment["id"] == comment_id:
                if comment["author"]["username"] != author["username"]:
                    raise PermissionError("forbidden")
                comments.pop(index)
                return True
        return False

    def get_profile(self, username: str, viewer: dict[str, str] | None) -> dict[str, Any] | None:
        """Return a profile payload, optionally annotated with follow state."""
        if username not in self.seeded_profiles and not any(
            user["username"] == username for user in self.users_by_email.values()
        ):
            return None
        following = False
        if viewer is not None:
            following = (viewer["username"], username) in self.follows
        return {"profile": _author_profile(username, following=following)}

    def follow_profile(self, username: str, follower: dict[str, str]) -> dict[str, Any] | None:
        """Follow a profile as the authenticated user."""
        profile = self.get_profile(username, follower)
        if profile is None:
            return None
        self.follows.add((follower["username"], username))
        return {"profile": _author_profile(username, following=True)}

    def unfollow_profile(self, username: str, follower: dict[str, str]) -> dict[str, Any] | None:
        """Unfollow a profile as the authenticated user."""
        profile = self.get_profile(username, follower)
        if profile is None:
            return None
        self.follows.discard((follower["username"], username))
        return {"profile": _author_profile(username, following=False)}


STATE = MockState()


class ConduitMockHandler(BaseHTTPRequestHandler):
    """Serve RealWorld-compatible Conduit routes backed by in-memory state."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default stdout logging during automated runs."""
        return

    def do_GET(self) -> None:
        """Handle supported Conduit GET routes."""
        parsed = urlparse(self.path)
        route_path = parsed.path
        query = parse_qs(parsed.query)

        if route_path == f"{_API_PREFIX}/tags":
            self._send_json(HTTPStatus.OK, {"tags": ["testing", "automation", "conduit"]})
            return

        if route_path == f"{_API_PREFIX}/articles":
            limit = int(query.get("limit", ["10"])[0])
            offset = int(query.get("offset", ["0"])[0])
            with STATE.lock:
                payload = STATE.list_articles(limit=limit, offset=offset)
            self._send_json(HTTPStatus.OK, payload)
            return

        if match := re.fullmatch(
            rf"{re.escape(_API_PREFIX)}/articles/([^/]+)/comments",
            route_path,
        ):
            slug = match.group(1)
            with STATE.lock:
                comments_payload = STATE.list_comments(slug)
            if comments_payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, comments_payload)
            return

        if match := re.fullmatch(rf"{re.escape(_API_PREFIX)}/articles/([^/]+)", route_path):
            slug = match.group(1)
            with STATE.lock:
                article_payload = STATE.get_article(slug)
            if article_payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, article_payload)
            return

        if match := re.fullmatch(rf"{re.escape(_API_PREFIX)}/profiles/([^/]+)", route_path):
            username = match.group(1)
            viewer = self._resolve_user()
            with STATE.lock:
                profile_payload = STATE.get_profile(username, viewer)
            if profile_payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, profile_payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})

    def do_POST(self) -> None:
        """Handle supported Conduit POST routes."""
        parsed = urlparse(self.path)
        route_path = parsed.path
        body = self._read_json_body()

        if route_path == f"{_API_PREFIX}/users":
            user_data = body.get("user", {})
            try:
                with STATE.lock:
                    payload = STATE.register_user(
                        {
                            "email": user_data.get("email", ""),
                            "username": user_data.get("username", ""),
                            "password": user_data.get("password", ""),
                        },
                    )
            except ValueError as exc:
                if str(exc) == "invalid_email":
                    self._send_json(
                        HTTPStatus.UNPROCESSABLE,
                        {"errors": {"body": ["Invalid email"]}},
                    )
                    return
                self._send_json(
                    HTTPStatus.UNPROCESSABLE,
                    {"errors": {"body": ["Duplicate email"]}},
                )
                return
            self._send_json(HTTPStatus.CREATED, payload)
            return

        if route_path == f"{_API_PREFIX}/users/login":
            credentials = body.get("user", {})
            try:
                with STATE.lock:
                    payload = STATE.login_user(credentials)
            except ValueError:
                self._send_json(
                    HTTPStatus.UNPROCESSABLE,
                    {"errors": {"body": ["Invalid credentials"]}},
                )
                return
            except LookupError:
                self._send_json(HTTPStatus.UNAUTHORIZED, {"errors": {"body": ["Unauthorized"]}})
                return
            self._send_json(HTTPStatus.OK, payload)
            return

        if route_path == f"{_API_PREFIX}/articles":
            author = self._require_auth()
            if author is None:
                return
            article_data = body.get("article", {})
            with STATE.lock:
                payload = STATE.create_article(author, article_data)
            self._send_json(HTTPStatus.CREATED, payload)
            return

        if match := re.fullmatch(
            rf"{re.escape(_API_PREFIX)}/articles/([^/]+)/comments",
            route_path,
        ):
            slug = match.group(1)
            author = self._require_auth()
            if author is None:
                return
            comment_body = body.get("comment", {}).get("body", "")
            with STATE.lock:
                comment_payload = STATE.add_comment(slug, author, comment_body)
            if comment_payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, comment_payload)
            return

        if match := re.fullmatch(
            rf"{re.escape(_API_PREFIX)}/profiles/([^/]+)/follow",
            route_path,
        ):
            username = match.group(1)
            follower = self._require_auth()
            if follower is None:
                return
            with STATE.lock:
                follow_payload = STATE.follow_profile(username, follower)
            if follow_payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, follow_payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})

    def do_PUT(self) -> None:
        """Handle supported Conduit PUT routes."""
        parsed = urlparse(self.path)
        route_path = parsed.path
        body = self._read_json_body()

        if match := re.fullmatch(rf"{re.escape(_API_PREFIX)}/articles/([^/]+)", route_path):
            slug = match.group(1)
            author = self._require_auth()
            if author is None:
                return
            article_data = body.get("article", {})
            try:
                with STATE.lock:
                    payload = STATE.update_article(slug, author, article_data)
            except PermissionError:
                self._send_json(HTTPStatus.FORBIDDEN, {"errors": {"body": ["Forbidden"]}})
                return
            if payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})

    def do_DELETE(self) -> None:
        """Handle supported Conduit DELETE routes."""
        parsed = urlparse(self.path)
        route_path = parsed.path

        if match := re.fullmatch(
            rf"{re.escape(_API_PREFIX)}/articles/([^/]+)/comments/(\d+)",
            route_path,
        ):
            slug = match.group(1)
            comment_id = int(match.group(2))
            author = self._require_auth()
            if author is None:
                return
            try:
                with STATE.lock:
                    deleted = STATE.delete_comment(slug, comment_id, author)
            except PermissionError:
                self._send_json(HTTPStatus.FORBIDDEN, {"errors": {"body": ["Forbidden"]}})
                return
            if not deleted:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, {})
            return

        if match := re.fullmatch(rf"{re.escape(_API_PREFIX)}/articles/([^/]+)", route_path):
            slug = match.group(1)
            author = self._require_auth()
            if author is None:
                return
            try:
                with STATE.lock:
                    deleted = STATE.delete_article(slug, author)
            except PermissionError:
                self._send_json(HTTPStatus.FORBIDDEN, {"errors": {"body": ["Forbidden"]}})
                return
            if not deleted:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, {})
            return

        if match := re.fullmatch(rf"{re.escape(_API_PREFIX)}/profiles/([^/]+)/follow", route_path):
            username = match.group(1)
            follower = self._require_auth()
            if follower is None:
                return
            with STATE.lock:
                payload = STATE.unfollow_profile(username, follower)
            if payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})
                return
            self._send_json(HTTPStatus.OK, payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"errors": {"body": ["Not Found"]}})

    def _read_json_body(self) -> dict[str, Any]:
        """Parse the request body as JSON, returning an empty dict when absent."""
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw_body = self.rfile.read(length)
        parsed = json.loads(raw_body.decode("utf-8"))
        if isinstance(parsed, dict):
            return parsed
        return {}

    def _extract_token(self) -> str | None:
        """Extract the bearer token from the Authorization header."""
        authorization = self.headers.get("Authorization", "")
        if authorization.startswith("Token "):
            return authorization.removeprefix("Token ").strip()
        return None

    def _resolve_user(self) -> dict[str, str] | None:
        """Resolve the authenticated user from the Authorization header."""
        with STATE.lock:
            return STATE.resolve_user(self._extract_token())

    def _require_auth(self) -> dict[str, str] | None:
        """Return the authenticated user or emit a 401 response."""
        user = self._resolve_user()
        if user is None:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"errors": {"body": ["Unauthorized"]}})
            return None
        return user

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        """Write a JSON response with the given HTTP status code."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HTTPStatus:
    """HTTP status codes used by the mock Conduit API."""

    OK: Final[int] = 200
    CREATED: Final[int] = 201
    UNAUTHORIZED: Final[int] = 401
    FORBIDDEN: Final[int] = 403
    NOT_FOUND: Final[int] = 404
    UNPROCESSABLE: Final[int] = 422


def main() -> None:
    """Start the mock Conduit API server."""
    server = ThreadingHTTPServer((_HOST, _PORT), ConduitMockHandler)
    print(f"Mock Conduit API listening on http://localhost:{_PORT}/api")
    server.serve_forever()


if __name__ == "__main__":
    main()
