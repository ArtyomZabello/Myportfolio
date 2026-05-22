"""Validate Locust HTML report thresholds for CI quality gates."""

from __future__ import annotations

import sys
from pathlib import Path

from config.locust_report import extract_aggregated_p95_ms
from config.settings import Config


def main() -> int:
    """Fail when aggregated p95 exceeds the configured threshold."""
    config = Config()
    report_path = Path("performance/locust_report.html")

    if not report_path.exists():
        print(f"Locust report not found: {report_path}")
        return 1 if not config.ALLOW_LOAD_FAILURES else 0

    p95_ms = extract_aggregated_p95_ms(report_path)
    if p95_ms is None:
        print("Unable to parse aggregated p95 from Locust report.")
        return 1 if not config.ALLOW_LOAD_FAILURES else 0

    print(
        f"Locust aggregated p95: {p95_ms:.2f} ms "
        f"(threshold: {config.LOCUST_P95_THRESHOLD_MS} ms)",
    )

    if p95_ms > config.LOCUST_P95_THRESHOLD_MS:
        print("Locust p95 threshold exceeded.")
        return 0 if config.ALLOW_LOAD_FAILURES else 1

    print("Locust threshold check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
