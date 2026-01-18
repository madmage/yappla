"""Debug prove method with print statements"""

from abduction03 import *

# Create KB with fact
kb = KnowledgeBase()
kb.add_fact(parse_atom("sick(alice)"))

class DebugEngine(EntailmentEngine):
    def prove(self, kb: KnowledgeBase, goal: Atom, depth=0) -> bool:
        """Prove goal from knowledge base using SLD resolution"""
        print(f"{'  ' * depth}prove({goal}, depth={depth})")
        
        if depth > self.max_depth:
            print(f"{'  ' * depth}  -> depth exceeded")
            return False
        
        # Handle negation-as-failure
        if goal.negated:
            print(f"{'  ' * depth}  -> handling negation")
            return not self.prove(kb, goal.negate(), depth)
        
        # Check facts
        print(f"{'  ' * depth}  checking {len(kb.facts)} facts")
        for fact in kb.facts:
            print(f"{'  ' * depth}    fact: {fact}")
            result = unify_atoms(goal, fact)
            print(f"{'  ' * depth}      unify result: {result}")
            if result is not None:
                print(f"{'  ' * depth}  -> returning True (fact match)")
                return True
        
        # Check rules
        print(f"{'  ' * depth}  checking {len(kb.rules)} rules")
        for rule in kb.rules:
            subst = unify_atoms(goal, rule.head)
            print(f"{'  ' * depth}    rule: {rule}")
            print(f"{'  ' * depth}      unify result: {subst}")
            if subst is not None:
                # Prove all body literals
                body_goals = [lit.ground(subst) for lit in rule.body]
                if self.prove_all(kb, body_goals, depth + 1):
                    print(f"{'  ' * depth}  -> returning True (rule match)")
                    return True
        
        print(f"{'  ' * depth}  -> returning False (no match)")
        return False

engine = DebugEngine()

# Test proving simple fact
goal = parse_atom("sick(alice)")
print(f"Testing prove for: {goal}\n")
result = engine.prove(kb, goal)
print(f"\nResult: {result}")
