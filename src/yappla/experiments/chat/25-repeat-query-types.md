## Prompt:
Some time ago in this chat, we listed a set of possible query types, that included ENTAIL, CONSISTENT, and other, can you repeat here the list?

## Response:
Yes — let me restate the **full, coherent set of query types** we discussed (and implicitly used) for this kind of **layered logic + CLP + optimization system**, in a clean and canonical way.

I’ll group them by **logical purpose**, because that’s how real systems (SMT solvers, planners, MPC stacks) organize them.

* * *

1\. Truth & Logical Consequence Queries
---------------------------------------

These ask _what follows logically_ from the knowledge base.

### 1\. **ENTAIL**

> _Which substitutions make this formula true?_

**Form**

```text
ENTAIL φ(x̄)
```

**Returns**

*   set of substitutions (partial or full, depending on labeling)

**Example**

```text
ENTAIL At(x,y)
```

* * *

### 2\. **VALID**

> _Is this formula true in all models of the knowledge base?_

**Form**

```text
VALID φ
```

**Returns**

*   boolean

**Relation**

```text
VALID φ  ⇔  ¬CONSISTENT(¬φ)
```

* * *

2\. Consistency & Feasibility Queries
-------------------------------------

These ask whether something is _possible at all_.

### 3\. **CONSISTENT**

> _Is there at least one assignment satisfying these constraints?_

**Form**

```text
CONSISTENT C
```

**Returns**

*   boolean

**Example**

```text
CONSISTENT
WHERE x ∈ {1,2} AND x ≠ 1 AND x ≠ 2
```

* * *

### 4\. **SAT**

> _Produce one satisfying assignment (if any)._

**Form**

```text
SAT C
```

**Returns**

*   one substitution (or `None`)

**Relation**

```text
SAT = CONSISTENT + labeling
```

* * *

3\. Optimization Queries
------------------------

These ask _what is best_ among what is possible.

### 5\. **OPTIMIZE**

> _Find the best satisfying substitution under a cost._

**Form**

```text
OPTIMIZE φ MIN/MAX cost
```

**Returns**

*   best substitution
*   cost value

**Example**

```text
ENTAIL Control(u) OPTIMIZE MIN energy(u)
```

* * *

### 6\. **PARETO**

> _Find all non-dominated solutions for multiple objectives._

**Form**

```text
PARETO φ OBJECTIVES [c₁, c₂, …]
```

**Returns**

*   set of substitutions

* * *

4\. Model Exploration Queries
-----------------------------

These ask about _space of solutions_, not just one.

### 7\. **COUNT**

> _How many solutions exist?_

**Form**

```text
COUNT φ
```

**Returns**

*   integer

* * *

### 8\. **ENUMERATE**

> _Enumerate all solutions (possibly bounded)._

**Form**

```text
ENUMERATE φ LIMIT k
```

**Returns**

*   list of substitutions

* * *

5\. Explanation & Debugging Queries
-----------------------------------

These ask _why_ something is (im)possible.

### 9\. **WHY**

> _Explain why φ is entailed._

**Form**

```text
WHY φ
```

**Returns**

*   proof / derivation graph

* * *

### 10\. **WHYNOT**

> _Explain why φ is not entailed._

**Form**

```text
WHYNOT φ
```

**Returns**

*   minimal conflicting constraints

* * *

6\. Temporal & Hypothetical Queries
-----------------------------------

These reason about _change and alternatives_.

### 11\. **PROJECT**

> _What will be true after applying actions / time?_

**Form**

```text
PROJECT φ AFTER τ
```

* * *

### 12\. **WHATIF**

> _Is φ possible if we assume ψ?_

**Form**

```text
WHATIF ψ ⊢ φ
```

* * *

7\. Learning & Uncertainty Queries
----------------------------------

These connect logic with data.

### 13\. **PROBABILITY**

> _What is the probability that φ holds?_

**Form**

```text
PROBABILITY φ
```

* * *

### 14\. **MOSTLIKELY**

> _Which assignment maximizes likelihood?_

**Form**

```text
MOSTLIKELY φ
```

* * *

8\. Safety & Robustness Queries (Robotics / MPC-Oriented)
---------------------------------------------------------

These are especially relevant for your context.

### 15\. **SAFE**

> _Is φ guaranteed under all uncertainties?_

**Form**

```text
SAFE φ
```

* * *

### 16\. **ROBUST**

> _What is the safety margin of φ?_

**Form**

```text
ROBUST φ
```

* * *

9\. Structural Summary Table
----------------------------

| Category | Query Type |
| --- | --- |
| Logical | ENTAIL, VALID |
| Feasibility | CONSISTENT, SAT |
| Optimization | OPTIMIZE, PARETO |
| Enumeration | COUNT, ENUMERATE |
| Explanation | WHY, WHYNOT |
| Temporal | PROJECT, WHATIF |
| Uncertainty | PROBABILITY, MOSTLIKELY |
| Safety | SAFE, ROBUST |

* * *

10\. Key Unifying Insight
-------------------------

All these queries reduce to **four core mechanisms**:

1.  **Unification**
2.  **Constraint propagation**
3.  **Labeling / search**
4.  **Optimization / aggregation**

Everything else is _syntax and orchestration_.

* * *

11\. Final Takeaway
-------------------

> **ENTAIL and CONSISTENT are the logical ядро (core); labeling, optimization, explanation, and robustness are structured ways of consuming the same underlying constraint-solving machinery.**
