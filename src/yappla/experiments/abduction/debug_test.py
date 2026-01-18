"""Debug script to understand why abduction is not working"""

from abduction03 import *

# Simple test case
kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("person(alice)"))

engine = EntailmentEngine()
abducer = AbductiveReasoner(kb, engine)
abducer.declare_abducible("sick", 1, cost=1.0)

# Debug: Check what constants are extracted
print("Constants in KB:", abducer._extract_constants())

# Test observation
obs = parse_atom("not_working(alice)")
print(f"\nObservation: {obs}")
print(f"Is ground: {obs.is_ground()}")
print(f"Predicate: {obs.predicate}, Arity: {obs.arity}")

# Check if observation is already provable
print(f"\nAlready provable from KB: {engine.prove(kb, obs)}")

# Get backward chained abducibles
relevant = abducer._backward_chain_abducibles(obs)
print(f"\nRelevant abducibles from backward chain: {relevant}")

# Check what _generate_candidate_abducibles returns
candidates = abducer._generate_candidate_abducibles({obs})
print(f"\nCandidate abducibles: {candidates}")

# Now test with the hypothesis
obs_sick = parse_atom("sick(alice)")
print(f"\n\nTesting hypothesis: {obs_sick}")
kb_augmented = abducer._augment_kb({obs_sick})
print(f"Can we prove not_working(alice) with hypothesis: {engine.prove(kb_augmented, obs)}")

# Test abduce
print("\n\n=== Testing abduce ===")
observations = [parse_atom("not_working(alice)")]
explanations = abducer.abduce(observations, strategy='greedy_coverage')
print(f"Explanations: {explanations}")
