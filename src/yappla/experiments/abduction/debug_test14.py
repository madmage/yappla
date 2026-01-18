"""Test with explicit implementation"""

from abduction03 import KnowledgeBase, Atom, Term, parse_atom, parse_rule, unify_atoms
from typing import List

class TestEngine:
    def __init__(self, max_depth=50):
        self.max_depth = max_depth
    
    def prove(self, kb: KnowledgeBase, goal: Atom, depth=0) -> bool:
        """Prove goal from knowledge base using SLD resolution"""
        print(f"{'  ' * depth}prove({goal})")
        if depth > self.max_depth:
            print(f"{'  ' * depth}  -> depth exceeded")
            return False
        
        # Handle negation-as-failure
        if goal.negated:
            print(f"{'  ' * depth}  -> negation")
            return not self.prove(kb, goal.negate(), depth)
        
        # Check facts
        print(f"{'  ' * depth}  facts: {kb.facts}")
        for fact in kb.facts:
            print(f"{'  ' * depth}    checking {fact}")
            if unify_atoms(goal, fact):
                print(f"{'  ' * depth}    -> UNIFIED")
                return True
        
        # Check rules
        print(f"{'  ' * depth}  rules: {kb.rules}")
        for rule in kb.rules:
            subst = unify_atoms(goal, rule.head)
            if subst is not None:
                # Prove all body literals
                body_goals = [lit.ground(subst) for lit in rule.body]
                if self.prove_all(kb, body_goals, depth + 1):
                    return True
        
        return False
    
    def prove_all(self, kb: KnowledgeBase, goals: List[Atom], depth=0) -> bool:
        """Prove all goals"""
        if not goals:
            return True
        return all(self.prove(kb, goal, depth) for goal in goals)

kb = KnowledgeBase()
kb.add_fact(parse_atom("sick(alice)"))
kb.add_rule(parse_rule("not_working(X) :- sick(X)"))

engine = TestEngine()
print("Test 1: Direct fact")
result = engine.prove(kb, parse_atom("sick(alice)"))
print(f"Result: {result}\n")

print("Test 2: Via rule")
result = engine.prove(kb, parse_atom("not_working(alice)"))
print(f"Result: {result}")
