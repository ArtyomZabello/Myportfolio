"""Helpers for reading Locust HTML report metrics."""

from __future__ import annotations

import json
from pathlib import Path


def load_locust_report_args(report_path: Path) -> dict[str, object]:
    """Parse the embedded ``window.templateArgs`` JSON from a Locust HTML report."""
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    marker = "window.templateArgs = "
    start = content.find(marker)
    if start == -1:
        raise ValueError("Locust report does not contain window.templateArgs")

    json_start = start + len(marker)
    depth = 0
    for index, char in enumerate(content[json_start:], start=json_start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                parsed = json.loads(content[json_start : index + 1])
                if isinstance(parsed, dict):
                    return parsed
                raise ValueError("Locust templateArgs is not a JSON object")

    raise ValueError("Unterminated JSON in Locust report")


def extract_aggregated_p95_ms(report_path: Path) -> float | None:
    """Return aggregated p95 response time in milliseconds from a Locust HTML report."""
    try:
        report_args = load_locust_report_args(report_path)
    except (ValueError, json.JSONDecodeError):
        return None

    request_stats = report_args.get("requests_statistics")
    if isinstance(request_stats, list):
        for row in request_stats:
            if not isinstance(row, dict) or row.get("name") != "Aggregated":
                continue
            p95 = row.get("response_time_percentile_0.95")
            if p95 is not None:
                return float(p95)

    response_stats = report_args.get("response_time_statistics")
    if isinstance(response_stats, list):
        for row in response_stats:
            if not isinstance(row, dict) or row.get("name") != "Aggregated":
                continue
            p95 = row.get("0.95")
            if p95 is not None:
                return float(p95)

    return None
