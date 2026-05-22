"""Cross-platform turnkey runner for the Conduit test automation framework."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _python_env() -> dict[str, str]:
    """Build an environment with project import paths configured."""
    env = os.environ.copy()
    pythonpath_parts = [str(ROOT), str(ROOT / "src"), env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(part for part in pythonpath_parts if part)
    return env


def _run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Execute a command from the repository root."""
    print(f"\n>>> {' '.join(command)}")
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        env=_python_env(),
    )


def _ensure_env_file() -> None:
    """Create `.env` from `.env.example` when missing."""
    env_path = ROOT / ".env"
    example_path = ROOT / ".env.example"
    if not env_path.exists() and example_path.exists():
        env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        print("Created .env from .env.example")


def _resolve_docker_compose_command() -> list[str] | None:
    """Return a usable Docker Compose invocation when Docker is available."""
    if shutil.which("docker") is None:
        return None

    compose_check = subprocess.run(
        ["docker", "compose", "version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if compose_check.returncode == 0:
        return ["docker", "compose", "-f", "app/docker-compose.yml"]

    if shutil.which("docker-compose") is not None:
        return ["docker-compose", "-f", "app/docker-compose.yml"]

    return None


def _start_mock_server() -> subprocess.Popen[str]:
    """Launch the in-process mock Conduit API on port 8000."""
    print("Docker unavailable — starting mock Conduit API on port 8000...")
    return subprocess.Popen(
        [sys.executable, "scripts/mock_conduit_api.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def main() -> int:
    """Run env bootstrap, SUT startup, health check, and API tests."""
    _ensure_env_file()

    mock_process: subprocess.Popen[str] | None = None
    compose_command = _resolve_docker_compose_command()

    try:
        if compose_command is not None:
            _run([*compose_command, "up", "-d", "--build"])
        else:
            mock_process = _start_mock_server()
            time.sleep(1)

        health_exit_code = _run(
            [sys.executable, "scripts/wait_for_backend.py"],
            check=False,
        ).returncode
        if health_exit_code != 0:
            return health_exit_code

        api_exit_code = _run(
            [sys.executable, "-m", "pytest", "tests/api/", "-v", "--alluredir=allure-results"],
            check=False,
        ).returncode
        return api_exit_code
    finally:
        if compose_command is not None:
            _run([*compose_command, "down", "-v"], check=False)
        elif mock_process is not None:
            mock_process.terminate()
            mock_process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
