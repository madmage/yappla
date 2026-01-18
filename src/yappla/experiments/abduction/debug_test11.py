"""Debug Term construction"""

from abduction03 import Term, Atom, unify_atoms, parse_atom

# Test 1: Direct Term construction
t1 = Term('alice')
t2 = Term('alice')
print(f"t1 == t2: {t1 == t2}")
print(f"t1.is_variable: {t1.is_variable}")
print(f"t2.is_variable: {t2.is_variable}")

# Test 2: Atoms from parsed
fact = parse_atom("sick(alice)")
goal = parse_atom("sick(alice)")
print(f"\nfact == goal: {fact == goal}")
print(f"fact.terms[0]: {fact.terms[0]}")
print(f"goal.terms[0]: {goal.terms[0]}")
print(f"fact.terms[0] == goal.terms[0]: {fact.terms[0] == goal.terms[0]}")
print(f"fact.terms[0].is_variable: {fact.terms[0].is_variable}")
print(f"goal.terms[0].is_variable: {goal.terms[0].is_variable}")

# Test unification
result = unify_atoms(fact, goal)
print(f"\nunify_atoms(fact, goal): {result}")

# Test with Term created directly
fact2 = Atom('sick', (Term('alice'),))
goal2 = Atom('sick', (Term('alice'),))
result2 = unify_atoms(fact2, goal2)
print(f"unify_atoms(fact2, goal2): {result2}")
