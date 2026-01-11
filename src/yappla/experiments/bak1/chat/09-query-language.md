Excellent — we’ll now **make this concrete and implementable**.

I’ll do this in **four tight layers**, each cleanly mapping to the next:

1.  **Conceptual query language (declarative, logic-facing)**
2.  **Concrete textual syntax (human / LLM writable)**
3.  **Python API (what you actually call)**
4.  **Execution mapping (which engine runs what)**

By the end, you’ll have something you could realistically:

*   parse,
*   dispatch,
*   execute,
*   and debug.

I’ll keep the language **small, orthogonal, and explicit**.

* * *

1\. Conceptual Query Language (Abstract Level)
==============================================

Every query has the same _abstract shape_:

$$
Q = \langle \text{type}, \text{scope}, \text{payload}, \text{options} \rangle
$$

Where:

*   **type**: what kind of reasoning is requested
*   **scope**: time, model, or context
*   **payload**: formulas, observations, goals
*   **options**: bounds, costs, explanation flags

This uniformity is _intentional_ — it keeps orchestration sane.

* * *

2\. Concrete Query Language (Textual DSL)
=========================================

This is a **minimal DSL** that is:

*   readable by humans,
*   writable by LLMs,
*   trivial to parse.

Think _SQL meets Prolog_, not full logic syntax.

* * *

2.1 Core Grammar (informal)
---------------------------

```text
QUERY <type>
AT <time>
GIVEN <assumptions>
ASK <formula | observation | goal>
WITH <options>
```

All clauses except `QUERY` and `ASK` are optional.

* * *

2.2 Query Types (Keywords)
--------------------------

| Type | Meaning |
| --- | --- |
| ENTAIL | Deductive entailment |
| CONSISTENT | Constraint consistency |
| EXPLAIN | Abductive explanation |
| POSSIBLE | Existential feasibility |
| ACTIONS | Admissible actions |
| PROJECT | Temporal projection |
| COUNTERFACTUAL | Minimal change |
| DIAGNOSE | Model failure |
| INDUCE | Hypothesis formation |
| WHY | Meta-reasoning |

* * *

2.3 Examples in the DSL
-----------------------

### Example 1 — Entailment

```text
QUERY ENTAIL
AT t=42
ASK collision(r1, p1)
```

* * *

### Example 2 — Abduction

```text
QUERY EXPLAIN
AT t=42
ASK observed(collision)
WITH max_explanations=3
```

* * *

### Example 3 — Counterfactual

```text
QUERY COUNTERFACTUAL
AT t=42
ASK reachable(r1, corridor_c)
WITH minimize=interventions
```

* * *

### Example 4 — Actions

```text
QUERY ACTIONS
AT now
ASK allowed
```

* * *

### Example 5 — Temporal projection

```text
QUERY PROJECT
AT t=42
GIVEN policy=go_to_loading_bay
ASK safe
WITH horizon=5s
```

* * *

This language **never mixes semantics**:

*   No probabilities inside formulas
*   No fuzzy truth
*   No hidden inference

