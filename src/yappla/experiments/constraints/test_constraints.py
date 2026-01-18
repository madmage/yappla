from copy import deepcopy
from constraints import DomainConstraint, NotEqualConstraint
from logic_classes import Predicate, Rule, Variable
from knowledge_base import KnowledgeBase
from substitution import Unifier, Substitution

# -------------------------
# Constraint propagation
# -------------------------
def propagate_constraints(constraints, domains):
    for c in constraints:
        if isinstance(c, (DomainConstraint, NotEqualConstraint)):
            if not c.propagate(domains):
                return False
    return True


# -------------------------
# Backward-Chaining Entailment
# -------------------------
def entails(kb, query):
    domains = {}
    return prove(query, kb, domains)


def prove(atom, kb, domains):
    # 1. Check if atom is a fact
    for f in kb.get_facts():
        result = Unifier.unify(atom, f)
        if result is not None:
            subs = result.bindings
            # Assign variables in domains
            for v, val in subs.items():
                if v not in domains:
                    domains[v] = {val}
                else:
                    domains[v] &= {val}
                    if not domains[v]:
                        return False
            if not propagate_constraints(kb.constraints, domains):
                return False
            return True

    # 2. Try rules
    for rule in kb.get_rules():
        result = Unifier.unify(rule.head, atom)
        if result is None:
            continue
        
        subs = result.bindings
        local_domains = deepcopy(domains)
        # assign head variables
        for v, val in subs.items():
            if v not in local_domains:
                local_domains[v] = {val}
            else:
                local_domains[v] &= {val}
                if not local_domains[v]:
                    break
        else:
            consistent = True
            # Apply substitutions from head unification to rule body
            substitution = Substitution(subs)
            body = []
            for item in rule.body:
                if isinstance(item, Predicate):
                    body.append(substitution.apply(item))
                else:
                    # For constraints, we don't apply the substitution (they work with variable names)
                    body.append(item)
            
            for b in body:
                if isinstance(b, (DomainConstraint, NotEqualConstraint)):
                    if not b.propagate(local_domains):
                        consistent = False
                        break
                else:
                    if not prove(b, kb, local_domains):
                        consistent = False
                        break
            if consistent and propagate_constraints(kb.constraints, local_domains):
                # merge back
                for k, v in local_domains.items():
                    if k not in domains:
                        domains[k] = set(v)
                    else:
                        domains[k] &= v
                        if not domains[k]:
                            return False
                return True
    return False


# -------------------------
# Branch-and-Bound Labeling
# -------------------------
def label_variables_branch_and_bound(domains, kb_constraints, objective, maximize=True, objective_vars=None, bounds_fn=None):
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

            if not propagate_constraints(kb_constraints, new_domains):
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


def test_labeling():
    # Domains for numeric variables
    domains = {
        "X1": {1, 2, 3},
        "X2": {1, 2, 3},
        "X3": {1, 2, 3},
    }

    constraints = [
        NotEqualConstraint("X1","X2"),
        NotEqualConstraint("X2","X3"),
    ]

    # Define bounds function for linear objective X1+X2
    def bounds_for_sum(current_domains, vars_to_label, index, maximize):
        """Compute bound for sum objective (upper bound if maximizing, lower bound if minimizing)"""
        objective_vars = ["X1", "X2"]
        current_sum = sum(next(iter(current_domains[vars_to_label[i]])) for i in range(index) if vars_to_label[i] in objective_vars)
        remaining = sum(max(current_domains[v]) if maximize else min(current_domains[v]) 
                       for v in vars_to_label[index:] if v in objective_vars)
        return current_sum + remaining

    print("\nBranch-and-bound optimization (maximize X1+X2 with X1!=X2!=X3):")
    best = label_variables_branch_and_bound(domains, constraints,
                                            objective=lambda s: s["X1"] + s["X2"],
                                            maximize=True,
                                            objective_vars=["X1", "X2"],
                                            bounds_fn=bounds_for_sum)
    for s in best:
        print(s)


if __name__ == "__main__":
    test_labeling()

