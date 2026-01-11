Below is a **formal, system-level taxonomy of query types** for the architecture we’ve been designing. I’ll be precise enough that each query type could be given:

*   a **syntax**,
*   a **semantics**,
*   and an **execution strategy**,

without committing you to a single language (Prolog, ASP, Python API, etc.).

I’ll structure this as follows:

1.  **Foundational model assumptions** (what queries range over)
2.  **Core query types** (the minimal set)
3.  **Extended query types** (temporal, counterfactual, meta)
4.  **Operational semantics** (how each query is actually answered)
5.  **Why this decomposition matters architecturally**

* * *

1\. Foundational Model Assumptions
==================================

We assume the system maintains, at each time step  $t$ :

*   A **belief state**  
     $B_t = \langle F_t, H_t, C_t, P_t \rangle$ 

Where:

*    $F_t$ : hard facts (logic kernel, consistent)
*    $H_t$ : hypotheses (abducible, defeasible)
*    $C_t$ : constraints (spatial, temporal, safety)
*    $P_t$ : probabilistic weights over hypotheses/models

We also assume:

*   A transition model  $T$ 
*   An observation model  $O$ 
*   A control model (e.g. MPC)

All queries are evaluated **relative to a time index** (explicit or implicit).

* * *

2\. Core Query Types (Minimal Set)
==================================

These are the **irreducible queries** your system must support.

* * *

2.1 Entailment Queries (Deductive)
----------------------------------

### Intent

> “What must be true given what I know?”

### Formal form

$$
B_t \models \varphi \; ?
$$

Where:

*    $\varphi$  is a formula in the logic kernel

### Semantics

*   True iff  $\varphi$  holds in **all models** consistent with  $F_t \cup C_t$ 

### Examples

*   “Is this state valid?”
*   “Is action A allowed?”
*   “Is safety invariant S violated?”

### Output

*   Boolean
*   Optional proof / justification graph

* * *

2.2 Consistency Queries (Constraint Satisfaction)
-------------------------------------------------

### Intent

> “Is my current belief state coherent?”

### Formal form

$$
\text{Consistent}(F_t \cup H'_t \cup C_t) \; ?
$$

Where:

*    $H'_t \subseteq H_t$  (possibly empty)

### Semantics

*   True iff constraint propagation succeeds

### Examples

*   “Is explanation E physically possible?”
*   “Can these spatial relations coexist?”

### Output

*   Boolean
*   Minimal conflict set if false

* * *

2.3 Abductive Queries (Explanation)
-----------------------------------

### Intent

> “What could explain this observation?”

### Formal form

$$
\text{Explain}(O_t \mid B_{t-1})
$$

Equivalent to:

$$
\Delta \subseteq \mathcal{A} \;\text{s.t.}\; B_{t-1} \cup \Delta \models O_t
$$

Where:

*    $\mathcal{A}$  = abducibles

### Semantics

*   Find minimal (or bounded)  $\Delta$  making observation derivable

### Examples

*   “Why did a collision occur?”
*   “Why did the plan fail?”

### Output

*   Set of candidate explanations
*   Ranked by probability / cost
*   Each explanation is a set of hypotheses

* * *

2.4 Possibility Queries (Existential Feasibility)
-------------------------------------------------

### Intent

> “Is there _some_ consistent way this could be true?”

### Formal form

$$
\exists M \in \mathcal{M}(B_t) : M \models \varphi \; ?
$$

### Semantics

*   True iff at least one consistent model satisfies  $\varphi$ 

### Examples

*   “Could the robot reach region R?”
*   “Is there a plan that avoids collision?”

### Output

*   Boolean
*   Optional witness (model, plan, explanation)

* * *

2.5 Action-Admissibility Queries (Logic → Control)
--------------------------------------------------

### Intent

> “Which actions are allowed right now?”

### Formal form

$$
\{ a \in A \mid B_t \cup \text{Do}(a) \not\models \bot \}
$$

### Semantics

*   Actions whose preconditions and constraints are satisfied

### Examples

*   “Which actions can MPC consider?”
*   “Is emergency stop mandatory?”

### Output

*   Set of actions
*   Optional exclusion reasons

* * *

3\. Extended Query Types
========================

These are **compositions** of the core types, but extremely powerful.

* * *

3.1 Temporal Projection Queries (Prediction)
--------------------------------------------

### Intent

> “What will (or might) be true in the future?”

### Formal form

$$
\text{Project}(B_t, \pi, \Delta t) \models \varphi \; ?
$$

Where:

*    $\pi$ : policy or action sequence

### Semantics

*   Simulate belief evolution under transition model
*   Check entailment or possibility at  $t + \Delta t$ 

### Examples

*   “Will this plan violate safety?”
*   “What is the earliest time the corridor becomes free?”

### Output

*   Boolean or time index
*   Optional trace

* * *

3.2 Counterfactual Queries (What-if / Why-not)
----------------------------------------------

### Intent

> “What would need to change for X to be true?”

### Formal form

$$
\text{MinChange}(\Delta) \;\text{s.t.}\; B_t \cup \Delta \models \varphi
$$

### Semantics

*   Abduction over _missing conditions_
*   Minimize change cost

### Examples

*   “Why can’t I pass here?”
*   “What would allow action A?”

### Output

*   Required conditions
*   Ranked by cost / plausibility

* * *

3.3 Diagnostic Queries (Model Adequacy)
---------------------------------------

### Intent

> “Is my model still valid?”

### Formal form

$$
B_{t-1} \cup T \models O_t \; ?
$$

If false:

$$
\text{Explain}(\neg(B_{t-1} \cup T \models O_t))
$$

### Semantics

*   Detect prediction failure
*   Abduce model faults

### Examples

*   “Is my dynamics model wrong?”
*   “Has the environment changed?”

### Output

*   Violation flag
*   Suspected faulty assumptions

* * *

3.4 Inductive Queries (Hypothesis Formation)
--------------------------------------------

### Intent

> “What general rules explain repeated patterns?”

### Formal form

$$
\text{Induce}(\{B_{t_i}, O_{t_i}\}_{i=1}^n)
$$

### Semantics

*   Propose candidate rules
*   Validate only as hypotheses

### Examples

*   “What usually causes navigation slowdown?”
*   “Which spatial patterns precede collisions?”

### Output

*   Soft rules
*   Confidence scores
*   No hard assertions

* * *

3.5 Meta-Reasoning Queries (Introspection)
------------------------------------------

### Intent

> “Why did you reason this way?”

### Formal form

$$
\text{ExplainReasoning}(Q)
$$

### Semantics

*   Trace inference steps
*   Expose pruning, thresholds, failures

### Examples

*   “Why was explanation E rejected?”
*   “Why wasn’t plan P considered?”

### Output

*   Proof tree
*   Pruning reasons
*   Resource limits hit

* * *

4\. Operational Semantics (How Queries Are Answered)
====================================================

Each query type maps to a **pipeline**, not a single solver.

| Query Type | Main Mechanisms |
| --- | --- |
| Entailment | Logic kernel |
| Consistency | Constraint propagation |
| Abduction | Hypothesis search + kernel filtering |
| Possibility | SAT / CSP / planning |
| Action admissibility | Kernel + guards |
| Temporal projection | Simulation + checking |
| Counterfactual | Abduction + cost |
| Diagnostic | Prediction check + abduction |
| Induction | Pattern mining + validation |
| Meta | Proof & control traces |

This separation is **intentional and essential**.

* * *

5\. Why This Decomposition Matters
==================================

### 1\. Avoids semantic confusion

You never ask:

*   “Is this probably true?”  
    You ask:
*   “Is it entailed?”
*   “Is it possible?”
*   “Is it the best explanation?”

These are _different questions_.

* * *

### 2\. Enables clean APIs

Each query type:

*   Has clear inputs
*   Clear outputs
*   Clear failure modes

This is crucial for:

*   Robotics
*   Real-time systems
*   Debugging

* * *

### 3\. Prevents neural overreach

Neural components:

*   Feed hypotheses
*   Rank explanations
*   Never answer entailment queries

This preserves correctness.

* * *

One-sentence summary
--------------------

> You are not building a system that answers “Is X true?”, but a system that can precisely distinguish **must be true**, **could be true**, **best explains**, **would be true if**, and **cannot be true**, and justify each answer.

