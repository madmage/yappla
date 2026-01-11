from typing import List, Optional, Dict, Any
from copy import deepcopy
from logic_classes import Predicate, Rule, Variable
from substitution import Substitution, Unifier
from knowledge_base import KnowledgeBase
from constraints import DomainConstraint, NotEqualConstraint


class InferenceEngine:
    """Handles queries and inference"""
    
    def __init__(self, db: 'KnowledgeBase'):
        self.db = db
        self.query_counter = 0
    
    def query(self, goal: Predicate, depth: int = 0, max_depth: int = 100, domains: Optional[Dict[str, Any]] = None) -> List[Substitution]:
        """
        Query the knowledge base for predicates matching the goal.
        Returns a list of substitutions that satisfy the goal.
        Supports constraint propagation via domain tracking.
        """
        if depth > max_depth:
            return []
        
        if domains is None:
            domains = {}
        
        results = []
        
        # Try to match against facts
        for fact in self.db.get_facts(goal.name):
            subst = Unifier.unify(goal, fact, Substitution())
            if subst is not None:
                # Assign variables in domains
                local_domains = deepcopy(domains)
                valid = True
                for v, val in subst.bindings.items():
                    if v not in local_domains:
                        local_domains[v] = {val}
                    else:
                        local_domains[v] &= {val}
                        if not local_domains[v]:
                            valid = False
                            break
                
                if valid and self._propagate_constraints(self.db.constraints, local_domains):
                    results.append(subst)
        
        # Try to match against rules
        for rule in self.db.get_rules(goal.name):
            # Rename variables in the rule to avoid conflicts
            renamed_rule = self._rename_rule_variables(rule)
            
            # Try to unify goal with rule head
            subst = Unifier.unify(goal, renamed_rule.head, Substitution())
            if subst is not None:
                # Set up domains from head unification
                local_domains = deepcopy(domains)
                valid = True
                for v, val in subst.bindings.items():
                    if v not in local_domains:
                        local_domains[v] = {val}
                    else:
                        local_domains[v] &= {val}
                        if not local_domains[v]:
                            valid = False
                            break
                
                if valid:
                    # Try to prove all subgoals in the body
                    body_results = self._prove_all(renamed_rule.body, subst, depth + 1, max_depth, local_domains)
                    results.extend(body_results)
        
        return results
    
    def _prove_all(self, goals: List[Predicate], subst: Substitution, depth: int, max_depth: int, domains: Optional[Dict[str, Any]] = None) -> List[Substitution]:
        """Prove all goals in a list"""
        if domains is None:
            domains = {}
        
        if not goals:
            return [subst]
        
        # Apply current substitution to first goal
        first_goal = subst.apply(goals[0])
        remaining_goals = goals[1:]
        
        results = []
        
        # Handle constraints specially
        if isinstance(first_goal, (DomainConstraint, NotEqualConstraint)):
            local_domains = deepcopy(domains)
            if first_goal.propagate(local_domains):
                # Constraint satisfied, continue with remaining goals
                results.extend(self._prove_all(remaining_goals, subst, depth, max_depth, local_domains))
        else:
            # Regular predicate - query it
            for goal_subst in self.query(first_goal, depth, max_depth, domains):
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
                results.extend(self._prove_all(remaining_goals, merged, depth, max_depth, domains))
        
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
            elif isinstance(term, DomainConstraint):
                # Rename the variable reference in the constraint
                renamed_var = var_mapping.get(term.var, term.var)
                if isinstance(renamed_var, Variable):
                    renamed_var = renamed_var.name
                return DomainConstraint(renamed_var, term.values)
            elif isinstance(term, NotEqualConstraint):
                # Rename variable references in the constraint
                renamed_x = var_mapping.get(term.x, term.x)
                renamed_y = var_mapping.get(term.y, term.y)
                if isinstance(renamed_x, Variable):
                    renamed_x = renamed_x.name
                if isinstance(renamed_y, Variable):
                    renamed_y = renamed_y.name
                return NotEqualConstraint(renamed_x, renamed_y)
            else:
                return term
        
        new_head = rename_term(rule.head)
        new_body = [rename_term(fact) for fact in rule.body]
        
        return Rule(new_head, new_body)
    
    def _propagate_constraints(self, constraints: List, domains: Dict[str, Any]) -> bool:
        """Propagate all constraints over domains"""
        for c in constraints:
            if isinstance(c, (DomainConstraint, NotEqualConstraint)):
                if not c.propagate(domains):
                    return False
        return True