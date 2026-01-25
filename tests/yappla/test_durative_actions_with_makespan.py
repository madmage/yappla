import time

import yappla
from yappla.plan import PlannerOutcome
from yappla.temporal_planner import TemporalPlanner

from .perf import perf_line
from .plan_report import record_plan


def test_durative_actions_event_preparation():
    """Test durative actions with mutual exclusion and time optimization.
    
    Scenario: Preparing two rooms (ballroom and kitchen) for an event.
    - Each room needs cleaning and decoration
    - Cleaning and decoration in the same room are mutually exclusive
    - Different rooms can be worked on in parallel
    - Goal is to complete both rooms as quickly as possible
    
    Without parallel execution: clean_ballroom(5) + decorate_ballroom(3) + clean_kitchen(4) + decorate_kitchen(3) = 15 time units
    With parallel execution: can overlap, so makespan is less
    """
    
    initial_state = yappla.State({
        "ballroom_clean": False,
        "ballroom_decorated": False,
        "kitchen_clean": False,
        "kitchen_decorated": False,
        "worker_busy": False,
    })
    
    domain = yappla.PlanningDomain()

    # TemporalPlanner expects primitive Action operators with duration.
    # Mutex constraints are approximated by overlapping "effect key" sets.
    # Here, actions for the same room share a room-specific resource key.
    domain.add_action(yappla.Action(
        "clean_ballroom",
        preconditions="ballroom_clean == False",
        effects={"ballroom_clean": True, "_res_ballroom": "used"},
        cost=1,
        duration=5,
    ))
    domain.add_action(yappla.Action(
        "clean_kitchen",
        preconditions="kitchen_clean == False",
        effects={"kitchen_clean": True, "_res_kitchen": "used"},
        cost=1,
        duration=4,
    ))
    domain.add_action(yappla.Action(
        "decorate_ballroom",
        preconditions="ballroom_clean == True and ballroom_decorated == False",
        effects={"ballroom_decorated": True, "_res_ballroom": "used"},
        cost=1,
        duration=3,
    ))
    domain.add_action(yappla.Action(
        "decorate_kitchen",
        preconditions="kitchen_clean == True and kitchen_decorated == False",
        effects={"kitchen_decorated": True, "_res_kitchen": "used"},
        cost=1,
        duration=3,
    ))
    
    goal = "ballroom_clean == True and ballroom_decorated == True and kitchen_clean == True and kitchen_decorated == True"
    
    planner = TemporalPlanner()
    planner.set_domain(domain)
    planner.max_verbosity_level = 0
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "durative_actions_event_preparation",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "durative_actions_event_preparation",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="TemporalPlanner",
    )
    
    assert planner_result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in planner_result.stats
    # Optimal schedule:
    # clean_ballroom@0..5, clean_kitchen@0..4, decorate_kitchen@4..7, decorate_ballroom@5..8 => makespan 8
    assert planner_result.stats["makespan"] <= 8.1

    action_steps = [step for (_, step) in planner_result.plan if step]
    assert all(isinstance(step, dict) for step in action_steps)

    def has_start(name: str, t: float) -> bool:
        return any(step.get("name") == name and abs(float(step.get("time")) - t) < 0.01 for step in action_steps)

    assert has_start("clean_ballroom", 0.0)
    assert has_start("clean_kitchen", 0.0)

    def start_time_of(action_name: str) -> float:
        for step in action_steps:
            if step.get("name") == action_name:
                return float(step.get("time"))
        raise AssertionError(f"Missing action step: {action_name}")

    # Decorations can't start before their respective cleaning completes.
    assert start_time_of("decorate_ballroom") >= 5.0
    assert start_time_of("decorate_kitchen") >= 4.0
    
    # Verify the plan reaches the goal state
    final_state = planner_result.plan[-1][0]
    assert final_state["ballroom_clean"] == True
    assert final_state["ballroom_decorated"] == True
    assert final_state["kitchen_clean"] == True
    assert final_state["kitchen_decorated"] == True


def test_durative_actions_sequential_vs_parallel():
    """Test durative actions where parallelism matters.
    
    Scenario: Two independent tasks that can run in parallel.
    - Task A: 5 time units
    - Task B: 3 time units
    - Optimal makespan: 5 time units
    """
    
    initial_state = yappla.State({
        "task_a_done": False,
        "task_b_done": False,
    })
    
    domain = yappla.PlanningDomain()

    domain.add_action(yappla.Action(
        "do_task_a",
        preconditions="task_a_done == False",
        effects={"task_a_done": True},
        cost=1,
        duration=5,
    ))
    domain.add_action(yappla.Action(
        "do_task_b",
        preconditions="task_b_done == False",
        effects={"task_b_done": True},
        cost=1,
        duration=3,
    ))
    
    goal = "task_a_done == True and task_b_done == True"
    
    planner = TemporalPlanner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "durative_actions_sequential_vs_parallel",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "durative_actions_sequential_vs_parallel",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="TemporalPlanner",
    )
    
    assert planner_result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in planner_result.stats
    assert planner_result.stats["makespan"] <= 5.1

    action_steps = [step for (_, step) in planner_result.plan if step]
    assert all(isinstance(step, dict) for step in action_steps)
    assert any(step.get("name") == "do_task_a" and abs(float(step.get("time")) - 0.0) < 0.01 for step in action_steps)
    assert any(step.get("name") == "do_task_b" and abs(float(step.get("time")) - 0.0) < 0.01 for step in action_steps)
    
    # Verify both tasks are completed
    final_state = planner_result.plan[-1][0]
    assert final_state["task_a_done"] == True
    assert final_state["task_b_done"] == True


def test_durative_actions_with_prerequisites():
    """Test durative actions with dependencies and sequential constraints.
    
    Scenario: Assembly line
    - Build frame (duration: 5)
    - Paint frame (duration: 3, requires frame built)
    - Install engine (duration: 4, requires frame built)
    - Install wheels (duration: 2, requires engine installed)
    
    Total: must be at least 5 (frame) + 3 (paint) + 4 (engine) + 2 (wheels) = 14 time units minimum
    if done sequentially. Paint and engine could run in parallel after frame is done.
    """
    
    initial_state = yappla.State({
        "frame_built": False,
        "frame_painted": False,
        "engine_installed": False,
        "wheels_installed": False,
    })
    
    domain = yappla.PlanningDomain()

    domain.add_action(yappla.Action(
        "build_frame",
        preconditions="frame_built == False",
        effects={"frame_built": True},
        cost=1,
        duration=5,
    ))
    # After the frame is built, painting and engine installation can overlap.
    domain.add_action(yappla.Action(
        "paint_frame",
        preconditions="frame_built == True and frame_painted == False",
        effects={"frame_painted": True},
        cost=1,
        duration=3,
    ))
    domain.add_action(yappla.Action(
        "install_engine",
        preconditions="frame_built == True and engine_installed == False",
        effects={"engine_installed": True},
        cost=1,
        duration=4,
    ))
    domain.add_action(yappla.Action(
        "install_wheels",
        preconditions="engine_installed == True and wheels_installed == False",
        effects={"wheels_installed": True},
        cost=1,
        duration=2,
    ))
    
    goal = "frame_built == True and frame_painted == True and engine_installed == True and wheels_installed == True"
    
    planner = TemporalPlanner()
    planner.set_domain(domain)
    planner.max_verbosity_level = 0
    t0 = time.perf_counter()
    planner_result = planner.plan(initial_state, goal)
    elapsed = time.perf_counter() - t0
    perf_line(
        "durative_actions_with_prerequisites",
        elapsed,
        outcome=getattr(planner_result.outcome, "name", planner_result.outcome),
        iterations=planner_result.stats.get("iterations"),
        plan_len=len(planner_result.plan) if planner_result.plan is not None else None,
    )
    record_plan(
        "durative_actions_with_prerequisites",
        initial_state=initial_state,
        goal=goal,
        result=planner_result,
        planner_type="TemporalPlanner",
    )
    
    assert planner_result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in planner_result.stats
    # Optimal:
    # build_frame@0..5, paint_frame@5..8 and install_engine@5..9, install_wheels@9..11 => makespan 11
    assert planner_result.stats["makespan"] <= 11.1

    action_steps = [step for (_, step) in planner_result.plan if step]
    assert all(isinstance(step, dict) for step in action_steps)
    assert any(step.get("name") == "build_frame" and abs(float(step.get("time")) - 0.0) < 0.01 for step in action_steps)

    def start_time_of(action_name: str) -> float:
        for step in action_steps:
            if step.get("name") == action_name:
                return float(step.get("time"))
        raise AssertionError(f"Missing action step: {action_name}")

    assert start_time_of("paint_frame") >= 5.0
    assert start_time_of("install_engine") >= 5.0
    assert start_time_of("install_wheels") >= 9.0
    
    # Verify the goal is reached
    final_state = planner_result.plan[-1][0]
    assert final_state["frame_built"] == True
    assert final_state["frame_painted"] == True
    assert final_state["engine_installed"] == True
    assert final_state["wheels_installed"] == True


if __name__ == "__main__":
    print("Running durative action tests with makespan considerations...\n")
    
    print("Test 1: Event preparation with mutual exclusion")
    test_durative_actions_event_preparation()
    print("✓ Passed\n")
    
    print("Test 2: Sequential vs parallel tasks")
    test_durative_actions_sequential_vs_parallel()
    print("✓ Passed\n")
    
    print("Test 3: Assembly line with prerequisites")
    test_durative_actions_with_prerequisites()
    print("✓ Passed\n")
    
    print("All durative action tests completed successfully!")
