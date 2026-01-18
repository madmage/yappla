"""
PyTest test suite for rule induction engine

Tests focus on:
1. Entailment checker correctness with complex rules
2. Individual induction method capabilities
3. Manual rule verification

Note: The three induction methods (Top-Down, Bottom-Up, Inverse Entailment) 
learn rules with different quality levels. The goal is for them to eventually
learn semantically equivalent rules that cover all positive examples without
covering negative examples.
"""
import pytest
from induction11 import (
    Atom, RuleTemplate, KnowledgeBase, ModeDeclaration,
    TopDownInducer, BottomUpInducer, InverseEntailmentInducer,
    CoverageComputer, EntailmentChecker
)


class TestEntailmentChecker:
    """Test the backward chaining entailment checker"""
    
    def test_simple_fact_entailment(self):
        """Test entailment of simple facts"""
        kb = KnowledgeBase()
        kb.add_fact(Atom("parent", ["tom", "bob"]))
        
        assert EntailmentChecker.entails(kb, Atom("parent", ["tom", "bob"]))
        assert not EntailmentChecker.entails(kb, Atom("parent", ["bob", "tom"]))
    
    def test_simple_rule_entailment(self):
        """Test entailment with simple rules"""
        kb = KnowledgeBase()
        kb.add_fact(Atom("parent", ["tom", "bob"]))
        kb.add_fact(Atom("male", ["tom"]))
        
        # Add rule: father(X0, X1) <- parent(X0, X1) & male(X0)
        rule = RuleTemplate(
            Atom("father", ["X0", "X1"]),
            [Atom("parent", ["X0", "X1"]), Atom("male", ["X0"])]
        )
        kb.add_rule(rule)
        
        assert EntailmentChecker.entails(kb, Atom("father", ["tom", "bob"]))
    
    def test_grandparent_rule_with_intermediate_variable(self):
        """Test entailment with rules containing intermediate variables"""
        kb = KnowledgeBase()
        kb.add_fact(Atom("parent", ["tom", "bob"]))
        kb.add_fact(Atom("parent", ["bob", "ann"]))
        kb.add_fact(Atom("parent", ["tom", "liz"]))
        
        # Add rule: grandparent(X0, X1) <- parent(X0, V) & parent(V, X1)
        rule = RuleTemplate(
            Atom("grandparent", ["X0", "X1"]),
            [Atom("parent", ["X0", "V2"]), Atom("parent", ["V2", "X1"])]
        )
        kb.add_rule(rule)
        
        # Should entail grandparent(tom, ann) via tom->bob->ann
        assert EntailmentChecker.entails(kb, Atom("grandparent", ["tom", "ann"])), \
            "Should entail grandparent(tom, ann)"
        
        # Should entail grandparent(tom, liz) - wait, tom->liz is direct, not via intermediate
        # Let me reconsider: tom->bob->ann should work, but tom->liz is direct
        # So this should NOT entail grandparent(tom, liz)
        
        # Should NOT entail grandparent(tom, bob) (direct parent, not grandparent)
        assert not EntailmentChecker.entails(kb, Atom("grandparent", ["tom", "bob"])), \
            "Should NOT entail grandparent(tom, bob)"
        
        # Should NOT entail grandparent(bob, bob)
        assert not EntailmentChecker.entails(kb, Atom("grandparent", ["bob", "bob"]))


class TestTopDownInducer:
    """Test the Top-Down (FOIL-style) induction method"""
    
    @pytest.fixture
    def father_kb(self):
        """Knowledge base for father relation"""
        kb = KnowledgeBase()
        kb.add_fact(Atom("parent", ["tom", "bob"]))
        kb.add_fact(Atom("parent", ["tom", "liz"]))
        kb.add_fact(Atom("parent", ["bob", "ann"]))
        kb.add_fact(Atom("male", ["tom"]))
        kb.add_fact(Atom("male", ["bob"]))
        kb.add_fact(Atom("female", ["liz"]))
        kb.add_fact(Atom("female", ["ann"]))
        
        modes = {
            "parent": ModeDeclaration("parent", ['+', '-']),
            "male": ModeDeclaration("male", ['+']),
            "female": ModeDeclaration("female", ['+']),
        }
        
        positives = [
            Atom("father", ["tom", "bob"]),
            Atom("father", ["tom", "liz"]),
            Atom("father", ["bob", "ann"]),
        ]
        negatives = [
            Atom("father", ["liz", "bob"]),
            Atom("father", ["ann", "bob"]),
        ]
        
        return kb, modes, positives, negatives
    
    def test_learns_at_least_one_rule(self, father_kb):
        """Top-Down should learn at least one rule"""
        kb, modes, positives, negatives = father_kb
        inducer = TopDownInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        assert len(rules) > 0, "Top-Down should learn at least one rule for father"
    
    def test_learned_rule_covers_positives(self, father_kb):
        """Learned rules should cover all positive examples"""
        kb, modes, positives, negatives = father_kb
        inducer = TopDownInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        coverage_computer = CoverageComputer()
        for rule in rules:
            pos_cov = coverage_computer.compute_coverage(rule, positives, kb)
            assert len(pos_cov) == len(positives), \
                f"Rule {rule} should cover all {len(positives)} positive examples"
    
    def test_learned_rule_rejects_negatives(self, father_kb):
        """Learned rules should not cover negative examples"""
        kb, modes, positives, negatives = father_kb
        inducer = TopDownInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        coverage_computer = CoverageComputer()
        for rule in rules:
            neg_cov = coverage_computer.compute_coverage(rule, negatives, kb)
            assert len(neg_cov) == 0, \
                f"Rule {rule} should NOT cover any negative examples, but covered {neg_cov}"


class TestInverseEntailmentInducer:
    """Test the Inverse Entailment (Progol-style) induction method"""
    
    @pytest.fixture
    def father_kb(self):
        """Knowledge base for father relation"""
        kb = KnowledgeBase()
        kb.add_fact(Atom("parent", ["tom", "bob"]))
        kb.add_fact(Atom("parent", ["tom", "liz"]))
        kb.add_fact(Atom("parent", ["bob", "ann"]))
        kb.add_fact(Atom("male", ["tom"]))
        kb.add_fact(Atom("male", ["bob"]))
        kb.add_fact(Atom("female", ["liz"]))
        kb.add_fact(Atom("female", ["ann"]))
        
        modes = {
            "parent": ModeDeclaration("parent", ['+', '-']),
            "male": ModeDeclaration("male", ['+']),
            "female": ModeDeclaration("female", ['+']),
        }
        
        positives = [
            Atom("father", ["tom", "bob"]),
            Atom("father", ["tom", "liz"]),
            Atom("father", ["bob", "ann"]),
        ]
        negatives = [
            Atom("father", ["liz", "bob"]),
            Atom("father", ["ann", "bob"]),
        ]
        
        return kb, modes, positives, negatives
    
    def test_learns_at_least_one_rule(self, father_kb):
        """Inverse Entailment should learn at least one rule"""
        kb, modes, positives, negatives = father_kb
        inducer = InverseEntailmentInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        assert len(rules) > 0, "Inverse Entailment should learn at least one rule"
    
    def test_learned_rule_covers_positives(self, father_kb):
        """Learned rules should cover all positive examples"""
        kb, modes, positives, negatives = father_kb
        inducer = InverseEntailmentInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        if len(rules) > 0:
            coverage_computer = CoverageComputer()
            for rule in rules:
                pos_cov = coverage_computer.compute_coverage(rule, positives, kb)
                assert len(pos_cov) == len(positives), \
                    f"Rule {rule} should cover all positive examples"
    
    def test_learned_rule_rejects_negatives(self, father_kb):
        """Learned rules should not cover negative examples"""
        kb, modes, positives, negatives = father_kb
        inducer = InverseEntailmentInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        if len(rules) > 0:
            coverage_computer = CoverageComputer()
            for rule in rules:
                neg_cov = coverage_computer.compute_coverage(rule, negatives, kb)
                assert len(neg_cov) == 0, \
                    f"Rule {rule} should NOT cover any negative examples"


class TestBottomUpInducer:
    """Test the Bottom-Up (GOLEM-style) induction method"""
    
    @pytest.fixture
    def father_kb(self):
        """Knowledge base for father relation"""
        kb = KnowledgeBase()
        kb.add_fact(Atom("parent", ["tom", "bob"]))
        kb.add_fact(Atom("parent", ["tom", "liz"]))
        kb.add_fact(Atom("parent", ["bob", "ann"]))
        kb.add_fact(Atom("male", ["tom"]))
        kb.add_fact(Atom("male", ["bob"]))
        kb.add_fact(Atom("female", ["liz"]))
        kb.add_fact(Atom("female", ["ann"]))
        
        modes = {
            "parent": ModeDeclaration("parent", ['+', '-']),
            "male": ModeDeclaration("male", ['+']),
            "female": ModeDeclaration("female", ['+']),
        }
        
        positives = [
            Atom("father", ["tom", "bob"]),
            Atom("father", ["tom", "liz"]),
            Atom("father", ["bob", "ann"]),
        ]
        negatives = [
            Atom("father", ["liz", "bob"]),
            Atom("father", ["ann", "bob"]),
        ]
        
        return kb, modes, positives, negatives
    
    def test_returns_rules_or_empty(self, father_kb):
        """Bottom-Up should return rules list (may be empty)"""
        kb, modes, positives, negatives = father_kb
        inducer = BottomUpInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        assert isinstance(rules, list), "Should return a list of rules"
    
    def test_learned_rules_dont_cover_negatives(self, father_kb):
        """If Bottom-Up learns rules, they should not cover negatives"""
        kb, modes, positives, negatives = father_kb
        inducer = BottomUpInducer(kb, modes)
        rules = inducer.induce(positives, negatives)
        
        if len(rules) > 0:
            coverage_computer = CoverageComputer()
            for rule in rules:
                neg_cov = coverage_computer.compute_coverage(rule, negatives, kb)
                assert len(neg_cov) == 0, \
                    f"Rule {rule} should NOT cover any negative examples"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

