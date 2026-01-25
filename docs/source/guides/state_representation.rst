====================
State Representation
====================

This guide covers how YAPPLA represents and works with states.

What is a State?
================

A state in YAPPLA is a complete assignment of all state variables to concrete values. It represents a snapshot of the world at a particular moment.

.. code-block:: python

    from yappla import State
    
    # A state is a dictionary-like object
    state = State({
        "robot_location": "room_a",
        "light": False,
        "battery_level": 80
    })

Creating States
===============

Method 1: Direct Creation
--------------------------

.. code-block:: python

    from yappla import State
    
    initial_state = State({
        "location": "home",
        "has_keys": False,
        "time": "morning"
    })

Method 2: From PlanningDomain Initial State
-----------------------------------------------

.. code-block:: python

    from yappla import PlanningDomain, StateVariable
    
    # Define domain with state variables
    domain = PlanningDomain()
    domain.add_variable(StateVariable("location", ["home", "office"], "home"))
    domain.add_variable(StateVariable("raining", [True, False], False))
    
    # Get initial state from domain
    initial_state = domain.get_initial_state()

Accessing State Values
======================

Like a dictionary:

.. code-block:: python

    state = State({"robot": "room_a", "task": "idle"})
    
    # Get value
    location = state["robot"]  # "room_a"
    
    # Set value
    state["robot"] = "room_b"
    
    # Check if key exists
    if "task" in state:
        print(state["task"])

State Hashing
=============

YAPPLA computes MD5 hashes of states for efficient comparison:

.. code-block:: python

    state = State({"location": "home", "light": False})
    
    # Get 6-character hash
    hash_value = state.hash()  # e.g., "a1b2c3"

Hashes are used to:

- Avoid revisiting states in the search
- Efficiently compare states
- Display states compactly in output

State Equality
==============

States are equal if they have the same variable assignments:

.. code-block:: python

    state1 = State({"x": 1, "y": 2})
    state2 = State({"x": 1, "y": 2})
    
    # These are equal (as dictionaries)
    print(state1 == state2)  # True

Checking State Conditions
==========================

Test if a state satisfies conditions:

.. code-block:: python

    state = State({"location": "office", "time": "morning"})
    
    # Check conditions
    satisfies = state.satisfies_conditions(
        "location == 'office' and time == 'morning'"
    )
    print(satisfies)  # True

Multiple Conditions
-------------------

.. code-block:: python

    constraints = [
        {
            "conditions": "robot_type == 'mobile'",
            "constraint": "battery_level > 20"
        },
        {
            "conditions": "light == True",
            "constraint": "power_available == True"
        }
    ]
    
    if state.satisfies_constraints(constraints):
        print("All constraints satisfied")

State Representation in Output
==============================

Pretty Printing
---------------

.. code-block:: python

    state = State({"location": "home", "light": False, "battery": 85})
    
    # Compact output
    print(state.pretty_str(columns=False))
    # Output: location:home, light:False, battery:85
    
    # Column-formatted output
    print(state.pretty_str(columns=True))
    # Output formatted across multiple lines
    
    # With state hash
    print(state.pretty_str(show_hashes=True))
    # Output: [a1b2c3] location:home, light:False, battery:85

State Copying
=============

Create independent copies of states:

.. code-block:: python

    from copy import deepcopy
    
    original = State({"x": 1, "y": 2})
    copy = State(original)  # Shallow copy
    deep_copy = deepcopy(original)  # Deep copy
    
    # Modify copy
    copy["x"] = 10
    print(original["x"])  # Still 1

Large State Spaces
==================

YAPPLA efficiently handles large state spaces by:

1. Using compact state representation (dictionary-based)
2. Computing state hashes for quick lookup
3. Using priority queues to minimize memory overhead

For very large state spaces, consider:

- Reducing the number of state variables
- Limiting the domain of each state variable
- Using abstraction/hierarchical planning
