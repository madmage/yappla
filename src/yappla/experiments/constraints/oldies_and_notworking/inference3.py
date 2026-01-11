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
    if head.predicate != query.predicate or len(head

