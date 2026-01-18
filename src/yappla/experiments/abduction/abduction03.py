"""
Complete Abductive Logic Programming Engine
Implements abductive reasoning with multiple optimization strategies
"""

from dataclasses import dataclass, field
from typing import Set, List, Dict, Tuple, Optional, FrozenSet
from collections import defaultdict
import heapq
from itertools import combinations, product
import re


# ============================================================================
# BASIC DATA STRUCTURES
# ============================================================================

@dataclass(frozen=True)
class Term:
    """Represents a term (constant or variable)"""
    value: str
    is_variable: bool = field(default=False, compare=False)
    
    def __post_init__(self):
        # Variables start with uppercase
        object.__setattr__(self, 'is_variable', self.value[0].isupper() if self.value else False)
    
    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Atom:
    """Represents an atom: predicate(term1, term2, ...)"""
    predicate: str
    terms: Tuple[Term, ...]
    negated: bool = False
    
    @property
    def arity(self):
        return len(self.terms)
    
    def __str__(self):
        args = ', '.join(str(t) for t in self.terms)
        atom_str = f"{self.predicate}({args})" if self.terms else self.predicate
        return f"not {atom_str}" if self.negated else atom_str
    
    def negate(self):
        return Atom(self.predicate, self.terms, not self.negated)
    
    def ground(self, substitution: Dict[str, Term]) -> 'Atom':
        """Apply substitution to create ground atom"""
        new_terms = tuple(
            substitution.get(t.value, t) if t.is_variable else t
            for t in self.terms
        )
        return Atom(self.predicate, new_terms, self.negated)
    
    def is_ground(self) -> bool:
        """Check if atom contains no variables"""
        return all(not t.is_variable for t in self.terms)


@dataclass
class Rule:
    """Represents a rule: head :- body"""
    head: Atom
    body: List[Atom] = field(default_factory=list)
    
    def __str__(self):
        if not self.body:
            return str(self.head)
        body_str = ', '.join(str(atom) for atom in self.body)
        return f"{self.head} :- {body_str}"


@dataclass
class KnowledgeBase:
    """Knowledge base containing facts and rules"""
    facts: Set[Atom] = field(default_factory=set)
    rules: List[Rule] = field(default_factory=list)
    constraints: List[Atom] = field(default_factory=list)
    
    def add_fact(self, atom: Atom):
        """Add a ground fact"""
        if not atom.is_ground():
            raise ValueError(f"Facts must be ground: {atom}")
        self.facts.add(atom)
    
    def add_rule(self, rule: Rule):
        """Add a rule"""
        self.rules.append(rule)
    
    def add_constraint(self, atom: Atom):
        """Add an integrity constraint (must not be provable)"""
        self.constraints.append(atom)
    
    def copy(self):
        """Create a copy of the knowledge base"""
        kb = KnowledgeBase()
        kb.facts = self.facts.copy()
        kb.rules = self.rules.copy()
        kb.constraints = self.constraints.copy()
        return kb


# ============================================================================
# UNIFICATION AND SUBSTITUTION
# ============================================================================

def unify(term1: Term, term2: Term, subst: Dict[str, Term] = None) -> Optional[Dict[str, Term]]:
    """Unify two terms, return substitution or None if unification fails"""
    if subst is None:
        subst = {}
    
    # Dereference variables
    while term1.is_variable and term1.value in subst:
        term1 = subst[term1.value]
    while term2.is_variable and term2.value in subst:
        term2 = subst[term2.value]
    
    # Same term
    if term1 == term2:
        return subst
    
    # Variable cases
    if term1.is_variable:
        subst = subst.copy()
        subst[term1.value] = term2
        return subst
    if term2.is_variable:
        subst = subst.copy()
        subst[term2.value] = term1
        return subst
    
    # Constants don't match
    return None


def unify_atoms(atom1: Atom, atom2: Atom) -> Optional[Dict[str, Term]]:
    """Unify two atoms"""
    if atom1.predicate != atom2.predicate or atom1.arity != atom2.arity:
        return None
    if atom1.negated != atom2.negated:
        return None
    
    subst = {}
    for t1, t2 in zip(atom1.terms, atom2.terms):
        subst = unify(t1, t2, subst)
        if subst is None:
            return None
    
    return subst


# ============================================================================
# ENTAILMENT ENGINE (SLD Resolution)
# ============================================================================

class EntailmentEngine:
    """Simple backward chaining proof engine"""
    
    def __init__(self, max_depth=50):
        self.max_depth = max_depth
    
    def prove(self, kb: KnowledgeBase, goal: Atom, depth=0) -> bool:
        """Prove goal from knowledge base using SLD resolution"""
        if depth > self.max_depth:
            return False
        
        # Handle negation-as-failure
        if goal.negated:
            return not self.prove(kb, goal.negate(), depth)
        
        # Check facts
        for fact in kb.facts:
            if unify_atoms(goal, fact) is not None:
                return True
        
        # Check rules
        for rule in kb.rules:
            subst = unify_atoms(goal, rule.head)
            if subst is not None:
                # Prove all body literals
                body_goals = [lit.ground(subst) for lit in rule.body]
                if self.prove_all(kb, body_goals, depth + 1):
                    return True
        
        return False
    
    def prove_all(self, kb: KnowledgeBase, goals: List[Atom], depth=0) -> bool:
        """Prove all goals"""
        if not goals:
            return True
        return all(self.prove(kb, goal, depth) for goal in goals)


# ============================================================================
# EXPLANATION DATA STRUCTURE
# ============================================================================

@dataclass
class Explanation:
    """Represents a candidate explanation with metrics"""
    hypotheses: Set[Atom]
    covered_observations: Set[Atom]
    cost: float
    
    def __lt__(self, other):
        # For priority queue: prefer more coverage, then lower cost
        if len(self.covered_observations) != len(other.covered_observations):
            return len(self.covered_observations) > len(other.covered_observations)
        return self.cost < other.cost
    
    def __str__(self):
        hyp_str = '{' + ', '.join(str(h) for h in sorted(self.hypotheses, key=str)) + '}'
        return f"Explanation(hypotheses={hyp_str}, coverage={len(self.covered_observations)}, cost={self.cost})"


# ============================================================================
# ABDUCTIVE REASONER
# ============================================================================

class AbductiveReasoner:
    """Main abductive reasoning engine"""
    
    def __init__(self, kb: KnowledgeBase, engine: EntailmentEngine = None):
        self.kb = kb
        self.engine = engine or EntailmentEngine()
        self.abducibles: Set[Tuple[str, int]] = set()  # (predicate, arity)
        self.abducible_costs: Dict[Tuple[str, int], float] = {}
        
        # Caching
        self.entailment_cache: Dict = {}
        self.coverage_cache: Dict = {}
    
    def declare_abducible(self, predicate: str, arity: int, cost: float = 1.0):
        """Mark a predicate as abducible with optional cost"""
        self.abducibles.add((predicate, arity))
        self.abducible_costs[(predicate, arity)] = cost
    
    def abduce(self, observations: List[Atom], 
               strategy: str = 'greedy_coverage',
               max_size: int = 10,
               beam_width: int = 5) -> List[Explanation]:
        """
        Find explanations for observations
        
        Args:
            observations: List of atoms to explain
            strategy: 'greedy_coverage', 'branch_and_bound', or 'beam_search'
            max_size: Maximum explanation size
            beam_width: For beam search
        
        Returns:
            List of explanations ranked by quality
        """
        # Clear caches for new query
        self.entailment_cache.clear()
        self.coverage_cache.clear()
        
        observations_set = set(observations)
        
        # Filter already explained observations
        unexplained = self._filter_unexplained(observations_set)
        
        if not unexplained:
            return [Explanation(set(), observations_set, 0.0)]
        
        # Route to appropriate strategy
        if strategy == 'greedy_coverage':
            return self._greedy_coverage_search(observations_set, unexplained, max_size)
        elif strategy == 'branch_and_bound':
            return self._branch_and_bound_search(observations_set, unexplained, max_size)
        elif strategy == 'beam_search':
            return self._beam_search(observations_set, unexplained, max_size, beam_width)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _filter_unexplained(self, observations: Set[Atom]) -> Set[Atom]:
        """Return observations not already provable from KB"""
        unexplained = set()
        for obs in observations:
            if not self._prove_cached(self.kb, obs, frozenset()):
                unexplained.add(obs)
        return unexplained
    
    def _greedy_coverage_search(self, all_observations: Set[Atom],
                                unexplained: Set[Atom], 
                                max_size: int) -> List[Explanation]:
        """Greedy algorithm: select abducible with best coverage repeatedly"""
        remaining = unexplained.copy()
        hypothesis = set()
        
        max_iterations = max_size * 2  # Safety limit
        iteration = 0
        
        while remaining and len(hypothesis) < max_size and iteration < max_iterations:
            iteration += 1
            best_abducible = None
            best_coverage = set()
            best_score = -1
            
            # Generate candidates (limit to avoid explosion)
            candidates = self._generate_candidate_abducibles(remaining)
            
            # Limit number of candidates to check
            candidates = list(candidates)[:50]
            
            for abducible in candidates:
                if abducible in hypothesis:
                    continue
                
                # Test coverage
                test_hypothesis = hypothesis | {abducible}
                coverage = self._compute_coverage(test_hypothesis, remaining)
                
                if not coverage:
                    continue
                
                # Score: coverage / cost ratio
                score = len(coverage) / self._get_cost(abducible)
                
                if score > best_score:
                    best_score = score
                    best_abducible = abducible
                    best_coverage = coverage
            
            if best_abducible is None:
                break
            
            # Add best abducible
            hypothesis.add(best_abducible)
            remaining -= best_coverage
            
            # Consistency check
            if not self._is_consistent(hypothesis):
                hypothesis.remove(best_abducible)
                continue
        
        # Final verification
        if self._is_valid_explanation(hypothesis, all_observations):
            covered = self._compute_coverage(hypothesis, all_observations)
            cost = sum(self._get_cost(h) for h in hypothesis)
            return [Explanation(hypothesis, covered, cost)]
        
        return []
    
    def _branch_and_bound_search(self, all_observations: Set[Atom],
                                 unexplained: Set[Atom],
                                 max_size: int) -> List[Explanation]:
        """Branch and bound search for optimal explanation"""
        best_solution = None
        best_cost = float('inf')
        
        # Build relevance map
        relevance_map = self._build_relevance_map(unexplained)
        
        # Priority queue: (lower_bound, current_cost, hypothesis, remaining)
        initial_lb = self._lower_bound(set(), unexplained, relevance_map)
        queue = [(initial_lb, 0.0, frozenset(), frozenset(unexplained))]
        
        iterations = 0
        max_iterations = 10000
        
        while queue and iterations < max_iterations:
            iterations += 1
            lb, current_cost, hypothesis_frozen, remaining_frozen = heapq.heappop(queue)
            
            hypothesis = set(hypothesis_frozen)
            remaining = set(remaining_frozen)
            
            # Pruning
            if lb >= best_cost:
                continue
            if current_cost >= max_size:
                continue
            
            # Goal check
            if not remaining:
                if current_cost < best_cost and self._is_consistent(hypothesis):
                    best_cost = current_cost
                    covered = self._compute_coverage(hypothesis, all_observations)
                    best_solution = Explanation(hypothesis, covered, current_cost)
                continue
            
            # Branch
            candidates = self._get_relevant_abducibles(remaining, relevance_map)
            
            for abducible in candidates:
                if abducible in hypothesis:
                    continue
                
                new_hypothesis = hypothesis | {abducible}
                
                # Quick consistency check
                if not self._is_consistent(new_hypothesis):
                    continue
                
                # Compute coverage
                new_coverage = self._compute_coverage({abducible}, remaining)
                new_remaining = remaining - new_coverage
                new_cost = current_cost + self._get_cost(abducible)
                
                # Lower bound
                new_lb = new_cost + self._lower_bound(
                    new_hypothesis, new_remaining, relevance_map
                )
                
                if new_lb < best_cost:
                    heapq.heappush(queue, (
                        new_lb,
                        new_cost,
                        frozenset(new_hypothesis),
                        frozenset(new_remaining)
                    ))
        
        return [best_solution] if best_solution else []
    
    def _beam_search(self, all_observations: Set[Atom],
                    unexplained: Set[Atom],
                    max_size: int,
                    beam_width: int) -> List[Explanation]:
        """Beam search: keep top-k candidates at each level"""
        beam = [Explanation(set(), set(), 0.0)]
        
        for depth in range(max_size):
            candidates = []
            
            for current in beam:
                remaining = unexplained - current.covered_observations
                
                if not remaining:
                    candidates.append(current)
                    continue
                
                # Generate successors
                abducibles = self._generate_candidate_abducibles(remaining)
                
                for abd in abducibles:
                    if abd in current.hypotheses:
                        continue
                    
                    new_hyp = current.hypotheses | {abd}
                    
                    if not self._is_consistent(new_hyp):
                        continue
                    
                    new_coverage = current.covered_observations | \
                                 self._compute_coverage({abd}, unexplained)
                    new_cost = current.cost + self._get_cost(abd)
                    
                    candidates.append(Explanation(new_hyp, new_coverage, new_cost))
            
            if not candidates:
                break
            
            # Keep top beam_width
            candidates.sort(reverse=True)
            beam = candidates[:beam_width]
            
            # Check for complete solutions
            complete = [exp for exp in beam 
                       if len(exp.covered_observations) == len(unexplained)]
            if complete:
                return complete
        
        return beam[:beam_width]
    
    def _build_relevance_map(self, observations: Set[Atom]) -> Dict[Atom, Set[Atom]]:
        """Map each observation to relevant abducibles"""
        relevance_map = {}
        for obs in observations:
            relevance_map[obs] = self._backward_chain_abducibles(obs)
        return relevance_map
    
    def _backward_chain_abducibles(self, observation: Atom) -> Set[Atom]:
        """Find abducibles that could help prove observation"""
        relevant = set()
        visited = set()
        max_relevant = 20  # Limit to prevent explosion
        
        # Direct match
        if (observation.predicate, observation.arity) in self.abducibles:
            if observation.is_ground():
                relevant.add(observation)
            else:
                # Generate groundings
                groundings = self._generate_groundings(observation)
                relevant.update(list(groundings)[:max_relevant])
        
        if len(relevant) >= max_relevant:
            return relevant
        
        # Check rules (only one level deep to avoid infinite recursion)
        for rule in self.kb.rules:
            subst = unify_atoms(observation, rule.head)
            if subst is not None:
                for body_literal in rule.body:
                    grounded = body_literal.ground(subst)
                    
                    if (grounded.predicate, grounded.arity) in self.abducibles:
                        if grounded.is_ground():
                            relevant.add(grounded)
                            if len(relevant) >= max_relevant:
                                return relevant
                        else:
                            groundings = self._generate_groundings(grounded)
                            for g in list(groundings)[:max_relevant - len(relevant)]:
                                relevant.add(g)
                            if len(relevant) >= max_relevant:
                                return relevant
        
        return relevant
    
    def _generate_candidate_abducibles(self, observations: Set[Atom]) -> Set[Atom]:
        """Generate candidate abducibles for observations"""
        candidates = set()
        for obs in observations:
            candidates.update(self._backward_chain_abducibles(obs))
        return candidates
    
    def _generate_groundings(self, atom: Atom, max_per_var: int = 3) -> Set[Atom]:
        """Generate ground instances of atom"""
        if atom.is_ground():
            return {atom}
        
        # Extract constants from KB
        constants = self._extract_constants()
        if not constants:
            constants = {Term('a'), Term('b'), Term('c')}
        
        # Limit to avoid explosion
        constants = list(constants)[:max_per_var]
        
        # Limit total groundings
        if len(constants) == 0:
            return set()
        
        # Find variables and their positions
        var_positions = [i for i, t in enumerate(atom.terms) if t.is_variable]
        
        if not var_positions:
            return {atom}
        
        # Limit combinatorial explosion
        max_groundings = 10
        groundings = set()
        
        for values in product(constants, repeat=len(var_positions)):
            if len(groundings) >= max_groundings:
                break
            subst = {atom.terms[pos].value: val 
                    for pos, val in zip(var_positions, values)}
            grounded = atom.ground(subst)
            groundings.add(grounded)
        
        return groundings
    
    def _extract_constants(self) -> Set[Term]:
        """Extract all constants from KB"""
        constants = set()
        for fact in self.kb.facts:
            constants.update(t for t in fact.terms if not t.is_variable)
        for rule in self.kb.rules:
            constants.update(t for t in rule.head.terms if not t.is_variable)
            for atom in rule.body:
                constants.update(t for t in atom.terms if not t.is_variable)
        return constants
    
    def _compute_coverage(self, hypothesis: Set[Atom], observations: Set[Atom]) -> Set[Atom]:
        """Determine which observations are explained by hypothesis"""
        cache_key = (frozenset(hypothesis), frozenset(observations))
        if cache_key in self.coverage_cache:
            return self.coverage_cache[cache_key]
        
        covered = set()
        augmented_kb = self._augment_kb(hypothesis)
        
        for obs in observations:
            if self._prove_cached(augmented_kb, obs, frozenset(hypothesis)):
                covered.add(obs)
        
        self.coverage_cache[cache_key] = covered
        return covered
    
    def _is_valid_explanation(self, hypothesis: Set[Atom], observations: Set[Atom]) -> bool:
        """Check if hypothesis explains all observations and is consistent"""
        augmented_kb = self._augment_kb(hypothesis)
        
        # Check all observations
        for obs in observations:
            if not self._prove_cached(augmented_kb, obs, frozenset(hypothesis)):
                return False
        
        return self._is_consistent(hypothesis)
    
    def _is_consistent(self, hypothesis: Set[Atom]) -> bool:
        """Check consistency of KB with hypothesis"""
        augmented_kb = self._augment_kb(hypothesis)
        
        # Check constraints
        for constraint in augmented_kb.constraints:
            if self.engine.prove(augmented_kb, constraint):
                return False
        
        # Check for contradictions (p and not p)
        for fact in augmented_kb.facts:
            if self.engine.prove(augmented_kb, fact.negate()):
                return False
        
        return True
    
    def _augment_kb(self, hypothesis: Set[Atom]) -> KnowledgeBase:
        """Create KB augmented with hypothesis"""
        augmented = self.kb.copy()
        for atom in hypothesis:
            augmented.add_fact(atom)
        return augmented
    
    def _prove_cached(self, kb: KnowledgeBase, goal: Atom, hyp_key: FrozenSet) -> bool:
        """Cached prove"""
        cache_key = (id(kb), goal, hyp_key)
        if cache_key not in self.entailment_cache:
            self.entailment_cache[cache_key] = self.engine.prove(kb, goal)
        return self.entailment_cache[cache_key]
    
    def _get_cost(self, abducible: Atom) -> float:
        """Get cost of abducible"""
        key = (abducible.predicate, abducible.arity)
        return self.abducible_costs.get(key, 1.0)
    
    def _get_relevant_abducibles(self, observations: Set[Atom], 
                                relevance_map: Dict) -> Set[Atom]:
        """Get abducibles relevant to observations"""
        relevant = set()
        for obs in observations:
            if obs in relevance_map:
                relevant.update(relevance_map[obs])
        return relevant
    
    def _lower_bound(self, current_hyp: Set[Atom], 
                    remaining: Set[Atom],
                    relevance_map: Dict) -> float:
        """Estimate minimum cost to cover remaining observations"""
        if not remaining:
            return 0.0
        
        # Optimistic: assume each abducible covers maximum observations
        uncovered = remaining.copy()
        total_cost = 0.0
        
        while uncovered:
            best_coverage = 0
            best_cost = float('inf')
            
            for obs in uncovered:
                for abd in relevance_map.get(obs, set()):
                    if abd in current_hyp:
                        continue
                    
                    # Count how many uncovered observations this could cover
                    coverage = sum(1 for o in uncovered if abd in relevance_map.get(o, set()))
                    cost = self._get_cost(abd)
                    
                    if coverage > best_coverage or (coverage == best_coverage and cost < best_cost):
                        best_coverage = coverage
                        best_cost = cost
            
            if best_coverage == 0:
                return float('inf')
            
            # Optimistically remove best_coverage observations
            uncovered = set(list(uncovered)[best_coverage:])
            total_cost += best_cost
        
        return total_cost


# ============================================================================
# PARSER (Simple parser for convenience)
# ============================================================================

def parse_atom(s: str) -> Atom:
    """Parse atom from string like 'bird(tweety)' or 'not flies(X)'"""
    s = s.strip()
    negated = False
    
    if s.startswith('not '):
        negated = True
        s = s[4:].strip()
    
    match = re.match(r'(\w+)\((.*)\)', s)
    if match:
        predicate = match.group(1)
        args_str = match.group(2).strip()
        if args_str:
            terms = tuple(Term(arg.strip()) for arg in args_str.split(','))
        else:
            terms = ()
    else:
        # Propositional atom
        predicate = s
        terms = ()
    
    return Atom(predicate, terms, negated)


def parse_rule(s: str) -> Rule:
    """Parse rule from string like 'flies(X) :- bird(X), not abnormal(X)'"""
    if ':-' in s:
        head_str, body_str = s.split(':-', 1)
        head = parse_atom(head_str.strip())
        body = [parse_atom(b.strip()) for b in body_str.split(',')]
        return Rule(head, body)
    else:
        # Just a fact
        return Rule(parse_atom(s.strip()))


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    print("=" * 70)
    print("ABDUCTIVE LOGIC PROGRAMMING ENGINE - EXAMPLES")
    print("=" * 70)
    
    # Example 1: Medical Diagnosis
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Medical Diagnosis")
    print("=" * 70)
    
    kb1 = KnowledgeBase()
    
    # Rules
    kb1.add_rule(parse_rule("not_working(X) :- sick(X)"))
    kb1.add_rule(parse_rule("not_working(X) :- tired(X)"))
    kb1.add_rule(parse_rule("not_working(X) :- injured(X)"))
    kb1.add_rule(parse_rule("irritable(X) :- stressed(X)"))
    kb1.add_rule(parse_rule("irritable(X) :- tired(X)"))
    kb1.add_rule(parse_rule("irritable(X) :- sick(X)"))
    
    # Facts
    kb1.add_fact(parse_atom("person(alice)"))
    kb1.add_fact(parse_atom("person(bob)"))
    
    engine1 = EntailmentEngine()
    abducer1 = AbductiveReasoner(kb1, engine1)
    
    # Declare abducibles with costs
    abducer1.declare_abducible("sick", 1, cost=2.0)
    abducer1.declare_abducible("tired", 1, cost=1.0)
    abducer1.declare_abducible("stressed", 1, cost=1.5)
    abducer1.declare_abducible("injured", 1, cost=3.0)
    
    # Observations
    observations1 = [
        parse_atom("not_working(alice)"),
        parse_atom("irritable(alice)")
    ]
    
    print("\nKnowledge Base:")
    for rule in kb1.rules:
        print(f"  {rule}")
    
    print("\nObservations:")
    for obs in observations1:
        print(f"  {obs}")
    
    print("\n--- Greedy Coverage Strategy ---")
    print("EXPECTED: Explanation(hypotheses={tired(alice)}, coverage=2, cost=1.0)")
    print("ANALYSIS: tired(alice) covers both not_working and irritable with minimum cost")
    explanations = abducer1.abduce(observations1, strategy='greedy_coverage')
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    print("\n--- Branch and Bound Strategy ---")
    print("EXPECTED: Explanation(hypotheses={tired(alice)}, coverage=2, cost=1.0)")
    print("ANALYSIS: Optimal explanation - tired is cheapest solution covering both observations")
    explanations = abducer1.abduce(observations1, strategy='branch_and_bound', max_size=5)
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    print("\n--- Beam Search Strategy ---")
    print("EXPECTED: Explanation(hypotheses={tired(alice)}, coverage=2, cost=1.0)")
    print("ANALYSIS: Should find same optimal solution as branch and bound")
    explanations = abducer1.abduce(observations1, strategy='beam_search', beam_width=3)
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    # Example 2: Animal Classification
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Animal Classification")
    print("=" * 70)
    
    kb2 = KnowledgeBase()
    
    # Rules
    kb2.add_rule(parse_rule("flies(X) :- bird(X), not abnormal(X)"))
    kb2.add_rule(parse_rule("has_feathers(X) :- bird(X)"))
    kb2.add_rule(parse_rule("lays_eggs(X) :- bird(X)"))
    kb2.add_rule(parse_rule("swims(X) :- penguin(X)"))
    kb2.add_rule(parse_rule("bird(X) :- penguin(X)"))
    kb2.add_rule(parse_rule("abnormal(X) :- penguin(X)"))
    
    # Facts
    kb2.add_fact(parse_atom("animal(tweety)"))
    kb2.add_fact(parse_atom("animal(opus)"))
    
    engine2 = EntailmentEngine()
    abducer2 = AbductiveReasoner(kb2, engine2)
    
    # Declare abducibles
    abducer2.declare_abducible("bird", 1)
    abducer2.declare_abducible("penguin", 1)
    abducer2.declare_abducible("abnormal", 1)
    
    observations2 = [
        parse_atom("has_feathers(tweety)"),
        parse_atom("flies(tweety)"),
    ]
    
    print("\nKnowledge Base:")
    for rule in kb2.rules:
        print(f"  {rule}")
    
    print("\nObservations:")
    for obs in observations2:
        print(f"  {obs}")
    
    print("\n--- Explanations ---")
    print("EXPECTED: Explanation(hypotheses={bird(tweety)}, coverage=2, cost=1)")
    print("ANALYSIS: bird(tweety) entails has_feathers(tweety) and flies(tweety)")
    print("          (since abnormal(tweety) is not abduced, not abnormal(tweety) is true)")
    explanations = abducer2.abduce(observations2, strategy='branch_and_bound')
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    # Example 3: Non-flying bird
    observations3 = [
        parse_atom("has_feathers(opus)"),
        parse_atom("not flies(opus)"),
    ]
    
    print("\nObservations for opus:")
    for obs in observations3:
        print(f"  {obs}")
    
    print("\n--- Explanations ---")
    print("EXPECTED: Explanation(hypotheses={bird(opus), abnormal(opus)}, coverage=2, cost=2)")
    print("ANALYSIS: To explain not flies(opus), need bird(opus) AND abnormal(opus)")
    print("          - bird(opus) is needed for has_feathers(opus)")
    print("          - abnormal(opus) makes flies(opus) false via negation-as-failure")
    explanations = abducer2.abduce(observations3, strategy='branch_and_bound')
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    # Example 4: Complex scenario with multiple observations
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Technical Support Diagnosis")
    print("=" * 70)
    
    kb3 = KnowledgeBase()
    
    # Rules
    kb3.add_rule(parse_rule("no_display(X) :- power_issue(X)"))
    kb3.add_rule(parse_rule("no_display(X) :- broken_screen(X)"))
    kb3.add_rule(parse_rule("no_boot(X) :- power_issue(X)"))
    kb3.add_rule(parse_rule("no_boot(X) :- hard_drive_failure(X)"))
    kb3.add_rule(parse_rule("slow_performance(X) :- insufficient_ram(X)"))
    kb3.add_rule(parse_rule("slow_performance(X) :- malware(X)"))
    kb3.add_rule(parse_rule("overheating(X) :- dust_buildup(X)"))
    kb3.add_rule(parse_rule("overheating(X) :- fan_failure(X)"))
    
    # Facts
    kb3.add_fact(parse_atom("computer(laptop1)"))
    
    engine3 = EntailmentEngine()
    abducer3 = AbductiveReasoner(kb3, engine3)
    
    # Declare abducibles with different costs
    abducer3.declare_abducible("power_issue", 1, cost=2.0)
    abducer3.declare_abducible("broken_screen", 1, cost=5.0)
    abducer3.declare_abducible("hard_drive_failure", 1, cost=4.0)
    abducer3.declare_abducible("insufficient_ram", 1, cost=1.5)
    abducer3.declare_abducible("malware", 1, cost=1.0)
    abducer3.declare_abducible("dust_buildup", 1, cost=1.0)
    abducer3.declare_abducible("fan_failure", 1, cost=3.0)
    
    observations3 = [
        parse_atom("no_display(laptop1)"),
        parse_atom("no_boot(laptop1)")
    ]
    
    print("\nKnowledge Base:")
    for rule in kb3.rules:
        print(f"  {rule}")
    
    print("\nObservations:")
    for obs in observations3:
        print(f"  {obs}")
    
    print("\n--- Branch and Bound (finds optimal explanation) ---")
    print("EXPECTED: Explanation(hypotheses={power_issue(laptop1)}, coverage=2, cost=2.0)")
    print("ANALYSIS: power_issue explains both no_display and no_boot with cost 2.0")
    print("          - Much better than broken_screen(5.0) + hard_drive_failure(4.0)")
    explanations = abducer3.abduce(observations3, strategy='branch_and_bound', max_size=5)
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    print("\n--- Greedy Coverage (fast heuristic) ---")
    print("EXPECTED: Explanation(hypotheses={power_issue(laptop1)}, coverage=2, cost=2.0)")
    print("ANALYSIS: Greedy should also find power_issue as it covers both observations")
    explanations = abducer3.abduce(observations3, strategy='greedy_coverage', max_size=5)
    for exp in explanations:
        print(f"ACTUAL:   {exp}")
    
    # Example 4: Comparison of strategies on complex case
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Strategy Comparison")
    print("=" * 70)
    
    observations4 = [
        parse_atom("no_display(laptop1)"),
        parse_atom("no_boot(laptop1)"),
        parse_atom("slow_performance(laptop1)")
    ]
    
    print("\nMultiple observations:")
    for obs in observations4:
        print(f"  {obs}")
    
    print("\n--- Greedy Coverage ---")
    print("EXPECTED: Explanation(hypotheses={power_issue(laptop1), malware(laptop1)}, coverage=3, cost=3.0)")
    print("ANALYSIS: power_issue(2.0) covers no_display & no_boot")
    print("          malware(1.0) covers slow_performance")
    print("          Total cost: 2.0 + 1.0 = 3.0 (optimal)")
    explanations = abducer3.abduce(observations4, strategy='greedy_coverage', max_size=5)
    for i, exp in enumerate(explanations, 1):
        print(f"{i}. ACTUAL:   {exp}")
    
    print("\n--- Branch and Bound (optimal) ---")
    print("EXPECTED: Explanation(hypotheses={power_issue(laptop1), malware(laptop1)}, coverage=3, cost=3.0)")
    print("ANALYSIS: Should find the optimal minimal explanation")
    explanations = abducer3.abduce(observations4, strategy='branch_and_bound', max_size=5)
    for i, exp in enumerate(explanations, 1):
        print(f"{i}. ACTUAL:   {exp}")
    
    print("\n--- Beam Search (beam_width=3) ---")
    print("EXPECTED: Top result should have {power_issue(laptop1), malware(laptop1)} with cost=3.0")
    print("ANALYSIS: Beam search should maintain optimal in top-k beam")
    explanations = abducer3.abduce(observations4, strategy='beam_search', beam_width=3, max_size=5)
    for i, exp in enumerate(explanations, 1):
        print(f"{i}. ACTUAL:   {exp}")
    
    print("\n" + "=" * 70)
    print("Analysis:")
    print("  - power_issue(laptop1) explains both no_display and no_boot")
    print("  - This is preferred due to parsimony (Occam's Razor)")
    print("  - Additional hypothesis needed for slow_performance")
    print("  - Branch & Bound finds the optimal minimal explanation")
    print("=" * 70)


if __name__ == "__main__":
    main()
