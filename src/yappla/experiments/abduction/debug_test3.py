"""Debug unification"""

from abduction03 import *

# Create atoms
fact = parse_atom("sick(alice)")
goal = parse_atom("sick(alice)")

print(f"Fact: {fact}")
print(f"Goal: {goal}")
print(f"Fact == Goal: {fact == goal}")
print(f"Fact repr: {repr(fact)}")
print(f"Goal repr: {repr(goal)}")

# Check unification
result = unify_atoms(goal, fact)
print(f"Unify result: {result}")

# Check KB facts
kb = KnowledgeBase()
kb.add_fact(fact)
print(f"\nFacts in KB: {kb.facts}")
print(f"Fact in set: {fact in kb.facts}")

# Check if we can find it
for f in kb.facts:
    print(f"Checking {f}")
    if unify_atoms(goal, f):
        print(f"  Unified!")
