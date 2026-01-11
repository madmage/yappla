from typing import Dict, List, Tuple, Optional
from logic_classes import Predicate, Rule


class KnowledgeBase:
    """In-memory database for storing facts and rules.
    
    In logic programming:
    - A Fact is a ground predicate that is unconditionally true (e.g., "parent(john, mary)")
    - A Rule is a conditional statement in the form "head :- body" where the head is true
      if all goals in the body are provable (e.g., "grandparent(X,Z) :- parent(X,Y), parent(Y,Z)")
    """
    
    def __init__(self):
        self.facts_by_predicate: Dict[str, List[Predicate]] = {}
        self.all_facts: List[Predicate] = []
        self.rules_by_predicate: Dict[str, List[Rule]] = {}
        self.all_rules: List[Rule] = []
        self.constraints: List = []  # Constraints for the knowledge base
    
    def add_fact(self, fact: Predicate) -> bool:
        """Add a fact to the database"""
        if fact in self.all_facts:
            return False
        
        self.all_facts.append(fact)
        
        if fact.name not in self.facts_by_predicate:
            self.facts_by_predicate[fact.name] = []
        
        self.facts_by_predicate[fact.name].append(fact)
        return True
    
    def add_rule(self, rule: Rule) -> bool:
        """Add a rule to the database"""
        self.all_rules.append(rule)
        
        if rule.head.name not in self.rules_by_predicate:
            self.rules_by_predicate[rule.head.name] = []
        
        self.rules_by_predicate[rule.head.name].append(rule)
        return True
    
    def add_constraint(self, constraint) -> bool:
        """Add a constraint to the knowledge base"""
        self.constraints.append(constraint)
        return True
    
    def get_facts(self, predicate: Optional[str] = None) -> List[Predicate]:
        """Get all facts, or facts matching a specific predicate"""
        if predicate is None:
            return self.all_facts.copy()
        return self.facts_by_predicate.get(predicate, []).copy()
    
    def get_rules(self, predicate: Optional[str] = None) -> List[Rule]:
        """Get all rules, or rules matching a specific predicate"""
        if predicate is None:
            return self.all_rules.copy()
        return self.rules_by_predicate.get(predicate, []).copy()
    
    def clear(self):
        """Clear all facts and rules from the database"""
        self.facts_by_predicate.clear()
        self.all_facts.clear()
        self.rules_by_predicate.clear()
        self.all_rules.clear()
        self.constraints.clear()
    
    def count(self) -> Tuple[int, int]:
        """Return the number of facts and rules in the database"""
        return len(self.all_facts), len(self.all_rules)