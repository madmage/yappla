========
Planning
========

This guide covers how to use the YAPPLA planner and interpret results.

The Planner
===========

The core planner implements Dijkstra's algorithm for state-space search:

.. code-block:: python

    from yappla import Planner, PlanningDomain, State, Action
    
    # Create domain and actions...
    domain = PlanningDomain()
    # Add variables and actions...
    
    # Create planner
    planner = Planner()
    planner.set_domain(domain)
    
    # Define goal and solve
    goal = "target_location == 'goal'"
    result = planner.plan(initial_state, goal)

Planner Configuration
=====================

Verbosity Levels
----------------

Control output detail:

.. code-block:: python

    planner = Planner()
    
    # Quiet mode (no output)
    planner.max_verbosity_level = 0
    
    # Some output (planning progress)
    planner.max_verbosity_level = 1
    
    # Verbose (detailed state exploration)
    planner.max_verbosity_level = 2

Iteration Limits
----------------

Prevent infinite search:

.. code-block:: python

    planner.max_iterations = 10000  # Default
    planner.max_iterations = 1000   # Faster, less thorough
    planner.max_iterations = 100000 # More thorough
    
    result = planner.plan(initial_state, goal)

Running Planning
================

Basic Planning
--------------

.. code-block:: python

    from yappla import Planner, PlannerOutcome
    
    planner = Planner()
    planner.set_domain(domain)
    
    result = planner.plan(initial_state, goal_expression)
    
    # Check if planning succeeded
    if result.outcome == PlannerOutcome.SUCCESS:
        print("Found a plan!")
    elif result.outcome == PlannerOutcome.FAILURE:
        print("No plan found")
    elif result.outcome == PlannerOutcome.ALREADY_AT_GOAL:
        print("Already at goal")

Goals
-----

Goals can be specified as:

.. code-block:: python

    # String expression
    goal = "location == 'home' and light == True"
    
    # Using Goal object
    from yappla import Goal
    goal_obj = Goal()
    goal_obj.append({"goal": "location == 'home'"})
    goal_obj.append({"goal": "light == True", "priority": 5})

Understanding Results
=====================

The PlannerResult contains:

.. code-block:: python

    result = planner.plan(initial_state, goal)
    
    # Outcome (success, failure, already at goal, invalid)
    print(f"Outcome: {result.outcome}")
    
    # The plan (list of (state, action) tuples)
    print(f"Plan length: {len(result.plan)}")
    for state, action in result.plan:
        if action:
            print(f"  Execute {action}")
        else:
            print(f"  Goal reached")
    
    # Statistics
    print(f"Planning time: {result.stats['time']*1000:.2f}ms")
    print(f"States explored: {result.stats['iterations']}")

Plan Representation
===================

A plan is a list of (state, action) tuples:

.. code-block:: python

    # First element: (initial_state, None)
    # Middle elements: (current_state, action_name)
    # Last element: (goal_state, None)
    
    if result.outcome == PlannerOutcome.SUCCESS:
        initial = result.plan[0][0]
        print(f"Initial state: {initial}")
        
        for state, action in result.plan[1:-1]:
            print(f"Execute: {action}")
            print(f"Result state: {state}")
        
        goal_state = result.plan[-1][0]
        print(f"Goal state: {goal_state}")

Displaying Plans
================

Pretty Output
-------------

.. code-block:: python

    # Full output with state details
    print(result.pretty_str())
    
    # With state hashes
    print(result.pretty_str(show_state_hashes=True))
    
    # Only state differences
    print(result.pretty_str(only_diffs=True))

Custom Plan Display
-------------------

.. code-block:: python

    if result.outcome == PlannerOutcome.SUCCESS:
        print(f"Plan with {len(result.plan) - 1} actions:")
        
        for i, (state, action) in enumerate(result.plan):
            if action:
                print(f"\nStep {i}: {action}")
                print(f"  State hash: {state.hash()}")
                print(f"  State: {state}")
            else:
                print(f"\n{i}: Initial or Goal state")
                print(f"  State: {state}")

Debugging Failed Planning
==========================

If Planning Fails
-----------------

.. code-block:: python

    result = planner.plan(initial_state, goal)
    
    if result.outcome == PlannerOutcome.FAILURE:
        print("Planning failed")
        print(f"Explored {result.stats['iterations']} states")
        print("Debugging tips:")
        print("1. Check if goal is reachable from initial state")
        print("2. Verify preconditions of actions")
        print("3. Check goal expression syntax")
        print("4. Increase max_iterations if search space is large")
        print("5. Use max_verbosity_level=2 for detailed trace")

Using Detailed Trace
--------------------

.. code-block:: python

    planner.max_verbosity_level = 2
    result = planner.plan(initial_state, goal)
    
    # This will show:
    # - Each state explored
    # - Available actions for each state
    # - State transitions and costs
    # - Search progress

Advanced Usage
==============

Multiple Goals with Priorities
-------------------------------

.. code-block:: python

    from yappla import Goal
    
    goals = Goal()
    goals.append({
        "goal": "primary_objective == 'complete'",
        "priority": 10
    })
    goals.append({
        "goal": "secondary_objective == 'complete'",
        "priority": 5
    })
    
    result = planner.plan(initial_state, goals)

Conditional Goals
-----------------

.. code-block:: python

    goals = Goal()
    goals.append({
        "conditions": "weather == 'rain'",
        "goal": "has_umbrella == True"
    })
    goals.append({
        "conditions": "weather == 'sunny'",
        "goal": "has_sunscreen == True"
    })

Performance Optimization
========================

For Large Problems
-------------------

1. **Reduce state space**:
   - Fewer state variables
   - Smaller value domains

Temporal Planning
=================

For problems where actions take time and can overlap, use `TemporalPlanner`.

Key points:

- High-level durative actions are modeled with `DurativeActionSpec`.
- `Planner.set_domain(...)` and `TemporalPlanner.set_domain(...)` automatically compile/split
  action specs into primitive `Action` operators.
- `TemporalPlanner` tracks a `makespan` and can schedule non-conflicting actions in parallel.

.. code-block:: python

    from yappla import PlanningDomain, StateVariable, DurativeActionSpec, TemporalPlanner

    domain = PlanningDomain()
    domain.add_variable(StateVariable("room1", ["clean", "painted"], "clean"))
    domain.add_variable(StateVariable("room2", ["clean", "painted"], "clean"))

    domain.add_action(DurativeActionSpec(
        name="paint_room1",
        duration=10.0,
        conditions={"to_start": "room1 == 'clean'"},
        effects={"on_success": {"room1": "painted"}},
    ))
    domain.add_action(DurativeActionSpec(
        name="paint_room2",
        duration=6.0,
        conditions={"to_start": "room2 == 'clean'"},
        effects={"on_success": {"room2": "painted"}},
    ))

    initial_state = domain.get_initial_state()
    planner = TemporalPlanner()
    planner.set_domain(domain)

    result = planner.plan(initial_state, "room1 == 'painted' and room2 == 'painted'")
    print(result.outcome)
    print("makespan", result.stats.get("makespan"))
    print(result.pretty_str())

Temporal Plans and Action Steps
-------------------------------

`TemporalPlanner` records action steps as dictionaries like:

- `{"name": "paint_room1", "time": 0.0, "duration": 10.0}`

`PlannerResult.pretty_str()` renders these in a compact stable format (e.g. `paint_room1 @0.0 (dur=10.0)`).
   - Use hierarchical planning

2. **Improve action definitions**:
   - More restrictive preconditions
   - Avoid unnecessary non-determinism
   - Use reasonable costs

3. **Tune planner**:
   - Increase iteration limits for complex problems
   - Decrease for quick solutions
   - Use lower verbosity levels for speed

.. code-block:: python

    # Performance-optimized configuration
    planner.max_iterations = 50000
    planner.max_verbosity_level = 0
