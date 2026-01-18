from typing import List, Optional, Dict, Any
from copy import deepcopy
from core import Atom, Rule, Variable
from substitution import Substitution, Unifier
from knowledge_base import KnowledgeBase
from constraints import DomainConstraint, NotEqualConstraint


class EntailmentEngine:
    """Handles queries and inference for entailment checking"""
    
    def __init__(self, db: 'KnowledgeBase'):
        self.db = db
        self.query_counter = 0
    
    def query(self, goal, depth: int = 0, max_depth: int = 100, domains: Optional[Dict[str, Any]] = None) -> List[Substitution]:
        """
        Query the knowledge base for atoms matching the goal.
        
        The goal can be:
        - A single Atom: parent(john, X)
        - A list of goals (conjunction): [parent(john, X), old(X)]
        
        Returns a list of substitutions that satisfy the goal(s).
        Supports constraint propagation via domain tracking.
        """
        # Handle conjunctive queries (multiple goals)
        if isinstance(goal, list):
            return self._query_conjunction(goal, depth, max_depth, domains)
        
        # Handle single goal (predicate or constraint)
        return self._query_single(goal, depth, max_depth, domains)
    
    def _query_single(self, goal: Atom, depth: int = 0, max_depth: int = 100, domains: Optional[Dict[str, Any]] = None) -> List[Substitution]:
        """Query the knowledge base for a single goal."""
        if depth > max_depth:
            return []
        
        if domains is None:
            domains = {}
        
        results = []
        
        # Try to match against facts
        for fact in self.db.get_facts(goal.predicate):
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
        for rule in self.db.get_rules(goal.predicate):
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
        
        # Deduplicate results based on query variables to avoid duplicates
        # from multiple proof paths
        if depth == 0:  # Only deduplicate at top level
            results = self._deduplicate_results(goal, results)
        
        return results
    
    def _query_conjunction(self, goals: List[Any], depth: int = 0, max_depth: int = 100, domains: Optional[Dict[str, Any]] = None) -> List[Substitution]:
        """Query the knowledge base for a conjunction of goals (AND)."""
        if not goals:
            return [Substitution()]
        
        if domains is None:
            domains = {}
        
        # Prove all goals in sequence
        return self._prove_all(goals, Substitution(), depth, max_depth, domains)
    
    def _prove_all(self, goals: List[Atom], subst: Substitution, depth: int, max_depth: int, domains: Optional[Dict[str, Any]] = None) -> List[Substitution]:
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
            # Regular atom - query it
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
            elif isinstance(term, Atom):
                new_args = [rename_term(arg) for arg in term.arguments]
                return Atom(term.predicate, new_args)
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
    
    def _extract_query_variables(self, term: Any) -> List[str]:
        """Extract all variable names from a term"""
        variables = []
        
        if isinstance(term, Variable):
            variables.append(term.name)
        elif isinstance(term, Atom):
            for arg in term.arguments:
                variables.extend(self._extract_query_variables(arg))
        
        return variables
    
    def _deduplicate_results(self, goal: Atom, results: List[Substitution]) -> List[Substitution]:
        """
        Deduplicate results based on bindings for query variables only.
        This avoids returning multiple solutions that differ only in non-query variables.
        """
        query_vars = self._extract_query_variables(goal)
        
        if not query_vars:
            # No variables in query, return at most one result
            return results[:1] if results else []
        
        # Track unique solutions based on query variable bindings
        seen = set()
        unique_results = []
        
        for subst in results:
            # Create a key from query variable bindings only
            key_bindings = []
            for var in sorted(query_vars):
                val = subst.apply(Variable(var))
                key_bindings.append((var, str(val)))
            
            key = tuple(key_bindings)
            
            if key not in seen:
                seen.add(key)
                unique_results.append(subst)
        
        return unique_results

    def label_variables(self, domains: Dict[str, Any], constraints: List, objective, 
                       maximize: bool = True, objective_vars: Optional[List[str]] = None, 
                       bounds_fn = None) -> List[Dict[str, Any]]:
        """
        Branch-and-bound labeling for constraint satisfaction and optimization.
        
        Args:
            domains: Dictionary mapping variable names to sets of possible values
            constraints: List of DomainConstraint and NotEqualConstraint objects
            objective: Function that takes an assignment dict and returns a numeric objective value
            maximize: Whether to maximize (True) or minimize (False) the objective
            objective_vars: List of variable names to include in the objective (default: all variables)
            bounds_fn: Optional function for pruning that computes bounds on remaining variables
        
        Returns:
            List of assignment dictionaries representing optimal solutions
        """
        best_val = None
        best_solutions = []
        vars_to_label = list(domains.keys())
        
        # If objective_vars not specified, use all variables
        if objective_vars is None:
            objective_vars = vars_to_label

        def search(index, current_domains):
            nonlocal best_val, best_solutions

            if index == len(vars_to_label):
                assignment = {v: next(iter(current_domains[v])) for v in vars_to_label}
                val = objective(assignment)
                if best_val is None or (val > best_val if maximize else val < best_val):
                    best_val = val
                    best_solutions = [assignment]
                elif val == best_val:
                    best_solutions.append(assignment)
                return

            var = vars_to_label[index]
            for value in sorted(current_domains[var]):
                new_domains = deepcopy(current_domains)
                new_domains[var] = {value}

                if not self._propagate_constraints(constraints, new_domains):
                    continue

                # Pruning using bounds function if provided
                if bounds_fn is not None:
                    bound = bounds_fn(new_domains, vars_to_label, index, maximize)
                    if maximize and best_val is not None and bound < best_val:
                        continue
                    elif not maximize and best_val is not None and bound > best_val:
                        continue

                search(index + 1, new_domains)

        search(0, deepcopy(domains))
        return best_solutions
