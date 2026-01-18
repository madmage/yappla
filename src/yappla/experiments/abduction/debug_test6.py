"""Detailed trace of abduce method"""

from abduction03 import *

kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("person(alice)"))

engine = EntailmentEngine()
abducer = AbductiveReasoner(kb, engine)
abducer.declare_abducible("sick", 1, cost=1.0)

obs = parse_atom("not_working(alice)")
print(f"Observation: {obs}")

# Step 1: Check if already provable
print(f"\nStep 1: Check if observation is already provable")
is_provable = abducer._prove_cached(kb, obs, frozenset())
print(f"  Already provable: {is_provable}")

# Step 2: Filter unexplained
print(f"\nStep 2: Filter unexplained")
observations_set = {obs}
unexplained = abducer._filter_unexplained(observations_set)
print(f"  Unexplained: {unexplained}")

if unexplained:
    # Step 3: Generate candidates
    print(f"\nStep 3: Generate candidates")
    candidates = abducer._generate_candidate_abducibles(unexplained)
    print(f"  Candidates: {candidates}")
    
    # Step 4: For each candidate, check coverage
    print(f"\nStep 4: Check coverage for each candidate")
    for abd in list(candidates)[:3]:  # Just show first 3
        hypothesis = {abd}
        coverage = abducer._compute_coverage(hypothesis, unexplained)
        print(f"  Hypothesis: {abd}")
        print(f"    Coverage: {coverage}")
        
        # Check augmented KB
        augmented = abducer._augment_kb(hypothesis)
        can_prove = abducer.engine.prove(augmented, obs)
        print(f"    Can prove with augmented KB: {can_prove}")
