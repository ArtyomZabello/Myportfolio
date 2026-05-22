"""Run OWASP ZAP scans and enforce configurable security quality gates."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from config.settings import Config

ROOT = Path(__file__).resolve().parents[1]
SECURITY_DIR = ROOT / "security"
HIGH_RISK_CODES = {"3", "4"}


def count_high_alerts(report_path: Path) -> int | None:
    """Count High and Critical alerts in a ZAP JSON report."""
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
            if str(alert.get("riskcode", "")) in HIGH_RISK_CODES:
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

    if baseline_exit != 0:
        print(f"ZAP baseline scan failed with exit code {baseline_exit}.")
        return baseline_exit
    if api_exit != 0:
        print(f"ZAP API scan failed with exit code {api_exit}.")
        return api_exit

    high_alert_count = 0
    for report_path in (baseline_json, api_json):
        report_high_count = count_high_alerts(report_path)
        if report_high_count is None:
            print(f"ZAP JSON report not found: {report_path}")
            return 1
        high_alert_count += report_high_count

    print(
        f"ZAP High/Critical alerts: {high_alert_count} "
        f"(threshold: {config.SECURITY_MAX_HIGH_ALERTS})",
    )
    if high_alert_count > config.SECURITY_MAX_HIGH_ALERTS:
        print("ZAP high-alert threshold exceeded.")
        return 1

    print("Security scans passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
