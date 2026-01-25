========
Concepts
========

This page explains the core concepts behind automated planning and YAPPLA.

What is Automated Planning?
============================

Automated planning is the process of finding a sequence of actions that transforms an initial state of the world into a desired goal state. The planner automatically discovers this sequence without explicit programming of the solution.

Components of a Planning Problem
================================

1. **State Variables**: Properties or attributes of the world that can change
2. **Initial State**: The starting configuration of all state variables
3. **Actions**: Operations that can change the state
4. **Goal**: A condition or set of conditions to achieve
5. **Domain**: A description of the planning problem including state variables and actions

State Space Search
==================

YAPPLA uses **Dijkstra's algorithm** to search through the state space. This means:

- The algorithm explores states by applying applicable actions
- Each action has a cost (default: 10)
- The planner finds the lowest-cost path from initial state to goal
- This guarantees finding an optimal solution (minimum cost plan)

State Variables
===============

State variables represent properties that can have different values:

.. code-block:: python

    from yappla import StateVariable
    
    # Simple binary state variable
    light = StateVariable(
        name="light",
        possible_values=[True, False],
        initial_value=False
    )
    
    # Multi-valued state variable
    robot_location = StateVariable(
        name="robot_location",
        possible_values=["room_a", "room_b", "room_c"],
        initial_value="room_a"
    )

Actions
=======

Actions represent the things the planner can do:

.. code-block:: python

    from yappla import Action
    
    # Simple action
    turn_on_light = Action(
        name="turn_on_light",
        preconditions="light == False",
        effects=[{"light": True}],
        cost=1
    )
    
    # Action with non-deterministic effects (probabilistic planning)
    roll_dice = Action(
        name="roll_dice",
        preconditions="",
        effects=[
            {"result": "1"},
            {"result": "2"},
            {"result": "3"},
            {"result": "4"},
            {"result": "5"},
            {"result": "6"}
        ],
        cost=1
    )

Deterministic vs Probabilistic Planning
=========================================

**Deterministic Planning**: Each action produces a single, predictable outcome.

**Probabilistic Planning**: Actions can produce multiple possible outcomes. The planner finds a plan that achieves the goal from any possible outcome (a contingency plan).

Cost Functions
==============

Each action has a cost that affects plan quality:

.. code-block:: python

    # Cheap action
    think = Action(..., cost=1)
    
    # Expensive action
    call_taxi = Action(..., cost=100)

The planner finds plans with minimum total cost.

Preconditions and Effects
==========================

**Preconditions**: Boolean expressions that must be true for an action to be applicable.

**Effects**: Changes to state variables caused by executing an action.

.. code-block:: python

    board_plane = Action(
        name="board_plane",
        preconditions="location == 'airport' and ticket == True",
        effects=[{"location": "flight"}],
        cost=10
    )

Expression Syntax
=================

Preconditions are Python expressions evaluated against the current state:

.. code-block:: python

    # Simple equality
    "light == True"
    
    # Complex conditions
    "location == 'office' and time == 'morning' and energy > 50"
    
    # Logical operators
    "light == True or light == False"
    "(location == 'home' or location == 'office') and weather == 'sunny'"

Durative Actions
================

Durative actions represent activities that take time:

.. code-block:: python

    from yappla import DurativeActionSpec
    
    bake_cake = DurativeActionSpec(
        name="bake_cake",
        conditions={
            "to_start": "oven_temperature == 'ready' and ingredients == 'mixed'",
            "to_success": "time >= 60"
        },
        effects={
            "on_start": {"oven_status": "running"},
            "on_success": {"cake": "baked"},
            "on_failure": {}
        },
        duration=60.0
    )

Planning Horizons
=================

The planning horizon is the maximum length of the plan:

- **Finite horizon**: Find plans within a time limit or iteration limit
- **Infinite horizon**: Search until a solution is found or proven impossible

YAPPLA uses iteration limits and iteration counting to manage search.
