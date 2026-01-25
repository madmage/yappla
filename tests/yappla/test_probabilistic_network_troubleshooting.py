import time

import yappla
from yappla.plan import PlannerOutcome

from .perf import perf_line
from .plan_report import record_plan


def test_probabilistic_network_troubleshooting():
    initial_state = yappla.State({"internet_state": "down", "has_tools": "no"})
    
    domain = yappla.PlanningDomain()
    domain.add_action(yappla.Action("restart_router",
        cost=5,
        effects=[
            {"%": 0.6, "internet_state": "working"}
        ]
    ))
    domain.add_action(yappla.Action("call_isp",
        cost=20,
        effects=[
            {"%": 0.9, "internet_state": "working"}
        ]
    ))
    domain.add_action(yappla.Action("buy_new_router",
        cost=100,
        effects=[
            {"%": 0.95, "internet_state": "working"}
        ]
    ))

    goal = "internet_state == 'working'"

    planner = yappla.Planner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "probabilistic_network_troubleshooting",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "probabilistic_network_troubleshooting",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="Planner",
    )

    assert planner_result.outcome == PlannerOutcome.SUCCESS
    # Plan should find the cheapest action that achieves the goal
    assert len(planner_result.plan) >= 2  # At least initial action + goal state
