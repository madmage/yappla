==========================
Contributing and Testing
==========================

How to Contribute
=================

YAPPLA welcomes contributions! See `CONTRIBUTING.md <../../CONTRIBUTING.md>`_ for detailed guidelines.

Quick Start for Contributors
-----------------------------

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a branch for your feature/fix
4. Make your changes
5. Write tests for new functionality
6. Ensure code quality (black, isort, flake8, mypy)
7. Run the full test suite
8. Submit a pull request

Testing Overview
================

YAPPLA uses pytest for testing. Tests are organized by package:

- `tests/yappla/`: Core library tests
- `tests/up_yappla/`: Unified Planning interface tests

Running Tests
=============

Run All Tests
-------------

.. code-block:: bash

    pytest

Run with Verbose Output
------------------------

.. code-block:: bash

    pytest -v

Run Specific Test File
----------------------

.. code-block:: bash

    pytest tests/yappla/test_planner.py

Run Specific Test
-----------------

.. code-block:: bash

    pytest tests/yappla/test_planner.py::TestPlanner::test_simple_planning

Coverage Reports
================

Generate Coverage Report
------------------------

.. code-block:: bash

    pytest --cov=src/yappla --cov=src/up_yappla --cov-report=html

View HTML Coverage
-------------------

.. code-block:: bash

    open htmlcov/index.html  # macOS
    xdg-open htmlcov/index.html  # Linux
    start htmlcov/index.html  # Windows

Coverage Targets
----------------

Aim for:

- Core library (yappla): >85% coverage
- UP interface (up_yappla): >80% coverage

Writing Tests
=============

Basic Test Structure
--------------------

.. code-block:: python

    import pytest
    from yappla import State, Action, PlanningDomain, Planner
    
    class TestPlanner:
        def test_simple_planning(self):
            # Setup
            initial_state = State({"x": 0})
            
            # Execute
            planner = Planner()
            # ... configure and plan
            
            # Verify
            assert result.outcome == PlannerOutcome.SUCCESS

Using Fixtures
--------------

Common test setup is defined in `tests/conftest.py`:

.. code-block:: python

    def test_with_sample_domain(sample_domain):
        """Test using shared fixture"""
        assert sample_domain is not None

Creating New Fixtures
---------------------

Add fixtures to `tests/conftest.py`:

.. code-block:: python

    @pytest.fixture
    def complex_domain():
        """Fixture providing a complex domain"""
        domain = PlanningDomain()
        # ... setup complex domain
        return domain

Parametrized Tests
------------------

Test multiple scenarios:

.. code-block:: python

    @pytest.mark.parametrize("initial,expected", [
        (State({"x": 0}), True),
        (State({"x": 1}), False),
        (State({"x": 10}), True),
    ])
    def test_conditions(initial, expected):
        assert initial.satisfies_conditions("x == 0 or x == 10") == expected

Test Organization
==================

Test File Naming
----------------

Follow the pattern: `test_<module>.py`

- `test_state.py`: Tests for state.py
- `test_planner.py`: Tests for planner.py
- `test_integration.py`: Integration tests

Test Class Organization
-----------------------

.. code-block:: python

    class TestState:
        """Tests for State class"""
        
        def test_creation(self):
            pass
        
        def test_hashing(self):
            pass
        
        def test_equality(self):
            pass
    
    class TestStateUtilities:
        """Tests for state utility functions"""
        pass

Code Quality Checks
===================

Code Formatting
---------------

.. code-block:: bash

    # Format with black
    black src/ tests/
    
    # Sort imports
    isort src/ tests/

Linting
-------

.. code-block:: bash

    # Run flake8
    flake8 src/ tests/

Type Checking
-------------

.. code-block:: bash

    # Run mypy
    mypy src/yappla src/up_yappla

Running All Checks
-------------------

.. code-block:: bash

    # One command to do everything
    black src/ tests/ && \
    isort src/ tests/ && \
    flake8 src/ tests/ && \
    mypy src/yappla src/up_yappla && \
    pytest --cov=src/yappla --cov=src/up_yappla

Documentation
==============

Building Documentation
----------------------

.. code-block:: bash

    cd docs
    make html

Viewing Documentation
---------------------

.. code-block:: bash

    open build/html/index.html  # macOS
    xdg-open build/html/index.html  # Linux

Writing Documentation
---------------------

- Add docstrings to functions and classes (Google style)
- Update relevant `.rst` files in `docs/source/`
- Include examples in docstrings

Common Issues
=============

Import Errors
-------------

If you get import errors:

.. code-block:: bash

    # Ensure src is in PYTHONPATH
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    pytest

Missing Dependencies
--------------------

.. code-block:: bash

    # Install development dependencies
    pip install ".[dev,docs]"
    
    # Or using requirements file
    pip install -r requirements-dev.txt

Coverage Not Collected
----------------------

Ensure tests import from src:

.. code-block:: python

    # Correct
    from yappla import State
    
    # Avoid
    import sys; sys.path.insert(0, '..'); from yappla import State

Getting Help
============

- Check `CONTRIBUTING.md` for more details
- Open an issue on GitHub for questions
- Review existing tests for examples
