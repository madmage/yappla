from copy import deepcopy
from constraints import ConstraintAtom, NotEqualConstraint
from logic import Atom, Rule, KB

# -------------------------
# Unification / substitution
# -------------------------
def unify(head, query):
    if head.predicate != query.predicate or len(head.args) != len(query.args):
        return None
    subs = {}
    for h_arg, q_arg in zip(head.args, query.args):
        if isinstance(h_arg, str) and h_arg[0].isupper():  # h_arg is variable
            if isinstance(q_arg, str) and q_arg[0].isupper():  # q_arg is variable
                if h_arg != q_arg:
                    return None  # different variables, can't unify in this simple implementation
            else:
                subs[h_arg] = q_arg
        else:
            if isinstance(q_arg, str) and q_arg[0].isupper():
                return None  # h_arg ground, q_arg variable, can't unify
            elif h_arg != q_arg:
                return None
    return subs


def substitute(atom, subs):
    return Atom(atom.predicate, [subs.get(a, a) for a in atom.args])


# -------------------------
# Constraint propagation
# -------------------------
def propagate_constraints(constraints, domains):
    for c in constraints:
        if isinstance(c, (ConstraintAtom, NotEqualConstraint)):
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
    for f in kb.facts:
        subs = unify(atom, f)
        if subs is not None:
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
    for rule in kb.rules:
        subs = unify(rule.head, atom)
        if subs is None:
            continue

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
            for b in rule.body:
                if isinstance(b, ConstraintAtom):
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


# -------------------------
# Test Engine
# -------------------------
def test_entailment():
    kb = KB()
    # Facts
    kb.facts.add(Atom("robot", ("r1",)))
    kb.facts.add(Atom("robot", ("r2",)))
    kb.facts.add(Atom("robot", ("r3",)))

    # Rules
    kb.rules.append(Rule(Atom("robot_valid", ("X",)), [ConstraintAtom("X", {"r1","r2"})]))
    kb.rules.append(Rule(Atom("mobile", ("X",)), [Atom("robot", ("X",))]))
    kb.rules.append(Rule(Atom("alarm", ("X",)), [Atom("mobile", ("X",)), ConstraintAtom("X", {"r1","r2"})]))

    print("Entailment tests:")
    print("robot_valid(r1)?", entails(kb, Atom("robot_valid", ("r1",))))
    print("robot_valid(r3)?", entails(kb, Atom("robot_valid", ("r3",))))
    print("alarm(r1)?", entails(kb, Atom("alarm", ("r1",))))
    print("alarm(r3)?", entails(kb, Atom("alarm", ("r3",))))


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
    test_entailment()
    test_labeling()

