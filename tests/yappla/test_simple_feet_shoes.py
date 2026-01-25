import time

import yappla
from yappla.plan import PlannerOutcome

from .perf import perf_line
from .plan_report import record_plan


def test_simple_feet_shoes():
    initial_state = yappla.State({"left_foot": "has_nothing", "right_foot": "has_nothing"})
    put_left_sock = yappla.Action(
        "put_left_sock",
        preconditions="left_foot == 'has_nothing'",
        effects=[{"left_foot": "has_sock"}])
    put_right_sock = yappla.Action(
        "put_right_sock",
        preconditions="right_foot == 'has_nothing'",
        effects=[{"right_foot": "has_sock"}])
    put_left_shoe = yappla.Action(
        "put_left_shoe",
        preconditions="left_foot == 'has_sock'",
        effects=[{"left_foot": "has_shoe"}])
    put_right_shoe = yappla.Action(
        "put_right_shoe",
        preconditions="right_foot == 'has_sock'",
        effects=[{"right_foot": "has_shoe"}])

    domain = yappla.PlanningDomain()
    domain.add_action(put_left_sock)
    domain.add_action(put_right_sock)
    domain.add_action(put_left_shoe)
    domain.add_action(put_right_shoe)

    #goal = yappla.Goal()
    #goal.append({"goal": "left_foot == 'has_shoe' and right_foot == 'has_shoe'"})
    goal = "left_foot == 'has_shoe' and right_foot == 'has_shoe'"

    planner = yappla.Planner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "simple_feet_shoes",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "simple_feet_shoes",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="Planner",
    )

    assert planner_result.outcome == PlannerOutcome.SUCCESS
    assert len(planner_result.plan) == 5  # 4 actions + the final goal state without actions
