from copy import deepcopy
from itertools import product

# -------------------------
# Core classes
# -------------------------
class Atom:
    """Represents a predicate with arguments"""
    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = tuple(args)

    def __eq__(self, other):
        return isinstance(other, Atom) and self.predicate == other.predicate and self.args == other.args

    def __hash__(self):
        return hash((self.predicate, self.args))

    def __repr__(self):
        return f"{self.predicate}{self.args}"


class ConstraintAtom:
    """Constraint on a single variable (symbolic or numeric)"""
    def __init__(self, var, values):
        self.var = var
        self.values = set(values)

    def propagate(self, domains):
        if self.var not in domains:
            domains[self.var] = set(self.values)
            return True
        old = domains[self.var]
        new = old & self.values
        if not new:
            return False
        if new != old:
            domains[self.var] = new
            return True
        return False


class NotEqualConstraint:
    """Binary constraint X != Y"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def propagate(self, domains):
        dx = domains.get(self.x, set())
        dy = domains.get(self.y, set())
        old_dx, old_dy = dx.copy(), dy.copy()

        if len(dx) == 1:
            dy -= dx
        if len(dy) == 1:
            dx -= dy

        if not dx or not dy:
            return False

        domains[self.x] = dx
        domains[self.y] = dy

        return dx != old_dx or dy != old_dy


class Rule:
    """Horn rule: head :- body"""
    def __init__(self, head, body):
        self.head = head
        self.body = body  # list of Atom or ConstraintAtom

    def __repr__(self):
        return f"{self.head} :- {self.body}"


class KB:
    """Knowledge base"""
    def __init__(self):
        self.facts = set()
        self.rules = []
        self.constraints = []  # multi-variable CLP constraints


# -------------------------
# Unification / substitution
# -------------------------
def unify(head, query):
    if head.predicate != query.predicate or len(head.args) != len(query.args):
        return None
    subs = {}
    for h_arg, q_arg in zip(head.args, query.args):
        if isinstance(h_arg, str) and h_arg[0].isupper():  # variable
            subs[h_arg] = q_arg
        elif h_arg != q_arg:
            return None
    return subs


def substitute(atom, subs):
    return Atom(atom.predicate, [subs.get(a, a) for a in atom.args])


# -------------------------
# Constraint propagation
# -------------------------
def propagate_constraints(constraints, domains):
    """
    Apply constraints until a fixpoint is reached.
    Returns False if inconsistency is found.
    """
    changed = True
    while changed:
        changed = False
        for c in constraints:
            if isinstance(c, (ConstraintAtom, NotEqualConstraint)):
                result = c.propagate(domains)
                if result is False:
                    return False
                changed = changed or result
    # check consistency
    for d in domains.values():
        if not d:
            return False
    return True


# -------------------------
# Branch-and-Bound Labeling for Optimization
# -------------------------
def label_variables_branch_and_bound(domains, kb_constraints, objective, maximize=True):
    """
    Branch-and-bound labeling:
    Returns assignments maximizing/minimizing objective, respecting multi-variable constraints.
    """
    best_val = None
    best_solutions = []

    vars_to_label = list(domains.keys())

    def search(index, current_domains):
        nonlocal best_val, best_solutions

        if index == len(vars_to_label):
            # Leaf node: all variables assigned
            assignment = {v: next(iter(current_domains[v])) for v in vars_to_label}
            val = objective(assignment)
            if best_val is None or (maximize and val > best_val) or (not maximize and val < best_val):
                best_val = val
                best_solutions = [assignment]
            elif val == best_val:
                best_solutions.append(assignment)
            return

        var = vars_to_label[index]
        for value in sorted(current_domains[var]):
            new_domains = deepcopy(current_domains)
            new_domains[var] = {value}

            # Propagate constraints immediately
            if not propagate_constraints(kb_constraints, new_domains):
                continue  # inconsistent → prune

            # Compute upper bound: sum of max/min after propagation
            if maximize:
                ub = sum(max(new_domains[v]) for v in vars_to_label[index:])
                if best_val is not None and ub <= best_val:
                    continue  # prune branch
            else:
                lb = sum(min(new_domains[v]) for v in vars_to_label[index:])
                if best_val is not None and lb >= best_val:
                    continue  # prune branch

            # Recurse
            search(index + 1, new_domains)

    search(0, deepcopy(domains))
    return best_solutions


# -------------------------
# Backward-Chaining Entailment
# -------------------------
def entails(kb, query, query_domains=None):
    if query_domains is None:
        query_domains = {}
    return prove(query, kb, deepcopy(query_domains))


def prove(atom, kb, domains):
    """
    Returns True if atom can be entailed given KB, rules, and constraints.
    """
    if atom in kb.facts:
        return True

    for rule in kb.rules:
        subs = unify(rule.head, atom)
        if subs is None:
            continue
        body = [substitute(b, subs) if isinstance(b, Atom) else b for b in rule.body]
        local_domains = deepcopy(domains)
        consistent = True
        for b in body:
            if isinstance(b, ConstraintAtom):
                if not b.propagate(local_domains):
                    consistent = False
                    break
            else:
                if not prove(b, kb, local_domains):
                    consistent = False
                    break
        if consistent and propagate_constraints(kb.constraints, local_domains):
            return True
    return False


# -------------------------
# Test CLP + Horn + Branch-and-Bound
# -------------------------
def test_engine():
    kb = KB()

    # Facts
    kb.facts.add(Atom("robot", ("r1",)))
    kb.facts.add(Atom("robot", ("r2",)))
    kb.facts.add(Atom("robot", ("r3",)))

    # Rules with constraints in head/body
    kb.rules.append(Rule(Atom("robot_valid", ("X",)), [ConstraintAtom("X", {"r1","r2"})]))
    kb.rules.append(Rule(Atom("mobile", ("X",)), [Atom("robot", ("X",))]))
    kb.rules.append(Rule(Atom("alarm", ("X",)), [Atom("mobile", ("X",)), ConstraintAtom("X", {"r1","r2"})]))

    # Multi-variable CLP(FD) constraints
    kb.constraints.append(NotEqualConstraint("X1","X2"))
    kb.constraints.append(NotEqualConstraint("X2","X3"))

    # Domains for numeric variables
    domains = {
        "X1": set(range(1,4)),
        "X2": set(range(1,4)),
        "X3": set(range(1,4)),
    }

    print("Entailment tests:")
    print("robot_valid(r1)?", entails(kb, Atom("robot_valid", ("r1",))))
    print("robot_valid(r3)?", entails(kb, Atom("robot_valid", ("r3",))))
    print("alarm(r1)?", entails(kb, Atom("alarm", ("r1",))))
    print("alarm(r3)?", entails(kb, Atom("alarm", ("r3",))))

    print("\nBranch-and-bound optimization (maximize X1+X2 with X1!=X2!=X3):")
    best = label_variables_branch_and_bound(domains, kb.constraints,
                                            objective=lambda s: s["X1"] + s["X2"],
                                            maximize=True)
    for s in best:
        print(s)


if __name__ == "__main__":
    test_engine()

