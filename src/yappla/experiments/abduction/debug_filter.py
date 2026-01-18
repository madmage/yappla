"""Debug _filter_unexplained"""

from abduction03 import *

kb = KnowledgeBase()
kb.add_rule(parse_rule("flies(X) :- bird(X), not abnormal(X)"))
kb.add_rule(parse_rule("has_feathers(X) :- bird(X)"))

engine = EntailmentEngine()
abducer = AbductiveReasoner(kb, engine)
abducer.declare_abducible("bird", 1)
abducer.declare_abducible("abnormal", 1)

# Check what _filter_unexplained does
obs_set = {
    parse_atom("has_feathers(opus)"),
    parse_atom("not flies(opus)")
}

print(f"Observations: {obs_set}")

for obs in obs_set:
    print(f"\nChecking: {obs}")
    # Check if already provable from KB
    result = abducer._prove_cached(kb, obs, frozenset())
    print(f"  Already provable from KB: {result}")
    
    # Manually prove
    result2 = engine.prove(kb, obs)
    print(f"  engine.prove: {result2}")
