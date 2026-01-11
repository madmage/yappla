## Prompt:
Why do we have to split the ontology from the rules?

## Response:
This is a **fundamental question**, and the short answer is:  
**you don’t have to — but if you don’t, the system will eventually break in subtle, expensive ways**.

Below I’ll give you the **deep, non-hand-wavy reason**, grounded in logic, learning, robotics, and system evolution.

* * *

1\. Ontology vs Rules: What Is the Actual Difference?
-----------------------------------------------------

### Ontology answers:

> **What exists, and what is impossible regardless of time or situation?**

### Rules answer:

> **Given certain conditions, what usually or necessarily follows?**

They live at **different logical levels**.

* * *

2\. Ontology = Model Theory
---------------------------

Rules = Proof Theory

This is the **cleanest formal explanation**.

### Ontology (K₀) defines the _models_

Ontology fixes:

*   symbols
*   domains
*   admissible interpretations
*   invariants that _every possible world must satisfy_

Formally:

> An interpretation is **invalid** if it violates ontology.

Example:

```
forbidden(holding(robot,human))
```

There is **no possible world** where this is true.

* * *

### Rules (K₁) define _derivations inside a model_

Rules tell you:

*   how facts relate
*   how to infer new facts _within_ a model

Example:

```
collision(X,Y) :- overlapping(X,Y)
```

This may or may not apply depending on the world state.

* * *

🔑 **Mixing them collapses model theory and proof theory**, which is one of the classic design errors in reasoning systems.

* * *

3\. Logical Consequences of Not Splitting Them
----------------------------------------------

Let’s examine what breaks if you don’t split.

* * *

### 3.1 Invariants become defeasible (dangerous)

If ontology and rules are merged:

```prolog
forbidden(holding(robot,human)) :- true.
```

Now:

*   It _looks like_ a rule
*   It can be:
    *   overridden
    *   abducted
    *   probabilistically weakened
    *   learned away

But **invariants must not be defeasible**.

In robotics or safety-critical systems, this is catastrophic.

* * *

### 3.2 Learning systems will destroy your ontology

If rules and ontology are mixed, induction systems will happily produce:

```
holding(robot,human) :- emergency.
```

This:

*   violates invariants
*   but looks like a perfectly good rule to an ML system

If ontology is separated:

*   the learner is **constrained**
*   the rule is rejected _before_ it enters the system

* * *

4\. Time and Modality Make the Split Mandatory
----------------------------------------------

You explicitly want:

*   temporal logic
*   modal logic
*   counterfactuals

Ontology facts are:

| Aspect | Ontology |
| --- | --- |
| Time | Atemporal |
| Modality | Necessary |
| Uncertainty | None |
| Revision | Rare |

Rules are:

| Aspect | Rules |
| --- | --- |
| Time | Implicit / contextual |
| Modality | Necessary or default |
| Uncertainty | Possible |
| Revision | Expected |

Once you introduce time or modality, **ontology must live outside time**.

Otherwise:

> “The type system itself becomes time-dependent.”

This is almost always a mistake.

* * *

5\. Abduction Forces the Separation
-----------------------------------

Abduction asks:

> “What _could_ be true to explain this?”

You must be able to say:

*   ❌ “This cannot be hypothesized”
*   ❌ “This violates the domain”
*   ❌ “This breaks physical law”

Only ontology can do that.

If rules and ontology are mixed:

*   abductive hypotheses will include impossible worlds
*   you’ll need expensive post-hoc filtering

* * *

6\. Probabilistic & Neural-Symbolic Integration
-----------------------------------------------

In hybrid systems:

| Component | Ontology | Rules |
| --- | --- | --- |
| Neural | NO | YES |
| Probabilistic | NO | YES |
| Learnable | NO | YES |
| Soft constraints | NO | YES |

Ontology must be:

*   hard
*   crisp
*   symbolic
*   non-learned

Rules may be:

*   weighted
*   neuralized
*   approximate
*   revised

If you don’t separate them, you **cannot safely hybridize**.

* * *

7\. Cognitive Architecture Analogy (Why Humans Do This)
-------------------------------------------------------

Humans separate:

*   **conceptual knowledge** (“A wall is solid”)
*   **situational reasoning** (“This wall might have a door”)

You do not revise:

> “Walls are solid”  
> every time you see a door.

That distinction is _exactly_ ontology vs rules.

* * *

8\. Software Engineering Reason (The Unavoidable One)
-----------------------------------------------------

Even if you ignore theory:

### Ontology changes:

*   break everything
*   require migration
*   invalidate data

### Rule changes:

*   are expected
*   are local
*   are iterative

If they live together:

*   every rule change risks semantic collapse
*   versioning becomes impossible
*   explanations become untrustworthy

* * *

9\. When Is It OK _Not_ to Split Them?
--------------------------------------

There are valid exceptions:

*   Toy systems
*   Single-purpose Prolog programs
*   One-off research prototypes
*   Pure theorem provers

But **the moment you add**:

*   learning
*   explanation
*   time
*   uncertainty
*   robotics
*   safety

👉 **the split becomes non-negotiable**

* * *

10\. A Useful Litmus Test
-------------------------

Ask this about a statement:

> “Could this ever be false in any conceivable world?”

*   **No** → Ontology
*   **Yes** → Rule or fact

That rule of thumb alone will save you years.

* * *

11\. Final Takeaway
-------------------

You are not splitting ontology and rules for elegance.

You are doing it because:

*   logic requires it
*   learning requires it
*   time requires it
*   safety requires it
*   maintenance requires it

If you want, next I can:

*   show a **formal model-theoretic definition**
*   show **how Prolog conflates these and how to fix it**
*   show **how ontologies act as hard constraints in neural-symbolic systems**
*   or relate this directly to **robotics world models**

Just say the word.

