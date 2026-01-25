import time

import yappla
from yappla.plan import PlannerOutcome

from .perf import perf_line
from .plan_report import record_plan


def test_durative_actions_parallel_house_renovation():
    initial_state = yappla.State({"room1": "clean", "room2": "clean"})

    domain = yappla.PlanningDomain()
    domain.add_variable(yappla.StateVariable("room1", ["clean", "painted"]))
    domain.add_variable(yappla.StateVariable("room2", ["clean", "painted"]))
    domain.add_action(yappla.DurativeActionSpec("paint_room1",
        duration=10,
        conditions={
            "to_start": "room1 == 'clean'",
        },
        effects={
            "on_success": {"room1": "painted"},
        },
    ))
    domain.add_action(yappla.DurativeActionSpec("paint_room2",
        duration=6,
        conditions={
            "to_start": "room2 == 'clean'",
        },
        effects={
            "on_success": {"room2": "painted"},
        },
    ))

    goal = "room1 == 'painted' and room2 == 'painted'"

    domain2 = domain.compile_action_specs()

    planner = yappla.Planner()
    planner.set_domain(domain2)
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "durative_actions_parallel_house_renovation",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "durative_actions_parallel_house_renovation",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="Planner",
    )

    assert planner_result.outcome == PlannerOutcome.SUCCESS
    assert len(planner_result.plan) == 5  # 4 actions + the final goal state without actions
