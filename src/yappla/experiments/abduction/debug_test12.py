"""Instrument the actual prove method"""

from abduction03 import EntailmentEngine, KnowledgeBase, Term, Atom, parse_atom, parse_rule, unify_atoms
from typing import List

# Monkey-patch the prove method
original_prove = EntailmentEngine.prove

call_count = [0]

def instrumented_prove(self, kb: KnowledgeBase, goal: Atom, depth=0) -> bool:
    call_count[0] += 1
    call_id = call_count[0]
    indent = '  ' * depth
    print(f"{indent}[{call_id}] prove({goal}, depth={depth})")
    
    if depth > self.max_depth:
        print(f"{indent}[{call_id}]  -> False (depth exceeded)")
        return False
    
    # Handle negation-as-failure
    if goal.negated:
        print(f"{indent}[{call_id}]  -> handling negation")
        result = not self.prove(kb, goal.negate(), depth)
        print(f"{indent}[{call_id}]  -> negation returns {result}")
        return result
    
    # Check facts
    print(f"{indent}[{call_id}]  checking {len(kb.facts)} facts")
    for fact in kb.facts:
        print(f"{indent}[{call_id}]    checking fact {fact}")
        result = unify_atoms(goal, fact)
        print(f"{indent}[{call_id}]      unify result: {result}")
        if result:
            print(f"{indent}[{call_id}]  -> True (fact match)")
            return True
    
    # Check rules
    print(f"{indent}[{call_id}]  checking {len(kb.rules)} rules")
    for rule in kb.rules:
        print(f"{indent}[{call_id}]    checking rule {rule}")
        subst = unify_atoms(goal, rule.head)
        print(f"{indent}[{call_id}]      unify result: {subst}")
        if subst is not None:
            # Prove all body literals
            body_goals = [lit.ground(subst) for lit in rule.body]
            print(f"{indent}[{call_id}]      body goals: {body_goals}")
            if self.prove_all(kb, body_goals, depth + 1):
                print(f"{indent}[{call_id}]  -> True (rule match)")
                return True
    
    print(f"{indent}[{call_id}]  -> False (no match)")
    return False

EntailmentEngine.prove = instrumented_prove

# Now test
kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("sick(alice)"))

engine = EntailmentEngine()
goal = parse_atom("sick(alice)")

print(f"Testing: {goal}\n")
result = engine.prove(kb, goal)
print(f"\nResult: {result}")
