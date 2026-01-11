3\. Python API (What You Actually Call)
=======================================

Now we map this to a **Python-first API**.

* * *

3.1 Core Data Structures
------------------------

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
```

### Query type enum

```python
class QueryType(Enum):
    ENTAIL = "entail"
    CONSISTENT = "consistent"
    EXPLAIN = "explain"
    POSSIBLE = "possible"
    ACTIONS = "actions"
    PROJECT = "project"
    COUNTERFACTUAL = "counterfactual"
    DIAGNOSE = "diagnose"
    INDUCE = "induce"
    WHY = "why"
```

* * *

### Query object

```python
@dataclass
class Query:
    type: QueryType
    ask: Any
    time: Optional[int] = None
    given: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
```

* * *

3.2 Result Objects (Typed, Explicit)
------------------------------------

```python
@dataclass
class Result:
    success: bool
    answer: Any = None
    explanation: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
```

Examples:

*   `answer=True`
*   `answer=["turn_left", "wait"]`
*   `answer=[Explanation(...)]`

* * *

3.3 Reasoning Engine Facade
---------------------------

This is **the only entry point**.

```python
class ReasoningEngine:

    def query(self, q: Query) -> Result:
        dispatch = {
            QueryType.ENTAIL: self._entail,
            QueryType.CONSISTENT: self._consistent,
            QueryType.EXPLAIN: self._explain,
            QueryType.POSSIBLE: self._possible,
            QueryType.ACTIONS: self._actions,
            QueryType.PROJECT: self._project,
            QueryType.COUNTERFACTUAL: self._counterfactual,
            QueryType.DIAGNOSE: self._diagnose,
            QueryType.INDUCE: self._induce,
            QueryType.WHY: self._why,
        }
        return dispatch[q.type](q)
```

This **enforces separation**:

*   No query touches the wrong subsystem
*   Easy to test and profile

* * *

4\. Execution Mapping (What Runs Under the Hood)
================================================

This is the _most important_ part architecturally.

* * *

4.1 Entailment → Logic Kernel
-----------------------------

```python
def _entail(self, q: Query) -> Result:
    holds, proof = self.logic.entails(
        formula=q.ask,
        time=q.time
    )
    return Result(
        success=holds,
        answer=holds,
        explanation=proof
    )
```

*   Uses **only** hard facts + constraints
*   No probabilities
*   No learning

* * *

4.2 Consistency → Constraint Propagation
----------------------------------------

```python
def _consistent(self, q: Query) -> Result:
    ok, conflict = self.constraints.check(
        assumptions=q.ask,
        time=q.time
    )
    return Result(
        success=ok,
        answer=ok,
        explanation=conflict
    )
```

* * *

4.3 Abduction → Hypothesis Search + Filtering
---------------------------------------------

```python
def _explain(self, q: Query) -> Result:
    candidates = self.abducer.generate(
        observation=q.ask,
        time=q.time,
        limit=q.options.get("max_explanations", 5)
    )

    valid = []
    for hyp in candidates:
        if self.logic.consistent(hyp, time=q.time):
            score = self.probability.score(hyp)
            valid.append((hyp, score))

    return Result(
        success=len(valid) > 0,
        answer=sorted(valid, key=lambda x: -x[1]),
    )
```

This makes **abduction safe**.

* * *

4.4 Actions → Logic Guards
--------------------------

```python
def _actions(self, q: Query) -> Result:
    allowed = []
    for action in self.actions.available():
        if self.logic.entails(f"allowed({action})", time=q.time):
            allowed.append(action)
    return Result(success=True, answer=allowed)
```

* * *

4.5 Counterfactual → Abduction Over Missing Conditions
------------------------------------------------------

```python
def _counterfactual(self, q: Query) -> Result:
    changes = self.abducer.minimal_changes(
        goal=q.ask,
        time=q.time,
        cost_fn=self.costs.intervention
    )
    return Result(success=True, answer=changes)
```

* * *

4.6 Temporal Projection → Simulation + Checking
-----------------------------------------------

```python
def _project(self, q: Query) -> Result:
    trace = self.simulator.rollout(
        start_time=q.time,
        policy=q.given["policy"],
        horizon=q.options["horizon"]
    )

    violations = [
        t for t, state in trace
        if not self.logic.consistent(state)
    ]

    return Result(
        success=len(violations) == 0,
        answer=violations
    )
```

* * *

4.7 Meta-Reasoning → Proof & Control Traces
-------------------------------------------

```python
def _why(self, q: Query) -> Result:
    trace = self.tracer.explain(q.ask)
    return Result(success=True, answer=trace)
```

* * *

5\. Why This Design Holds Up
============================

### 1\. Queries are **semantically pure**

No query ever:

*   mixes probability and logic,
*   asks ambiguous questions.

* * *

### 2\. Python stays clean

You don’t write:

```python
engine.entails_probably(...)
```

You write:

```python
engine.query(Query(
    type=QueryType.EXPLAIN,
    ask="collision(r1,p1)",
    time=42
))
```

* * *

### 3\. LLMs can safely sit _on top_

LLMs can:

*   generate DSL queries,
*   explain results,
*   suggest hypotheses.

They **never** answer entailment themselves.

* * *

6\. Minimal End-to-End Example
==============================

```python
q = Query(
    type=QueryType.EXPLAIN,
    ask="observed(collision)",
    time=42,
    options={"max_explanations": 3}
)

result = engine.query(q)

for hyp, score in result.answer:
    print(hyp, score)
```

* * *

Final takeaway
--------------

> You now have a **cleanly stratified query language** where each question maps to exactly one reasoning mode, one engine, and one semantic contract.

