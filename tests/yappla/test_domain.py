"""Unit tests for PlanningDomain class."""
import pytest
import time
from yappla import PlanningDomain, Action, StateVariable, State

from .perf import perf_line


class TestDomain:
    """Tests for the PlanningDomain class."""

    def test_domain_creation(self):
        """Test creating an empty domain."""
        domain = PlanningDomain()
        assert len(domain.actions) == 0
        assert len(domain.variables) == 0

    def test_domain_add_action(self):
        """Test adding an action to domain."""
        domain = PlanningDomain()
        action = Action("test", preconditions="", effects=[{"x": 1}], cost=1)
        domain.add_action(action)
        assert len(domain.actions) == 1
        assert domain.action("test") == action

    def test_domain_add_multiple_actions(self):
        """Test adding multiple actions to domain."""
        domain = PlanningDomain()
        action1 = Action("action1", preconditions="", effects=[{"x": 1}], cost=1)
        action2 = Action("action2", preconditions="", effects=[{"y": 2}], cost=1)
        domain.add_action(action1)
        domain.add_action(action2)
        assert len(domain.actions) == 2
        assert "action1" in domain.actions
        assert "action2" in domain.actions

    def test_domain_get_nonexistent_action(self):
        """Test getting a non-existent action returns None."""
        domain = PlanningDomain()
        assert domain.action("nonexistent") is None

    def test_domain_add_variable(self):
        """Test adding a state variable to domain."""
        domain = PlanningDomain()
        var = StateVariable("location", ["home", "office"], "home")
        domain.add_variable(var)
        assert len(domain.variables) == 1
        assert domain.variable("location") == var

    def test_domain_add_multiple_variables(self):
        """Test adding multiple variables to domain."""
        domain = PlanningDomain()
        var1 = StateVariable("x", [0, 1], 0)
        var2 = StateVariable("y", [0, 1], 0)
        domain.add_variable(var1)
        domain.add_variable(var2)
        assert len(domain.variables) == 2

    def test_domain_get_nonexistent_variable(self):
        """Test getting a non-existent variable returns None."""
        domain = PlanningDomain()
        assert domain.variable("nonexistent") is None

    def test_domain_get_initial_state(self):
        """Test getting initial state from domain."""
        domain = PlanningDomain()
        var1 = StateVariable("x", [0, 1], 0)
        var2 = StateVariable("y", [True, False], True)
        domain.add_variable(var1)
        domain.add_variable(var2)
        
        initial = domain.get_initial_state()
        assert initial["x"] == 0
        assert initial["y"] is True

    def test_domain_initial_state_with_none_values(self):
        """Test initial state with None initial values."""
        domain = PlanningDomain()
        var = StateVariable("unknown", [0, 1])  # No initial_value
        domain.add_variable(var)
        
        initial = domain.get_initial_state()
        assert initial["unknown"] == "UNK"

    def test_domain_repr(self):
        """Test string representation of domain."""
        domain = PlanningDomain()
        var = StateVariable("x", [0, 1], 0)
        action = Action("move", preconditions="", effects=[{"x": 1}], cost=1)
        domain.add_variable(var)
        domain.add_action(action)
        
        repr_str = repr(domain)
        assert "DOMAIN" in repr_str
        assert "move" in repr_str

    def test_domain_actions_property(self):
        """Test accessing actions property."""
        domain = PlanningDomain()
        action1 = Action("a1", preconditions="", effects=[{"x": 1}], cost=1)
        action2 = Action("a2", preconditions="", effects=[{"x": 2}], cost=1)
        domain.add_action(action1)
        domain.add_action(action2)
        
        actions = domain.actions
        assert len(actions) == 2
        assert "a1" in actions
        assert "a2" in actions

    def test_domain_variables_property(self):
        """Test accessing variables property."""
        domain = PlanningDomain()
        var1 = StateVariable("x", [0, 1], 0)
        var2 = StateVariable("y", [0, 1], 0)
        domain.add_variable(var1)
        domain.add_variable(var2)
        
        variables = domain.variables
        assert len(variables) == 2
        assert "x" in variables
        assert "y" in variables

    def test_domain_action_lookup(self):
        """Test looking up actions by name."""
        domain = PlanningDomain()
        action = Action("test_action", preconditions="x == 0", effects=[{"x": 1}], cost=5)
        domain.add_action(action)
        
        found = domain.action("test_action")
        assert found.name == "test_action"
        assert found.cost == 5

    def test_domain_variable_lookup(self):
        """Test looking up variables by name."""
        domain = PlanningDomain()
        var = StateVariable("test_var", [1, 2, 3], 1)
        domain.add_variable(var)
        
        found = domain.variable("test_var")
        assert found.name == "test_var"
        assert found.initial_value == 1


class TestDomainComplexScenarios:
    """Tests for complex domain scenarios."""

    def test_domain_with_interdependent_actions(self):
        """Test domain with actions that depend on each other."""
        domain = PlanningDomain()
        
        # Add variables
        domain.add_variable(StateVariable("door_locked", [True, False], True))
        domain.add_variable(StateVariable("door_open", [True, False], False))
        
        # Action 1: Unlock door
        unlock = Action(
            "unlock",
            preconditions="door_locked == True",
            effects=[{"door_locked": False}],
            cost=1
        )
        
        # Action 2: Open door (depends on unlock)
        open_door = Action(
            "open",
            preconditions="door_locked == False",
            effects=[{"door_open": True}],
            cost=1
        )
        
        domain.add_action(unlock)
        domain.add_action(open_door)
        
        assert len(domain.actions) == 2
        initial = domain.get_initial_state()
        assert initial["door_locked"] is True
        assert initial["door_open"] is False

    def test_large_domain(self):
        """Test creating a large domain."""
        t0 = time.perf_counter()
        domain = PlanningDomain()
        
        # Add many variables
        for i in range(50):
            var = StateVariable(f"var_{i}", [0, 1], 0)
            domain.add_variable(var)
        
        # Add many actions
        for i in range(50):
            action = Action(
                f"action_{i}",
                preconditions="",
                effects=[{f"var_{i}": 1}],
                cost=1
            )
            domain.add_action(action)
        
        assert len(domain.variables) == 50
        assert len(domain.actions) == 50
        
        initial = domain.get_initial_state()
        assert len(initial) == 50
        elapsed = time.perf_counter() - t0
        perf_line(
            "domain_large_domain",
            elapsed,
            variables=len(domain.variables),
            actions=len(domain.actions),
        )

    def test_domain_without_durative_actions(self):
        """Test domain without durative actions."""
        domain = PlanningDomain()
        action = Action("simple", preconditions="", effects=[{"x": 1}], cost=1)
        domain.add_action(action)
        
        assert not domain.contains_action_specs()

    def test_domain_initial_state_consistency(self):
        """Test that initial state is consistent across calls."""
        domain = PlanningDomain()
        var = StateVariable("x", [0, 1, 2], 1)
        domain.add_variable(var)
        
        state1 = domain.get_initial_state()
        state2 = domain.get_initial_state()
        
        assert state1 == state2
        assert state1.hash() == state2.hash()

        def test_durative_action_spec_split_metadata(self):
            import yappla

            spec = yappla.DurativeActionSpec(
                name="job",
                conditions={
                    "to_start": "True",
                    "to_abort": "True",
                    "to_success": "True",
                    "to_failure": "True",
                    "to_aborted": "True",
                },
                effects={
                    "on_start": {"x": 1},
                    "on_success": {"x": 2},
                    "on_failure": {"x": 3},
                    "on_abort": {"x": 4},
                    "on_aborted": {"x": 5},
                },
                duration=7.0,
            )

            split = spec.split()
            assert len(split) == 5

            by_kind = {a.split_kind: a for a in split}
            assert set(by_kind.keys()) == {"start", "abort", "success", "failure", "aborted"}

            for a in split:
                assert a.parent_action_name == "job"
                assert a.split_kind in ("start", "abort", "success", "failure", "aborted")
                assert a.split_category in ("decision", "event")

            assert by_kind["start"].split_category == "decision"
            assert by_kind["abort"].split_category == "decision"
            assert by_kind["success"].split_category == "event"
            assert by_kind["failure"].split_category == "event"
            assert by_kind["aborted"].split_category == "event"


class TestDomainLoadFromDict:
    """Tests for loading domain from dictionary."""

    def test_load_from_dict_simple(self):
        """Test loading domain from dictionary."""
        t0 = time.perf_counter()
        domain = PlanningDomain()
        definition = {
            "domain": {
                "variables": {
                    "x": {
                        "possible_values": [0, 1],
                        "initial_value": 0
                    }
                },
                "actions": {
                    "toggle": {
                        "preconditions": "x == 0",
                        "effects": [{"x": 1}],
                        "cost": 1
                    }
                }
            }
        }
        
        domain.load_from_dict(definition)
        assert "x" in domain.variables
        assert "toggle" in domain.actions
        elapsed = time.perf_counter() - t0
        perf_line(
            "domain_load_from_dict_simple",
            elapsed,
            variables=len(domain.variables),
            actions=len(domain.actions),
        )

    def test_load_from_dict_without_domain_wrapper(self):
        """Test loading domain from dict without 'domain' wrapper."""
        domain = PlanningDomain()
        definition = {
            "variables": {
                "x": {
                    "possible_values": [0, 1],
                    "initial_value": 0
                }
            },
            "actions": {
                "toggle": {
                    "preconditions": "x == 0",
                    "effects": [{"x": 1}],
                    "cost": 1
                }
            }
        }
        
        domain.load_from_dict(definition)
        assert "x" in domain.variables
        assert "toggle" in domain.actions
