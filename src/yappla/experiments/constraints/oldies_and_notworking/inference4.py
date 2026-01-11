from copy import deepcopy
from itertools import product

# -------------------------
# Core classes (same as before)
# -------------------------
class Atom:
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
    def __init__(self, head, body):
        self.head = head
        self.body = body
    def __repr__(self):
        return f"{self.head} :- {self.body}"


class KB:
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
        if isinstance(h_arg, str) and h_arg[0].isupper():
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
    changed = True
    while changed:
        changed = False
        for c in constraints:
            if isinstance(c, (ConstraintAtom, NotEqualConstraint)):
                if c.propagate(domains):
                    changed = True
    # check consistency
    for d in domains.values():
        if not d:
            return False
    return True


# -------------------------
# Labeling / search
# -------------------------
def label_variables(domains, kb_constraints):
    """Return a list of all consistent assignments"""
    vars_to_label = list(domains.keys())
    domains_list = [list(domains[v]) for v in vars_to_label]

    solutions = []
    for combination in product(*domains_list):
        assignment = dict(zip(vars_to_label, combination))
        local_domains = {v: {val} for v, val in assignment.items()}
        if propagate_constraints(kb_constraints, local_domains):
            solutions.append(assignment)
    return solutions


# -------------------------
# Backward-chaining with labeling
# -------------------------
def entails(kb, query, query_domains=None):
    if query_domains is None:
        query_domains = {}
    solutions = prove_all(query, kb, deepcopy(query_domains))
    return len(solutions) > 0


def prove_all(atom, kb, domains):
    """Return all consistent solutions for this atom and domains"""
    # 1. Ground fact
    if atom in kb.facts:
        return [domains]

    solutions = []
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
                # recursive
                recursive_solutions = prove_all(b, kb, local_domains)
                if not recursive_solutions:
                    consistent = False
                    break
                # merge first solution (can be extended to all)
                local_domains.update(recursive_solutions[0])
        if consistent:
            # propagate KB constraints
            if propagate_constraints(kb.constraints, local_domains):
                # labeling: find all assignments consistent with multi-variable constraints
                solutions.extend(label_variables(local_domains, kb.constraints))
    return solutions


# -------------------------
# Test CLP(FD) with labeling
# -------------------------
def test_labeling():
    kb = KB()

    # Facts
    kb.facts.add(Atom("robot", ("r1",)))
    kb.facts.add(Atom("robot", ("r2",)))
    kb.facts.add(Atom("robot", ("r3",)))

    # Rules with constraints in head or body
    kb.rules.append(Rule(Atom("robot_valid", ("X",)), [ConstraintAtom("X", {"r1","r2"})]))
    kb.rules.append(Rule(Atom("mobile", ("X",)), [Atom("robot", ("X",))]))
    kb.rules.append(Rule(Atom("alarm", ("X",)), [Atom("mobile", ("X",)), ConstraintAtom("X", {"r1","r2"})]))

    # Multi-variable CLP constraints
    kb.constraints.append(NotEqualConstraint("X1", "X2"))
    kb.constraints.append(NotEqualConstraint("X2", "X3"))

    # Initial domains
    domains = {
        "X1": set(range(1,4)),
        "X2": set(range(1,4)),
        "X3": set(range(1,4)),
    }

    # Label variables to get all assignments satisfying X1 != X2 != X3
    solutions = label_variables(domains, kb.constraints)
    print("All consistent assignments for X1,X2,X3 with X1!=X2!=X3:")
    for s in solutions:
        print(s)

    # Test entail queries
    print("\nEntail tests with labeling:")
    print("robot_valid(r1)?", entails(kb, Atom("robot_valid", ("r1",))))
    print("robot_valid(r3)?", entails(kb, Atom("robot_valid", ("r3",))))
    print("alarm(r1)?", entails(kb, Atom("alarm", ("r1",))))
    print("alarm(r3)?", entails(kb, Atom("alarm", ("r3",))))


if __name__ == "__main__":
    test_labeling()

