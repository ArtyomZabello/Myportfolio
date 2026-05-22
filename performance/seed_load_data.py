"""Generate and verify versioned Locust load-test datasets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TypedDict

import httpx

from config.constants import (
    API_PATH_USERS,
    API_PATH_USERS_LOGIN,
    HTTP_OK,
    SUCCESS_CREATE_STATUSES,
    profile_path,
)
from config.settings import Config

PERFORMANCE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = PERFORMANCE_DIR / "datasets"
LOAD_V1_PATH = DATASETS_DIR / "load_v1.json"

# Canonical v1 dataset — offline generation always reproduces this document.
LOAD_V1_DATASET: dict[str, Any] = {
    "version": 1,
    "profile_users": [
        {
            "username": "load_v1_user_01",
            "email": "load_v1_user_01@load.example.com",
            "password": "LoadPass_v1_01!",
        },
        {
            "username": "load_v1_user_02",
            "email": "load_v1_user_02@load.example.com",
            "password": "LoadPass_v1_02!",
        },
        {
            "username": "load_v1_user_03",
            "email": "load_v1_user_03@load.example.com",
            "password": "LoadPass_v1_03!",
        },
        {
            "username": "load_v1_user_04",
            "email": "load_v1_user_04@load.example.com",
            "password": "LoadPass_v1_04!",
        },
    ],
    "login_rejection_emails": [
        "load_v1_reject_01@load.example.com",
        "load_v1_reject_02@load.example.com",
        "load_v1_reject_03@load.example.com",
        "load_v1_reject_04@load.example.com",
    ],
}


class ProfileUser(TypedDict):
    """Registered profile user entry in a load dataset."""

    username: str
    email: str
    password: str


def generate_dataset(output_path: Path = LOAD_V1_PATH) -> Path:
    """Write the deterministic v1 dataset without contacting the backend."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(LOAD_V1_DATASET, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def load_dataset(dataset_path: Path = LOAD_V1_PATH) -> dict[str, Any]:
    """Load and validate a versioned Locust dataset file."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if payload.get("version") != 1:
        raise ValueError(f"Unsupported dataset version in {dataset_path}.")

    profile_users = payload.get("profile_users", [])
    login_rejection_emails = payload.get("login_rejection_emails", [])
    if not profile_users:
        raise ValueError(f"No profile_users in {dataset_path}.")
    if not login_rejection_emails:
        raise ValueError(f"No login_rejection_emails in {dataset_path}.")

    return payload


def _register_profile_user(client: httpx.Client, user: ProfileUser) -> None:
    """Register one dataset user via raw HTTP."""
    response = client.post(
        API_PATH_USERS,
        json={
            "user": {
                "username": user["username"],
                "email": user["email"],
                "password": user["password"],
            },
        },
    )
    if response.status_code in SUCCESS_CREATE_STATUSES:
        return

    if response.status_code in {400, 422}:
        login_response = client.post(
            API_PATH_USERS_LOGIN,
            json={"user": {"email": user["email"], "password": user["password"]}},
        )
        if login_response.status_code == HTTP_OK:
            return

    raise RuntimeError(
        f"Registration failed for '{user['username']}': "
        f"{response.status_code} {response.text}",
    )


def _verify_profile_user(client: httpx.Client, username: str) -> None:
    """Ensure a registered profile responds with HTTP 200."""
    response = client.get(profile_path(username))
    if response.status_code != HTTP_OK:
        raise RuntimeError(
            f"Profile check failed for '{username}': "
            f"{response.status_code} {response.text}",
        )


def verify_dataset(dataset_path: Path = LOAD_V1_PATH) -> None:
    """Register dataset users and fail fast when profiles are not readable."""
    config = Config()
    payload = load_dataset(dataset_path)
    profile_users: list[ProfileUser] = payload["profile_users"]

    with httpx.Client(base_url=config.BASE_URL, timeout=config.API_TIMEOUT) as client:
        for user in profile_users:
            _register_profile_user(client, user)
            _verify_profile_user(client, user["username"])


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``generate``, ``verify``, or both (default)."""
    parser = argparse.ArgumentParser(description="Manage Locust load-test datasets.")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("generate", "verify", "all"),
        default="all",
        help="generate: offline dataset only; verify: HTTP checks; all: both (default)",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=LOAD_V1_PATH,
        help=f"Dataset path (default: {LOAD_V1_PATH})",
    )
    args = parser.parse_args(argv)

    try:
        if args.command in {"generate", "all"}:
            path = generate_dataset(args.dataset)
            print(f"Generated deterministic dataset: {path}")

        if args.command in {"verify", "all"}:
            verify_dataset(args.dataset)
            print(f"Verified dataset against backend: {args.dataset}")
    except (FileNotFoundError, ValueError, RuntimeError, httpx.HTTPError) as exc:
        print(f"Load dataset command failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
