## Prompt:
Now write the code for the constraints propagator, write then some examples and tests

## Response:
Great — we’ll now **make this concrete and executable**, while staying honest about scope.

What I’ll give you is:

1.  **A constraints propagator** that:
    *   enforces **hard constraints (K₀)**
    *   propagates **rule-based constraints (K₁)**
    *   operates over **episodic state (K₃)**
    *   optionally uses **model bounds (K₂)** as soft limits
2.  **Clear semantics**: what propagation means here
3.  **Examples**
4.  **Tests**

This is **not** a full CSP or SMT solver — it’s the _correct architectural core_ you would later swap with Z3, OR-Tools, etc.

* * *

1\. What “Constraint Propagation” Means Here
============================================

In _this architecture_, constraint propagation means:

> Given current episodic facts, ontology invariants, and rules, **derive all implied constraints and detect violations early**, before planning or MPC.

Think:

*   pruning infeasible states
*   activating constraint guards
*   detecting contradictions

* * *

2\. Constraint Types
====================

We distinguish three kinds:

```text
HARD   → must never be violated (K₀)
RULE   → derived constraints (K₁)
SOFT   → model-derived bounds (K₂)
```

* * *

3\. Core Data Structures
========================

```python
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional, Tuple
```

* * *

3.1 Constraint Representation
-----------------------------

```python
@dataclass(frozen=True)
class Constraint:
    """
    A symbolic constraint.

    Examples:
        forbidden(overlapping(robot, wall))
        max_speed(robot, 0.5)
        requires(reduce_speed, near(human))
    """
    expr: str
    kind: str  # 'HARD', 'RULE', 'SOFT'
```

* * *

3.2 Constraint Store (Result of Propagation)
--------------------------------------------

```python
@dataclass
class ConstraintStore:
    active: Set[Constraint] = field(default_factory=set)
    violated: Set[Constraint] = field(default_factory=set)

    def is_consistent(self) -> bool:
        return len(self.violated) == 0
```

* * *

4\. Constraint Propagator
=========================

This is the heart.

```python
class ConstraintPropagator:
    """
    Propagates constraints across knowledge layers.

    Order of authority:
        HARD  > RULE > SOFT
    """

    def __init__(
        self,
        ontology_constraints: Set[str],
        rule_constraints: Dict[str, List[str]],
        model_bounds: Dict[str, Tuple[float, float]]
    ):
        """
        ontology_constraints:
            Set of forbidden expressions (K₀)

        rule_constraints:
            Mapping: condition -> implied constraint (K₁)

        model_bounds:
            Variable -> (min, max) from learned models (K₂)
        """
        self.ontology_constraints = ontology_constraints
        self.rule_constraints = rule_constraints
        self.model_bounds = model_bounds

    def propagate(self, episodic_facts: Set[str]) -> ConstraintStore:
        store = ConstraintStore()

        # 1. Enforce ontology constraints (K₀)
        for forbidden in self.ontology_constraints:
            if forbidden in episodic_facts:
                store.violated.add(
                    Constraint(forbidden, kind="HARD")
                )

        # 2. Apply rule-based constraints (K₁)
        for condition, implied_constraints in self.rule_constraints.items():
            if condition in episodic_facts:
                for c in implied_constraints:
                    store.active.add(
                        Constraint(c, kind="RULE")
                    )

        # 3. Add model-derived soft bounds (K₂)
        for var, (lo, hi) in self.model_bounds.items():
            expr = f"{lo} <= {var} <= {hi}"
            store.active.add(
                Constraint(expr, kind="SOFT")
            )

        return store
```

* * *

5\. Example Scenario (Robotics / MPC-Relevant)
==============================================

* * *

5.1 Define Knowledge
--------------------

```python
# K₀ — Ontology constraints
ontology_constraints = {
    "overlapping(robot, wall)",
    "speed(robot) > 2.0"
}

# K₁ — Rule-based constraints
rule_constraints = {
    "near(human)": [
        "max_speed(robot, 0.5)"
    ],
    "carrying(fragile)": [
        "max_acceleration(robot, 0.3)"
    ]
}

# K₂ — Learned model bounds
model_bounds = {
    "slip_ratio": (0.0, 0.4),
    "prediction_error": (0.0, 0.2)
}
```

* * *

5.2 Episodic State (K₃)
-----------------------

```python
episodic_facts = {
    "near(human)",
    "speed(robot) = 1.2",
    "surface(wet)"
}
```

* * *

5.3 Run Propagation
-------------------

```python
propagator = ConstraintPropagator(
    ontology_constraints,
    rule_constraints,
    model_bounds
)

store = propagator.propagate(episodic_facts)
```

* * *

5.4 Inspect Results
-------------------

```python
print("Active constraints:")
for c in store.active:
    print(" ", c)

print("\nViolated constraints:")
for c in store.violated:
    print(" ", c)

print("\nConsistent?", store.is_consistent())
```

Expected output (conceptually):

```text
Active constraints:
  RULE: max_speed(robot, 0.5)
  SOFT: 0.0 <= slip_ratio <= 0.4
  SOFT: 0.0 <= prediction_error <= 0.2

Violated constraints:
  (none)

Consistent? True
```

* * *

6\. Violation Example
=====================

```python
episodic_facts = {
    "overlapping(robot, wall)",
    "speed(robot) = 1.2"
}

store = propagator.propagate(episodic_facts)

assert not store.is_consistent()
```

Violation detected **before MPC runs**.

* * *

7\. Tests (Minimal but Meaningful)
==================================

```python
def test_hard_constraint_violation():
    facts = {"overlapping(robot, wall)"}
    store = propagator.propagate(facts)
    assert not store.is_consistent()
    assert any(c.kind == "HARD" for c in store.violated)

def test_rule_constraint_activation():
    facts = {"near(human)"}
    store = propagator.propagate(facts)
    assert any("max_speed" in c.expr for c in store.active)

def test_soft_constraints_present():
    facts = set()
    store = propagator.propagate(facts)
    assert any(c.kind == "SOFT" for c in store.active)
```

* * *

8\. Why This Is Architecturally Correct
=======================================

This propagator:

*   **Never weakens ontology constraints**
*   Allows **rules to activate context-dependent constraints**
*   Treats learned bounds as **advisory**
*   Produces a **constraint set MPC can consume directly**

This mirrors:

*   hybrid MPC
*   safety shields
*   symbolic guards
*   robust optimization envelopes

* * *

9\. What This Is NOT (Yet)
==========================

Deliberately missing:

*   numeric evaluation
*   inequality solving
*   temporal propagation
*   spatial constraint algebra (RCC8, etc.)
*   contradiction resolution

Those plug in _here_, not elsewhere.

* * *

10\. Next Logical Extensions
============================

Given your interests, the natural next steps are:

1.  **Numeric constraint checking** (`speed(robot)=1.2` vs `max_speed`)
2.  **Temporal propagation** (`always`, `until`)
3.  **Spatial constraint propagation (RCC8)**
4.  **Integration with MPC cost & constraints**
5.  **Explanation of violated constraints (WHY)**

