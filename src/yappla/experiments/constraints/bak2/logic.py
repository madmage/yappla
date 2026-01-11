class Atom:
    """Predicate with arguments"""
    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = tuple(args)

    def __eq__(self, other):
        return isinstance(other, Atom) and self.predicate == other.predicate and self.args == other.args

    def __hash__(self):
        return hash((self.predicate, self.args))

    def __repr__(self):
        return f"{self.predicate}{self.args}"


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
        self.constraints = []