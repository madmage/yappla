"""Unit tests for Planner class."""
import pytest
import time
from yappla import Planner, PlanningDomain, State, Action, StateVariable
from yappla.plan import PlannerOutcome

from .perf import perf_line
from .plan_report import record_plan


class TestPlanner:
    """Tests for the Planner class."""

    def test_planner_creation(self):
        """Test creating a planner."""
        planner = Planner()
        assert planner.max_iterations == 10000
        assert planner.max_verbosity_level == 0

    def test_planner_set_domain(self):
        """Test setting domain for planner."""
        planner = Planner()
        domain = PlanningDomain()
        planner.set_domain(domain)
        assert planner.domain == domain

    def test_planner_simple_planning(self):
        """Test simple planning scenario."""
        # Create domain
        domain = PlanningDomain()
        
        # Create actions
        toggle = Action(
            "toggle",
            preconditions="x == 0",
            effects=[{"x": 1}],
            cost=1
        )
        domain.add_action(toggle)
        
        # Create planner
        planner = Planner()
        planner.set_domain(domain)
        
        # Plan
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 1")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_simple_planning",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_simple_planning",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        # Verify
        assert result.outcome == PlannerOutcome.SUCCESS
        assert len(result.plan) == 2  # initial state + final state

    def test_planner_goal_already_satisfied(self):
        """Test planning when goal is already satisfied."""
        domain = PlanningDomain()
        domain.add_action(Action("noop", preconditions="", effects=[{"x": 0}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 1})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 1")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_goal_already_satisfied",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_goal_already_satisfied",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.ALREADY_AT_GOAL

    def test_planner_impossible_goal(self):
        """Test planning with impossible goal."""
        domain = PlanningDomain()
        domain.add_action(Action("noop", preconditions="", effects=[{"x": 0}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 10")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_impossible_goal",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
        )
        record_plan(
            "planner_impossible_goal",
            initial_state=initial,
            goal="x == 10",
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.FAILURE

    def test_planner_multi_step_plan(self):
        """Test planning with multiple steps."""
        domain = PlanningDomain()
        domain.add_action(Action("a1", preconditions="x == 0", effects=[{"x": 1}], cost=1))
        domain.add_action(Action("a2", preconditions="x == 1", effects=[{"x": 2}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 2")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_multi_step_plan",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_multi_step_plan",
            initial_state=initial,
            goal="x == 2",
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.SUCCESS
        assert len(result.plan) == 3  # (state0, a1), (state1, a2), (state2, None)

    def test_planner_plan_contains_states_and_actions(self):
        """Test that plan contains state-action pairs."""
        domain = PlanningDomain()
        domain.add_action(Action("go", preconditions="", effects=[{"x": 1}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 1")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_plan_contains_states_and_actions",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_plan_contains_states_and_actions",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        # Plan should be list of (state, action) tuples
        assert len(result.plan) > 0
        for state, action in result.plan:
            assert isinstance(state, State)
            # action can be None for initial/goal states

    def test_planner_statistics(self):
        """Test that planner computes statistics."""
        domain = PlanningDomain()
        domain.add_action(Action("go", preconditions="", effects=[{"x": 1}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 1")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_statistics",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
        )
        record_plan(
            "planner_statistics",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        assert "time" in result.stats
        assert "iterations" in result.stats
        assert result.stats["time"] >= 0
        assert result.stats["iterations"] > 0

    def test_planner_set_goal(self):
        """Test setting goal directly."""
        domain = PlanningDomain()
        domain.add_action(Action("go", preconditions="", effects=[{"x": 1}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        planner.set_goal("x == 1")
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial)  # No goal passed, uses set_goal
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_set_goal",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
        )
        record_plan(
            "planner_set_goal",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.SUCCESS

    def test_planner_max_iterations_limit(self):
        """Test that planner respects max_iterations."""
        domain = PlanningDomain()
        domain.add_action(Action("go", preconditions="", effects=[{"x": 1}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        planner.max_iterations = 1  # Very low limit
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 1")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_max_iterations_limit",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
        )
        record_plan(
            "planner_max_iterations_limit",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        assert result.stats["iterations"] <= 1

    def test_planner_verbosity_levels(self):
        """Test different verbosity levels."""
        domain = PlanningDomain()
        domain.add_action(Action("go", preconditions="", effects=[{"x": 1}], cost=1))
        
        for verbosity in [0, 1, 2]:
            planner = Planner()
            planner.set_domain(domain)
            planner.max_verbosity_level = verbosity
            
            initial = State({"x": 0})
            t0 = time.perf_counter()
            result = planner.plan(initial, "x == 1")
            elapsed = time.perf_counter() - t0
            perf_line(
                f"planner_verbosity_levels_v{verbosity}",
                elapsed,
                iterations=result.stats.get("iterations"),
                outcome=getattr(result.outcome, "name", result.outcome),
            )
            record_plan(
                f"planner_verbosity_levels_v{verbosity}",
                initial_state=initial,
                goal="x == 1",
                result=result,
                planner_type="Planner",
            )
            
            # All should still succeed
            assert result.outcome == PlannerOutcome.SUCCESS

    def test_planner_cost_consideration(self):
        """Test that planner considers action costs."""
        domain = PlanningDomain()
        # Expensive path
        domain.add_action(Action("expensive", preconditions="x == 0", effects=[{"x": 2}], cost=100))
        # Cheap path (longer)
        domain.add_action(Action("cheap1", preconditions="x == 0", effects=[{"x": 1}], cost=1))
        domain.add_action(Action("cheap2", preconditions="x == 1", effects=[{"x": 2}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 2")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_cost_consideration",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_cost_consideration",
            initial_state=initial,
            goal="x == 2",
            result=result,
            planner_type="Planner",
        )
        
        # Should find the cheaper path (2 cheap actions = cost 2 vs 1 expensive = cost 100)
        assert result.outcome == PlannerOutcome.SUCCESS
        assert len(result.plan) >= 3  # At least 3 steps (initial + 2 actions + goal)

    def test_planner_complex_preconditions(self):
        """Test planning with complex preconditions."""
        domain = PlanningDomain()
        
        action1 = Action("setup", preconditions="", effects=[{"ready": True, "power": 100}], cost=1)
        action2 = Action(
            "execute",
            preconditions="ready == True and power > 50",
            effects=[{"executing": True, "power": 50}],
            cost=1
        )
        
        domain.add_action(action1)
        domain.add_action(action2)
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"ready": False, "power": 0, "executing": False})
        t0 = time.perf_counter()
        result = planner.plan(initial, "executing == True and power > 0")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_complex_preconditions",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
        )
        record_plan(
            "planner_complex_preconditions",
            initial_state=initial,
            goal="executing == True and power > 0",
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.SUCCESS

    def test_planner_pretty_string_output(self):
        """Test pretty string representation of plan."""
        domain = PlanningDomain()
        domain.add_action(Action("go", preconditions="", effects=[{"x": 1}], cost=1))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 1")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_pretty_string_output",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
        )
        record_plan(
            "planner_pretty_string_output",
            initial_state=initial,
            goal="x == 1",
            result=result,
            planner_type="Planner",
        )
        
        pretty = result.pretty_str()
        assert isinstance(pretty, str)
        assert "PLAN" in pretty.upper() or "GOAL" in pretty.upper()


class TestPlannerComplexScenarios:
    """Tests for complex planning scenarios."""

    def test_planner_branching_actions(self):
        """Test planning with non-deterministic actions."""
        domain = PlanningDomain()
        
        # Non-deterministic action
        domain.add_action(Action(
            "flip",
            preconditions="",
            effects=[{"coin": "heads"}, {"coin": "tails"}],
            cost=1
        ))
        
        domain.add_action(Action(
            "win_heads",
            preconditions="coin == 'heads'",
            effects=[{"won": True}],
            cost=1
        ))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"coin": "unknown", "won": False})
        t0 = time.perf_counter()
        result = planner.plan(initial, "won == True")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_branching_actions",
            elapsed,
            iterations=getattr(result, "stats", {}).get("iterations") if result is not None else None,
            outcome=getattr(getattr(result, "outcome", None), "name", getattr(result, "outcome", None)),
        )
        if result is not None:
            record_plan(
                "planner_branching_actions",
                initial_state=initial,
                goal="won == True",
                result=result,
                planner_type="Planner",
            )
        
        # Might succeed or fail depending on planning strategy
        # At minimum, should not crash
        assert result is not None

    def test_planner_multiple_variables(self):
        """Test planning with many variables."""
        domain = PlanningDomain()
        
        # Create actions for multiple variables
        for i in range(10):
            domain.add_action(Action(
                f"set_x{i}",
                preconditions=f"x{i} == 0",
                effects=[{f"x{i}": 1}],
                cost=1
            ))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({f"x{i}": 0 for i in range(10)})
        goal = " and ".join([f"x{i} == 1" for i in range(10)])
        
        t0 = time.perf_counter()
        result = planner.plan(initial, goal)
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_multiple_variables",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_multiple_variables",
            initial_state=initial,
            goal=goal,
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.SUCCESS
        assert len(result.plan) == 11  # (state0, a0), ..., (state10, None)

    def test_planner_long_plan(self):
        """Test planning for longer sequences."""
        domain = PlanningDomain()
        
        # Create a chain of actions
        for i in range(5):
            next_val = i + 1
            domain.add_action(Action(
                f"step_{i}",
                preconditions=f"x == {i}",
                effects=[{"x": next_val}],
                cost=1
            ))
        
        planner = Planner()
        planner.set_domain(domain)
        
        initial = State({"x": 0})
        t0 = time.perf_counter()
        result = planner.plan(initial, "x == 5")
        elapsed = time.perf_counter() - t0
        perf_line(
            "planner_long_plan",
            elapsed,
            iterations=result.stats.get("iterations"),
            outcome=getattr(result.outcome, "name", result.outcome),
            plan_len=len(result.plan) if result.plan is not None else None,
        )
        record_plan(
            "planner_long_plan",
            initial_state=initial,
            goal="x == 5",
            result=result,
            planner_type="Planner",
        )
        
        assert result.outcome == PlannerOutcome.SUCCESS
        assert len(result.plan) == 6  # (state0, s0), ..., (state5, None)
