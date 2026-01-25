"""Helpers for collecting and printing planner runs from tests.

Enabled via `pytest --show-plans`.

This is intended for tests that exercise Planner/TemporalPlanner. Tests can record
runs with `record_plan(...)`; the report is printed once at session end.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


def _show_plans_enabled() -> bool:
    return os.environ.get("YAPPLA_PYTEST_SHOW_PLANS", "").strip() not in ("", "0", "false", "False")


@dataclass(frozen=True)
class PlanRecord:
    test_id: str
    planner_type: str
    goal: str
    outcome: str
    initial_state: Dict[str, Any]
    actions: List[str]
    # Full plan trace as emitted by the planner result: list of (state_dict, action_str_or_None)
    # where the last item typically has action=None.
    trace: List[Tuple[Dict[str, Any], Optional[str]]] = field(default_factory=list)
    pretty_plan: Optional[str] = None
    final_state: Optional[Dict[str, Any]] = None
    iterations: Optional[int] = None
    makespan: Optional[float] = None


PLAN_RECORDS: List[PlanRecord] = []


def clear_plan_records() -> None:
    PLAN_RECORDS.clear()


def get_plan_records() -> List[PlanRecord]:
    return list(PLAN_RECORDS)


def record_plan(
    test_id: str,
    *,
    initial_state: Any,
    goal: str,
    result: Any,
    planner_type: str = "Planner",
) -> None:
    """Record a planner run for end-of-session reporting."""
    if not _show_plans_enabled():
        return

    try:
        init_dict = dict(initial_state)
    except Exception:
        init_dict = {"_repr": repr(initial_state)}

    actions: List[str] = []
    final_state = None
    trace: List[Tuple[Dict[str, Any], Optional[str]]] = []
    pretty_plan: Optional[str] = None
    if getattr(result, "plan", None):
        try:
            actions = [a for (_, a) in result.plan if a]
        except Exception:
            actions = ["<unavailable>"]

        try:
            for (state, action) in result.plan:
                try:
                    state_dict = dict(state)
                except Exception:
                    state_dict = {"_repr": repr(state)}
                trace.append((state_dict, None if action is None else str(action)))
        except Exception:
            trace = []
        try:
            final_state = dict(result.plan[-1][0])
        except Exception:
            final_state = None

    # Capture the canonical pretty plan rendering (if available).
    try:
        pretty_plan = result.pretty_str(show_state_hashes=False)
    except Exception:
        pretty_plan = None

    outcome = getattr(getattr(result, "outcome", None), "name", getattr(result, "outcome", None))

    stats = getattr(result, "stats", {}) or {}
    iterations = stats.get("iterations")
    makespan = stats.get("makespan")

    PLAN_RECORDS.append(
        PlanRecord(
            test_id=test_id,
            planner_type=planner_type,
            goal=str(goal),
            outcome=str(outcome),
            initial_state=init_dict,
            actions=[str(x) for x in actions],
            trace=trace,
            pretty_plan=pretty_plan,
            final_state=final_state,
            iterations=iterations,
            makespan=makespan,
        )
    )
