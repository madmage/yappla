"""Debug prove method step by step"""

from abduction03 import *

# Create KB with fact
kb = KnowledgeBase()
kb.add_fact(parse_atom("sick(alice)"))

engine = EntailmentEngine()

# Test proving simple fact
goal = parse_atom("sick(alice)")
print(f"Testing prove for: {goal}")
print(f"Facts in KB: {kb.facts}")

# Step through prove logic manually
# Check facts
for fact in kb.facts:
    print(f"Checking fact: {fact}")
    result = unify_atoms(goal, fact)
    print(f"  Unification result: {result}")
    if result is not None:
        print(f"  Would return True")

# Now actually call prove
result = engine.prove(kb, goal)
print(f"\nActual prove result: {result}")

# Test prove_all
print("\n\nTesting prove_all:")
results = engine.prove_all(kb, [goal])
print(f"prove_all result: {results}")
