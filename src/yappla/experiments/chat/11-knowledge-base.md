## Prompt:
How is the initial domain knowledge (and how to update it) in this system?

## Response:
This is a **crucial question** — it gets to the heart of why systems like this either remain robust for years _or_ collapse under their own weight.

I’ll answer in **four layers**, from formal to operational, and I’ll be explicit about:

*   **what is allowed to enter the core**,
*   **how it enters**,
*   **how it changes**,
*   **and what is never allowed to change automatically**.

* * *

1\. What “Domain Knowledge” Means in This Architecture
======================================================

Domain knowledge is **not one thing**. It is stratified by _epistemic status_.

We distinguish **four kinds of knowledge**, each with different update rules.

| Layer | Content | Mutable? | Who updates it |
| --- | --- | --- | --- |
| **K₀ – Ontology & invariants** | Types, safety rules, physics constraints | ❌ No | Humans |
| **K₁ – Structural rules** | Causal, spatial, temporal rules | ⚠️ Rare | Humans + offline validation |
| **K₂ – Hypotheses & models** | Faults, learned rules, dynamics | ✅ Yes | System |
| **K₃ – Episodic facts** | Observations, state estimates | ✅ Yes | System |

This separation is **non-negotiable**.

* * *

2\. Initial Domain Knowledge (Bootstrapping)
============================================

2.1 K₀ — Ontology & Invariants (Immutable Core)
-----------------------------------------------

### What goes here

*   Object types
*   Predicate signatures
*   Safety constraints
*   Physical impossibilities

Examples:

```prolog
robot(X) → object(X).
human(X) → object(X).

forbidden :-
    holding(robot, human).

forbidden :-
    rcc8(overlapping, robot, wall).
```

### Properties

*   Binary truth
*   No probabilities
*   No learning
*   No exceptions

### Why immutable

If these change automatically:

*   Safety proofs collapse
*   Explanations become meaningless

### How introduced

*   Hand-written
*   Version-controlled
*   Reviewed like code

* * *

2.2 K₁ — Structural Rules (Mostly Stable)
-----------------------------------------

### What goes here

*   Causal rules
*   Typical effects
*   Domain logic

Examples:

```prolog
collision :- rcc8(overlapping(X, Y)).
blocked(X) :- rcc8(tangential_proper_part, X, obstacle).
```

### Properties

*   Logical
*   Can be overridden by abduction
*   Rarely changed online

### How introduced

*   Initially hand-written
*   Possibly refined offline
*   Never replaced wholesale online

* * *

2.3 K₂ — Hypotheses & Models (Explicitly Uncertain)
---------------------------------------------------

### What goes here

*   Fault models
*   Learned rules
*   Alternative dynamics models

Examples:

```prolog
abducible(sensor_fault(lidar)).
abducible(wheel_slip).
```

Or:

```text
model: dynamics_v3
confidence: 0.72
```

### Properties

*   Explicitly defeasible
*   Weighted
*   Replaceable

* * *

2.4 K₃ — Episodic Facts (Continuously Updated)
----------------------------------------------

### What goes here

*   Observations
*   State estimates
*   Temporal facts

Examples:

```prolog
observed(position(r1, x=3.2), t=42).
near(r1, p1) : score=0.81
```

* * *

3\. How Knowledge Enters the System (Admission Control)
=======================================================

**Nothing enters the kernel directly.**  
Everything passes through **admission filters**.

* * *

3.1 Neural → Symbolic (K₃ only)
-------------------------------

Neural outputs:

```
is_near(r1, p1) = 0.83
```

Admission rule:

*   Stored as _hypothesis_ or _observation_
*   Never asserted as hard fact

```prolog
hypothesis(near(r1, p1)).
```

* * *

3.2 Abduction → Hypotheses (K₂)
-------------------------------

Abduction proposes:

```prolog
sensor_fault(lidar).
```

Admission rule:

*   Allowed only if declared abducible
*   Weighted
*   Time-scoped

* * *

3.3 Hard Facts → Kernel (Very rare)
-----------------------------------

Only two sources:

1.  Trusted sensors (with redundancy)
2.  Human assertions

Even then:

*   Passed through consistency checks
*   Often time-scoped

* * *

4\. How Knowledge Is Updated (Without Corrupting the Core)
==========================================================

4.1 K₃ Updates: Cheap and Frequent
----------------------------------

*   Sliding time window
*   Old facts decay
*   Contradictions allowed

This is your **belief buffer**.

* * *

4.2 K₂ Updates: Model Revision, Not Assertion
---------------------------------------------

### When?

*   Prediction errors
*   Repeated abduction failures
*   Systematic mismatches

### How?

*   Adjust weights
*   Add/remove hypotheses
*   Introduce alternative rules

Example:

```text
wheel_slip confidence ↑
dynamics_model_v2 confidence ↓
```

No hard facts are changed.

* * *

4.3 K₁ Updates: Offline and Audited
-----------------------------------

Triggered by:

*   Long-term evidence
*   Repeated explanation patterns

Process:

1.  Candidate rule induced
2.  Tested in simulation
3.  Reviewed
4.  Promoted (rarely)

* * *

4.4 K₀ Updates: Versioned, Human-Only
-------------------------------------

Changing:

*   Safety constraints
*   Ontology

Requires:

*   Explicit migration
*   Re-verification

This is equivalent to changing **the laws of the system**.

* * *

5\. Formal Update Semantics (What Is Allowed)
=============================================

| Operation | Allowed? | Where |
| --- | --- | --- |
| Add episodic fact | ✅ | K₃ |
| Remove episodic fact | ✅ | K₃ |
| Add hypothesis | ✅ | K₂ |
| Change hypothesis weight | ✅ | K₂ |
| Add structural rule | ⚠️ | K₁ (offline) |
| Modify invariant | ❌ | K₀ |

* * *

6\. Belief Revision Without Explosion
=====================================

When contradiction occurs:

1.  **Never retract K₀**
2.  Prefer retracting:
    *   K₃ facts
    *   then K₂ hypotheses
3.  Log conflict for learning

This is **prioritized belief revision**.

* * *

7\. Example: Full Update Cycle
==============================

### Step 1 — Unexpected collision

```
observed(collision, t=42)
```

### Step 2 — Abduction

```
sensor_fault(lidar)
wheel_slip
```

### Step 3 — Repeated evidence

```
sensor_fault(lidar) at t=43, t=44
```

### Step 4 — Update

```
P(sensor_fault(lidar)) ↑
trust(lidar) ↓
```

### Step 5 — Kernel unchanged

Safety rule still applies.

* * *

8\. Why This Works
==================

Because:

*   Learning is sandboxed
*   Logic is protected
*   Updates are explicit and typed
*   Mistakes are localized

* * *

Final Mental Model
==================

> The system does not “learn the world”.  
> It **learns which explanations are currently plausible**, while the world model itself remains structurally intact.

That’s the only way to combine logic, learning, time, and safety coherently.

