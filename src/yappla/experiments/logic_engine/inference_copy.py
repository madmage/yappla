from typing import List, Optional
from logic_classes import Predicate, Rule, Variable
from substitution import Substitution, Unifier
from knowledge_base import KnowledgeBase


class InferenceEngine:
    """Handles queries and inference"""
    
    def __init__(self, db: 'KnowledgeBase'):
        self.db = db
        self.query_counter = 0
    
    def query(self, goal: Predicate, depth: int = 0, max_depth: int = 100) -> List[Substitution]:
        """
        Query the knowledge base for predicates matching the goal.
        Returns a list of substitutions that satisfy the goal.
        """
        if depth > max_depth:
            return []
        
        results = []
        
        # Try to match against facts
        for fact in self.db.get_facts(goal.name):
            subst = Unifier.unify(goal, fact, Substitution())
            if subst is not None:
                results.append(subst)
        
        # Try to match against rules
        for rule in self.db.get_rules(goal.name):
            # Rename variables in the rule to avoid conflicts
            renamed_rule = self._rename_rule_variables(rule)
            
            # Try to unify goal with rule head
            subst = Unifier.unify(goal, renamed_rule.head, Substitution())
            if subst is not None:
                # Try to prove all subgoals in the body
                body_results = self._prove_all(renamed_rule.body, subst, depth + 1, max_depth)
                results.extend(body_results)
        
        return results
    
    def _prove_all(self, goals: List[Predicate], subst: Substitution, depth: int, max_depth: int) -> List[Substitution]:
        """Prove all goals in a list"""
        if not goals:
            return [subst]
        
        # Apply current substitution to first goal
        first_goal = subst.apply(goals[0])
        remaining_goals = goals[1:]
        
        results = []
        for goal_subst in self.query(first_goal, depth, max_depth):
            # Merge the substitutions: start with existing, add new bindings
            merged_bindings = {}
            
            # First, add all existing bindings
            for var, val in subst.bindings.items():
                merged_bindings[var] = val
            
            # Then add new bindings from the goal proof
            for var, val in goal_subst.bindings.items():
                if var not in merged_bindings:
                    merged_bindings[var] = val
                # If variable already bound, we need to unify the values
                else:
                    # This shouldn't happen in well-formed queries, but handle it
                    unified = Unifier.unify(merged_bindings[var], val, Substitution())
                    if unified is None:
                        continue  # Skip this solution, incompatible bindings
                    # Apply any additional bindings from unification
                    for uvar, uval in unified.bindings.items():
                        merged_bindings[uvar] = uval
            
            merged = Substitution(merged_bindings)
            
            # Prove remaining goals with merged substitution
            results.extend(self._prove_all(remaining_goals, merged, depth, max_depth))
        
        return results
    
    def _rename_rule_variables(self, rule: Rule) -> Rule:
        """Rename variables in a rule to avoid conflicts"""
        self.query_counter += 1
        suffix = f"_{self.query_counter}"
        
        var_mapping = {}
        
        def rename_term(term):
            if isinstance(term, Variable):
                if term.name not in var_mapping:
                    var_mapping[term.name] = Variable(term.name + suffix)
                return var_mapping[term.name]
            elif isinstance(term, Predicate):
                new_args = [rename_term(arg) for arg in term.arguments]
                return Predicate(term.name, new_args)
            else:
                return term
        
        new_head = rename_term(rule.head)
        new_body = [rename_term(fact) for fact in rule.body]
        
        return Rule(new_head, new_body)