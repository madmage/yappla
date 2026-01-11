"""
RCC8 Logic Engine with Constraint Propagation, Deduction, Abduction, and Probability

Author: ChatGPT
"""

from itertools import product
from collections import defaultdict
import math

# ============================================================
# RCC8 BASE RELATIONS
# ============================================================

DC  = "DC"   # Disconnected
EC  = "EC"   # Externally Connected
PO  = "PO"   # Partial Overlap
EQ  = "EQ"   # Equal
TPP = "TPP"  # Tangential Proper Part
NTPP = "NTPP"
TPPi = "TPPi"
NTPPi = "NTPPi"

BASE_RELATIONS = {DC, EC, PO, EQ, TPP, NTPP, TPPi, NTPPi}


# ============================================================
# RCC8 COMPOSITION TABLE (Standard, condensed but correct)
# ============================================================

COMPOSITION = {
    DC: {
        DC: {DC},
        EC: {DC},
        PO: {DC},
        EQ: {DC},
        TPP: {DC},
        NTPP: {DC},
        TPPi: {DC},
        NTPPi: {DC},
    },
    EC: {
        DC: {DC},
        EC: {DC, EC},
        PO: {DC, EC, PO},
        EQ: {EC},
        TPP: {EC, PO},
        NTPP: {PO},
        TPPi: {EC},
        NTPPi: {EC, PO},
    },
    PO: {
        DC: {DC},
        EC: {DC, EC, PO},
        PO: {DC, EC, PO, TPP, TPPi},
        EQ: {PO},
        TPP: {PO, TPP},
        NTPP: {TPP},
        TPPi: {PO, TPPi},
        NTPPi: {TPPi},
    },
    EQ: {
        r: {r} for r in BASE_RELATIONS
    },
    TPP: {
        DC: {DC},
        EC: {EC},
        PO: {PO},
        EQ: {TPP},
        TPP: {TPP},
        NTPP: {NTPP},
        TPPi: {PO, EC, DC},
        NTPPi: {PO, EC, DC},
    },
    NTPP: {
        DC: {DC},
        EC: {EC},
        PO: {PO},
        EQ: {NTPP},
        TPP: {NTPP},
        NTPP: {NTPP},
        TPPi: {PO, EC, DC},
        NTPPi: {PO, EC, DC},
    },
    TPPi: {
        DC: {DC},
        EC: {EC},
        PO: {PO},
        EQ: {TPPi},
        TPP: {PO, EC, DC},
        NTPP: {PO, EC, DC},
        TPPi: {TPPi},
        NTPPi: {NTPPi},
    },
    NTPPi: {
        DC: {DC},
        EC: {EC},
        PO: {PO},
        EQ: {NTPPi},
        TPP: {PO, EC, DC},
        NTPP: {PO, EC, DC},
        TPPi: {NTPPi},
        NTPPi: {NTPPi},
    }
}


def compose(r1, r2):
    """Compose two RCC8 relations (sets)."""
    result = set()
    for a, b in product(r1, r2):
        result |= COMPOSITION[a][b]
    return result


# ============================================================
# RCC8 CONSTRAINT NETWORK
# ============================================================

class RCC8Network:
    def __init__(self):
        self.nodes = set()
        self.constraints = defaultdict(lambda: set(BASE_RELATIONS))

    def add_node(self, x):
        self.nodes.add(x)

    def add_constraint(self, x, y, relations):
        self.add_node(x)
        self.add_node(y)
        self.constraints[(x, y)] &= set(relations)
        self.constraints[(y, x)] &= self.inverse(relations)

    def inverse(self, relations):
        inv = set()
        for r in relations:
            if r == TPP:
                inv.add(TPPi)
            elif r == NTPP:
                inv.add(NTPPi)
            elif r == TPPi:
                inv.add(TPP)
            elif r == NTPPi:
                inv.add(NTPP)
            else:
                inv.add(r)
        return inv

    def propagate(self):
        """Path-consistency propagation"""
        changed = True
        while changed:
            changed = False
            for x, y, z in product(self.nodes, repeat=3):
                if x == y or y == z or x == z:
                    continue

                xy = self.constraints[(x, y)]
                yz = self.constraints[(y, z)]
                xz = self.constraints[(x, z)]

                inferred = compose(xy, yz)
                new_xz = xz & inferred

                if new_xz != xz:
                    if not new_xz:
                        raise ValueError(f"Inconsistency detected: {x}, {y}, {z}")
                    self.constraints[(x, z)] = new_xz
                    self.constraints[(z, x)] = self.inverse(new_xz)
                    changed = True

    # ========================================================
    # DEDUCTION
    # ========================================================

    def deduce(self):
        self.propagate()
        return dict(self.constraints)

    # ========================================================
    # ABDUCTION (Simple)
    # ========================================================

    def abduct(self, observation):
        """
        observation = (x, y, relation)
        Returns minimal assumptions that explain it
        """
        x, y, r = observation
        possible = []
        for a, b in product(self.nodes, repeat=2):
            if (a, b) == (x, y):
                continue
            for rel in BASE_RELATIONS:
                temp = RCC8Network()
                temp.nodes = set(self.nodes)
                temp.constraints = defaultdict(lambda: set(BASE_RELATIONS),
                                               {k: set(v) for k, v in self.constraints.items()})
                temp.add_constraint(a, b, {rel})
                try:
                    temp.propagate()
                    if r in temp.constraints[(x, y)]:
                        possible.append((a, b, rel))
                except ValueError:
                    pass
        return possible

    # ========================================================
    # PROBABILISTIC INFERENCE
    # ========================================================

    def probabilistic_relation(self, x, y):
        """
        Uniform probability over remaining relations
        """
        rels = self.constraints[(x, y)]
        p = 1.0 / len(rels)
        return {r: p for r in rels}


# ============================================================
# TESTS / EXAMPLES
# ============================================================

def test_deduction():
    print("\n=== Deduction Test ===")
    net = RCC8Network()
    net.add_constraint("A", "B", {TPP})
    net.add_constraint("B", "C", {EQ})
    net.propagate()
    print("A C:", net.constraints[("A", "C")])

def test_inconsistency():
    print("\n=== Inconsistency Test ===")
    net = RCC8Network()
    net.add_constraint("A", "B", {DC})
    net.add_constraint("B", "C", {EQ})
    net.add_constraint("A", "C", {PO})
    try:
        net.propagate()
    except ValueError as e:
        print("Correctly detected inconsistency:", e)

def test_abduction():
    print("\n=== Abduction Test ===")
    net = RCC8Network()
    net.add_constraint("A", "B", {TPP})
    net.add_constraint("B", "C", {TPP})
    explanations = net.abduct(("A", "C", NTPP))
    print("Possible explanations:")
    for e in explanations[:5]:
        print(e)

def test_probability():
    print("\n=== Probabilistic Inference Test ===")
    net = RCC8Network()
    net.add_constraint("A", "B", {PO, EC})
    probs = net.probabilistic_relation("A", "B")
    for r, p in probs.items():
        print(f"P({r}) = {p:.2f}")

def test_full():
    test_deduction()
    test_inconsistency()
    test_abduction()
    test_probability()

if __name__ == "__main__":
    test_full()
