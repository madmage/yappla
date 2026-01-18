"""Further debugging of the proof engine"""

from abduction03 import *

# Simple test case
kb = KnowledgeBase()
rule = parse_rule("not_working(X) :- sick(X)")
kb.add_rule(rule)
kb.add_fact(parse_atom("sick(alice)"))

engine = EntailmentEngine()

# Test proving
goal = parse_atom("not_working(alice)")
print(f"Goal: {goal}")
print(f"Rule: {rule}")

# Check unification
subst = unify_atoms(goal, rule.head)
print(f"\nUnification of goal with rule head: {subst}")

# Check if body can be proven
if subst:
    body_ground = [b.ground(subst) for b in rule.body]
    print(f"Body after grounding: {body_ground}")
    
    # Check if body literal can be proven
    for lit in body_ground:
        print(f"  Can prove {lit}: {engine.prove(kb, lit)}")

# Now test full prove
result = engine.prove(kb, goal)
print(f"\nCan prove {goal}: {result}")
