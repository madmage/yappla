from copy import deepcopy

# -------------------------
# Core classes
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
    """Constraint X != Y"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def propagate(self, domains):
        dx = domains.get(self.x, set())
        dy = domains.get(self.y, set())
        old_dx, old_dy = dx.copy(), dy.copy()

        # propagate disequality
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
        self.constraints = []  # CLP(FD) constraints like NotEqualConstraint


# -------------------------
# Unification
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
# CLP(FD) propagation
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
# Backward-chaining entailment
# -------------------------
def entails(kb, query, query_domains=None):
    if query_domains is None:
        query_domains = {}
    return prove(query, kb, deepcopy(query_domains))


def prove(atom, kb, domains):
    # Check if atom is a ground fact
    if atom in kb.facts:
        return True

    # Try rules whose head unifies
    for rule in kb.rules:
        subs = unify(rule.head, atom)
        if subs is None:
            continue

        # Apply substitution to body
        body = [substitute(b, subs) if isinstance(b, Atom) else b for b in rule.body]

        local_domains = deepcopy(domains)
        success = True

        for b in body:
            if isinstance(b, ConstraintAtom):
                if not b.propagate(local_domains):
                    success = False
                    break
            else:  # Atom
                if not prove(b, kb, local_domains):
                    success = False
                    break

        # propagate KB-level constraints (multi-variable)
        if success and not propagate_constraints(kb.constraints, local_domains):
            success = False

        if success:
            return True

    return False


# -------------------------
# Example KB and tests
# -------------------------
def test_clp_fd_engine():
    kb = KB()

    # --- Facts ---
    kb.facts.add(Atom("robot", ("r1",)))
    kb.facts.add(Atom("robot", ("r2",)))
    kb.facts.add(Atom("robot", ("r3",)))

    # --- Horn rules with constraint in head ---
    kb.rules.append(Rule(Atom("robot_valid", ("X",)), [ConstraintAtom("X", {"r1","r2"})]))
    kb.rules.append(Rule(Atom("mobile", ("X",)), [Atom("robot", ("X",))]))
    kb.rules.append(Rule(Atom("alarm", ("X",)), [Atom("mobile", ("X",)), ConstraintAtom("X", {"r1","r2"})]))

    # --- Multi-variable CLP constraints ---
    kb.constraints.append(NotEqualConstraint("X1", "X2"))  # X1 != X2
    kb.constraints.append(NotEqualConstraint("X2", "X3"))  # X2 != X3

    # --- Domain initialization ---
    domains = {
        "X1": set(range(1,4)),
        "X2": set(range(1,4)),
        "X3": set(range(1,4)),
    }

    print("Test 1: robot_valid(r1/r2/r3)")
    print("robot_valid(r1)?", entails(kb, Atom("robot_valid", ("r1",))))
    print("robot_valid(r2)?", entails(kb, Atom("robot_valid", ("r2",))))
    print("robot_valid(r3)?", entails(kb, Atom("robot_valid", ("r3",))))

    print("\nTest 2: alarm(r1/r2/r3)")
    print("alarm(r1)?", entails(kb, Atom("alarm", ("r1",))))
    print("alarm(r2)?", entails(kb, Atom("alarm", ("r2",))))
    print("alarm(r3)?", entails(kb, Atom("alarm", ("r3",))))

    print("\nTest 3: multi-variable CLP constraint propagation")
    print("X1,X2,X3 domains before propagation:", domains)
    consistent = propagate_constraints(kb.constraints, deepcopy(domains))
    print("Domains consistent after propagation?", consistent)


# -------------------------
# Run tests
# -------------------------
if __name__ == "__main__":
    test_clp_fd_engine()

