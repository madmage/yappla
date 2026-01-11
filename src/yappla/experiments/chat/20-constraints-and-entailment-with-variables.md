## Prompt:
In our previous examples in Python, we were not considering possible substitutions of variables. How does entails and constraint queries work in this case?

## Response:
Excellent — this is a **crucial inflection point**. What you are noticing is exactly the boundary between:

*   **ground (propositional) reasoning**, and
*   **first-order (relational) reasoning with variables and substitutions**

I’ll explain **precisely** how `ENTAILS` and `CONSTRAINT` queries behave once **variables and substitutions** are introduced, and how this fits into the Python architecture we’ve been sketching.

* * *

1\. Ground vs First-Order: What We Were Doing Before
----------------------------------------------------

In the earlier Python examples, we implicitly assumed:

```text
At(robot, room1)
At(robot, room2)
```

These are **ground atoms**:

*   no variables
*   truth is boolean
*   entailment = yes/no

Constraint propagation was:

*   domain pruning over _constants_
*   no substitutions
*   no quantification

This is essentially **propositional logic + constraints**.

* * *

2\. Once Variables Exist, Everything Changes (But Cleanly)
----------------------------------------------------------

Now we allow:

```text
At(x, y)
```

where:

*   `x`, `y` are variables
*   meaning is _quantified_
*   answers are **substitutions**, not booleans

This is where **unification** enters.

* * *

3\. Substitutions: The Central Object
-------------------------------------

A **substitution** is a mapping:

```text
σ = { x → robot1, y → roomA }
```

Queries no longer ask:

> “Is this true?”

They ask:

> “For which substitutions is this true?”

* * *

4\. ENTAILS with Variables
--------------------------

### 4.1 Semantics

A knowledge base **entails** a formula with variables if:

> There exists a substitution σ such that the ground instance is entailed.

Formally:

```
KB ⊨ φ(x)    iff    ∃σ . KB ⊨ φσ
```

* * *

### 4.2 Example

#### Knowledge (K₀ + K₃)

```text
At(robot1, roomA)
At(robot2, roomB)
```

#### Query

```text
ENTAILS At(x, y)
```

#### Result

```text
{ x → robot1, y → roomA }
{ x → robot2, y → roomB }
```

The result is **a set of substitutions**.

* * *

### 4.3 Existential vs Universal

| Query | Meaning |
| --- | --- |
| `ENTAILS At(x,y)` | Find _some_ bindings |
| `ENTAILS ∀x At(x,y)` | For all x |
| `ENTAILS ∃x At(x,y)` | There exists x |

Most logic engines default to **existential queries**.

* * *

5\. Constraint Queries with Variables
-------------------------------------

Constraint queries _restrict substitutions_.

### 5.1 Example

```text
At(x, y)
y ≠ restricted_zone
```

This is **not a yes/no query** — it is a **filter on substitutions**.

* * *

### 5.2 Operationally

1.  Generate candidate substitutions
2.  Apply constraints
3.  Remove violating substitutions

* * *

### 5.3 Concrete Example

#### Knowledge

```text
At(robot1, roomA)
At(robot2, restricted_zone)
```

#### Query

```text
ENTAILS At(x,y) WHERE y ≠ restricted_zone
```

#### Result

```text
{ x → robot1, y → roomA }
```

Constraint propagation removed invalid bindings.

* * *

6\. Constraint Propagation with Variables (Key Insight)
-------------------------------------------------------

With variables, **domains are sets of constants**.

### Before propagation:

```text
x ∈ {robot1, robot2}
y ∈ {roomA, restricted_zone}
```

### Constraint:

```text
y ≠ restricted_zone
```

### After propagation:

```text
y ∈ {roomA}
x ∈ {robot1}
```

Propagation:

*   reduces domains
*   tightens substitutions
*   may eliminate variables entirely

* * *

7\. How ENTAILS Works Algorithmically (First-Order)
---------------------------------------------------

### High-level algorithm

1.  **Unify** query with facts and rule heads
2.  Generate candidate substitutions
3.  Apply constraints
4.  Propagate constraints across variables
5.  Return remaining substitutions

This is essentially:

*   **SLD resolution** (Prolog-style)
*   *   **constraint filtering**

* * *

8\. Example with Rules and Variables
------------------------------------

### Rules (K₁)

```text
CanEnter(x, y) :- At(x, z), Connected(z, y), Open(y)
```

### Facts (K₀ + K₃)

```text
At(robot1, roomA)
Connected(roomA, roomB)
Open(roomB)
```

### Query

```text
ENTAILS CanEnter(x, y)
```

### Resolution + Propagation

1.  Match rule head → `x`, `y`
2.  Unify body predicates
3.  Bind:

```text
x → robot1
y → roomB
```

Result:

```text
{ x → robot1, y → roomB }
```

* * *

9\. Constraints Inside Rules
----------------------------

Rules may introduce constraints:

```text
Safe(x) :- Speed(x, v), v ≤ vmax
```

During resolution:

*   `v` gets a domain
*   constraint propagation tightens it
*   substitutions violating constraints are rejected

This is **Constraint Logic Programming (CLP)**.

* * *

10\. Important Design Choice: When Do We Propagate?
---------------------------------------------------

Two options:

### A. Eager propagation (recommended)

*   propagate constraints after each unification step
*   prune early

### B. Lazy propagation

*   generate many substitutions
*   filter later
*   slower, simpler

Your architecture clearly wants **eager propagation**.

* * *

11\. Python-Level View (Mental Model)
-------------------------------------

Instead of:

```python
bool entails(atom)
```

You now have:

```python
List[Substitution] entails(query)
```

Where:

```python
Substitution = Dict[Variable, Constant]
```

Constraints are functions:

```python
def constraint(subst) -> bool
```

Constraint propagation reduces the candidate substitutions **before evaluation completes**.

* * *

12\. Why This Matters for MPC and Robotics
------------------------------------------

This allows queries like:

```text
ENTAILS Control(u)
WHERE
  Reachable(x_t+1)
  AND Safe(x_t+1)
  AND u ∈ U
```

The result:

*   is not a single control
*   but a **set of admissible bindings**
*   which can then be optimized numerically

Symbolic pruning before numeric optimization.

* * *

13\. Summary Table
------------------

| Aspect | Ground Logic | First-Order Logic |
| --- | --- | --- |
| Truth | Boolean | Substitutions |
| Query result | True/False | Set of bindings |
| Constraints | On facts | On variable domains |
| Propagation | Prune facts | Prune substitutions |
| Expressivity | Limited | Relational |

* * *

14\. One Key Sentence to Remember
---------------------------------

> **In first-order entailment, a query does not return truth — it returns the substitutions under which the query is true, and constraint propagation removes substitutions that violate constraints.**
