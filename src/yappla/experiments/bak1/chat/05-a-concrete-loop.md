3\. A Concrete Abductive–Temporal–Spatial Reasoning Loop
========================================================

This is the **operational heart** of the system.

* * *

3.1 Why abduction is central
----------------------------

In robotics, you mostly observe _effects_, not causes:

*   Unexpected collisions
*   Failed grasps
*   Sensor discrepancies

Deduction alone is useless here.

* * *

3.2 The loop (high-level)
-------------------------

```
Sense
 ↓
Symbol grounding (neural)
 ↓
Abduction (what could explain this?)
 ↓
Logical consistency check
 ↓
Temporal update
 ↓
Planning / control
```

* * *

3.3 Step-by-step detail
-----------------------

### Step 1: Sense → Symbol grounding

Neural models produce:

```
near(robot, pallet) : 0.83
occluded(camera, pallet) : 0.61
```

These are **not truths**.

* * *

### Step 2: Candidate fact proposal

Convert scores to **hypotheses**:

```
hypothesis(rcc8(overlapping, robot, pallet))
hypothesis(sensor_fault(camera))
```

* * *

### Step 3: Abduction

Given observations and domain rules:

```
collision :- overlapping(robot, pallet).
collision :- sensor_fault(camera).
```

Abduction produces:

*   Multiple explanations
*   Partial explanations
*   Ranked explanations

* * *

### Step 4: Logical filtering

Each explanation:

*   Is tested against the kernel
*   Spatial constraints propagated
*   Inconsistent explanations discarded

This step is _hard and binary_.

* * *

### Step 5: Temporal update

Accepted explanations:

*   Update belief state
*   Affect future hypotheses
*   Decay over time

* * *

### Step 6: Decision

Best explanation → control policy → MPC

* * *

3.4 Why this loop works
-----------------------

*   Search space is pruned early
*   Logic enforces structure
*   Probability ranks, not decides
*   Learning feeds hypotheses, not truth

