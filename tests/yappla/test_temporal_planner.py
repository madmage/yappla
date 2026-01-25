"""Test suite for the TemporalPlanner with makespan optimization and mutex constraints."""

import pytest
import time

import yappla
from yappla.temporal_planner import TemporalPlanner, TemporalState, ScheduledAction
from yappla.plan import PlannerOutcome

from .perf import perf_line
from .plan_report import record_plan


def test_temporal_planner_basic():
    """Test basic temporal planning with action durations."""
    initial_state = yappla.State({"x": 0})
    
    domain = yappla.PlanningDomain()
    # Add actions with different durations
    domain.add_action(yappla.Action("a1", preconditions="x == 0", effects=[{"x": 1}], cost=1, duration=5))
    domain.add_action(yappla.Action("a2", preconditions="x == 1", effects=[{"x": 2}], cost=1, duration=3))
    
    planner = TemporalPlanner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    result = planner.plan(initial_state, "x == 2")
    elapsed = time.perf_counter() - t0
    
    assert result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in result.stats
    assert result.stats["makespan"] > 0
    perf_line(
        "temporal_planner_basic",
        elapsed,
        makespan=f"{result.stats['makespan']:.3f}",
        iterations=result.stats.get("iterations"),
    )
    record_plan(
        "temporal_planner_basic",
        initial_state=initial_state,
        goal="x == 2",
        result=result,
        planner_type="TemporalPlanner",
    )


def test_temporal_planner_mutex_constraints():
    """Test that mutex constraints prevent overlapping conflicting actions."""
    initial_state = yappla.State({
        "room1_clean": False,
        "room1_decorated": False,
        "worker_busy": False,
    })
    
    domain = yappla.PlanningDomain()
    # These two actions modify the same variables, so they must not overlap
    domain.add_action(yappla.Action(
        "clean_room1",
        preconditions="room1_clean == False and worker_busy == False",
        effects=[{"room1_clean": True, "worker_busy": False}],
        cost=1,
        duration=5
    ))
    
    domain.add_action(yappla.Action(
        "decorate_room1",
        preconditions="room1_clean == True and room1_decorated == False and worker_busy == False",
        effects=[{"room1_decorated": True, "worker_busy": False}],
        cost=1,
        duration=3
    ))
    
    planner = TemporalPlanner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    result = planner.plan(initial_state, "room1_clean == True and room1_decorated == True")
    elapsed = time.perf_counter() - t0
    
    assert result.outcome == PlannerOutcome.SUCCESS
    # With mutex constraints, actions should be sequential
    # Minimum makespan should be at least 5 + 3 = 8
    assert result.stats["makespan"] >= 7.9, f"Expected makespan >= 8, got {result.stats['makespan']}"
    perf_line(
        "temporal_planner_mutex_constraints",
        elapsed,
        makespan=f"{result.stats['makespan']:.3f}",
        iterations=result.stats.get("iterations"),
    )
    record_plan(
        "temporal_planner_mutex_constraints",
        initial_state=initial_state,
        goal="room1_clean == True and room1_decorated == True",
        result=result,
        planner_type="TemporalPlanner",
    )


def test_temporal_state_active_actions():
    """Test TemporalState tracking of active actions."""
    t0 = time.perf_counter()
    state = TemporalState(state_vars={"x": 0}, current_time=0.0)
    
    # Create dummy action
    action = yappla.Action("test", preconditions="", effects=[{"x": 1}], duration=5)
    scheduled = ScheduledAction(action=action, start_time=0, end_time=5, action_type='primitive')
    state.scheduled_actions.append(scheduled)
    
    # At time 0-5, action should be active
    active = state.get_active_actions_at(2.5)
    assert len(active) == 1
    assert active[0].action.name == "test"
    
    # At time 6, action should not be active
    active = state.get_active_actions_at(6)
    assert len(active) == 0

    elapsed = time.perf_counter() - t0
    perf_line("temporal_state_active_actions", elapsed)


def test_temporal_state_decision_points():
    """Test TemporalState next decision point calculation."""
    t0 = time.perf_counter()
    state = TemporalState(state_vars={"x": 0}, current_time=0.0)
    
    # With no scheduled actions, decision point is current time
    assert state.get_next_decision_point() == 0.0
    
    # Add an action that runs from 0-5
    action = yappla.Action("test", preconditions="", effects=[{"x": 1}], duration=5)
    scheduled = ScheduledAction(action=action, start_time=0, end_time=5, action_type='primitive')
    state.scheduled_actions.append(scheduled)
    
    # Next decision point should be when action ends
    assert state.get_next_decision_point() == 5.0

    elapsed = time.perf_counter() - t0
    perf_line("temporal_state_decision_points", elapsed)


def test_temporal_state_mutex_detection():
    """Test TemporalState mutex conflict detection."""
    t0 = time.perf_counter()
    state = TemporalState(state_vars={"x": 0}, current_time=0.0)
    
    # Schedule first action that modifies 'x' from time 0-5
    action1 = yappla.Action("a1", preconditions="", effects=[{"x": 1}], duration=5)
    scheduled1 = ScheduledAction(action=action1, start_time=0, end_time=5, action_type='primitive')
    state.scheduled_actions.append(scheduled1)
    
    # Try to schedule conflicting action during overlap
    action2 = yappla.Action("a2", preconditions="", effects=[{"x": 2}], duration=3)
    has_conflict = state.has_mutex_conflict(action2, 3)
    
    # Should detect conflict since both modify 'x' and would overlap
    assert has_conflict, "Should detect mutex conflict"
    
    # Advance time to 5, now action2 should not conflict
    state.current_time = 5.0
    has_conflict = state.has_mutex_conflict(action2, 3)
    assert not has_conflict, "Should not detect conflict after first action completes"

    elapsed = time.perf_counter() - t0
    perf_line("temporal_state_mutex_detection", elapsed)


def test_temporal_planner_with_multiple_actions():
    """Test temporal planner with a sequence of dependent actions."""
    initial_state = yappla.State({"step": 0})
    
    domain = yappla.PlanningDomain()
    domain.add_action(yappla.Action("s0_to_1", preconditions="step == 0", effects=[{"step": 1}], cost=1, duration=2))
    domain.add_action(yappla.Action("s1_to_2", preconditions="step == 1", effects=[{"step": 2}], cost=1, duration=3))
    domain.add_action(yappla.Action("s2_to_3", preconditions="step == 2", effects=[{"step": 3}], cost=1, duration=2))
    
    planner = TemporalPlanner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    result = planner.plan(initial_state, "step == 3")
    elapsed = time.perf_counter() - t0
    
    assert result.outcome == PlannerOutcome.SUCCESS
    # Minimum makespan: 2 + 3 + 2 = 7
    assert result.stats["makespan"] >= 6.9, f"Expected makespan >= 7, got {result.stats['makespan']}"
    perf_line(
        "temporal_planner_with_multiple_actions",
        elapsed,
        makespan=f"{result.stats['makespan']:.3f}",
        iterations=result.stats.get("iterations"),
    )
    record_plan(
        "temporal_planner_with_multiple_actions",
        initial_state=initial_state,
        goal="step == 3",
        result=result,
        planner_type="TemporalPlanner",
    )


def test_temporal_planner_parallel_durative_optimization():
    """Test that independent durative actions are parallelized to minimize makespan.

    Scenario:
    - Two independent tasks (a and b) each take 5 time units and can run in parallel.
    - A final assembly task takes 1 time unit and requires both results.

    Optimal schedule:
    - a@0..5 and b@0..5 in parallel
    - assemble@5..6
    => makespan = 6
    """
    initial_state = yappla.State({
        "a_done": False,
        "b_done": False,
        "assembled": False,
    })

    domain = yappla.PlanningDomain()
    domain.add_action(yappla.Action(
        "do_a",
        preconditions="a_done == False",
        effects=[{"a_done": True}],
        cost=1,
        duration=5,
    ))
    domain.add_action(yappla.Action(
        "do_b",
        preconditions="b_done == False",
        effects=[{"b_done": True}],
        cost=1,
        duration=5,
    ))
    domain.add_action(yappla.Action(
        "assemble",
        preconditions="a_done == True and b_done == True and assembled == False",
        effects=[{"assembled": True}],
        cost=1,
        duration=1,
    ))

    planner = TemporalPlanner()
    planner.set_domain(domain)
    t0 = time.perf_counter()
    result = planner.plan(initial_state, "assembled == True")
    elapsed = time.perf_counter() - t0

    assert result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in result.stats
    assert result.stats["makespan"] <= 6.1, f"Expected optimal makespan ~6, got {result.stats['makespan']}"

    # The plan should include both do_a and do_b starting at time 0.0.
    action_steps = [step for (_, step) in result.plan if step]
    assert all(isinstance(step, dict) for step in action_steps)

    def by_name(name: str):
        return [s for s in action_steps if s.get("name") == name]

    assert any(abs(s.get("time", -1.0) - 0.0) < 0.01 for s in by_name("do_a")), action_steps
    assert any(abs(s.get("time", -1.0) - 0.0) < 0.01 for s in by_name("do_b")), action_steps
    assert any(abs(s.get("time", -1.0) - 5.0) < 0.01 for s in by_name("assemble")), action_steps

    perf_line(
        "temporal_planner_parallel_durative_optimization",
        elapsed,
        makespan=f"{result.stats['makespan']:.3f}",
        iterations=result.stats.get("iterations"),
    )
    record_plan(
        "temporal_planner_parallel_durative_optimization",
        initial_state=initial_state,
        goal="assembled == True",
        result=result,
        planner_type="TemporalPlanner",
    )


def test_temporal_planner_fails_if_durative_action_in_domain():
    """TemporalPlanner should raise upfront if DurativeActionSpec objects are still in its domain.

    This guards against accidentally bypassing the durative-action compilation/splitting step.
    """
    domain = yappla.PlanningDomain()
    domain.add_action(yappla.DurativeActionSpec(
        name="d",
        conditions={},
        effects={},
        duration=1,
    ))

    planner = TemporalPlanner()

    # Bypass set_domain on purpose: this simulates a bug / misuse where durative
    # actions were not compiled into primitive Action operators.
    planner._domain = domain

    t0 = time.perf_counter()
    with pytest.raises(ValueError, match=r"DurativeActionSpec"):
        planner.plan(yappla.State({"x": 0}), "x == 0")
    elapsed = time.perf_counter() - t0
    perf_line("temporal_planner_fails_if_durative_action_in_domain", elapsed)


def test_temporal_planner_supports_compiled_start_success_pairs():
    """TemporalPlanner should treat start__/success__ as one durative activity.

    Key expectations:
    - start effects apply immediately at the start time (so they can lock resources)
    - success effects apply at the completion time
    - two actions that lock the same resource cannot overlap
    """

    domain = yappla.PlanningDomain()

    # Two durative actions sharing a single worker resource.
    domain.add_action(yappla.DurativeActionSpec(
        "job_a",
        duration=5,
        conditions={
            "to_start": "worker_busy == False and job_a_done == False",
            "to_success": "True",
            "to_abort": "True",
            "to_aborted": "True",
            "to_failure": "True",
        },
        effects={
            "on_start": {"worker_busy": True},
            "on_success": {"job_a_done": True, "worker_busy": False},
        },
    ))
    domain.add_action(yappla.DurativeActionSpec(
        "job_b",
        duration=1,
        conditions={
            "to_start": "worker_busy == False and job_b_done == False",
            "to_success": "True",
            "to_abort": "True",
            "to_aborted": "True",
            "to_failure": "True",
        },
        effects={
            "on_start": {"worker_busy": True},
            "on_success": {"job_b_done": True, "worker_busy": False},
        },
    ))

    planner = TemporalPlanner()
    planner.set_domain(domain)
    planner.max_verbosity_level = 0

    initial_state = yappla.State({
        "worker_busy": False,
        "job_a_done": False,
        "job_b_done": False,
    })
    goal = "job_a_done == True and job_b_done == True"

    result = planner.plan(initial_state, goal)
    assert result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in result.stats
    assert result.stats["makespan"] <= 6.1

    steps = [step for (_, step) in result.plan if step]
    assert all(isinstance(step, dict) for step in steps)

    def start_time_of(action_name: str) -> float:
        for step in steps:
            if step.get("name") == action_name:
                return float(step.get("time"))
        raise AssertionError(f"Missing action step: {action_name}; steps={steps}")

    t_a = start_time_of("job_a")
    t_b = start_time_of("job_b")
    # They must not overlap (single worker).
    if t_a <= t_b:
        assert t_a + 5.0 <= t_b + 0.01
    else:
        assert t_b + 1.0 <= t_a + 0.01


def test_temporal_planner_supports_abort_and_aborted_completion():
    """Abort during execution should lead to aborted__ completion effects at end."""

    domain = yappla.PlanningDomain()
    domain.add_action(yappla.DurativeActionSpec(
        "job",
        duration=5,
        conditions={
            "to_start": "job_state == 'idle'",
            "to_abort": "True",
            "to_aborted": "True",
            "to_success": "True",
            "to_failure": "True",
        },
        effects={
            "on_start": {"job_state": "running"},
            "on_abort": {"job_state": "aborting"},
            "on_aborted": {"job_aborted": True, "job_state": "idle"},
            "on_success": {"job_done": True, "job_state": "idle"},
        },
    ))

    planner = TemporalPlanner()
    planner.set_domain(domain)
    planner.max_verbosity_level = 0

    initial_state = yappla.State({
        "job_state": "idle",
        "job_done": False,
        "job_aborted": False,
    })
    goal = "job_aborted == True"

    result = planner.plan(initial_state, goal)
    assert result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in result.stats
    assert result.stats["makespan"] <= 5.1


def test_temporal_planner_abort_duration_shortens_makespan():
    """Aborting a running compiled durative should be able to complete sooner than success.

    We model this by giving abort__X a shorter duration than start__X.
    """

    domain = yappla.PlanningDomain()
    domain.add_action(yappla.DurativeActionSpec(
        "job",
        duration=10,
        conditions={
            "to_start": "job_state == 'idle'",
            "to_abort": "True",
            "to_aborted": "True",
            "to_success": "True",
            "to_failure": "True",
        },
        effects={
            "on_start": {"job_state": "running"},
            "on_abort": {"job_state": "aborting"},
            "on_aborted": {"job_aborted": True, "job_state": "idle"},
            "on_success": {"job_done": True, "job_state": "idle"},
        },
    ))

    planner = TemporalPlanner()
    planner.set_domain(domain)
    planner.max_verbosity_level = 0

    # Make abort faster than full completion.
    abort_op = planner.domain.action("abort__job")
    assert abort_op is not None
    abort_op.duration = 1.0

    initial_state = yappla.State({
        "job_state": "idle",
        "job_done": False,
        "job_aborted": False,
    })
    goal = "job_aborted == True"

    result = planner.plan(initial_state, goal)
    assert result.outcome == PlannerOutcome.SUCCESS
    assert "makespan" in result.stats
    assert result.stats["makespan"] <= 1.1

if __name__ == "__main__":
    print("Testing TemporalPlanner...\n")
    
    print("Test 1: Basic temporal planning")
    test_temporal_planner_basic()
    
    print("\nTest 2: Mutex constraints")
    test_temporal_planner_mutex_constraints()
    
    print("\nTest 3: Active actions tracking")
    test_temporal_state_active_actions()
    
    print("\nTest 4: Decision points")
    test_temporal_state_decision_points()
    
    print("\nTest 5: Mutex detection")
    test_temporal_state_mutex_detection()
    
    print("\nTest 6: Multiple actions sequence")
    test_temporal_planner_with_multiple_actions()
    
    print("\n✅ All temporal planner tests passed!")
