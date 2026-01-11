1\. Designing a Logic Kernel for Robotics & Spatial Reasoning
=============================================================

1.1 What the kernel is (and is not)
-----------------------------------

Your **logic kernel** is:

*   The _only_ place where truth is binary
*   The _only_ place where inconsistency is not allowed
*   The _only_ place where inference must terminate

It is **not**:

*   The place for probabilities
*   The place for learning
*   The place for perception noise
*   The place for open-ended hypothesis generation

Think of it as the **rigid skeleton** of the system.

* * *

1.2 Required properties of the kernel
-------------------------------------

For robotics and spatial reasoning, the kernel must support:

1.  **Relational reasoning**
2.  **Constraints**
3.  **Incremental updates**
4.  **Fast consistency checking**
5.  **Explainability**

This immediately excludes:

*   Full FOL
*   Arbitrary modal logics
*   Unrestricted negation

* * *

1.3 Recommended kernel fragment
-------------------------------

### Core logic

Use a **Horn-clause–based constraint logic**:

*   Datalog or Datalog+
*   No function symbols
*   Stratified negation only
*   Finite domain per timestep

Why:

*   Guaranteed termination
*   Can be incrementally maintained
*   Easy to explain

* * *

### Spatial reasoning module (pluggable)

Do **not** encode spatial reasoning in FOL.

Instead:

*   Treat spatial relations as **constraints**
*   Delegate propagation to a dedicated solver

Examples:

*   RCC8
*   Double Cross
*   Allen Interval Algebra (for temporal intervals)

The logic kernel:

*   Asserts spatial facts
*   Calls the constraint propagator
*   Accepts or rejects states

* * *

### Temporal handling

Time is **outside** the kernel.

Kernel only reasons about:

```
State(t)
```

Temporal transitions are handled by:

*   A state manager
*   An event model
*   Or an MPC controller

* * *

1.4 Example kernel vocabulary
-----------------------------

```
object(robot)
object(pallet)

rcc8(disconnected, robot, pallet)
holding(robot, pallet)

forbidden :- holding(robot, pallet),
             rcc8(disconnected, robot, pallet).
```

This kernel:

*   Is small
*   Is decidable
*   Can run at control-loop rates

* * *

1.5 Why this kernel survives integration
----------------------------------------

Because:

*   It is boring
*   It is limited
*   It is fast
*   It fails loudly

This is exactly what you want at the center.

* * *

