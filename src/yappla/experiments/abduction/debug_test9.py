"""Debug prove with detailed tracing"""

from abduction03 import *

kb = KnowledgeBase()
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))
kb.add_fact(parse_atom("person(alice)"))
kb.add_fact(parse_atom("sick(alice)"))

class DebugEngine(EntailmentEngine):
    def prove(self, kb: KnowledgeBase, goal: Atom, depth=0) -> bool:
        """Prove goal from knowledge base using SLD resolution"""
        indent = '  ' * depth
        print(f"{indent}prove({goal}, depth={depth})")
        
        if depth > self.max_depth:
            print(f"{indent}  -> FAIL: max_depth exceeded")
            return False
        
        # Handle negation-as-failure
        if goal.negated:
            print(f"{indent}  -> handling negation")
            result = not self.prove(kb, goal.negate(), depth)
            print(f"{indent}  -> negation result: {result}")
            return result
        
        # Check facts
        print(f"{indent}  checking {len(kb.facts)} facts")
        for fact in kb.facts:
            unif = unify_atoms(goal, fact)
            if unif is not None:
                print(f"{indent}    FACT MATCH: {fact}")
                return True
        
        # Check rules
        print(f"{indent}  checking {len(kb.rules)} rules")
        for rule in kb.rules:
            subst = unify_atoms(goal, rule.head)
            if subst is not None:
                print(f"{indent}    RULE MATCH: {rule}")
                # Prove all body literals
                body_goals = [lit.ground(subst) for lit in rule.body]
                print(f"{indent}      body goals: {body_goals}")
                if self.prove_all(kb, body_goals, depth + 1):
                    print(f"{indent}    -> RULE PROVED")
                    return True
        
        print(f"{indent}  -> FAIL: no match")
        return False

engine = DebugEngine()

goal = parse_atom("not_working(alice)")
print(f"Testing prove for: {goal}\n")
result = engine.prove(kb, goal)
print(f"\nFinal result: {result}")
