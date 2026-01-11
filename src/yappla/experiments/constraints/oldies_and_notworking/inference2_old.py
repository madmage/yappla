from copy import deepcopy

# -------------------------
# Simplified engine classes
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
    """Domain constraint in rule body or head."""
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


class Rule:
    """Horn rule: head :- body"""
    def __init__(self, head, body):
        self.head = head
        self.body = body  # list of Atom or ConstraintAtom

    def __repr__(self):
        return f"{self.head} :- {self.body}"


# -------------------------
# Simplified KB
# -------------------------
class KB:
    def __init__(self):
        self.facts = set()
        self.rules = []
        self.constraints = []


# -------------------------
# Backward-chaining entailment
# -------------------------
def entails(kb, query, domains=None):
    if domains is None:
        domains = {}
    return prove(query, kb, deepcopy(domains))


def prove(atom, kb, domains):
    # 1. Ground fact
    if atom in kb.facts:
        return True

    # 2. Try rules
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
        if success:
            return True

    return False


# -------------------------
# Simple unification for atoms
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
# Test cases
# -------------------------
def test_constraints_cases():
    kb = KB()

    # --- Case 1: constraint in head ---
    # robot(X) :- X in {r1,r2}
    kb.rules.append(Rule(Atom("robot", ("X",)), [ConstraintAtom("X", {"r1","r2"})]))

    # --- Case 2: constraint in body ---
    # alarm(X) :- mobile(X), X in {r1,r2}
    kb.facts.add(Atom("robot", ("r1",)))
    kb.facts.add(Atom("robot", ("r2",)))
    kb.facts.add(Atom("robot", ("r3",)))
    kb.rules.append(Rule(Atom("mobile", ("X",)), [Atom("robot", ("X",))]))
    kb.rules.append(Rule(Atom("alarm", ("X",)), [Atom("mobile", ("X",)), ConstraintAtom("X", {"r1","r2"})]))

    # --- Case 3: constraint in query ---
    # query: mobile(X) with X in {r1,r3}
    query_domains = {"X": {"r1", "r3"}}

    # Test Case 1: robot(X)
    print("Case 1: Constraint in head")
    print("robot(r1) entailed?", entails(kb, Atom("robot", ("r1",))))
    print("robot(r3) entailed?", entails(kb, Atom("robot", ("r3",))))

    # Test Case 2: alarm(X)
    print("\nCase 2: Constraint in body")
    print("alarm(r1) entailed?", entails(kb, Atom("alarm", ("r1",))))
    print("alarm(r3) entailed?", entails(kb, Atom("alarm", ("r3",))))

    # Test Case 3: query with constraint
    print("\nCase 3: Constraint in query")
    print("mobile(X) with X in {r1,r3} entailed?", entails(kb, Atom("mobile", ("X",)), query_domains))


# -------------------------
# Run tests
# -------------------------
if __name__ == "__main__":
    test_constraints_cases()
