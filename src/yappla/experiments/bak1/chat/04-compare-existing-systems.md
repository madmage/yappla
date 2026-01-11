2\. Comparing Existing Systems Through This Lens
================================================

Now let’s evaluate existing systems **not by ambition**, but by **architectural sanity**.

* * *

2.1 OpenCog
-----------

### Strengths

*   Extremely expressive
*   Unified hypergraph representation
*   Supports deduction, induction, abduction

### Fatal problems

*   No hard semantic boundaries
*   Truth values are fuzzy/probabilistic everywhere
*   Inference control is heuristic and fragile

### Verdict

❌ Too unconstrained  
❌ Hard to make safe  
❌ Difficult to integrate with real-time systems

* * *

2.2 NARS (Non-Axiomatic Reasoning System)
-----------------------------------------

### Strengths

*   Explicit bounded rationality
*   Truth is time-dependent
*   Designed for incomplete knowledge

### Weaknesses

*   Weak spatial reasoning
*   Custom logic semantics
*   Poor interoperability

### Verdict

🟡 Conceptually excellent  
🟡 Architecturally interesting  
❌ Hard to adapt to robotics constraints

* * *

2.3 ProbLog / Probabilistic Logic Programming
---------------------------------------------

### Strengths

*   Clear separation between logic and probability
*   Clean semantics
*   Abduction is natural

### Weaknesses

*   Poor temporal support
*   Scalability limits
*   Not designed for incremental updates

### Verdict

✅ Strong inspiration  
🟡 Needs temporal and control layers  
🟡 Needs constraint solvers

* * *

2.4 DeepProbLog
---------------

### Strengths

*   Neural predicate grounding
*   Differentiable learning
*   Maintains symbolic structure

### Weaknesses

*   Training cost explodes
*   Limited explainability
*   Still expensive inference

### Verdict

✅ Very relevant for perception → symbols  
❌ Not suitable as a central reasoning engine

* * *

2.5 Logic Tensor Networks (LTN)
-------------------------------

### Strengths

*   Continuous semantics
*   Elegant neural-symbolic fusion
*   Good for soft constraints

### Weaknesses

*   No crisp logic layer
*   No hard guarantees
*   Poor for safety-critical reasoning

### Verdict

🟡 Good _pre-logic_ layer  
❌ Not a kernel  
❌ No hard consistency guarantees

* * *

2.6 Summary table
-----------------

| System | Kernel-worthy? | Why |
| --- | --- | --- |
| OpenCog | ❌ | Too unconstrained |
| NARS | ❌ | Custom semantics |
| ProbLog | 🟡 | Good structure, missing layers |
| DeepProbLog | ❌ | Too heavy |
| LTN | ❌ | No crisp core |

**Conclusion:**  
👉 Build your own kernel  
👉 Steal ideas, not architectures

* * *

