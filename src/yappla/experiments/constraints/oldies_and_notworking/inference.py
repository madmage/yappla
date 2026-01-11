from dataclasses import dataclass
from typing import List, Tuple, Set, Dict
from itertools import product
from collections import deque
import copy

@dataclass(frozen=True)
class Atom:
    pred: str
    args: Tuple[str, ...]

    def __repr__(self):
        return f"{self.pred}({', '.join(self.args)})"


@dataclass
class Rule:
    head: Atom
    body: List[Atom]


class Constraint: pass

class LogicalConstraint(Constraint):
    def __init__(self, body):
        self.body = body  # list[Atom]

    def violated(self, closure: set) -> bool:
        return all(atom in closure for atom in self.body)

    def __repr__(self):
        return f":- {', '.join(map(str, self.body))}"

class CLPConstraint:
    def propagate(self, domains) -> bool:
        raise NotImplementedError

class NotEqualConstraint(Constraint):
    def __init__(self, x, y):
        self.x = x
        self.y = y
 
    def propagate(self, domains):
        dx = domains.get(self.x, set())
        dy = domains.get(self.y, set())
        if len(dx) == 1:
            dy -= dx
        if len(dy) == 1:
            dx -= dy
        domains[self.x] = dx
        domains[self.y] = dy
        return bool(dx) and bool(dy)

    def __repr__(self):
        return f"{self.x} != {self.y}"

class DomainConstraint(Constraint):
    def __init__(self, var, values):
        """
        var: variable name
        values: set of allowed values (int or str)
        """
        self.var = var
        self.values = set(values)

    def propagate(self, domains):
        if self.var not in domains:
            domains[self.var] = set(self.values)
            return True
        else:
            old = domains[self.var]
            domains[self.var] &= self.values  # intersect current domain with allowed values
            return bool(domains[self.var]) and old != set()  # True if domain not empty

class KnowledgeBase:
    def __init__(self):
        self.facts: Set[Atom] = set()
        self.rules: List[Rule] = []
        self.constraints: List[Constraint] = []

def parse_atom(s: str) -> Atom:
    name, rest = s.split("(")
    args = rest.rstrip(")").split(",")
    return Atom(name.strip(), tuple(a.strip() for a in args if a.strip()))

def parse_clp_constraint(s: str) -> Constraint:
    if "!=" in s:
        x, y = map(str.strip, s.split("!="))
        return NotEqualConstraint(x, y)
    else:
        raise ValueError(f"Unknown CLP constraint: {s}")

def parse_domain_constraint(s: str) -> DomainConstraint:
    var, rest = map(str.strip, s.split("in"))
    # Numeric range
    if ".." in rest:
        start, end = map(int, rest.split(".."))
        values = set(range(start, end+1))
    # Enumerated symbols
    elif rest.startswith("{") and rest.endswith("}"):
        values = set(x.strip() for x in rest[1:-1].split(","))
    else:
        raise ValueError(f"Invalid domain specification: {s}")
    return DomainConstraint(var, values)


class ConstraintStore:
    def __init__(self, domains):
        self.domains = domains
        self.constraints = []

    def add(self, c):
        self.constraints.append(c)

    def propagate(self):
        changed = True
        while changed:
            changed = False
            for c in self.constraints:
                if not c.propagate(self.domains):
                    return False
        return True

def load_kb_file(path: str):
    facts = set()
    rules = []
    constraints = []

    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.endswith("."):
                line = line[:-1]

            # Constraint
            if line.startswith(":-"):
                raw = line[2:].strip()
                if "!=" in raw:
                    constraints.append(NotEqualConstraint(*map(str.strip, raw.split("!="))))
                else:
                    atoms = [parse_atom(x.strip()) for x in raw.split(",")]
                    constraints.append(LogicalConstraint(atoms))
            # Domain constraint
            elif " in " in line:
                constraints.append(parse_domain_constraint(line))
            # Rule
            elif ":-" in line:
                h, b = line.split(":-")
                rules.append(
                    Rule(parse_atom(h.strip()), [parse_atom(x.strip()) for x in b.split(",")])
                )
            # Fact
            else:
                facts.add(parse_atom(line))

    return facts, rules, constraints


def check_logical_constraints(constraints, closure):
    for c in constraints:
        if isinstance(c, LogicalConstraint) and c.violated(closure):
            return False
    return True


def propagate_clp_constraints(constraints, domains):
    domains = copy.deepcopy(domains)
    """
    Propagate all CLP constraints over the given domains.
    Returns False if any domain becomes empty (inconsistent), True otherwise.
    """
    changed = True
    while changed:
        changed = False
        for c in constraints:
            if isinstance(c, DomainConstraint):
                old_domain = domains.get(c.var, set())
                if c.var not in domains:
                    domains[c.var] = set(c.values)
                    changed = True
                else:
                    new_domain = old_domain & c.values
                    if not new_domain:
                        return False
                    if new_domain != old_domain:
                        domains[c.var] = new_domain
                        changed = True

            elif isinstance(c, NotEqualConstraint):
                dx = domains.get(c.x, set())
                dy = domains.get(c.y, set())
                old_dx, old_dy = dx.copy(), dy.copy()

                # propagate disequality
                if len(dx) == 1:
                    dy -= dx
                if len(dy) == 1:
                    dx -= dy

                if not dx or not dy:
                    return False

                domains[c.x] = dx
                domains[c.y] = dy

                # mark changed only if any domain actually shrank
                if dx != old_dx or dy != old_dy:
                    changed = True

    return True


def compute_closure(kb):
    """
    Forward chaining with unification for multi-body rules.
    kb.facts: set of Atom (ground)
    kb.rules: list of Rule(head:Atom, body:list[Atom])
    Returns: closure (set of Atom)
    """
    closure = set(kb.facts)
    worklist = deque(kb.facts)

    while worklist:
        f = worklist.popleft()

        for rule in kb.rules:
            body_atoms = rule.body

            # Generate all candidate substitutions for body atoms
            # For each body atom, collect matching facts
            matches_per_atom = []
            for b in body_atoms:
                matches = []
                for fact in closure:
                    subs = unify(b, fact)
                    if subs is not None:
                        matches.append(subs)
                if not matches:
                    break  # no match for this body atom
                matches_per_atom.append(matches)
            else:
                # Cartesian product of substitutions across body atoms
                for combo in product(*matches_per_atom):
                    # Merge substitutions
                    merged = {}
                    conflict = False
                    for sub in combo:
                        for k, v in sub.items():
                            if k in merged and merged[k] != v:
                                conflict = True
                                break
                            merged[k] = v
                        if conflict:
                            break
                    if conflict:
                        continue

                    # Instantiate head
                    head_inst = substitute(rule.head, merged)
                    if head_inst not in closure:
                        closure.add(head_inst)
                        worklist.append(head_inst)

    return closure



def is_consistent(kb, closure, domains) -> bool:
    """
    Checks whether the knowledge base is consistent under:
    - CLP constraint propagation
    - Logical (Horn-style) constraints
    """

    # 1. Propagate CLP constraints
    if not propagate_clp_constraints(kb.constraints, domains):
        return False

    # 2. Check logical constraints
    for c in kb.constraints:
        if isinstance(c, LogicalConstraint):
            if c.violated(closure):
                return False

    return True


def load_all(ontology_file, rules_file, constraints_file):
    kb = KnowledgeBase()

    for f in [ontology_file, rules_file]:
        facts, rules, _ = load_kb_file(f)
        kb.facts.update(facts)
        kb.rules.extend(rules)

    _, _, constraints = load_kb_file(constraints_file)
    kb.constraints.extend(constraints)

    return kb

def entails(kb, query, domains=None):
    """
    Check if the query is entailed by KB.
    domains: dict of variable domains (CLP(FD))
    """
    closure = compute_closure(kb)

    if domains is not None:
        # make a local copy for this query
        local_domains = copy.deepcopy(domains)
        if not is_consistent(kb, closure, local_domains):
            return False
    else:
        local_domains = {}

    return query in closure


def consistent(kb, domains):
    closure = compute_closure(kb)
    return is_consistent(kb, closure, domains)

def substitute(atom: Atom, subs: dict) -> Atom:
    return Atom(atom.pred, tuple(subs.get(a, a) for a in atom.args))


def unify(a: Atom, b: Atom, subs=None):
    """
    Attempt to unify atom a (possibly with variables) with atom b (ground or partially instantiated)
    subs: existing substitutions (dict)
    Returns updated substitutions if successful, else None
    """
    if subs is None:
        subs = {}

    if a.pred != b.pred or len(a.args) != len(b.args):
        return None

    new_subs = subs.copy()
    for arg_a, arg_b in zip(a.args, b.args):
        # Variable: uppercase convention
        if arg_a[0].isupper():  # variable
            if arg_a in new_subs:
                if new_subs[arg_a] != arg_b:
                    return None
            else:
                new_subs[arg_a] = arg_b
        else:
            if arg_a != arg_b:
                return None
    return new_subs


def test_engine_old():
    kb = load_all(
        "ontology.kb",
        "rules.kb",
        "constraints.kb"
    )

    print("FACTS:", kb.facts)
    print("RULES:", kb.rules)
    print("CONSTRAINTS:", kb.constraints)

    print("=== Closure ===")
    closure = compute_closure(kb)
    for a in sorted(closure, key=str):
        print(a)

    print("\n=== ENTAIL tests ===")
    print("mobile(r1):", entails(kb, Atom("mobile", ("r1",))))
    print("alarm(r1):", entails(kb, Atom("alarm", ("r1",))))

    print("\n=== CONSISTENT test (initial) ===")
    print("Consistent:", is_consistent(kb))

    print("\n=== Add fire(r1) ===")
    kb.facts.add(Atom("fire", ("r1",)))
    print("alarm(r1):", entails(kb, Atom("alarm", ("r1",))))
    print("danger(r1):", entails(kb, Atom("danger", ("r1",))))
    print("Consistent:", is_consistent(kb))

    print("\n=== Add intrusion(r1) (should break consistency) ===")
    kb.facts.add(Atom("intrusion", ("r1",)))
    print("Consistent:", is_consistent(kb))

def test_engine():
    # 1. Load the KB from files
    kb = load_all(
        "ontology.kb",
        "rules.kb",
        "constraints.kb"
    )

    # 2. Initialize domains for all variables appearing in CLP constraints
    # We'll collect all variable names from NotEqualConstraint instances
    domains = {}
    for c in kb.constraints:
        if isinstance(c, NotEqualConstraint):
            if c.x not in domains:
                domains[c.x] = set(range(1, 4))  # Example finite domain
            if c.y not in domains:
                domains[c.y] = set(range(1, 4))

    # 3. Compute closure for initial KB
    closure = compute_closure(kb)
    print("=== Initial Closure ===")
    for a in sorted(closure, key=str):
        print(a)

    # 4. ENTAIL tests
    print("\n=== ENTAIL Tests ===")
    print("mobile(r1):", entails(kb, Atom("mobile", ("r1",)), domains))
    print("alarm(r1):", entails(kb, Atom("alarm", ("r1",)), domains))

    # 5. CONSISTENT test
    print("\n=== CONSISTENT Test (initial) ===")
    print("Consistent:", is_consistent(kb, closure, domains))

    # 6. Add a fact: fire(r1)
    print("\n=== Add fire(r1) ===")
    kb.facts.add(Atom("fire", ("r1",)))
    closure = compute_closure(kb)
    print("alarm(r1):", entails(kb, Atom("alarm", ("r1",)), domains))
    print("danger(r1):", entails(kb, Atom("danger", ("r1",)), domains))
    print("Consistent:", is_consistent(kb, closure, domains))

    # 7. Add a fact: intrusion(r1) (may violate a logical constraint)
    print("\n=== Add intrusion(r1) ===")
    kb.facts.add(Atom("intrusion", ("r1",)))
    closure = compute_closure(kb)
    print("Consistent:", is_consistent(kb, closure, domains))

    # 8. Show current domains for CLP constraints
    print("\n=== CLP Domains ===")
    for var, dom in domains.items():
        print(f"{var}: {dom}")


def test_domains():
    kb = KnowledgeBase()
    kb.facts, kb.rules, kb.constraints = load_kb_file("constraints_test.kb")

    domains = {}
    for c in kb.constraints:
        if isinstance(c, DomainConstraint):
            c.propagate(domains)

    print("Initial domains after propagation:")
    for var, dom in domains.items():
        print(f"{var}: {dom}")

    # Test intersection propagation
    # Add a constraint X1 != 2
    c = DomainConstraint("X1", {1,3})
    c.propagate(domains)
    print("Domains after intersecting X1 with {1,3}:")
    for var, dom in domains.items():
        print(f"{var}: {dom}")


test_engine()

test_domains()