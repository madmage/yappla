"""
Complete Rule Induction System implementing three different strategies:
- Top-Down (FOIL-style)
- Bottom-Up (GOLEM-style)  
- Inverse Entailment (Progol-style)
"""

import math
from typing import List, Set, Dict, Optional
from abc import ABC, abstractmethod


# ============================================================================
# Core Data Structures
# ============================================================================

class Atom:
    """Represents a logical atom: predicate(arg1, arg2, ...)"""
    
    def __init__(self, predicate: str, args: List[str]):
        self.predicate = predicate
        self.args = args
    
    def get_variables(self) -> Set[str]:
        """Extract all variables (uppercase start)"""
        return {arg for arg in self.args if self.is_variable(arg)}
    
    @staticmethod
    def is_variable(term: str) -> bool:
        """Check if term is a variable (starts with uppercase)"""
        return term and term[0].isupper()
    
    def apply_substitution(self, subst: Dict[str, str]) -> 'Atom':
        """Apply substitution to create new atom"""
        new_args = [subst.get(arg, arg) for arg in self.args]
        return Atom(self.predicate, new_args)
    
    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        return self.predicate == other.predicate and self.args == other.args
    
    def __hash__(self):
        return hash((self.predicate, tuple(self.args)))
    
    def __repr__(self):
        args_str = ', '.join(self.args)
        return f"{self.predicate}({args_str})"


class RuleTemplate:
    """Represents a rule: head ← body1 ∧ body2 ∧ ..."""
    
    def __init__(self, head: Atom, body: List[Atom]):
        self.head = head
        self.body = body
        self.variables = self._extract_variables()
    
    def _extract_variables(self) -> Set[str]:
        """Extract all variables from head and body"""
        vars_set = set()
        for atom in [self.head] + self.body:
            vars_set.update(atom.get_variables())
        return vars_set
    
    def apply_substitution(self, subst: Dict[str, str]) -> 'RuleTemplate':
        """Apply substitution to entire rule"""
        new_head = self.head.apply_substitution(subst)
        new_body = [atom.apply_substitution(subst) for atom in self.body]
        return RuleTemplate(new_head, new_body)
    
    def __eq__(self, other):
        if not isinstance(other, RuleTemplate):
            return False
        return self.head == other.head and self.body == other.body
    
    def __hash__(self):
        return hash((self.head, tuple(self.body)))
    
    def __repr__(self):
        if not self.body:
            return f"{self.head} ← true"
        body_str = " ∧ ".join(str(atom) for atom in self.body)
        return f"{self.head} ← {body_str}"


class ModeDeclaration:
    """Mode declaration for predicates: specifies input/output positions"""
    
    def __init__(self, predicate: str, argument_modes: List[str]):
        self.predicate = predicate
        self.argument_modes = argument_modes
    
    def __repr__(self):
        modes = ','.join(self.argument_modes)
        return f"mode({self.predicate}({modes}))"


class KnowledgeBase:
    """Knowledge base containing facts and rules"""
    
    def __init__(self):
        self.facts: List[Atom] = []
        self.rules: List[RuleTemplate] = []
    
    def add_fact(self, fact: Atom):
        self.facts.append(fact)
    
    def add_rule(self, rule: RuleTemplate):
        self.rules.append(rule)
    
    def copy(self) -> 'KnowledgeBase':
        kb = KnowledgeBase()
        kb.facts = self.facts.copy()
        kb.rules = self.rules.copy()
        return kb


# ============================================================================
# Utilities
# ============================================================================

class UnificationEngine:
    """Handles unification and substitution"""
    
    @staticmethod
    def unify(atom1: Atom, atom2: Atom, subst: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """Unify two atoms, return substitution or None if fails"""
        if subst is None:
            subst = {}
        
        if atom1.predicate != atom2.predicate:
            return None
        if len(atom1.args) != len(atom2.args):
            return None
        
        subst = subst.copy()
        
        for arg1, arg2 in zip(atom1.args, atom2.args):
            arg1 = subst.get(arg1, arg1)
            arg2 = subst.get(arg2, arg2)
            
            if arg1 == arg2:
                continue
            elif Atom.is_variable(arg1):
                subst[arg1] = arg2
            elif Atom.is_variable(arg2):
                subst[arg2] = arg1
            else:
                return None
        
        return subst


class EntailmentChecker:
    """Simple backward chaining entailment checker"""
    
    @staticmethod
    def entails(kb: KnowledgeBase, query: Atom, max_depth: int = 5) -> bool:
        """Check if KB entails query using backward chaining"""
        return EntailmentChecker._prove(kb, query, {}, max_depth, set())
    
    @staticmethod
    def _prove(kb: KnowledgeBase, goal: Atom, subst: Dict[str, str], 
               depth: int, visited: Set[str]) -> bool:
        """Backward chaining proof"""
        if depth <= 0:
            return False
        
        goal = goal.apply_substitution(subst)
        goal_str = str(goal)
        
        if goal_str in visited:
            return False
        visited.add(goal_str)
        
        # Try facts
        for fact in kb.facts:
            new_subst = UnificationEngine.unify(goal, fact, subst)
            if new_subst is not None:
                return True
        
        # Try rules
        for rule in kb.rules:
            renamed_rule = EntailmentChecker._rename_rule_variables(rule)
            head_subst = UnificationEngine.unify(goal, renamed_rule.head, subst)
            
            if head_subst is not None:
                if EntailmentChecker._prove_conjunction(kb, renamed_rule.body, 
                                                       head_subst, depth - 1, visited):
                    return True
        
        return False
    
    @staticmethod
    def _prove_conjunction(kb: KnowledgeBase, goals: List[Atom], 
                          subst: Dict[str, str], depth: int, visited: Set[str]) -> bool:
        """Prove conjunction of goals"""
        if not goals:
            return True
        
        goal = goals[0].apply_substitution(subst)
        remaining = goals[1:]
        
        if EntailmentChecker._prove(kb, goal, subst, depth, visited.copy()):
            if not remaining:
                return True
            return EntailmentChecker._prove_conjunction(kb, remaining, subst, depth, visited)
        
        return False
    
    @staticmethod
    def _rename_rule_variables(rule: RuleTemplate, suffix: str = "_r") -> RuleTemplate:
        """Rename all variables in a rule"""
        var_map = {var: var + suffix for var in rule.variables}
        return rule.apply_substitution(var_map)


class CoverageComputer:
    """Computes which examples are covered by a rule"""
    
    @staticmethod
    def compute_coverage(rule: RuleTemplate, examples: List[Atom], 
                        kb: KnowledgeBase) -> Set[Atom]:
        """Determine which examples are covered by rule + KB"""
        covered = set()
        temp_kb = kb.copy()
        temp_kb.add_rule(rule)
        
        for example in examples:
            if EntailmentChecker.entails(temp_kb, example):
                covered.add(example)
        
        return covered


# ============================================================================
# Base Induction Class
# ============================================================================

class BaseInducer(ABC):
    """Abstract base class for rule induction"""
    
    def __init__(self, background_kb: KnowledgeBase, mode_declarations: Dict[str, ModeDeclaration]):
        self.background_kb = background_kb
        self.mode_declarations = mode_declarations
        self.coverage_computer = CoverageComputer()
    
    @abstractmethod
    def induce(self, positive_examples: List[Atom], 
               negative_examples: List[Atom]) -> List[RuleTemplate]:
        """Induce rules from examples"""
        pass
    
    def compute_coverage(self, rule: RuleTemplate, examples: List[Atom]) -> Set[Atom]:
        """Helper to compute coverage"""
        return self.coverage_computer.compute_coverage(rule, examples, self.background_kb)


# ============================================================================
# Top-Down Inducer (FOIL-style)
# ============================================================================

class TopDownInducer(BaseInducer):
    """Top-down rule induction using covering approach"""
    
    def __init__(self, background_kb: KnowledgeBase, mode_declarations: Dict[str, ModeDeclaration],
                 max_body_length: int = 5):
        super().__init__(background_kb, mode_declarations)
        self.max_body_length = max_body_length
        self.var_counter = 0
    
    def induce(self, positive_examples: List[Atom], 
               negative_examples: List[Atom]) -> List[RuleTemplate]:
        """Top-down covering algorithm"""
        induced_rules = []
        uncovered = set(positive_examples)
        
        while uncovered:
            rule = self._learn_single_rule(list(uncovered), negative_examples)
            
            if rule is None:
                break
            
            induced_rules.append(rule)
            covered = self.compute_coverage(rule, list(uncovered))
            uncovered -= covered
        
        return induced_rules
    
    def _learn_single_rule(self, positives: List[Atom], 
                          negatives: List[Atom]) -> Optional[RuleTemplate]:
        """Learn a single rule using greedy refinement"""
        if not positives:
            return None
        
        target_pred = positives[0].predicate
        arity = len(positives[0].args)
        head_vars = [f"X{i}" for i in range(arity)]
        
        current_rule = RuleTemplate(Atom(target_pred, head_vars), [])
        
        covered_pos = set(positives)
        covered_neg = self.compute_coverage(current_rule, negatives)
        
        # Continue refining while:
        # 1. We cover negatives (need to specialize), OR
        # 2. We can improve positive coverage without covering negatives
        while len(current_rule.body) < self.max_body_length:
            candidates = self._generate_refinements(current_rule)
            
            if not candidates:
                break
            
            best_rule = None
            best_score = -float('inf')
            best_pos = set()
            best_neg = set()
            
            for candidate in candidates:
                pos_cov = self.compute_coverage(candidate, positives)
                neg_cov = self.compute_coverage(candidate, negatives)
                
                if not pos_cov:
                    continue
                
                score = self._compute_gain(len(covered_pos), len(covered_neg),
                                          len(pos_cov), len(neg_cov))
                
                if score > best_score:
                    best_score = score
                    best_rule = candidate
                    best_pos = pos_cov
                    best_neg = neg_cov
            
            if best_rule is None or best_score <= 0:
                break
            
            current_rule = best_rule
            covered_pos = best_pos
            covered_neg = best_neg
            
            # Stop if we cover no negatives and all positives
            if not covered_neg and len(covered_pos) == len(positives):
                break
        
        # Accept rule if it covers some positives and no negatives
        if covered_pos and not covered_neg:
            return current_rule
        return None
    
    def _generate_refinements(self, rule: RuleTemplate) -> List[RuleTemplate]:
        """Generate all valid one-step refinements"""
        refinements = []
        current_vars = rule.variables
        
        for pred_name, mode_decl in self.mode_declarations.items():
            if pred_name == rule.head.predicate:
                continue
            
            literals = self._generate_literals_from_mode(mode_decl, current_vars)
            
            for literal in literals:
                new_body = rule.body + [literal]
                refinements.append(RuleTemplate(rule.head, new_body))
        
        return refinements
    
    def _generate_literals_from_mode(self, mode_decl: ModeDeclaration, 
                                    existing_vars: Set[str]) -> List[Atom]:
        """Generate literals based on mode declaration"""
        literals = []
        
        def generate_args(modes: List[str], idx: int = 0) -> List[List[str]]:
            if idx >= len(modes):
                return [[]]
            
            mode = modes[idx]
            rest = generate_args(modes, idx + 1)
            result = []
            
            if mode == '+':
                for var in existing_vars:
                    for r in rest:
                        result.append([var] + r)
            elif mode == '-':
                new_var = f"V{self.var_counter}"
                self.var_counter += 1
                for r in rest:
                    result.append([new_var] + r)
            
            return result if result else [[]]
        
        arg_combos = generate_args(mode_decl.argument_modes)
        
        for args in arg_combos:
            if args:
                literals.append(Atom(mode_decl.predicate, args))
        
        return literals
    
    def _compute_gain(self, p0: int, n0: int, p1: int, n1: int) -> float:
        """Compute FOIL information gain"""
        if p1 == 0:
            return -float('inf')
        
        def info(p: int, n: int) -> float:
            if p + n == 0 or p == 0:
                return 0
            return -math.log2(p / (p + n))
        
        return p1 * (info(p0, n0) - info(p1, n1))


# ============================================================================
# Bottom-Up Inducer (GOLEM-style)
# ============================================================================

class BottomUpInducer(BaseInducer):
    """Bottom-up rule induction via least general generalization"""
    
    def induce(self, positive_examples: List[Atom], 
               negative_examples: List[Atom]) -> List[RuleTemplate]:
        """Bottom-up induction via LGG"""
        if not positive_examples:
            return []
        
        if len(positive_examples) == 1:
            return [self._ground_rule(positive_examples[0])]
        
        current_rule = self._lgg(positive_examples[0], positive_examples[1])
        
        for example in positive_examples[2:]:
            current_rule = self._lgg_with_rule(current_rule, example)
        
        if negative_examples:
            neg_covered = self.compute_coverage(current_rule, negative_examples)
            if neg_covered:
                current_rule = self._reduce_rule(current_rule, positive_examples, 
                                                negative_examples)
        
        return [current_rule] if current_rule else []
    
    def _ground_rule(self, example: Atom) -> RuleTemplate:
        """Create ground rule from single example"""
        body = []
        for fact in self.background_kb.facts:
            if any(arg in example.args for arg in fact.args):
                body.append(fact)
        
        return RuleTemplate(example, body)
    
    def _lgg(self, ex1: Atom, ex2: Atom) -> RuleTemplate:
        """Least general generalization of two examples"""
        var_map = {}
        var_counter = [0]
        
        def get_var(t1: str, t2: str) -> str:
            if t1 == t2:
                return t1
            key = (t1, t2)
            if key not in var_map:
                var_map[key] = f"X{var_counter[0]}"
                var_counter[0] += 1
            return var_map[key]
        
        head_args = [get_var(a1, a2) for a1, a2 in zip(ex1.args, ex2.args)]
        head = Atom(ex1.predicate, head_args)
        
        # Get variables that appear in head
        head_vars = set(head.get_variables())
        
        body = []
        ex_args_set = set(ex1.args + ex2.args)
        
        for f1 in self.background_kb.facts:
            for f2 in self.background_kb.facts:
                if f1.predicate == f2.predicate and len(f1.args) == len(f2.args):
                    # Only include facts relevant to the examples
                    if any(arg in ex_args_set for arg in f1.args + f2.args):
                        gen_args = [get_var(a1, a2) 
                                   for a1, a2 in zip(f1.args, f2.args)]
                        gen_atom = Atom(f1.predicate, gen_args)
                        
                        # Only include if: 
                        # 1. Not already in body
                        # 2. Not a ground atom (all constants)
                        # 3. Contains at least one variable from head (connected)
                        has_head_var = any(arg in head_vars for arg in gen_atom.get_variables())
                        is_ground = len(gen_atom.get_variables()) == 0
                        
                        if gen_atom not in body and not is_ground and has_head_var:
                            body.append(gen_atom)
        
        return RuleTemplate(head, body)
    
    def _lgg_with_rule(self, rule: RuleTemplate, example: Atom) -> RuleTemplate:
        """Generalize rule with new example"""
        var_map = {}
        var_counter = [0]
        
        def get_var(t1: str, t2: str) -> str:
            if t1 == t2:
                return t1
            key = (t1, t2)
            if key not in var_map:
                var_map[key] = f"Y{var_counter[0]}"
                var_counter[0] += 1
            return var_map[key]
        
        head_args = [get_var(a1, a2) 
                    for a1, a2 in zip(rule.head.args, example.args)]
        new_head = Atom(rule.head.predicate, head_args)
        
        return RuleTemplate(new_head, rule.body)
    
    def _reduce_rule(self, rule: RuleTemplate, positives: List[Atom], 
                    negatives: List[Atom]) -> Optional[RuleTemplate]:
        """Reduce overly-general rule"""
        current_rule = rule
        
        for i in range(len(rule.body)):
            candidate_body = rule.body[:i] + rule.body[i+1:]
            candidate = RuleTemplate(rule.head, candidate_body)
            
            pos_cov = self.compute_coverage(candidate, positives)
            neg_cov = self.compute_coverage(candidate, negatives)
            
            if len(pos_cov) == len(positives) and not neg_cov:
                current_rule = candidate
                return self._reduce_rule(current_rule, positives, negatives)
        
        return current_rule


# ============================================================================
# Inverse Entailment Inducer (Progol-style)
# ============================================================================

class InverseEntailmentInducer(BaseInducer):
    """Inverse entailment-based induction"""
    
    def __init__(self, background_kb: KnowledgeBase, 
                 mode_declarations: Dict[str, ModeDeclaration],
                 max_bottom_depth: int = 2):
        super().__init__(background_kb, mode_declarations)
        self.max_bottom_depth = max_bottom_depth
    
    def induce(self, positive_examples: List[Atom], 
               negative_examples: List[Atom]) -> List[RuleTemplate]:
        """Inverse entailment induction"""
        induced_rules = []
        uncovered = set(positive_examples)
        
        while uncovered:
            seed = next(iter(uncovered))
            
            bottom = self._construct_bottom(seed)
            
            if bottom is None:
                break
            
            hypothesis = self._search_generalizations(bottom, positive_examples, 
                                                     negative_examples)
            
            if hypothesis:
                induced_rules.append(hypothesis)
                covered = self.compute_coverage(hypothesis, list(uncovered))
                uncovered -= covered
            else:
                uncovered.discard(seed)
        
        return induced_rules
    
    def _construct_bottom(self, example: Atom) -> Optional[RuleTemplate]:
        """Construct bottom clause (most specific hypothesis)"""
        head_vars = [f"X{i}" for i in range(len(example.args))]
        head = Atom(example.predicate, head_vars)
        
        theta = {example.args[i]: head_vars[i] for i in range(len(example.args))}
        
        body = []
        var_counter = [len(head_vars)]
        head_vars_set = set(head_vars)
        
        queue = [(set(example.args), 0)]
        
        while queue:
            current_terms, depth = queue.pop(0)
            
            if depth >= self.max_bottom_depth:
                continue
            
            for fact in self.background_kb.facts:
                if fact.predicate == example.predicate:
                    continue
                
                # Check if fact relates to current terms
                if any(arg in current_terms for arg in fact.args):
                    var_args = []
                    new_terms = set()
                    
                    for arg in fact.args:
                        if arg not in theta:
                            theta[arg] = f"V{var_counter[0]}"
                            var_counter[0] += 1
                            new_terms.add(arg)
                        var_args.append(theta[arg])
                    
                    var_atom = Atom(fact.predicate, var_args)
                    
                    # Only add if: 
                    # 1. Not already in body
                    # 2. Contains at least one head variable (connected to example)
                    has_head_var = any(arg in head_vars_set for arg in var_atom.get_variables())
                    
                    if var_atom not in body and has_head_var:
                        body.append(var_atom)
                        
                        if new_terms and depth < self.max_bottom_depth - 1:
                            queue.append((new_terms, depth + 1))
        
        return RuleTemplate(head, body) if body else None
    
    def _search_generalizations(self, bottom: RuleTemplate, 
                               positives: List[Atom],
                               negatives: List[Atom]) -> Optional[RuleTemplate]:
        """Search for good generalization using beam search"""
        beam_width = 5
        beam = [(self._evaluate_rule(bottom, positives, negatives), bottom)]
        best_rule = None
        best_score = -float('inf')
        
        visited = set()
        
        for _ in range(10):
            next_beam = []
            
            for score, rule in beam:
                rule_str = str(rule)
                if rule_str in visited:
                    continue
                visited.add(rule_str)
                
                pos_cov = self.compute_coverage(rule, positives)
                neg_cov = self.compute_coverage(rule, negatives)
                
                if pos_cov and not neg_cov:
                    if len(pos_cov) > best_score:
                        best_score = len(pos_cov)
                        best_rule = rule
                
                for gen in self._generalize_rule(rule):
                    gen_score = self._evaluate_rule(gen, positives, negatives)
                    next_beam.append((gen_score, gen))
            
            if not next_beam:
                break
            
            next_beam.sort(reverse=True, key=lambda x: x[0])
            beam = next_beam[:beam_width]
        
        return best_rule
    
    def _generalize_rule(self, rule: RuleTemplate) -> List[RuleTemplate]:
        """Generate generalizations by removing literals"""
        generalizations = []
        
        # Remove each literal one at a time
        for i in range(len(rule.body)):
            new_body = rule.body[:i] + rule.body[i+1:]
            if new_body:
                # Check if remaining literals still connect to head
                new_rule = RuleTemplate(rule.head, new_body)
                if self._is_connected(new_rule):
                    generalizations.append(new_rule)
        
        return generalizations
    
    def _is_connected(self, rule: RuleTemplate) -> bool:
        """Check if all body variables are connected to head variables"""
        head_vars = rule.head.get_variables()
        
        # Build connectivity graph
        connected = set(head_vars)
        changed = True
        
        while changed:
            changed = False
            for atom in rule.body:
                atom_vars = atom.get_variables()
                # If atom shares variables with connected set, add all its variables
                if atom_vars & connected:
                    before = len(connected)
                    connected |= atom_vars
                    if len(connected) > before:
                        changed = True
        
        # All body variables should be reachable from head
        all_body_vars = set()
        for atom in rule.body:
            all_body_vars |= atom.get_variables()
        
        return all_body_vars.issubset(connected)
    
    def _evaluate_rule(self, rule: RuleTemplate, positives: List[Atom],
                      negatives: List[Atom]) -> float:
        """Heuristic evaluation"""
        pos_cov = len(self.compute_coverage(rule, positives))
        neg_cov = len(self.compute_coverage(rule, negatives))
        
        if neg_cov > 0:
            return -float('inf')
        
        compression = len(positives) - len(rule.body)
        return pos_cov + 0.1 * compression


# ============================================================================
# Tests
# ============================================================================

def test_semantic_equivalence(rules_dict: Dict[str, List[RuleTemplate]], 
                             positives: List[Atom], 
                             negatives: List[Atom],
                             kb: KnowledgeBase) -> None:
    """Test if all learned rules have the same semantic coverage"""
    print("\n  Semantic Equivalence Check:")
    print("  " + "-" * 36)
    
    coverages = {}
    for name, rules in rules_dict.items():
        if not rules:
            coverages[name] = (set(), set())
            continue
        
        # Combine coverage from all rules for this method
        all_pos_covered = set()
        all_neg_covered = set()
        
        for rule in rules:
            pos_cov = CoverageComputer.compute_coverage(rule, positives, kb)
            neg_cov = CoverageComputer.compute_coverage(rule, negatives, kb)
            all_pos_covered |= pos_cov
            all_neg_covered |= neg_cov
        
        coverages[name] = (all_pos_covered, all_neg_covered)
        print(f"  {name}: covers {len(all_pos_covered)}/{len(positives)} positives, "
              f"{len(all_neg_covered)}/{len(negatives)} negatives")
    
    # Check equivalence
    coverage_values = list(coverages.values())
    if not coverage_values:
        return
    
    first_coverage = coverage_values[0]
    all_same = all(cov == first_coverage for cov in coverage_values)
    
    if all_same:
        print("  ✓ All methods have SAME semantic coverage")
    else:
        print("  ✗ Methods have DIFFERENT semantic coverage")
        for name, (pos, neg) in coverages.items():
            print(f"    {name}: pos={pos}, neg={neg}")


def test_family_relations():
    """Test learning family relations"""
    print("=" * 80)
    print("TEST: Family Relations")
    print("=" * 80)
    
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", ["tom", "bob"]))
    kb.add_fact(Atom("parent", ["tom", "liz"]))
    kb.add_fact(Atom("parent", ["bob", "ann"]))
    kb.add_fact(Atom("parent", ["bob", "pat"]))
    kb.add_fact(Atom("parent", ["pat", "jim"]))
    kb.add_fact(Atom("male", ["tom"]))
    kb.add_fact(Atom("male", ["bob"]))
    kb.add_fact(Atom("male", ["jim"]))
    kb.add_fact(Atom("female", ["liz"]))
    kb.add_fact(Atom("female", ["ann"]))
    kb.add_fact(Atom("female", ["pat"]))
    
    modes = {
        "parent": ModeDeclaration("parent", ['+', '-']),
        "male": ModeDeclaration("male", ['+']),
        "female": ModeDeclaration("female", ['+']),
    }
    
    print("\nLearning 'father' concept:")
    print("-" * 40)
    positives = [
        Atom("father", ["tom", "bob"]),
        Atom("father", ["tom", "liz"]),
        Atom("father", ["bob", "ann"]),
    ]
    negatives = [
        Atom("father", ["liz", "bob"]),
        Atom("father", ["pat", "jim"]),
    ]
    
    rules_dict = {}
    for name, inducer_class in [("Top-Down", TopDownInducer), 
                                 ("Bottom-Up", BottomUpInducer),
                                 ("Inverse Entailment", InverseEntailmentInducer)]:
        print(f"\n{name}:")
        inducer = inducer_class(kb, modes)
        rules = inducer.induce(positives, negatives)
        rules_dict[name] = rules
        for rule in rules:
            print(f"  {rule}")
    
    test_semantic_equivalence(rules_dict, positives, negatives, kb)


def test_grandparent():
    """Test learning grandparent relation"""
    print("\n\n" + "=" * 80)
    print("TEST: Grandparent Relation")
    print("=" * 80)
    
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", ["tom", "bob"]))
    kb.add_fact(Atom("parent", ["tom", "liz"]))
    kb.add_fact(Atom("parent", ["bob", "ann"]))
    kb.add_fact(Atom("parent", ["bob", "pat"]))
    kb.add_fact(Atom("parent", ["pat", "jim"]))
    
    modes = {
        "parent": ModeDeclaration("parent", ['+', '-']),
    }
    
    print("\nLearning 'grandparent' concept:")
    print("-" * 40)
    positives = [
        Atom("grandparent", ["tom", "ann"]),
        Atom("grandparent", ["tom", "pat"]),
        Atom("grandparent", ["bob", "jim"]),
    ]
    negatives = [
        Atom("grandparent", ["tom", "bob"]),
        Atom("grandparent", ["bob", "ann"]),
    ]
    
    rules_dict = {}
    for name, inducer_class in [("Top-Down", TopDownInducer), 
                                 ("Bottom-Up", BottomUpInducer),
                                 ("Inverse Entailment", InverseEntailmentInducer)]:
        print(f"\n{name}:")
        inducer = inducer_class(kb, modes)
        rules = inducer.induce(positives, negatives)
        rules_dict[name] = rules
        for rule in rules:
            print(f"  {rule}")
    
    test_semantic_equivalence(rules_dict, positives, negatives, kb)


def test_uncle():
    """Test learning uncle relation"""
    print("\n\n" + "=" * 80)
    print("TEST: Uncle Relation")
    print("=" * 80)
    
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", ["tom", "bob"]))
    kb.add_fact(Atom("parent", ["tom", "liz"]))
    kb.add_fact(Atom("parent", ["bob", "ann"]))
    kb.add_fact(Atom("parent", ["liz", "joe"]))
    kb.add_fact(Atom("male", ["tom"]))
    kb.add_fact(Atom("male", ["bob"]))
    kb.add_fact(Atom("male", ["joe"]))
    kb.add_fact(Atom("female", ["liz"]))
    kb.add_fact(Atom("female", ["ann"]))
    
    modes = {
        "parent": ModeDeclaration("parent", ['+', '-']),
        "male": ModeDeclaration("male", ['+']),
    }
    
    print("\nLearning 'uncle' concept:")
    print("-" * 40)
    positives = [
        Atom("uncle", ["bob", "joe"]),
    ]
    negatives = [
        Atom("uncle", ["tom", "ann"]),
        Atom("uncle", ["liz", "ann"]),
    ]
    
    rules_dict = {}
    for name, inducer_class in [("Top-Down", TopDownInducer), 
                                 ("Bottom-Up", BottomUpInducer),
                                 ("Inverse Entailment", InverseEntailmentInducer)]:
        print(f"\n{name}:")
        inducer = inducer_class(kb, modes)
        rules = inducer.induce(positives, negatives)
        rules_dict[name] = rules
        for rule in rules:
            print(f"  {rule}")
    
    test_semantic_equivalence(rules_dict, positives, negatives, kb)


if __name__ == "__main__":
    test_family_relations()
    test_grandparent()
    test_uncle()
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)
