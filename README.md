# YAPPLA - Yet Another Probabilistic Planning and Logic Architecture

A lightweight automated planning library implementing Dijkstra's algorithm in the state space, with support for deterministic and probabilistic planning. The library provides a clean Python API and integrates with the [Unified Planning](https://github.com/aiplan4eu/unified-planning) library.

## Features

- **State-space planning**: Efficient Dijkstra-based state space search
- **Flexible state representation**: Dictionaries with predefined value domains
- **Action support**: Deterministic and durative actions
- **Probabilistic planning**: Support for probabilistic outcomes
- **Unified Planning interface**: Full integration with the AIPlan4EU Unified Planning library via `up_yappla`

## Installation

### Core library only

```bash
pip install .
```

### With Unified Planning support

```bash
pip install ".[unified-planning]"
```

### Development setup

```bash
pip install ".[dev,docs]"
```

## Repository Structure

```
yappla/
├── src/
│   ├── yappla/              # Core planning library
│   │   ├── action.py        # Action definitions
│   │   ├── planning_domain.py  # Planning domain
│   │   ├── planner.py       # Main planner engine
│   │   ├── temporal_planner.py  # Temporal planner (durations, makespan)
│   │   ├── state.py         # State representation
│   │   ├── plan.py          # Plan representation
│   │   └── ...
│   └── up_yappla/           # Unified Planning interface
│       ├── engine.py        # UP engine implementation
│       └── ...
├── tests/
│   ├── yappla/              # Core library tests
│   ├── up_yappla/           # UP interface tests
│   └── conftest.py          # Shared test fixtures
├── docs/                    # Documentation
├── pyproject.toml           # Modern Python project configuration
└── README.md
```

## Quick Start

```python
from yappla import PlanningDomain, State, StateVariable, Action, Planner

# Create domain
domain = PlanningDomain()
domain.add_variable(StateVariable("position", ["kitchen", "bedroom", "living_room"], "kitchen"))
domain.add_variable(StateVariable("raining", [True, False], False))

# Initial state comes from domain variables
initial_state = domain.get_initial_state()

# Add an action
go_to_bedroom = Action(
    name="go_to_bedroom",
    preconditions="position == 'kitchen'",
    effects=[{"position": "bedroom"}],
    cost=1,
)
domain.add_action(go_to_bedroom)

# Solve
planner = Planner()
planner.set_domain(domain)
goal = "position == 'bedroom'"
result = planner.plan(initial_state, goal)
print(result.outcome)
print(result.pretty_str())
```

## Temporal Planning (Durative Actions)

YAPPLA also supports durative actions via `DurativeActionSpec` and the `TemporalPlanner`.

```python
from yappla import PlanningDomain, StateVariable, State, DurativeActionSpec, TemporalPlanner

domain = PlanningDomain()
domain.add_variable(StateVariable("room", ["clean", "painted"], "clean"))

domain.add_action(DurativeActionSpec(
    name="paint_room",
    duration=10.0,
    conditions={"to_start": "room == 'clean'"},
    effects={"on_success": {"room": "painted"}},
))

initial_state = domain.get_initial_state()
planner = TemporalPlanner()
planner.set_domain(domain)  # compiles/splits durative specs into primitive operators
result = planner.plan(initial_state, "room == 'painted'")

print(result.outcome)
print("makespan", result.stats.get("makespan"))
print(result.pretty_str())
```

## Documentation

Full documentation is available at [https://yappla.readthedocs.io](https://yappla.readthedocs.io)

For development documentation, see [CONTRIBUTING.md](CONTRIBUTING.md)

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/yappla --cov=src/up_yappla
```

## Acknowledgments

<img src="https://www.aiplan4eu-project.eu/wp-content/uploads/2021/07/euflag.png" width="60" height="40">

The development of this repository has been initiated for the AIPlan4EU H2020 project (https://aiplan4eu-project.eu) that is funded by the European Commission under grant agreement number 101016442.
