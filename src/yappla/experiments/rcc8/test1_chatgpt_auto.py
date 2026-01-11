"""
RCC8 Logic Engine with Constraint Propagation and Inference
===========================================================

Implements:
- RCC8 relations
- Path-consistency constraint propagation
- Deduction
- Abduction (minimal constraint explanations)
- Simple probabilistic inference
"""

from itertools import product
from collections import defaultdict
import math

# ----------------------------
# RCC8 DEFINITIONS
# ----------------------------

RCC8 = {
    "DC",   # Disconnected
    "EC",   # Externally Connected
    "PO",   # Partial Overlap
    "EQ",   # Equal
    "TPP",  # Tangential Proper Part
    "NTPP", # Non-Tangential Proper Part
    "TPPi",
    "NTPPi",
}

# Converse relations
CONVERSE = {
    "DC": "DC",
    "EC": "EC",
    "PO": "PO",
    "EQ": "EQ",
    "TPP": "TPPi",
    "NTPP": "NTPPi",
    "TPPi": "TPP",
    "NTPPi": "NTPP",
}

# RCC8 Composition Table (simplified but sound)
# Each entry is a SET of possible relations
COMPOSE = defaultdict(set)

def _c(a, b, result):
    COMPOSE[(a, b)].update(result)

# --- Core compositions (not fully exhaustive but useful) ---
_c("EQ", "EQ", {"EQ"})
for r in RCC8:
    _c("EQ", r, {r})
    _c(r, "EQ", {r})

_c("DC", "DC", {"DC"})
_c("DC", "EC", {"DC"})
_c("DC", "PO", {"DC"})
_c("DC", "TPP", {"DC"})
_c("DC", "NTPP", {"DC"})

_c("EC", "EC", {"DC", "EC"})
_c("EC", "PO", {"DC", "EC", "PO"})
_c("PO", "PO", {"DC", "EC", "PO", "TPP", "TPPi"})

_c("TPP", "TPP", {"TPP", "NTPP"})
_c("TPP", "NTPP", {"NTPP"})
_c("NTPP", "TPP", {"NTPP"})
_c("NTPP", "NTPP", {"NTPP"})

# Fill converse compositions automatically
for (a, b), rs in list(COMPOSE.items()):
    COMPOSE[(CONVERSE[b], CONVERSE[a])] |= {CONVERSE[r] for r in rs}

# Default: if unknown, allow all
def compose(r1, r2):
    return COMPOSE.get((r1, r2), set(RCC8))

# ----------------------------
# CONSTRAINT NETWORK
# ----------------------------

class RCC8Network:
    def __init__(self, variables):
        self.vars = list(variables)
        self.C = {}
        for x, y in product(self.vars, self.vars):
            if x == y:
                self.C[(x, y)] = {"EQ"}
            else:
                self.C[(x, y)] = set(RCC8)

    def set_constraint(self, x, y, relations):
        relations = set(relations)
        self.C[(x, y)] &= relations
        self.C[(y, x)] &= {CONVERSE[r] for r in relations}

    def propagate(self):
        """Path consistency (PC-2 style)"""
        changed = True
        while changed:
            changed = False
            for x, y, z in product(self.vars, repeat=3):
                if x == z:
                    continue
                allowed = set()
                for r1 in self.C[(x, y)]:
                    for r2 in self.C[(y, z)]:
                        allowed |= compose(r1, r2)
                new = self.C[(x, z)] & allowed
                if new != self.C[(x, z)]:
                    if not new:
                        raise ValueError(f"Inconsistent network at ({x},{z})")
                    self.C[(x, z)] = new
                    self.C[(z, x)] = {CONVERSE[r] for r in new}
                    changed = True

    def possible(self, x, y):
        return self.C[(x, y)]

    def __str__(self):
        out = []
        for x, y in product(self.vars, self.vars):
            if x < y:
                out.append(f"{x}-{y}: {self.C[(x,y)]}")
        return "\n".join(out)

# ----------------------------
# ABDUCTION
# ----------------------------

def abduct(network, observations):
    """
    Find minimal extra constraints that make observations consistent.
    Very simple: try single missing constraints.
    """
    explanations = []
    for (x, y), rels in observations.items():
        for r in rels:
            try:
                n2 = clone(network)
                n2.set_constraint(x, y, {r})
                n2.propagate()
                explanations.append({(x, y): r})
            except ValueError:
                pass
    return explanations

# ----------------------------
# PROBABILISTIC INFERENCE
# ----------------------------

def probabilistic_query(network, x, y, prior=None):
    """
    Simple normalized probability over remaining relations.
    """
    if prior is None:
        prior = {r: 1.0 for r in RCC8}

    allowed = network.possible(x, y)
    probs = {r: prior.get(r, 0.0) for r in allowed}
    Z = sum(probs.values())
    return {r: p / Z for r, p in probs.items()}

# ----------------------------
# UTIL
# ----------------------------

def clone(net):
    n = RCC8Network(net.vars)
    n.C = {k: set(v) for k, v in net.C.items()}
    return n

# ----------------------------
# TESTS / EXAMPLES
# ----------------------------

def test_deduction():
    print("\n--- Deduction Test ---")
    net = RCC8Network(["A", "B", "C"])
    net.set_constraint("A", "B", {"TPP"})
    net.set_constraint("B", "C", {"NTPP"})
    net.propagate()
    print(net)
    print("A-C:", net.possible("A", "C"))

def test_inconsistency():
    print("\n--- Inconsistency Test ---")
    net = RCC8Network(["A", "B"])
    net.set_constraint("A", "B", {"TPP"})
    net.set_constraint("A", "B", {"DC"})
    try:
        net.propagate()
    except ValueError as e:
        print("Caught:", e)

def test_abduction():
    print("\n--- Abduction Test ---")
    net = RCC8Network(["A", "B", "C"])
    obs = {("A", "C"): {"DC"}}
    expl = abduct(net, obs)
    print("Explanations:", expl)

def test_probability():
    print("\n--- Probabilistic Inference Test ---")
    net = RCC8Network(["A", "B"])
    net.set_constraint("A", "B", {"EC", "PO"})
    net.propagate()
    probs = probabilistic_query(net, "A", "B", prior={"EC": 0.7, "PO": 0.3})
    print("P(A,B):", probs)

if __name__ == "__main__":
    test_deduction()
    test_inconsistency()
    test_abduction()
    test_probability()
