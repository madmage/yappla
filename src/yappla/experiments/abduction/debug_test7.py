"""Trace _compute_coverage"""

from abduction03 import *

kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("person(alice)"))

engine = EntailmentEngine()
abducer = AbductiveReasoner(kb, engine)
abducer.declare_abducible("sick", 1, cost=1.0)

hypothesis = {parse_atom("sick(alice)")}
observations = {parse_atom("not_working(alice)")}

print(f"Hypothesis: {hypothesis}")
print(f"Observations: {observations}")

# Manually trace _compute_coverage
augmented_kb = abducer._augment_kb(hypothesis)
print(f"\nAugmented KB facts: {augmented_kb.facts}")
print(f"Augmented KB rules: {[str(r) for r in augmented_kb.rules]}")

covered = set()
for obs in observations:
    print(f"\nChecking observation: {obs}")
    
    # Try to prove it
    result = abducer._prove_cached(augmented_kb, obs, frozenset(hypothesis))
    print(f"  _prove_cached result: {result}")
    
    # Try direct prove
    result2 = engine.prove(augmented_kb, obs)
    print(f"  engine.prove result: {result2}")
    
    if result:
        covered.add(obs)

print(f"\nCovered: {covered}")

# Now try using _compute_coverage
coverage = abducer._compute_coverage(hypothesis, observations)
print(f"\n_compute_coverage result: {coverage}")
