"""Unit tests for Locust threshold parsing."""

from pathlib import Path

from config.locust_report import extract_aggregated_p95_ms


def test_extract_aggregated_p95_from_locust_html_report() -> None:
    """Verify p95 is read from the Aggregated row in a Locust 2.43 HTML report."""
    report_path = Path("performance/locust_report.html")
    if not report_path.exists():
        return

    p95_ms = extract_aggregated_p95_ms(report_path)

    assert p95_ms == 2000.0
