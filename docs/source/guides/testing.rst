=======
Testing
=======

Comprehensive Testing Guide
===========================

This page provides detailed information about YAPPLA's test suite.

Test Infrastructure
===================

Location
--------

- Test files: `tests/yappla/`, `tests/up_yappla/`
- Common fixtures: `tests/conftest.py`
- Test domains: `tests/domains/`

Framework
---------

- **Test Runner**: pytest
- **Coverage Tool**: pytest-cov
- **Fixtures**: conftest.py

Configuration
=============

Pytest Configuration
--------------------

Settings in `pyproject.toml`:

.. code-block:: toml

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    addopts = "--verbose --cov=src/yappla --cov=src/up_yappla --cov-report=term-missing"
    python_files = "test_*.py"
    python_classes = "Test*"
    python_functions = "test_*"

Coverage Configuration
----------------------

.. code-block:: toml

    [tool.coverage.run]
    source = ["src/yappla", "src/up_yappla"]
    branch = true

    [tool.coverage.report]
    exclude_lines = [
        "pragma: no cover",
        "def __repr__",
        "raise AssertionError",
        "raise NotImplementedError",
        "if __name__ == .__main__.:",
        "if TYPE_CHECKING:",
    ]

Test Categories
===============

Unit Tests
----------

Test individual functions and classes:

.. code-block:: python

    def test_state_creation():
        """Test State creation"""
        state = State({"x": 1})
        assert state["x"] == 1

Integration Tests
-----------------

Test multiple components together:

.. code-block:: python

    def test_planning_workflow():
        """Test complete planning workflow"""
        domain = create_domain()
        planner = Planner()
        planner.set_domain(domain)
        result = planner.plan(initial_state, goal)
        assert result.outcome == PlannerOutcome.SUCCESS

Edge Case Tests
---------------

Test boundary conditions:

.. code-block:: python

    def test_empty_state():
        """Test empty state"""
        state = State({})
        assert len(state) == 0
    
    def test_single_variable_domain():
        """Test domain with single variable"""
        # ... test domain with minimal variables

Performance Tests
-----------------

Test with realistic problem sizes:

.. code-block:: python

    @pytest.mark.slow
    def test_large_state_space():
        """Test planner with large state space"""
        # ... test with many states

Example Test Cases
==================

Testing States
--------------

.. code-block:: python

    class TestState:
        def test_creation_from_dict(self):
            state = State({"location": "home"})
            assert state["location"] == "home"
        
        def test_hash_consistency(self):
            state1 = State({"x": 1})
            state2 = State({"x": 1})
            assert state1.hash() == state2.hash()
        
        def test_satisfies_conditions(self):
            state = State({"x": 5})
            assert state.satisfies_conditions("x > 3")
            assert not state.satisfies_conditions("x > 10")

Testing Actions
---------------

.. code-block:: python

    class TestAction:
        def test_action_applicable(self):
            action = Action(
                name="open",
                preconditions="door_locked == True",
                effects=[{"door_locked": False}]
            )
            
            state = State({"door_locked": True})
            assert action.applicable(state)
            
            state = State({"door_locked": False})
            assert not action.applicable(state)
        
        def test_action_effects(self):
            action = Action(
                name="turn_on",
                preconditions="light == False",
                effects=[{"light": True}]
            )
            
            state = State({"light": False})
            outcomes = action.possible_outcomes(state)
            assert len(outcomes) == 1
            assert outcomes[0]["light"] == True

Testing Planning
----------------

.. code-block:: python

    class TestPlanner:
        def test_simple_planning(self, sample_domain):
            planner = Planner()
            planner.set_domain(sample_domain)
            
            initial = State({"x": 0})
            goal = "x == 1"
            
            result = planner.plan(initial, goal)
            assert result.outcome == PlannerOutcome.SUCCESS
            assert len(result.plan) > 1
        
        def test_impossible_goal(self, sample_domain):
            planner = Planner()
            planner.set_domain(sample_domain)
            
            initial = State({"x": 0})
            goal = "x == 1000"
            
            result = planner.plan(initial, goal)
            assert result.outcome == PlannerOutcome.FAILURE

Running Tests Effectively
==========================

Debug Failed Tests
------------------

.. code-block:: bash

    # Show full output
    pytest -v -s test_file.py::test_function
    
    # Print debugging information
    pytest --pdb test_file.py  # Drop into debugger on failure
    
    # Show local variables
    pytest -l test_file.py

Run Tests by Category
---------------------

.. code-block:: bash

    # Run fast tests only
    pytest -m "not slow"
    
    # Run only integration tests
    pytest -k "integration"

Continuous Testing
-------------------

.. code-block:: bash

    # Watch for changes and rerun (requires pytest-watch)
    ptw
    
    # Or manually rerun on changes
    while true; do pytest; inotifywait -e modify -r tests/ src/; done

Best Practices
==============

1. **Clear test names**: Describe what is tested
2. **Isolated tests**: No dependencies between tests
3. **Fixtures for setup**: Use conftest.py fixtures
4. **Assertions only**: Keep test logic simple
5. **One assertion per test**: When possible
6. **Docstrings**: Explain the test purpose
7. **Skip known failures**: Use @pytest.mark.skip
8. **Parametrize variants**: Test multiple scenarios

Troubleshooting
===============

Tests Not Found
---------------

Ensure:
- Files match pattern: `test_*.py`
- Classes match pattern: `Test*`
- Functions match pattern: `test_*`

Import Errors
-------------

Ensure:
- Installed in development mode: `pip install -e .`
- PYTHONPATH includes src: `export PYTHONPATH="$PWD/src"`

Coverage Issues
---------------

- Run with `--cov` flag
- Check `htmlcov/index.html` for detailed report
- Mark lines to exclude with `# pragma: no cover`

Flaky Tests
-----------

- Add `@pytest.mark.flaky(reruns=3)` for unreliable tests
- Debug non-deterministic behavior
- Use fixtures for consistent setup
