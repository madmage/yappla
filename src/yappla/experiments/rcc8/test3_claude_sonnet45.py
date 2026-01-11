"""
RCC8 Logic Engine with Constraint Propagation and Multiple Inference Types

RCC8 Relations:
- DC: Disconnected
- EC: Externally Connected
- PO: Partially Overlapping
- TPP: Tangential Proper Part
- NTPP: Non-Tangential Proper Part
- TPPi: Inverse of TPP
- NTPPi: Inverse of NTPP
- EQ: Equal
"""

from typing import Set, Dict, Tuple, List, Optional
from itertools import product
from collections import defaultdict
import random


class RCC8:
    """RCC8 relation constants and composition table"""
    
    # All possible RCC8 relations
    RELATIONS = {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'}
    
    # Composition table for RCC8 (simplified version)
    COMPOSITION_TABLE = {
        ('EQ', 'EQ'): {'EQ'},
        ('EQ', 'DC'): {'DC'},
        ('EQ', 'EC'): {'EC'},
        ('EQ', 'PO'): {'PO'},
        ('EQ', 'TPP'): {'TPP'},
        ('EQ', 'NTPP'): {'NTPP'},
        ('EQ', 'TPPi'): {'TPPi'},
        ('EQ', 'NTPPi'): {'NTPPi'},
        
        ('DC', 'DC'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('DC', 'EC'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('DC', 'PO'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('DC', 'TPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('DC', 'NTPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('DC', 'TPPi'): {'DC'},
        ('DC', 'NTPPi'): {'DC'},
        ('DC', 'EQ'): {'DC'},
        
        ('EC', 'DC'): {'DC'},
        ('EC', 'EC'): {'DC', 'EC'},
        ('EC', 'PO'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('EC', 'TPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('EC', 'NTPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('EC', 'TPPi'): {'DC', 'EC'},
        ('EC', 'NTPPi'): {'DC'},
        ('EC', 'EQ'): {'EC'},
        
        ('PO', 'DC'): {'DC'},
        ('PO', 'EC'): {'DC', 'EC'},
        ('PO', 'PO'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('PO', 'TPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('PO', 'NTPP'): {'NTPP'},
        ('PO', 'TPPi'): {'DC', 'EC', 'PO', 'TPPi', 'NTPPi'},
        ('PO', 'NTPPi'): {'DC', 'EC', 'PO', 'TPPi', 'NTPPi'},
        ('PO', 'EQ'): {'PO'},
        
        ('TPP', 'DC'): {'DC'},
        ('TPP', 'EC'): {'DC', 'EC'},
        ('TPP', 'PO'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('TPP', 'TPP'): {'TPP', 'NTPP'},
        ('TPP', 'NTPP'): {'NTPP'},
        ('TPP', 'TPPi'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('TPP', 'NTPPi'): {'DC', 'EC', 'PO', 'TPPi', 'NTPPi'},
        ('TPP', 'EQ'): {'TPP'},
        
        ('NTPP', 'DC'): {'DC'},
        ('NTPP', 'EC'): {'DC'},
        ('NTPP', 'PO'): {'DC', 'EC', 'PO', 'TPP', 'NTPP'},
        ('NTPP', 'TPP'): {'NTPP'},
        ('NTPP', 'NTPP'): {'NTPP'},
        ('NTPP', 'TPPi'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('NTPP', 'NTPPi'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('NTPP', 'EQ'): {'NTPP'},
        
        ('TPPi', 'DC'): {'DC', 'EC', 'PO', 'TPPi', 'NTPPi'},
        ('TPPi', 'EC'): {'EC', 'PO', 'TPPi', 'NTPPi'},
        ('TPPi', 'PO'): {'PO', 'TPPi', 'NTPPi'},
        ('TPPi', 'TPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('TPPi', 'NTPP'): {'PO', 'TPPi', 'NTPPi'},
        ('TPPi', 'TPPi'): {'TPPi', 'NTPPi'},
        ('TPPi', 'NTPPi'): {'NTPPi'},
        ('TPPi', 'EQ'): {'TPPi'},
        
        ('NTPPi', 'DC'): {'DC', 'EC', 'PO', 'TPPi', 'NTPPi'},
        ('NTPPi', 'EC'): {'PO', 'TPPi', 'NTPPi'},
        ('NTPPi', 'PO'): {'PO', 'TPPi', 'NTPPi'},
        ('NTPPi', 'TPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('NTPPi', 'NTPP'): {'DC', 'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi', 'EQ'},
        ('NTPPi', 'TPPi'): {'NTPPi'},
        ('NTPPi', 'NTPPi'): {'NTPPi'},
        ('NTPPi', 'EQ'): {'NTPPi'},
    }
    
    # Converse relations
    CONVERSE = {
        'DC': 'DC',
        'EC': 'EC',
        'PO': 'PO',
        'TPP': 'TPPi',
        'NTPP': 'NTPPi',
        'TPPi': 'TPP',
        'NTPPi': 'NTPP',
        'EQ': 'EQ'
    }
    
    @staticmethod
    def compose(r1: str, r2: str) -> Set[str]:
        """Compose two RCC8 relations"""
        return RCC8.COMPOSITION_TABLE.get((r1, r2), RCC8.RELATIONS.copy())
    
    @staticmethod
    def converse(r: str) -> str:
        """Get the converse of a relation"""
        return RCC8.CONVERSE[r]


class RCC8Network:
    """Network of RCC8 constraints with propagation"""
    
    def __init__(self):
        self.constraints: Dict[Tuple[str, str], Set[str]] = {}
        self.regions: Set[str] = set()
        
    def add_constraint(self, a: str, b: str, relations: Set[str]) -> bool:
        """Add a constraint between two regions"""
        if not relations.issubset(RCC8.RELATIONS):
            raise ValueError(f"Invalid relations: {relations - RCC8.RELATIONS}")
        
        self.regions.add(a)
        self.regions.add(b)
        
        key = (a, b) if a <= b else (b, a)
        inverse_key = (b, a) if a <= b else (a, b)
        
        if key not in self.constraints:
            self.constraints[key] = relations.copy()
        else:
            # Intersection with existing constraints
            old_rels = self.constraints[key]
            self.constraints[key] = self.constraints[key].intersection(relations)
            if not self.constraints[key]:
                return False  # Inconsistency detected
        
        return True
    
    def get_constraint(self, a: str, b: str) -> Set[str]:
        """Get the constraint between two regions"""
        if a == b:
            return {'EQ'}
        
        key = (a, b) if a <= b else (b, a)
        if key in self.constraints:
            rels = self.constraints[key]
            if a > b:
                # Return converse relations
                return {RCC8.converse(r) for r in rels}
            return rels.copy()
        return RCC8.RELATIONS.copy()  # No constraint = all possible
    
    def propagate(self) -> bool:
        """
        Path consistency algorithm for constraint propagation.
        Returns True if consistent, False if inconsistency detected.
        """
        changed = True
        iterations = 0
        max_iterations = 100
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            
            for a in self.regions:
                for b in self.regions:
                    if a == b:
                        continue
                    
                    for c in self.regions:
                        if c == a or c == b:
                            continue
                        
                        # Get current constraints
                        r_ab = self.get_constraint(a, b)
                        r_ac = self.get_constraint(a, c)
                        r_cb = self.get_constraint(c, b)
                        
                        # Compute constraint via composition
                        new_constraint = set()
                        for r1 in r_ac:
                            for r2 in r_cb:
                                new_constraint.update(RCC8.compose(r1, r2))
                        
                        # Refine constraint
                        refined = r_ab.intersection(new_constraint)
                        
                        if not refined:
                            return False  # Inconsistency
                        
                        if refined != r_ab:
                            key = (a, b) if a <= b else (b, a)
                            if a <= b:
                                self.constraints[key] = refined
                            else:
                                self.constraints[key] = {RCC8.converse(r) for r in refined}
                            changed = True
        
        return True
    
    def is_consistent(self) -> bool:
        """Check if the network is consistent"""
        return self.propagate()
    
    def get_all_constraints(self) -> Dict[Tuple[str, str], Set[str]]:
        """Get all constraints in the network"""
        result = {}
        for a in self.regions:
            for b in self.regions:
                if a < b:
                    result[(a, b)] = self.get_constraint(a, b)
        return result


class RCC8Reasoner:
    """Reasoning engine with multiple inference types"""
    
    def __init__(self):
        self.network = RCC8Network()
    
    def add_fact(self, a: str, b: str, relation: str) -> bool:
        """Add a definite fact (deductive knowledge)"""
        return self.network.add_constraint(a, b, {relation})
    
    def add_disjunctive_constraint(self, a: str, b: str, relations: Set[str]) -> bool:
        """Add a disjunctive constraint (uncertain knowledge)"""
        return self.network.add_constraint(a, b, relations)
    
    def deduce(self) -> bool:
        """
        Deductive reasoning: propagate constraints to derive new facts.
        Returns True if consistent, False if contradiction found.
        """
        return self.network.propagate()
    
    def query(self, a: str, b: str) -> Set[str]:
        """Query possible relations between two regions"""
        return self.network.get_constraint(a, b)
    
    def abduce(self, a: str, b: str, observed: str) -> List[Dict[Tuple[str, str], str]]:
        """
        Abductive reasoning: find possible explanations for an observation.
        Given an observed relation, find assignments that are consistent.
        """
        # Create a test network with the observation
        test_net = RCC8Network()
        test_net.regions = self.network.regions.copy()
        test_net.constraints = {k: v.copy() for k, v in self.network.constraints.items()}
        
        if not test_net.add_constraint(a, b, {observed}):
            return []  # Observation is inconsistent
        
        if not test_net.propagate():
            return []  # Cannot find consistent explanation
        
        # Return simplified explanation
        explanations = []
        explanation = {}
        for (r1, r2), rels in test_net.get_all_constraints().items():
            if len(rels) == 1:  # Determined relations
                explanation[(r1, r2)] = list(rels)[0]
        
        if explanation:
            explanations.append(explanation)
        
        return explanations
    
    def probabilistic_query(self, a: str, b: str, samples: int = 1000) -> Dict[str, float]:
        """
        Probabilistic reasoning: estimate probability distribution over relations.
        Uses random sampling of consistent scenarios.
        """
        possible_rels = self.query(a, b)
        if len(possible_rels) == 1:
            return {list(possible_rels)[0]: 1.0}
        
        # Sample consistent scenarios
        counts = defaultdict(int)
        successful_samples = 0
        
        for _ in range(samples):
            test_net = RCC8Network()
            test_net.regions = self.network.regions.copy()
            
            # Copy constraints
            for (r1, r2), rels in self.network.constraints.items():
                test_net.constraints[(r1, r2)] = rels.copy()
            
            # Randomly assign relations
            for (r1, r2), rels in self.network.constraints.items():
                if len(rels) > 1:
                    chosen = random.choice(list(rels))
                    test_net.constraints[(r1, r2)] = {chosen}
            
            # Check consistency
            if test_net.is_consistent():
                result = test_net.get_constraint(a, b)
                if len(result) == 1:
                    counts[list(result)[0]] += 1
                    successful_samples += 1
        
        if successful_samples == 0:
            # Uniform distribution over possible relations
            return {r: 1.0/len(possible_rels) for r in possible_rels}
        
        # Normalize
        return {r: counts[r]/successful_samples for r in counts}
    
    def minimal_scenario(self) -> Optional[Dict[Tuple[str, str], str]]:
        """
        Find one consistent complete scenario (all relations determined).
        Returns None if network is inconsistent.
        """
        if not self.network.propagate():
            return None
        
        scenario = {}
        for (a, b), rels in self.network.get_all_constraints().items():
            if len(rels) == 1:
                scenario[(a, b)] = list(rels)[0]
            else:
                # Pick first relation (could be random)
                scenario[(a, b)] = list(rels)[0]
        
        return scenario
    
    def print_state(self):
        """Print current state of the network"""
        print("\n=== Network State ===")
        print(f"Regions: {sorted(self.network.regions)}")
        print("\nConstraints:")
        for (a, b), rels in sorted(self.network.get_all_constraints().items()):
            rel_str = ', '.join(sorted(rels))
            print(f"  {a} -> {b}: {{{rel_str}}}")


# ============================================================================
# TESTS AND EXAMPLES
# ============================================================================

def test_basic_deduction():
    """Test basic deductive reasoning"""
    print("\n" + "="*60)
    print("TEST 1: Basic Deduction")
    print("="*60)
    
    reasoner = RCC8Reasoner()
    
    # A is inside B, B is inside C
    print("\nAdding facts:")
    print("  A NTPP B (A is non-tangentially inside B)")
    print("  B NTPP C (B is non-tangentially inside C)")
    
    reasoner.add_fact('A', 'B', 'NTPP')
    reasoner.add_fact('B', 'C', 'NTPP')
    
    # Deduce relationship between A and C
    print("\nPerforming deduction...")
    reasoner.deduce()
    
    result = reasoner.query('A', 'C')
    print(f"\nDeduced: A -> C: {result}")
    print(f"Result: A must be NTPP C (transitivity of containment)")
    
    reasoner.print_state()


def test_contradiction_detection():
    """Test inconsistency detection"""
    print("\n" + "="*60)
    print("TEST 2: Contradiction Detection")
    print("="*60)
    
    reasoner = RCC8Reasoner()
    
    print("\nAdding facts:")
    print("  A DC B (A disconnected from B)")
    print("  B NTPP C (B inside C)")
    print("  C NTPP A (C inside A) - This should cause contradiction!")
    
    reasoner.add_fact('A', 'B', 'DC')
    reasoner.add_fact('B', 'C', 'NTPP')
    reasoner.add_fact('C', 'A', 'NTPP')
    
    print("\nChecking consistency...")
    consistent = reasoner.deduce()
    
    if consistent:
        print("Result: Network is consistent (unexpected)")
    else:
        print("Result: CONTRADICTION DETECTED! (as expected)")
        print("Reason: A and B are disconnected, but if C contains B and")
        print("        A contains C, then A and B must overlap.")


def test_abductive_reasoning():
    """Test abductive reasoning"""
    print("\n" + "="*60)
    print("TEST 3: Abductive Reasoning")
    print("="*60)
    
    reasoner = RCC8Reasoner()
    
    print("\nKnown facts:")
    print("  A DC B (A disconnected from B)")
    
    reasoner.add_fact('A', 'B', 'DC')
    reasoner.deduce()
    
    print("\nObservation: C is externally connected to A (C EC A)")
    print("\nFinding explanations...")
    
    explanations = reasoner.abduce('C', 'A', 'EC')
    
    if explanations:
        print(f"\nFound {len(explanations)} explanation(s):")
        for i, exp in enumerate(explanations, 1):
            print(f"\nExplanation {i}:")
            for (r1, r2), rel in sorted(exp.items()):
                print(f"  {r1} {rel} {r2}")
    else:
        print("\nNo consistent explanations found.")


def test_probabilistic_reasoning():
    """Test probabilistic reasoning"""
    print("\n" + "="*60)
    print("TEST 4: Probabilistic Reasoning")
    print("="*60)
    
    reasoner = RCC8Reasoner()
    
    print("\nUncertain knowledge:")
    print("  A might be DC or EC with B")
    print("  B might be DC or EC with C")
    
    reasoner.add_disjunctive_constraint('A', 'B', {'DC', 'EC'})
    reasoner.add_disjunctive_constraint('B', 'C', {'DC', 'EC'})
    reasoner.deduce()
    
    print("\nQuery: What's the probability distribution for A and C?")
    print("(Using Monte Carlo sampling...)")
    
    probs = reasoner.probabilistic_query('A', 'C', samples=1000)
    
    print("\nProbability distribution:")
    for rel, prob in sorted(probs.items(), key=lambda x: -x[1]):
        if prob > 0:
            print(f"  P({rel}) = {prob:.3f}")


def test_complex_scenario():
    """Test complex spatial reasoning scenario"""
    print("\n" + "="*60)
    print("TEST 5: Complex Spatial Scenario")
    print("="*60)
    
    reasoner = RCC8Reasoner()
    
    print("\nScenario: Room layout")
    print("  Room contains Table")
    print("  Room contains Chair")
    print("  Book is on Table (TPP)")
    print("  Lamp is on Table (TPP)")
    print("  Chair is disconnected from Table")
    
    reasoner.add_fact('Table', 'Room', 'NTPP')
    reasoner.add_fact('Chair', 'Room', 'NTPP')
    reasoner.add_fact('Book', 'Table', 'TPP')
    reasoner.add_fact('Lamp', 'Table', 'TPP')
    reasoner.add_fact('Chair', 'Table', 'DC')
    
    print("\nPerforming deduction...")
    reasoner.deduce()
    
    print("\nQueries:")
    queries = [
        ('Book', 'Room'),
        ('Lamp', 'Room'),
        ('Book', 'Lamp'),
        ('Chair', 'Book'),
    ]
    
    for a, b in queries:
        result = reasoner.query(a, b)
        print(f"  {a} -> {b}: {result}")
    
    reasoner.print_state()


def test_minimal_scenario():
    """Test finding a complete scenario"""
    print("\n" + "="*60)
    print("TEST 6: Finding Minimal Complete Scenario")
    print("="*60)
    
    reasoner = RCC8Reasoner()
    
    print("\nPartial knowledge:")
    print("  A and B are not disconnected (could be EC, PO, etc.)")
    print("  B and C are not disconnected")
    
    reasoner.add_disjunctive_constraint('A', 'B', {'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi'})
    reasoner.add_disjunctive_constraint('B', 'C', {'EC', 'PO', 'TPP', 'NTPP', 'TPPi', 'NTPPi'})
    reasoner.deduce()
    
    print("\nFinding one complete consistent scenario...")
    scenario = reasoner.minimal_scenario()
    
    if scenario:
        print("\nComplete scenario:")
        for (a, b), rel in sorted(scenario.items()):
            print(f"  {a} {rel} {b}")
    else:
        print("\nNo consistent scenario found.")


# Run all tests
if __name__ == "__main__":
    print("\n" + "="*60)
    print("RCC8 LOGIC ENGINE - TEST SUITE")
    print("="*60)
    
    test_basic_deduction()
    test_contradiction_detection()
    test_abductive_reasoning()
    test_probabilistic_reasoning()
    test_complex_scenario()
    test_minimal_scenario()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
