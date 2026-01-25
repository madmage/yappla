"""Tiny helpers for emitting grep-friendly performance lines from tests.

Run with `pytest -v -s` (or redirect output to a log file) to capture stdout.

PERF output is disabled by default; enable with `pytest --perf`.

When enabled, PERF lines are collected during the test run and printed as a
single "PERF report" at the end of the pytest session.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
import os
from typing import Any, Dict


def _perf_enabled() -> bool:
    return os.environ.get("YAPPLA_PYTEST_PERF", "").strip() not in ("", "0", "false", "False")


# Stored as fully formatted lines for grep-friendly output.
PERF_LINES = []


def clear_perf_lines() -> None:
    PERF_LINES.clear()


def get_perf_lines():
    return list(PERF_LINES)


def perf_line(test_id: str, elapsed_s: float, **fields: Any) -> None:
    """Print a single, grep-friendly performance line.

    Example:
      PERF planner_simple_planning wall_ms=1.234 iterations=5

    Notes:
    - `elapsed_s` should be wall-clock time, typically from `time.perf_counter()`.
    - Keep `test_id` stable so logs are easy to diff across commits.
    """
    if not _perf_enabled():
        return
    parts = [f"PERF {test_id}", f"wall_ms={elapsed_s * 1000.0:.3f}"]
    for key, value in fields.items():
        if value is None:
            continue
        parts.append(f"{key}={value}")
    PERF_LINES.append(" ".join(parts))


@dataclass
class PerfTimer:
    """Simple context timer that prints a PERF line at exit."""

    test_id: str
    fields: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.fields is None:
            self.fields = {}
        self._t0 = None

    def __enter__(self) -> "PerfTimer":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        elapsed = time.perf_counter() - (self._t0 or time.perf_counter())
        perf_line(self.test_id, elapsed, **self.fields)
