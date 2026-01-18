"""Test with the actual engine directly"""

from abduction03 import EntailmentEngine, KnowledgeBase, parse_atom, parse_rule

kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("sick(alice)"))

engine = EntailmentEngine()
goal = parse_atom("not_working(alice)")

print(f"Goal: {goal}")
print(f"Facts: {kb.facts}")
print(f"Rules: {kb.rules}")

result = engine.prove(kb, goal)
print(f"\nProve result: {result}")

# Also test simple fact
result2 = engine.prove(kb, parse_atom("sick(alice)"))
print(f"Prove sick(alice): {result2}")
