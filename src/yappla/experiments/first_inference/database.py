from typing import Dict, List, Tuple, Optional
from terms import Fact, Rule


class FactDatabase:
    """In-memory database for storing facts and rules"""
    
    def __init__(self):
        self.facts_by_predicate: Dict[str, List[Fact]] = {}
        self.all_facts: List[Fact] = []
        self.rules_by_predicate: Dict[str, List[Rule]] = {}
        self.all_rules: List[Rule] = []
    
    def add_fact(self, fact: Fact) -> bool:
        """Add a fact to the database"""
        if fact in self.all_facts:
            return False
        
        self.all_facts.append(fact)
        
        if fact.predicate not in self.facts_by_predicate:
            self.facts_by_predicate[fact.predicate] = []
        
        self.facts_by_predicate[fact.predicate].append(fact)
        return True
    
    def add_rule(self, rule: Rule) -> bool:
        """Add a rule to the database"""
        self.all_rules.append(rule)
        
        if rule.head.predicate not in self.rules_by_predicate:
            self.rules_by_predicate[rule.head.predicate] = []
        
        self.rules_by_predicate[rule.head.predicate].append(rule)
        return True
    
    def get_facts(self, predicate: Optional[str] = None) -> List[Fact]:
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
    
    def count(self) -> Tuple[int, int]:
        """Return the number of facts and rules in the database"""
        return len(self.all_facts), len(self.all_rules)