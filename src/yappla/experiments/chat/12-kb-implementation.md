Below is a **refactored, documented version** of the previous prototype where:

*   `K0–K3` are given **semantically meaningful names**
*   Each knowledge layer is **explicitly documented** with:
    *   what it represents
    *   when it is updated
    *   whether it is mutable
    *   what kind of reasoning depends on it
*   The **architecture you described** is made explicit in code comments and docstrings

This is meant to be **readable by future maintainers**, not just executable.

* * *

Knowledge Layer Naming
======================

We rename the layers as follows:

| Old | New name | Meaning |
| --- | --- | --- |
| K₀ | `OntologyKnowledge` | Timeless domain truths and invariants |
| K₁ | `RuleKnowledge` | Structural/domain rules (derivation patterns) |
| K₂ | _(not yet implemented)_ | Learned / probabilistic models |
| K₃ | `EpisodicKnowledge` | Time-indexed, contingent facts |

* * *

1\. Core Term Imports
=====================

```python
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional
```

* * *

2\. OntologyKnowledge (formerly K₀)
===================================

```python
@dataclass(frozen=True)
class OntologyKnowledge:
    """
    OntologyKnowledge represents *timeless, invariant domain knowledge*.

    This includes:
    - Ontological declarations (types, predicates, symbols)
    - Hard invariants and integrity constraints
    - Facts that are assumed to be always true in the domain

    Characteristics:
    ----------------
    - Immutable after system initialization
    - Shared across all reasoning episodes
    - Used to:
        * reject inconsistent worlds
        * answer unconditional entailment queries
        * constrain learning and abduction

    Typical contents:
    -----------------
    - type(robot)
    - forbidden(holding(robot,human))
    - asymmetric(left_of)

    Update policy:
    --------------
    - Loaded at system startup
    - Updated ONLY by explicit ontology migration
    - Never modified during normal inference or learning
    """

    ontology: Set[str]
    invariants: Set[str]

    def entails(self, fact: str) -> bool:
        """
        Check whether a fact is entailed purely by domain invariants.
        """
        return fact in self.invariants
```

* * *

3\. RuleKnowledge (formerly K₁)
===============================

```python
@dataclass
class Rule:
    """
    A simple Horn-style rule:
        head :- body_1, body_2, ...
    """
    head: str
    body: List[str]

@dataclass
class RuleKnowledge:
    """
    RuleKnowledge encodes *structural and causal regularities* of the domain.

    This layer represents:
    - Logical implications
    - Causal templates
    - Deductive patterns independent of time

    Characteristics:
    ----------------
    - Mutable, but updated infrequently
    - Rules are assumed to be globally valid
    - Used primarily for:
        * deduction (ENTAIL)
        * explanation generation
        * abduction templates

    Typical contents:
    -----------------
    - collision :- overlapping(X,Y)
    - blocked(R) :- overlapping(R, obstacle)
    - unsafe(R) :- near(R, human), moving(R)

    Update policy:
    --------------
    - Loaded at startup
    - Can be extended by:
        * human experts
        * rule induction systems
        * offline learning
    - NOT updated automatically during normal inference
    """

    rules: List[Rule]
```

* * *

4\. EpisodicKnowledge (formerly K₃)
===================================

```python
@dataclass
class EpisodicKnowledge:
    """
    EpisodicKnowledge represents *contingent, time-indexed facts* about the world.

    This is the system's "working memory":
    - Observations
    - Sensor readings
    - Events
    - Hypotheses under consideration

    Characteristics:
    ----------------
    - Highly mutable
    - Indexed by discrete or logical time
    - Facts may be:
        * added
        * revised
        * forgotten

    Typical contents:
    -----------------
    t=42:
        overlapping(r1,p1)
        moving(r1)
    t=43:
        stopped(r1)

    Update policy:
    --------------
    - Updated continuously during execution
    - Can be modified by:
        * perception
        * planners
        * abductive hypotheses
        * learning feedback
    - Subject to revision, decay, and contradiction handling
    """

    facts_by_time: Dict[int, Set[str]] = field(default_factory=dict)

    def add_fact(self, fact: str, time: int):
        """Add a new episodic fact at a given time."""
        self.facts_by_time.setdefault(time, set()).add(fact)

    def get_facts(self, time: Optional[int] = None) -> Set[str]:
        """
        Retrieve facts.

        If time is None:
            returns the union of all episodic facts.
        If time is specified:
            returns facts true at that time.
        """
        if time is None:
            result = set()
            for fs in self.facts_by_time.values():
                result |= fs
            return result
        return self.facts_by_time.get(time, set())
```

* * *

5\. Logic Engine (Uses All Layers)
==================================

```python
class LogicEngine:
    """
    The LogicEngine orchestrates reasoning across knowledge layers.

    Responsibilities:
    -----------------
    - Route queries to appropriate knowledge layers
    - Combine invariant, structural, and episodic knowledge
    - Provide a clean API for higher-level agents or LLMs

    NOTE:
    -----
    This engine currently supports *basic entailment only*.
    It is intentionally conservative and extensible.
    """

    def __init__(
        self,
        ontology: OntologyKnowledge,
        rules: RuleKnowledge,
        episodic: EpisodicKnowledge
    ):
        self.ontology = ontology
        self.rules = rules
        self.episodic = episodic

    def entails(self, fact: str, time: Optional[int] = None) -> bool:
        """
        Determine whether a fact is entailed at a given time.

        Entailment sources (in order):
        1. Ontological invariants
        2. Explicit episodic facts
        3. One-step rule-based derivation
        """

        # 1. Ontology / invariants
        if self.ontology.entails(fact):
            return True

        # 2. Episodic memory
        known = self.episodic.get_facts(time)
        if fact in known:
            return True

        # 3. Rule-based deduction
        for rule in self.rules.rules:
            if rule.head == fact:
                if all(b in known for b in rule.body):
                    return True

        return False
```

* * *

6\. Why This Naming Matters
===========================

This naming enforces **conceptual discipline**:

*   `OntologyKnowledge`  
    → _What cannot change_
*   `RuleKnowledge`  
    → _How things usually follow_
*   `EpisodicKnowledge`  
    → _What happened / might have happened_

This mirrors:

*   knowledge representation theory
*   cognitive architectures
*   robotics world models
*   hybrid neuro-symbolic systems

* * *

7\. What We Have Not Yet Implemented (By Design)
================================================

*   Contradiction management
*   Abduction / explanation
*   Temporal operators
*   Probabilistic confidence
*   Neural-symbolic bridges

But the **scaffolding is now correct**.

