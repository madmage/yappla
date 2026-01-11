## Prompt:
Connect it to MPC and learned dynamics

## Response:
Great, this is where all the pieces _click together_.

I’ll connect the **layered knowledge architecture (K₀–K₃)** directly to **MPC with learned dynamics**, in a way that is faithful to both control theory _and_ logic / AI practice — not a buzzword mashup.

I’ll go step by step, from classical MPC to hybrid neuro-symbolic MPC.

* * *

1\. Classical MPC: What Knowledge Is Implicitly There?
------------------------------------------------------

A standard MPC problem is:

$$
\min_{u_{0:T}} \sum_{t=0}^T \ell(x_t, u_t)
$$

subject to:

$$
x_{t+1} = f(x_t, u_t)
$$
 
$$
x_t \in \mathcal{X}, \quad u_t \in \mathcal{U}
$$

Even in this “pure” formulation, you already have **multiple knowledge types**, just not explicitly separated.

* * *

2\. Mapping MPC to K₀–K₃
------------------------

### K₀ — OntologyKnowledge → _Hard physics & invariants_

This corresponds to **non-negotiable constraints**:

*   State and control bounds
*   Collision-free regions
*   Actuator limits
*   Conservation laws
*   Kinematic structure
*   Topology of the environment

Examples:

```text
velocity ≤ vmax
robot_mass > 0
robot ∉ wall
joint_limits(q)
```

In MPC terms:

*   These are **hard constraints**
*   They must _never_ be violated
*   They define the **admissible state space**

🔑 **This layer must remain symbolic and non-learned**  
You do _not_ want a neural network deciding whether walls are solid.

* * *

### K₁ — RuleKnowledge → _Symbolic task & safety logic_

This layer expresses **logical structure on top of physics**:

Examples:

```text
if near(human) then reduce_speed
if carrying fragile_object then limit_acceleration
if blocked then replan
```

In MPC terms:

*   These become **state-dependent constraint switches**
*   Or **mode-dependent costs**
*   Or **hybrid MPC guards**

This is where:

*   task logic
*   safety policies
*   operational rules

live.

🔑 K₁ determines _how the optimization problem itself is constructed_.

* * *

### K₂ — ModelKnowledge → _Learned dynamics & costs_

This is the key connection.

K₂ corresponds to:

*   Learned dynamics models
*   Residual dynamics (Δf)
*   Learned contact models
*   Learned cost shaping
*   Uncertainty estimates

Examples:

```text
x_{t+1} = f_physics(x_t, u_t) + f_learned(x_t, u_t)
P(slip | surface, speed) = 0.3
```

This includes:

*   Gaussian Processes
*   Neural ODEs
*   Liquid neural networks
*   Ensemble models
*   World models

In MPC:

*   K₂ provides **predictive power**
*   But **never authority**

🔑 K₂ proposes what _might_ happen, not what _must_ happen.

* * *

### K₃ — EpisodicKnowledge → _Current belief state_

This corresponds to:

*   State estimate
*   Belief distribution
*   Map updates
*   Detected obstacles
*   Human positions
*   Hypotheses

Examples:

```text
x̂_t
human_at(h1, p)
surface = slippery
```

In MPC:

*   K₃ defines the **initial condition**
*   And the **current planning context**

🔑 K₃ changes every control cycle.

* * *

3\. Why Learned Dynamics Belong in K₂ (Not K₀ or K₁)
----------------------------------------------------

This is crucial.

### Why not K₀?

*   Learned dynamics are approximate
*   Can be wrong
*   Can violate physics
*   Must be bounded

Putting learned models into K₀ would make:

> physics _learned_ instead of _assumed_

This breaks safety guarantees.

* * *

### Why not K₁?

Rules assume **logical reliability**.

A neural network saying:

> “I think you’ll stop in 1.2 m”

is not a rule — it’s a **belief**.

Rules can _use_ learned outputs, but must not _be_ learned outputs.

* * *

4\. Hybrid MPC: How the Layers Interact
---------------------------------------

Here’s the **actual control loop**, layered explicitly:

```
(loop)
    K3 ← perception + state estimation

    K2 ← update learned models (optional, slower timescale)

    constraints ← K0 ∪ K1(K3)

    predictions ← K2(x̂_t, u)

    MPC:
        minimize cost(predictions)
        subject to constraints

    apply u_0
```

Key insight:

> **K₀ and K₁ define the feasible space; K₂ shapes the objective.**

This is the _safe_ way to use learning in MPC.

* * *

5\. Example: Mobile Robot with Learned Slip Dynamics
----------------------------------------------------

### Ontology (K₀)

```text
robot ∉ obstacle
|u| ≤ umax
```

### Rules (K₁)

```text
if surface = slippery then reduce_speed
```

### Learned Model (K₂)

```text
slip_ratio = NN(speed, surface, load)
```

### Episodic State (K₃)

```text
surface = wet
speed = 1.2
```

MPC result:

*   Hard constraint: no collision (K₀)
*   Speed cap lowered (K₁)
*   Cost penalizes predicted slip (K₂)
*   Optimized using current belief (K₃)

No layer is confused with another.

* * *

6\. Why This Architecture Is Becoming Standard
----------------------------------------------

You’ll see this pattern in:

*   **Safe RL + MPC**
*   **Residual MPC**
*   **Robust MPC with learned disturbances**
*   **World-model-based planning**
*   **Neural MPC with constraint envelopes**

Often under different names:

*   “shielded learning”
*   “constrained RL”
*   “hybrid planning”
*   “model-based RL with priors”

They are all rediscovering the same separation.

* * *

7\. Relation to Your Interest in Liquid Neural Networks
-------------------------------------------------------

Liquid NNs fit **perfectly** into K₂:

*   Continuous-time
*   Adaptive
*   Data-efficient
*   Uncertain
*   Differentiable

They are excellent:

*   residual dynamics models
*   contact estimators
*   uncertainty-aware predictors

But they must be:

*   bounded
*   monitored
*   constrained by K₀ and K₁

* * *

8\. The Deep Insight (The One That Matters)
-------------------------------------------

**MPC is already a logic engine.**

*   Constraints = ontology
*   Mode switches = rules
*   Dynamics = models
*   State = episodes

Making the layers explicit:

*   improves safety
*   improves explainability
*   improves learning stability
*   improves debuggability

* * *

9\. One-Sentence Summary
------------------------

**The K₀–K₃ architecture is the epistemic decomposition that makes learned dynamics usable inside MPC without sacrificing safety or correctness.**

* * *

