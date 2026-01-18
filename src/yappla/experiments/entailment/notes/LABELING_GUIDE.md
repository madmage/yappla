# LABELING Query Guide

## Overview

The logic engine now supports **LABELING queries** for constraint satisfaction and optimization. LABELING is used to find variable assignments that satisfy a set of constraints.

## Syntax

```
LABELING variable1, variable2, ... SUBJECT TO constraint1, constraint2, ...
```

## Constraint Types

### 1. Domain Constraints

Restrict variables to specific values:

- **Range notation**: `X in 1..10` - X can be any integer from 1 to 10
- **Set notation**: `X in {a, b, c}` - X can be only 'a', 'b', or 'c'

### 2. Not-Equal Constraints

Ensure two variables have different values:

- **Syntax**: `X != Y` - X and Y must have different values

## Examples

### Example 1: Simple All-Different Constraint

Find all ways to assign 3 variables to values 1, 2, 3 where all are different:

```
LABELING X, Y, Z SUBJECT TO X in 1..3, Y in 1..3, Z in 1..3, X != Y, X != Z, Y != Z
```

Output: 6 solutions (3! = 6 permutations)
```
  Solution 1: X = 1, Y = 2, Z = 3
  Solution 2: X = 1, Y = 3, Z = 2
  Solution 3: X = 2, Y = 1, Z = 3
  Solution 4: X = 2, Y = 3, Z = 1
  Solution 5: X = 3, Y = 1, Z = 2
  Solution 6: X = 3, Y = 2, Z = 1
```

### Example 2: Scheduling with Different Slots

Assign two tasks to different time slots:

```
LABELING S1, S2 SUBJECT TO S1 in 0..5, S2 in 0..5, S1 != S2
```

Output: 30 solutions (6 slots × 5 remaining slots)

### Example 3: Set-Based Domains

Assign machines to jobs:

```
LABELING M1, M2, M3 SUBJECT TO M1 in {m1, m2, m3}, M2 in {m1, m2, m3}, M3 in {m1, m2, m3}, M1 != M2, M1 != M3, M2 != M3
```

## How It Works

The LABELING query uses **branch-and-bound search** with **constraint propagation**:

1. **Variable Selection**: Picks a variable to label
2. **Domain Exploration**: Tries each value in the variable's domain
3. **Constraint Propagation**: Reduces other variables' domains based on constraints
4. **Pruning**: Eliminates branches that violate constraints
5. **Backtracking**: Returns to try other values if constraints are violated

## Implementation Details

### Processing Steps

1. **Parse Variables**: Extract comma-separated variable names
2. **Parse Constraints**: Identify domain constraints and not-equal constraints
3. **Build Domains**: Create initial domain for each variable
4. **Constraint Propagation**: Apply constraints to reduce domains
5. **Search**: Use branch-and-bound to find all valid assignments

### Constraint Propagation Rules

- **Domain Constraint**: If `X in {1, 2, 3}` and current domain is `{1, 2, 3, 4, 5}`, intersect to get `{1, 2, 3}`
- **Not-Equal Constraint**: If `X != Y` and X is bound to value 5, remove 5 from Y's domain

## Testing

All LABELING queries are tested in `test_logic.py`:

- `test_labeling_branch_and_bound`: Tests basic labeling with optimization
- `test_labeling_with_constraints`: Tests labeling with constraint propagation

Run tests:
```bash
python3 -m pytest test_logic.py::test_labeling_branch_and_bound -v
python3 -m pytest test_logic.py::test_labeling_with_constraints -v
```

## Use Cases

- **Scheduling**: Assign tasks to time slots with no conflicts
- **Resource Allocation**: Distribute resources avoiding overallocation
- **Puzzle Solving**: Solve Sudoku, N-Queens, etc.
- **Configuration**: Find valid system configurations
- **Timetabling**: Create conflict-free schedules

## REPL Usage

Start the REPL:
```bash
python3 repl.py
```

Then:
```
> LABELING X, Y, Z SUBJECT TO X in 1..3, Y in 1..3, Z in 1..3, X != Y, X != Z, Y != Z
Variables: X, Y, Z
Domains: {'X': {1, 2, 3}, 'Y': {1, 2, 3}, 'Z': {1, 2, 3}}
Constraints: 3 constraint(s)

Found 6 solution(s):
  Solution 1: X = 1, Y = 2, Z = 3
  ...
```

## Limitations and Future Work

- **Objective Functions**: Current implementation finds all solutions with same cost
- **Advanced Propagation**: Could implement arc consistency (AC-3)
- **Heuristics**: Could use variable ordering heuristics (MRV, LCV)
- **Optimization**: Could minimize/maximize objective functions

## API Reference

### InferenceEngine.label_variables()

```python
def label_variables(self, 
                   domains: Dict[str, Any], 
                   constraints: List, 
                   objective, 
                   maximize: bool = True, 
                   objective_vars: Optional[List[str]] = None, 
                   bounds_fn = None) -> List[Dict[str, Any]]:
    """
    Branch-and-bound labeling for constraint satisfaction and optimization.
    
    Args:
        domains: Dictionary mapping variable names to sets of possible values
        constraints: List of DomainConstraint and NotEqualConstraint objects
        objective: Function that takes an assignment dict and returns a numeric objective value
        maximize: Whether to maximize (True) or minimize (False) the objective
        objective_vars: List of variable names to include in the objective
        bounds_fn: Optional function for pruning
    
    Returns:
        List of assignment dictionaries representing solutions
    """
```
