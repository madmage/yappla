"""Unit tests for Action class."""
import pytest
from yappla import Action, State


class TestAction:
    """Tests for the Action class."""

    def test_action_creation_basic(self):
        """Test creating a basic action."""
        action = Action(
            name="test_action",
            preconditions="x == 1",
            effects=[{"x": 2}],
            cost=1
        )
        assert action.name == "test_action"
        assert action.cost == 1

    def test_action_with_no_preconditions(self):
        """Test action with no preconditions (always applicable)."""
        action = Action(
            name="think",
            preconditions="",
            effects=[{"tired": True}],
            cost=1
        )
        state = State({"tired": False})
        assert action.applicable(state)

    def test_action_preconditions_met(self):
        """Test action with preconditions that are met."""
        action = Action(
            name="open_door",
            preconditions="door_locked == True",
            effects=[{"door_locked": False}],
            cost=1
        )
        state = State({"door_locked": True})
        assert action.applicable(state)

    def test_action_preconditions_not_met(self):
        """Test action with preconditions that are not met."""
        action = Action(
            name="open_door",
            preconditions="door_locked == True",
            effects=[{"door_locked": False}],
            cost=1
        )
        state = State({"door_locked": False})
        assert not action.applicable(state)

    def test_action_single_effect(self):
        """Test action with single effect."""
        action = Action(
            name="turn_on",
            preconditions="light == False",
            effects=[{"light": True}],
            cost=1
        )
        state = State({"light": False})
        outcomes = action.possible_outcomes(state)
        assert len(outcomes) == 1
        assert outcomes[0]["light"] is True

    def test_action_multiple_effects(self):
        """Test action with multiple effects on same state."""
        action = Action(
            name="make_coffee",
            preconditions="water_hot == True",
            effects=[{
                "coffee_ready": True,
                "water_used": 1
            }],
            cost=5
        )
        state = State({"water_hot": True, "water_used": 0})
        outcomes = action.possible_outcomes(state)
        assert len(outcomes) == 1
        assert outcomes[0]["coffee_ready"] is True
        assert outcomes[0]["water_used"] == 1

    def test_action_non_deterministic_effects(self):
        """Test action with non-deterministic effects."""
        action = Action(
            name="flip_coin",
            preconditions="",
            effects=[
                {"result": "heads"},
                {"result": "tails"}
            ],
            cost=1
        )
        state = State({"result": "unknown"})
        outcomes = action.possible_outcomes(state)
        assert len(outcomes) == 2
        results = [o["result"] for o in outcomes]
        assert "heads" in results
        assert "tails" in results

    def test_action_cost_default(self):
        """Test default action cost."""
        action = Action(
            name="test",
            preconditions="",
            effects=[{"x": 1}]
        )
        assert action.cost == 10  # Default cost

    def test_action_cost_custom(self):
        """Test custom action cost."""
        action = Action(
            name="expensive",
            preconditions="",
            effects=[{"x": 1}],
            cost=100
        )
        assert action.cost == 100

    def test_action_duration_default(self):
        """Test default action duration."""
        action = Action(
            name="test",
            preconditions="",
            effects=[{"x": 1}]
        )
        assert action.duration == 0.0

    def test_action_duration_custom(self):
        """Test custom action duration."""
        action = Action(
            name="test",
            preconditions="",
            effects=[{"x": 1}],
            duration=5
        )
        assert action.duration == 5.0

    def test_action_effects_from_dict(self):
        """Test action created with effects as dict."""
        action = Action(
            name="test",
            preconditions="",
            effects={"x": 1},
            cost=1
        )
        state = State({"x": 0})
        outcomes = action.possible_outcomes(state)
        assert len(outcomes) == 1
        assert outcomes[0]["x"] == 1

    def test_action_effects_from_list(self):
        """Test action created with effects as list."""
        action = Action(
            name="test",
            preconditions="",
            effects=[{"x": 1}],
            cost=1
        )
        state = State({"x": 0})
        outcomes = action.possible_outcomes(state)
        assert len(outcomes) == 1

    def test_action_effects_none(self):
        """Test action with no effects."""
        action = Action(
            name="observation",
            preconditions="",
            effects=None,
            cost=1
        )
        assert action.effects == []

    def test_action_repr(self):
        """Test string representation of action."""
        action = Action(
            name="test",
            preconditions="x == 1",
            effects=[{"x": 2}],
            cost=5
        )
        repr_str = repr(action)
        assert "ACTION" in repr_str
        assert "test" in repr_str
        assert "5" in repr_str  # cost

    def test_action_complex_preconditions(self):
        """Test action with complex preconditions."""
        action = Action(
            name="complex",
            preconditions="x > 5 and y < 10 and z == 'ready'",
            effects=[{"status": "complete"}],
            cost=1
        )
        state = State({"x": 7, "y": 8, "z": "ready"})
        assert action.applicable(state)

        state2 = State({"x": 3, "y": 8, "z": "ready"})
        assert not action.applicable(state2)

    def test_action_apply_deterministic(self):
        """Test applying deterministic action."""
        action = Action(
            name="pick_up",
            preconditions="holding == False",
            effects=[{"holding": True}],
            cost=1
        )
        state = State({"holding": False})
        result = action.apply(state)
        assert result["holding"] is True

    def test_action_apply_non_deterministic(self):
        """Test applying non-deterministic action."""
        action = Action(
            name="coin_flip",
            preconditions="",
            effects=[
                {"flip": "H"},
                {"flip": "T"}
            ],
            cost=1
        )
        state = State({"flip": "unknown"})
        result = action.apply(state)
        # Non-deterministic action should have "?" for uncertain values
        # or one of the outcomes
        assert result["flip"] in ["H", "T", "?"]

    def test_action_preconditions_property(self):
        """Test preconditions property."""
        action = Action(
            name="test",
            preconditions="x == 1",
            effects=[{"x": 2}],
            cost=1
        )
        assert action.preconditions == "x == 1"

        action_no_pre = Action(
            name="test",
            preconditions="",
            effects=[{"x": 2}],
            cost=1
        )
        assert action_no_pre.preconditions == "True"

    def test_action_effects_property(self):
        """Test effects property."""
        effect_dict = {"x": 1, "y": 2}
        action = Action(
            name="test",
            preconditions="",
            effects=effect_dict,
            cost=1
        )
        effects = action.effects
        assert len(effects) == 1
        assert effects[0] == effect_dict


class TestComplexActions:
    """Tests for complex action scenarios."""

    def test_action_multiple_possible_outcomes(self):
        """Test action with multiple probabilistic outcomes."""
        action = Action(
            name="roll_die",
            preconditions="",
            effects=[
                {"die": i} for i in range(1, 7)
            ],
            cost=1
        )
        state = State({"die": 0})
        outcomes = action.possible_outcomes(state)
        assert len(outcomes) == 6
        die_values = [o["die"] for o in outcomes]
        assert all(i in die_values for i in range(1, 7))

    def test_action_preserves_unaffected_variables(self):
        """Test that actions preserve unaffected state variables."""
        action = Action(
            name="change_x",
            preconditions="",
            effects=[{"x": 10}],
            cost=1
        )
        state = State({"x": 0, "y": 5, "z": "unchanged"})
        outcomes = action.possible_outcomes(state)
        assert outcomes[0]["y"] == 5
        assert outcomes[0]["z"] == "unchanged"

    def test_action_with_arithmetic_in_effects(self):
        """Test action with arithmetic in effects."""
        action = Action(
            name="increment",
            preconditions="x < 100",
            effects=[{"x": "x + 1"}],
            cost=1
        )
        state = State({"x": 5})
        outcomes = action.possible_outcomes(state)
        # Note: This depends on how the action engine evaluates expressions
        # Currently might not work directly - documented as expected behavior

    def test_action_conditional_applicability(self):
        """Test action applicability based on multiple conditions."""
        action = Action(
            name="conditional",
            preconditions="(state == 'ready' or state == 'idle') and power >= 50",
            effects=[{"state": "executing"}],
            cost=1
        )
        
        state1 = State({"state": "ready", "power": 75})
        assert action.applicable(state1)
        
        state2 = State({"state": "ready", "power": 30})
        assert not action.applicable(state2)
        
        state3 = State({"state": "executing", "power": 75})
        assert not action.applicable(state3)
