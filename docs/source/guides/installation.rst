==================
Installation Guide
==================

Requirements
============

- Python 3.8 or higher
- pip

Basic Installation
==================

To install the core YAPPLA library:

.. code-block:: bash

    pip install .

Installation with Unified Planning Support
============================================

If you want to use YAPPLA with the Unified Planning library:

.. code-block:: bash

    pip install ".[unified-planning]"

Development Installation
==========================

For development work, including testing and documentation building:

.. code-block:: bash

    pip install ".[dev,docs]"

Or using the requirements file:

.. code-block:: bash

    pip install -r requirements-dev.txt

Verification
============

To verify the installation works correctly:

.. code-block:: python

    import yappla
    print(f"YAPPLA version: {yappla.__version__}")

If you also installed the Unified Planning support:

.. code-block:: python

    import up_yappla
    from up_yappla.engine import EngineImpl
    print("Unified Planning interface available")
