===================
Unified Planning
===================

YAPPLA integrates with the AIPlan4EU `Unified Planning <https://github.com/aiplan4eu/unified-planning>`_ library through the `up_yappla` package.

What is Unified Planning?
=========================

The Unified Planning library provides a standard interface for defining and solving planning problems. It supports various planning algorithms including YAPPLA.

Installation
============

To use the Unified Planning interface:

.. code-block:: bash

    pip install "yappla[unified-planning]"

Basic Usage
===========

Using YAPPLA as a UP Engine
----------------------------

.. code-block:: python

    import unified_planning as up
    from up_yappla import EngineImpl
    
    # Register YAPPLA as an available engine
    up.engines.Compiler.supported_engines.append(EngineImpl)

Solving with YAPPLA
--------------------

.. code-block:: python

    import unified_planning as up
    from unified_planning.shortcuts import *
    
    # Define the planning problem using UP API
    Location = Enum("Location", ["HOME", "OFFICE", "COFFEE"])
    
    robot_location = Fluent("robot_location", Location)
    visited_office = Fluent("visited_office", BoolType())
    
    move = InstantaneousAction("move", target=Location)
    move.add_precondition(robot_location != move.target)
    move.add_effect(robot_location, move.target)
    
    # Create problem
    problem = Problem("robot_planning")
    problem.add_fluent(robot_location)
    problem.add_fluent(visited_office)
    problem.add_action(move)
    
    problem.set_initial_value(robot_location, Location.HOME)
    problem.set_initial_value(visited_office, False)
    
    goal = And(
        Equals(robot_location, Location.OFFICE),
        Equals(visited_office, True)
    )
    problem.add_goal(goal)
    
    # Solve with YAPPLA
    planner = up.engines.PlanGenerationJob(problem, engine_name="YAPPLA")
    result = planner.solve()
    
    if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
        print(f"Plan found with {len(result.plan.actions)} actions")
        for action in result.plan.actions:
            print(f"  {action}")

Advanced Topics
===============

Custom Engines
--------------

You can extend YAPPLA's UP integration by creating custom engine implementations.

Problem Translation
--------------------

The UP interface translates between:

- UP's problem representation (fluents, actions, constraints)
- YAPPLA's state representation (state variables, actions)

Expression Translation
-----------------------

UP expressions (preconditions, effects, goals) are translated to YAPPLA's Python expression syntax.

Performance Tips
================

1. **Keep state space small**: Fewer fluents = faster planning
2. **Use discrete domains**: Easier for state-space search
3. **Write specific preconditions**: Reduces branching factor
4. **Set reasonable costs**: Affects plan quality
5. **Tune iteration limits**: Balance speed vs optimality

Integration with Other UP Engines
==================================

YAPPLA works alongside other engines in the UP framework:

.. code-block:: python

    from unified_planning.engines import OneshotPlannerMixin
    
    # Try YAPPLA first, fall back to other engines
    engines = ["YAPPLA", "fast-downward", "tamer"]
    
    for engine_name in engines:
        try:
            result = up.engines.solve(problem, engine_name=engine_name)
            if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                print(f"Solved with {engine_name}")
                break
        except Exception as e:
            print(f"Failed with {engine_name}: {e}")

For more information on Unified Planning, visit the `official documentation <https://unified-planning.readthedocs.io/>`_.
