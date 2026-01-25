import time

import yappla
from yappla.durative_action_spec import DurativeActionSpec
from yappla.plan import PlannerOutcome

from .perf import perf_line
from .plan_report import record_plan


def test_durative_actions_paint_rooms():
    """Test that durative actions are converted and can be used in planning."""
    initial_state = yappla.State({"room1": "clean", "have_brush": "yes"})

    domain = yappla.PlanningDomain()
    domain.add_action(DurativeActionSpec("paint_room1",
        duration=10,
        conditions={
            "to_start": "room1 == 'clean' and have_brush == 'yes'",
        },
        effects={
            "on_start": {"have_brush": "no"},
            "on_success": {"room1": "painted"},
            "on_aborted": {"have_brush": "yes"},
        },
    ))

    goal = "room1 == 'painted'"

    planner = yappla.Planner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "durative_actions_paint_rooms",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "durative_actions_paint_rooms",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="Planner",
    )

    # Should be able to achieve the goal using the durative action
    assert planner_result.outcome == PlannerOutcome.SUCCESS
    # Plan should have at least the initial state and final goal state
    assert len(planner_result.plan) >= 2
