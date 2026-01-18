"""Debug Issue 3: Negation handling for 'not flies(opus)'"""

from abduction03 import *

kb = KnowledgeBase()
kb.add_rule(parse_rule("flies(X) :- bird(X), not abnormal(X)"))
kb.add_rule(parse_rule("has_feathers(X) :- bird(X)"))

engine = EntailmentEngine()
abducer = AbductiveReasoner(kb, engine)
abducer.declare_abducible("bird", 1)
abducer.declare_abducible("abnormal", 1)

# Test 1: Can we prove flies(opus)?
print("Test 1: Prove flies(opus) with bird(opus) but no abnormal(opus)")
kb_test1 = KnowledgeBase()
kb_test1.add_fact(parse_atom("bird(opus)"))
kb_test1.add_rule(parse_rule("flies(X) :- bird(X), not abnormal(X)"))

result = engine.prove(kb_test1, parse_atom("flies(opus)"))
print(f"  Result: {result}")
print(f"  Reason: bird(opus) is true, abnormal(opus) is false, so flies(opus) is true")

# Test 2: Can we prove not flies(opus)?
print("\nTest 2: Prove not flies(opus) with bird(opus) but no abnormal(opus)")
result = engine.prove(kb_test1, parse_atom("not flies(opus)"))
print(f"  Result: {result}")

# Test 3: Can we prove not flies(opus) with bird(opus) AND abnormal(opus)?
print("\nTest 3: Prove not flies(opus) with bird(opus) AND abnormal(opus)")
kb_test3 = KnowledgeBase()
kb_test3.add_fact(parse_atom("bird(opus)"))
kb_test3.add_fact(parse_atom("abnormal(opus)"))
kb_test3.add_rule(parse_rule("flies(X) :- bird(X), not abnormal(X)"))

result = engine.prove(kb_test3, parse_atom("not flies(opus)"))
print(f"  Result: {result}")
print(f"  Reason: bird(opus) is true, abnormal(opus) is true")
print(f"          So 'not abnormal(opus)' is false")
print(f"          So flies(opus) is false (body fails)")
print(f"          So not flies(opus) is true")

# Test 4: Check what hypotheses are generated for the observation
print("\nTest 4: Abduce for observations: has_feathers(opus), not flies(opus)")
observations = [
    parse_atom("has_feathers(opus)"),
    parse_atom("not flies(opus)")
]

print(f"Observations: {observations}")

# Check which are unexplained
unexplained = abducer._filter_unexplained(set(observations))
print(f"Unexplained: {unexplained}")

# Get candidates
if unexplained:
    candidates = abducer._generate_candidate_abducibles(unexplained)
    print(f"Candidates: {candidates}")
    
    # Check coverage with just bird
    hyp1 = {parse_atom("bird(opus)")}
    coverage1 = abducer._compute_coverage(hyp1, set(unexplained))
    print(f"\nWith {hyp1}: covers {coverage1}")
    
    # Check coverage with bird + abnormal
    hyp2 = {parse_atom("bird(opus)"), parse_atom("abnormal(opus)")}
    coverage2 = abducer._compute_coverage(hyp2, set(unexplained))
    print(f"With {hyp2}: covers {coverage2}")
