"""Debug engine.prove with augmented KB"""

from abduction03 import *

kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("person(alice)"))
kb.add_fact(parse_atom("sick(alice)"))

engine = EntailmentEngine()

goal = parse_atom("not_working(alice)")
print(f"Goal: {goal}")
print(f"KB facts: {kb.facts}")
print(f"KB rules: {[str(r) for r in kb.rules]}")

print(f"\n=== Proving ===")
# Step through manually
print(f"\nCheck facts for {goal}")
for fact in kb.facts:
    print(f"  Checking {fact}")
    result = unify_atoms(goal, fact)
    print(f"    Unify result: {result}")

print(f"\nCheck rules for {goal}")
for rule in kb.rules:
    print(f"  Checking rule: {rule}")
    subst = unify_atoms(goal, rule.head)
    print(f"    Head unify result: {subst}")
    if subst is not None:
        body_goals = [lit.ground(subst) for lit in rule.body]
        print(f"    Body goals after grounding: {body_goals}")
        
        # Check if body can be proven
        print(f"    Proving body goals...")
        for bg in body_goals:
            can_prove = engine.prove(kb, bg)
            print(f"      Can prove {bg}: {can_prove}")

result = engine.prove(kb, goal)
print(f"\nFinal result: {result}")
