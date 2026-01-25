===========
Quick Start
===========

This guide will help you get started with YAPPLA in 5 minutes.

Basic Planning Example
======================

Let's create a simple planning problem where an agent needs to change from being barefoot to wearing shoes.

.. code-block:: python

    from yappla import PlanningDomain, StateVariable, Action, Planner

    # Step 1: Define state variables
    # A state variable represents a property that can have different values
    left_foot = StateVariable(
        name="left_foot",
        possible_values=["has_nothing", "has_sock", "has_shoe"],
        initial_value="has_nothing"
    )
    
    right_foot = StateVariable(
        name="right_foot", 
        possible_values=["has_nothing", "has_sock", "has_shoe"],
        initial_value="has_nothing"
    )

    # Step 2: Create the domain
    domain = PlanningDomain()
    domain.add_variable(left_foot)
    domain.add_variable(right_foot)

    # Step 3: Get the initial state from the domain
    initial_state = domain.get_initial_state()
    
    # Action: put left sock
    put_left_sock = Action(
        name="put_left_sock",
        preconditions="left_foot == 'has_nothing'",
        effects=[{"left_foot": "has_sock"}],
        cost=1
    )
    
    # Action: put right sock
    put_right_sock = Action(
        name="put_right_sock",
        preconditions="right_foot == 'has_nothing'",
        effects=[{"right_foot": "has_sock"}],
        cost=1
    )
    
    # Action: put left shoe
    put_left_shoe = Action(
        name="put_left_shoe",
        preconditions="left_foot == 'has_sock'",
        effects=[{"left_foot": "has_shoe"}],
        cost=1
    )
    
    # Action: put right shoe
    put_right_shoe = Action(
        name="put_right_shoe",
        preconditions="right_foot == 'has_sock'",
        effects=[{"right_foot": "has_shoe"}],
        cost=1
    )
    
    # Add actions to domain
    domain.add_action(put_left_sock)
    domain.add_action(put_right_sock)
    domain.add_action(put_left_shoe)
    domain.add_action(put_right_shoe)

    # Step 4: Define the goal
    goal = "left_foot == 'has_shoe' and right_foot == 'has_shoe'"

    # Step 5: Create planner and solve
    planner = Planner()
    planner.set_domain(domain)
    planner.max_verbosity_level = 1  # Set verbosity (0=quiet, 1=some output, 2=verbose)
    
    result = planner.plan(initial_state, goal)

    # Step 6: Inspect the result
    print(f"Planning outcome: {result.outcome}")
    print(f"Plan length: {len(result.plan)}")
    print(f"Planning time: {result.stats['time']*1000:.2f}ms")
    print(f"Iterations: {result.stats['iterations']}")
    
    # Print the plan
    print(result.pretty_str())

Running this example should produce a plan with 5 steps:
1. Initial state: barefoot
2. Put left sock
3. Put left shoe  
4. Put right sock
5. Put right shoe
6. Goal state: wearing shoes

Key Concepts
============

- **State**: A complete assignment of all state variables. Represented as a dictionary.
- **State Variable**: A property of the world with a fixed set of possible values.
- **Action**: An operator that can be applied if preconditions are met, producing effects.
- **Domain**: A collection of state variables and actions defining a planning problem.
- **Goal**: A condition that the planner tries to achieve.
- **Plan**: A sequence of actions that transforms the initial state into a goal state.

Next Steps
==========

- Read :doc:`concepts` for a deeper understanding of planning concepts
- Explore :doc:`state_representation` for more about states
- Learn about :doc:`actions` in detail
- See :doc:`planning` for advanced planning topics
