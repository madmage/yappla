"""Unit tests for State class and related functions."""
import pytest
import time
from yappla import State, StateVariable

from .perf import perf_line


class TestState:
    """Tests for the State class."""

    def test_state_creation_from_dict(self):
        """Test creating a state from a dictionary."""
        state = State({"location": "home", "light": True})
        assert state["location"] == "home"
        assert state["light"] is True

    def test_state_access_like_dict(self):
        """Test accessing state values like a dictionary."""
        state = State({"x": 1, "y": 2})
        assert state["x"] == 1
        assert state["y"] == 2

    def test_state_modification(self):
        """Test modifying state values."""
        state = State({"x": 0})
        state["x"] = 5
        assert state["x"] == 5

    def test_state_contains(self):
        """Test membership testing in state."""
        state = State({"x": 1})
        assert "x" in state
        assert "y" not in state

    def test_state_hash_consistency(self):
        """Test that identical states produce identical hashes."""
        state1 = State({"a": 1, "b": 2})
        state2 = State({"a": 1, "b": 2})
        assert state1.hash() == state2.hash()

    def test_state_hash_different_values(self):
        """Test that different states produce different hashes."""
        state1 = State({"a": 1})
        state2 = State({"a": 2})
        assert state1.hash() != state2.hash()

    def test_state_pretty_str_basic(self):
        """Test basic pretty string representation."""
        state = State({"x": 1})
        pretty = state.pretty_str(columns=False)
        assert "x" in pretty
        assert "1" in pretty

    def test_state_pretty_str_with_hash(self):
        """Test pretty string with hash."""
        state = State({"x": 1})
        pretty = state.pretty_str(columns=False, show_hashes=True)
        assert state.hash() in pretty

    def test_state_satisfies_simple_condition(self):
        """Test condition satisfaction with simple expression."""
        state = State({"x": 5})
        assert state.satisfies_conditions("x == 5")
        assert not state.satisfies_conditions("x == 3")

    def test_state_satisfies_complex_condition(self):
        """Test condition satisfaction with complex expression."""
        state = State({"x": 5, "y": 10})
        assert state.satisfies_conditions("x < y and x > 0")
        assert not state.satisfies_conditions("x > y")

    def test_state_satisfies_string_condition(self):
        """Test condition satisfaction with string values."""
        state = State({"location": "home", "light": True})
        assert state.satisfies_conditions("location == 'home'")
        assert state.satisfies_conditions("light == True")

    def test_state_satisfies_constraints(self):
        """Test constraint satisfaction."""
        state = State({"battery": 50, "mode": "active"})
        constraints = [
            {
                "conditions": "mode == 'active'",
                "constraint": "battery > 20"
            }
        ]
        assert state.satisfies_constraints(constraints)

    def test_state_empty(self):
        """Test empty state."""
        state = State({})
        assert len(state) == 0

    def test_state_copy_independence(self):
        """Test that state copies are independent."""
        state1 = State({"x": 1})
        state2 = State(state1)
        state2["x"] = 2
        assert state1["x"] == 1
        assert state2["x"] == 2

    def test_state_iteration(self):
        """Test iterating over state items."""
        state = State({"x": 1, "y": 2})
        items = dict(state)
        assert items == {"x": 1, "y": 2}

    def test_state_with_various_types(self):
        """Test state with various value types."""
        state = State({
            "int_val": 42,
            "str_val": "test",
            "bool_val": True,
            "float_val": 3.14
        })
        assert state["int_val"] == 42
        assert state["str_val"] == "test"
        assert state["bool_val"] is True
        assert state["float_val"] == 3.14

    def test_state_hash_length(self):
        """Test that state hash has expected length (6 chars)."""
        state = State({"x": 1})
        assert len(state.hash()) == 6

    def test_state_equality(self):
        """Test state equality."""
        state1 = State({"x": 1, "y": 2})
        state2 = State({"x": 1, "y": 2})
        assert state1 == state2

    def test_state_inequality(self):
        """Test state inequality."""
        state1 = State({"x": 1})
        state2 = State({"x": 2})
        assert state1 != state2


class TestStateVariable:
    """Tests for the StateVariable class."""

    def test_state_variable_creation(self):
        """Test creating a state variable."""
        var = StateVariable(
            name="location",
            possible_values=["home", "work", "school"],
            initial_value="home"
        )
        assert var.name == "location"
        assert var.initial_value == "home"
        assert "home" in var.possible_values

    def test_state_variable_no_initial_value(self):
        """Test state variable without initial value."""
        var = StateVariable(
            name="temp",
            possible_values=[0, 100]
        )
        assert var.initial_value is None

    def test_state_variable_repr(self):
        """Test string representation of state variable."""
        var = StateVariable(
            name="x",
            possible_values=[1, 2, 3],
            initial_value=1
        )
        repr_str = repr(var)
        assert "x" in repr_str
        assert "VARIABLE" in repr_str

    def test_state_variable_binary(self):
        """Test binary state variable."""
        var = StateVariable(
            name="light",
            possible_values=[True, False],
            initial_value=False
        )
        assert var.initial_value is False


class TestComplexStates:
    """Tests for complex state scenarios."""

    def test_large_state(self):
        """Test state with many variables."""
        t0 = time.perf_counter()
        state_dict = {f"var_{i}": i for i in range(100)}
        state = State(state_dict)
        assert len(state) == 100
        assert state["var_50"] == 50
        elapsed = time.perf_counter() - t0
        perf_line("state_large_state", elapsed, variables=len(state))

    def test_deeply_nested_conditions(self):
        """Test complex nested conditions."""
        t0 = time.perf_counter()
        state = State({
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4
        })
        condition = "((a > 0 and b > 0) or (c > 10)) and (d < 5)"
        assert state.satisfies_conditions(condition)
        elapsed = time.perf_counter() - t0
        perf_line("state_deeply_nested_conditions", elapsed)

    def test_arithmetic_in_conditions(self):
        """Test arithmetic operations in conditions."""
        t0 = time.perf_counter()
        state = State({"x": 10, "y": 20})
        assert state.satisfies_conditions("x + y == 30")
        assert state.satisfies_conditions("y - x == 10")
        assert state.satisfies_conditions("x * 2 == y")
        elapsed = time.perf_counter() - t0
        perf_line("state_arithmetic_in_conditions", elapsed)
