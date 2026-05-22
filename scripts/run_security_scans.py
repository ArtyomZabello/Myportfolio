"""Run OWASP ZAP scans and enforce configurable security quality gates."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from config.settings import Config

ROOT = Path(__file__).resolve().parents[1]
SECURITY_DIR = ROOT / "security"

# ZAP risk codes: 2=Medium, 3=High, 4=Critical
GATE_RISK_CODES = {"2", "3", "4"}

# ZAP exit codes: 0=pass, 1=FAIL rules, 2=WARN only, 3+=scan/runtime error
ZAP_WARN_ONLY_EXIT_CODE = 2


def count_gate_alerts(report_path: Path) -> int | None:
    """Count Medium+ alerts in a ZAP JSON report."""
    if not report_path.exists():
        return None

    data = json.loads(report_path.read_text(encoding="utf-8"))
    count = 0
    for site in data.get("site", []):
        if not isinstance(site, dict):
            continue
        for alert in site.get("alerts", []):
            if not isinstance(alert, dict):
                continue
            if str(alert.get("riskcode", "")) in GATE_RISK_CODES:
                count += 1
    return count


def _run_zap_scan(args: list[str]) -> int:
    """Execute a ZAP container scan and return its exit code."""
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "host",
        "-v",
        f"{SECURITY_DIR}:/zap/wrk/:rw",
        "-t",
        "ghcr.io/zaproxy/zaproxy:stable",
        *args,
    ]
    print(f"\n>>> {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def _zap_scan_failed_to_run(exit_code: int) -> bool:
    """Return True only when the scan itself failed, not when WARN rules fired."""
    return exit_code >= 3


def main() -> int:
    """Execute baseline and API scans, optionally failing on non-zero exit codes."""
    config = Config()
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)

    baseline_json = SECURITY_DIR / "zap_baseline_report.json"
    api_json = SECURITY_DIR / "zap_api_report.json"

    baseline_exit = _run_zap_scan(
        [
            "zap-baseline.py",
            "-t",
            "http://localhost:8000/api",
            "-c",
            "zap_baseline.conf",
            "-I",
            "-r",
            "zap_baseline_report.html",
            "-J",
            "zap_baseline_report.json",
        ],
    )
    api_exit = _run_zap_scan(
        [
            "zap-api-scan.py",
            "-t",
            "http://localhost:8000/openapi.json",
            "-f",
            "openapi",
            "-r",
            "zap_api_report.html",
            "-J",
            "zap_api_report.json",
        ],
    )

    if config.ALLOW_SECURITY_FAILURES:
        print("ALLOW_SECURITY_FAILURES=true — security gate skipped.")
        return 0

    for label, exit_code in (("baseline", baseline_exit), ("API", api_exit)):
        if _zap_scan_failed_to_run(exit_code):
            print(f"ZAP {label} scan failed to run (exit code {exit_code}).")
            return exit_code
        if exit_code == ZAP_WARN_ONLY_EXIT_CODE:
            print(
                f"ZAP {label} scan reported WARN-only findings (exit code {exit_code}); "
                "continuing to JSON severity gate.",
            )

    gate_alert_count = 0
    for report_path in (baseline_json, api_json):
        report_count = count_gate_alerts(report_path)
        if report_count is None:
            print(f"ZAP JSON report not found: {report_path}")
            return 1
        gate_alert_count += report_count

    print(
        f"ZAP Medium+ alerts: {gate_alert_count} "
        f"(threshold: {config.SECURITY_MAX_HIGH_ALERTS})",
    )
    if gate_alert_count > config.SECURITY_MAX_HIGH_ALERTS:
        print("ZAP severity threshold exceeded.")
        return 1

    print("Security scans passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
