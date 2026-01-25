=======
Actions
=======

This guide covers how to define and use actions in YAPPLA.

Introduction to Actions
=======================

Actions represent the operators that can transform states. Each action has:

- **Name**: Unique identifier
- **Preconditions**: Requirements that must be satisfied
- **Effects**: Changes to state variables
- **Cost**: The expense of executing the action
- **Duration**: For durative actions

Basic Action Definition
=======================

.. code-block:: python

    from yappla import Action
    
    unlock_door = Action(
        name="unlock_door",
        preconditions="location == 'door' and has_key == True",
        effects=[{"door_locked": False}],
        cost=1
    )

Preconditions
=============

Preconditions are boolean expressions that must evaluate to true:

.. code-block:: python

    # Simple condition
    turn_on_light = Action(
        name="turn_on_light",
        preconditions="light == False",
        effects=[{"light": True}],
        cost=1
    )
    
    # Complex conditions
    drive_to_work = Action(
        name="drive_to_work",
        preconditions="location == 'home' and has_car == True and weather != 'snow'",
        effects=[{"location": "work"}],
        cost=30
    )
    
    # No preconditions (always applicable)
    think = Action(
        name="think",
        preconditions="",
        effects=[{"tiredness": "increased"}],
        cost=1
    )

Effects
=======

Effects specify how state variables change:

Single Effect
-------------

.. code-block:: python

    turn_off = Action(
        name="turn_off",
        preconditions="light == True",
        effects=[{"light": False}],
        cost=1
    )

Multiple Effects
----------------

.. code-block:: python

    make_coffee = Action(
        name="make_coffee",
        preconditions="kettle_on == True and cups_available > 0",
        effects=[{
            "coffee_ready": True,
            "cups_available": "cups_available - 1",
            "time_spent": 5
        }],
        cost=10
    )

Deterministic Effects
---------------------

All possible outcomes are the same:

.. code-block:: python

    pick_up = Action(
        name="pick_up_object",
        preconditions="object_available == True",
        effects=[{"holding": "object"}],
        cost=1
    )

Non-deterministic Effects (Probabilistic)
------------------------------------------

Multiple possible outcomes:

.. code-block:: python

    flip_coin = Action(
        name="flip_coin",
        preconditions="coin_available == True",
        effects=[
            {"coin_result": "heads"},
            {"coin_result": "tails"}
        ],
        cost=1
    )
    
    # When this action is applied, the planner generates states for both outcomes
    # If planning for contingency, it must handle all possible outcomes

Action Costs
============

Costs affect which plans the planner prefers:

.. code-block:: python

    # Low-cost actions
    walk = Action(name="walk", ..., cost=1)
    
    # Higher-cost actions
    call_taxi = Action(name="call_taxi", ..., cost=50)
    
    # The planner will prefer walking to calling a taxi when both reach the goal

Cost Considerations:

- Represents resource consumption (fuel, time, money)
- Affects plan quality (lower total cost = better plan)
- Enables optimization (find minimum-cost plan)

Checking Action Applicability
==============================

.. code-block:: python

    from yappla import State, Action
    
    unlock = Action(
        name="unlock",
        preconditions="door_locked == True and has_key == True",
        effects=[{"door_locked": False}],
        cost=1
    )
    
    state = State({"door_locked": True, "has_key": False})
    
    # Check if applicable
    if unlock.applicable(state):
        # Execute action
        new_states = unlock.possible_outcomes(state)
    else:
        print("Cannot apply unlock: preconditions not satisfied")

Applying Actions
================

Get Possible Outcomes
---------------------

.. code-block:: python

    action = ...
    current_state = ...
    
    # Get all possible resulting states
    next_states = action.possible_outcomes(current_state)
    
    for next_state in next_states:
        # Process each possible outcome
        print(next_state.pretty_str())

Apply (Collapsed Non-determinism)
----------------------------------

For non-deterministic actions, collapse to a single state with "?" for uncertain values:

.. code-block:: python

    state_after_flip = flip_coin.apply(current_state)
    # Result might be: {"coin": "?", ...}

Durative Actions
================

Actions that take time:

.. code-block:: python

    from yappla import DurativeActionSpec
    
    bake_cookies = DurativeActionSpec(
        name="bake_cookies",
        conditions={
            "to_start": "ingredients_mixed == True and oven_preheated == True",
            "to_success": "baking_time >= 30",
            "to_failure": "temperature > 300"
        },
        effects={
            "on_start": {"oven_status": "running"},
            "on_success": {"cookies": "ready"},
            "on_failure": {"cookies": "burned"}
        },
        duration=30.0,
        cost=50
    )

Key convention
--------------

- Preconditions are given in a `conditions` dict keyed by `to_*` (e.g. `to_start`, `to_success`).
- Effects are given in an `effects` dict keyed by `on_*` (e.g. `on_start`, `on_success`).

These keys match the YAML conventions used by Yappla domain fixtures.

Temporal semantics
------------------

When using `TemporalPlanner`, `on_start` effects apply immediately at the action start time
(useful for locking resources), while completion effects like `on_success` apply when the
action finishes.

Durative Action Events:

- **start**: Beginning of the action
- **success**: Action completes successfully
- **failure**: Action fails mid-execution  
- **abort**: Action is aborted by the planner
- **aborted**: Action has been aborted

The planner converts durative actions into multiple simple actions internally.

Creating Reusable Actions
==========================

Templates for common patterns:

.. code-block:: python

    def make_movement_action(from_loc, to_loc, duration=5):
        """Factory function for movement actions"""
        return Action(
            name=f"move_from_{from_loc}_to_{to_loc}",
            preconditions=f"location == '{from_loc}'",
            effects=[{"location": to_loc}],
            cost=duration
        )
    
    # Create multiple movement actions
    domain.add_action(make_movement_action("room_a", "room_b"))
    domain.add_action(make_movement_action("room_b", "room_c"))

Expression Syntax
=================

Supported in preconditions and effects:

- **Comparisons**: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical**: `and`, `or`, `not`
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Parentheses**: For grouping

.. code-block:: python

    # Complex expression
    action = Action(
        name="example",
        preconditions="(x > 10 or x < -10) and (y == 'safe') and not emergency",
        effects=[{"status": "active"}],
        cost=1
    )

Best Practices
==============

1. **Clear naming**: Use descriptive action names
2. **Atomic operations**: Keep actions focused
3. **Reasonable costs**: Reflect actual resource usage
4. **Specific preconditions**: Prevent invalid states
5. **Consistent effects**: Ensure effects are realistic
