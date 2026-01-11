## Prompt:
What is labeling and search?

## Response:
Great question. **Labeling and search** are the missing pieces that turn **constraint propagation** into a **full solver**.

Up to now, your engine is a **constraint propagator**. It can:

*   prune domains
*   detect inconsistency
*   narrow possibilities

But it **does not make choices**.

Labeling + search is _exactly_ about **making controlled choices when propagation alone is not enough**.

I’ll explain this in layers, with intuition, formal meaning, examples, and how it fits your CLP(FD) engine.

* * *

1\. The Big Picture
-------------------

Constraint solving has **two phases**:

1.  **Constraint propagation**  
    Remove impossible values _without guessing_
2.  **Search (labeling)**  
    Make choices when propagation stalls

Most problems require both.

* * *

2\. What Is Labeling?
---------------------

**Labeling** means:

> Assigning a concrete value to a variable **from its remaining domain**.

Example:

```
x ∈ {1,2,3}
```

Labeling picks one:

```
x = 1
```

This is a **decision**, not a logical consequence.

* * *

3\. What Is Search?
-------------------

**Search** is:

> Systematically exploring different labelings using backtracking.

If one choice fails:

*   undo it
*   try another

* * *

4\. Why Propagation Alone Is Insufficient
-----------------------------------------

### Example

```
x ∈ {1,2}
y ∈ {1,2}
Constraint: x ≠ y
```

Propagation does nothing:

```
x ∈ {1,2}
y ∈ {1,2}
```

But solutions exist:

```
x=1,y=2
x=2,y=1
```

Only **labeling + search** can find them.

* * *

5\. Labeling = Controlled Guessing
----------------------------------

But this is _not blind guessing_.

Good solvers:

*   choose variables with small domains
*   try values that are likely to work
*   propagate after each decision

This is **informed search**.

* * *

6\. Operational Flow
--------------------

```
propagate constraints
if all domains are singletons:
    solution found
else:
    choose variable v
    for value in domain(v):
        try v = value
        propagate
        recurse
```

This is **depth-first search with propagation**.

* * *

7\. Simple Example Walkthrough
------------------------------

### Problem

```
x ∈ {1,2}
y ∈ {1,2}
x ≠ y
```

### Step 1: Propagation

Nothing changes.

### Step 2: Label

Pick `x`.

Try:

```
x = 1
```

### Step 3: Propagate

```
y ≠ 1 → y = 2
```

### Solution found:

```
{x=1, y=2}
```

Backtrack:

```
x = 2 → y = 1
```

* * *

8\. Labeling vs ENTAIL
----------------------

| Operation | What it returns |
| --- | --- |
| ENTAIL | All consistent **partial** substitutions |
| LABELING | All **complete** substitutions |
| CONSISTENT | Whether _any_ solution exists |

Labeling is **optional**:

*   ENTAIL is enough for planning
*   Labeling is needed for **enumeration or optimization**

* * *

9\. Labeling Strategies (Very Important)
----------------------------------------

### Variable Selection

*   First unbound variable
*   Smallest domain (fail-fast)
*   Most constrained variable

### Value Selection

*   Lowest value
*   Random
*   Heuristic-based

Good heuristics = massive speedups.

* * *

10\. Labeling in CLP(FD)
------------------------

In Prolog CLP(FD):

```prolog
Vars ins 1..3,
X #\= Y,
label(Vars).
```

Without `label/1`, the solver:

*   **does not assign values**
*   just maintains domains

* * *

11\. How This Fits Your Engine
------------------------------

Right now you have:

✔ Unification  
✔ Constraint propagation  
✔ ENTAIL  
✔ CONSISTENT

You are missing:

❌ Search  
❌ Backtracking  
❌ Complete assignments

* * *

12\. Minimal Labeling Code (Python)
-----------------------------------

Here is a **minimal, correct** version:

```python
def label(subst: Substitution, constraints):
    engine = ConstraintEngine(constraints)

    # propagate first
    if not engine.propagate(subst):
        return []

    # if all domains are singleton → solution
    if all(len(d) == 1 for d in subst.domains.values()):
        return [subst]

    # choose variable with smallest domain > 1
    var = min(
        (v for v in subst.domains if len(subst.domains[v]) > 1),
        key=lambda v: len(subst.domains[v])
    )

    solutions = []
    for value in subst.domains[var]:
        new_subst = subst.copy()
        new_subst.domains[var] = {value}
        solutions.extend(label(new_subst, constraints))

    return solutions
```

* * *

13\. When to Use Labeling
-------------------------

Use labeling when you need:

*   concrete plans
*   schedules
*   assignments
*   exact control values
*   full enumerations

Do **not** use labeling when:

*   checking feasibility
*   pruning symbolic plans
*   running MPC inner loops

* * *

14\. MPC Analogy (Very Important)
---------------------------------

| CLP | MPC |
| --- | --- |
| Propagation | Constraint tightening |
| CONSISTENT | Feasibility check |
| ENTAIL | Admissible region |
| Labeling | Control selection |
| Search | Trajectory exploration |

MPC usually **avoids labeling** until the final step.

* * *

15\. One-Sentence Definition
----------------------------

> **Labeling is the act of assigning concrete values to variables, and search is the systematic exploration of those assignments using backtracking, guided by constraint propagation.**

* * *
