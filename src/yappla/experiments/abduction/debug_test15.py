"""Check what unify_atoms returns"""

from abduction03 import parse_atom, unify_atoms

fact = parse_atom("sick(alice)")
goal = parse_atom("sick(alice)")

result = unify_atoms(goal, fact)
print(f"unify_atoms result: {result}")
print(f"type: {type(result)}")
print(f"bool(result): {bool(result)}")
print(f"result is not None: {result is not None}")

if result:
    print("if result: TRUE")
else:
    print("if result: FALSE")

# Try with variables
goal2 = parse_atom("sick(X)")
result2 = unify_atoms(goal2, fact)
print(f"\nunify_atoms(sick(X), sick(alice)): {result2}")
print(f"bool(result2): {bool(result2)}")
