"""
Unit tests for the Logic Inference Engine
Run with: pytest-3 test_logic.py
"""

from knowledge_base import KnowledgeBase
from inference import InferenceEngine
from parser import LogicParser
from logic_classes import Variable, Predicate, Rule
from substitution import Unifier
from constraints import DomainConstraint, NotEqualConstraint
from copy import deepcopy


def test_variable_parsing():
    """Test parsing facts with variables"""
    fact = LogicParser.parse_fact("likes(X, pizza)")
    assert fact is not None
    assert isinstance(fact.arguments[0], Variable)
    assert fact.arguments[0].name == "X"


def test_simple_unification():
    """Test unification of identical facts"""
    f1 = LogicParser.parse_fact("parent(john, mary)")
    f2 = LogicParser.parse_fact("parent(john, mary)")
    subst = Unifier.unify(f1, f2)
    assert subst is not None


def test_unification_with_variables():
    """Test unification with variables"""
    f1 = LogicParser.parse_fact("parent(john, X)")
    f2 = LogicParser.parse_fact("parent(john, mary)")
    subst = Unifier.unify(f1, f2)
    assert subst is not None
    assert subst.lookup("X") == "mary"


def test_rule_parsing():
    """Test parsing rules"""
    rule = LogicParser.parse_rule("grandparent(X, Z) :- parent(X, Y), parent(Y, Z)")
    assert rule is not None
    assert rule.head.name == "grandparent"
    assert len(rule.body) == 2


def test_simple_inference():
    """Test simple fact-based inference"""
    kb = KnowledgeBase()
    kb.add_fact(LogicParser.parse_fact("parent(john, mary)"))
    kb.add_fact(LogicParser.parse_fact("parent(mary, sue)"))
    
    engine = InferenceEngine(kb)
    query = LogicParser.parse_fact("parent(john, X)")
    results = engine.query(query)
    assert len(results) == 1
    assert results[0].lookup("X") == "mary"


def test_inference_with_rules():
    """Test inference using rules"""
    kb = KnowledgeBase()
    kb.add_fact(LogicParser.parse_fact("parent(john, mary)"))
    kb.add_fact(LogicParser.parse_fact("parent(mary, sue)"))
    kb.add_rule(LogicParser.parse_rule("grandparent(X, Z) :- parent(X, Y), parent(Y, Z)"))
    
    engine = InferenceEngine(kb)
    query = LogicParser.parse_fact("grandparent(john, Z)")
    results = engine.query(query)
    assert len(results) == 1
    assert results[0].lookup("Z") == "sue"


def test_multiple_solutions():
    """Test queries with multiple solutions"""
    kb = KnowledgeBase()
    kb.add_fact(LogicParser.parse_fact("likes(john, pizza)"))
    kb.add_fact(LogicParser.parse_fact("likes(john, pasta)"))
    kb.add_fact(LogicParser.parse_fact("likes(mary, pizza)"))
    
    engine = InferenceEngine(kb)
    query = LogicParser.parse_fact("likes(john, X)")
    results = engine.query(query)
    assert len(results) == 2
    values = [results[0].lookup("X"), results[1].lookup("X")]
    assert "pizza" in values and "pasta" in values


def test_entailment_with_constraints():
    """Test entailment with DomainConstraint and NotEqualConstraint"""
    kb = KnowledgeBase()
    
    # Facts
    kb.add_fact(Predicate("robot", ["r1"]))
    kb.add_fact(Predicate("robot", ["r2"]))
    kb.add_fact(Predicate("robot", ["r3"]))

    # Rules with constraints
    kb.add_rule(Rule(Predicate("robot_valid", [Variable("X")]), [DomainConstraint("X", {"r1","r2"})]))
    kb.add_rule(Rule(Predicate("mobile", [Variable("X")]), [Predicate("robot", [Variable("X")])]))
    kb.add_rule(Rule(Predicate("alarm", [Variable("X")]), [Predicate("mobile", [Variable("X")]), DomainConstraint("X", {"r1","r2"})]))
    kb.add_rule(Rule(Predicate("pair_different", [Variable("X"), Variable("Y")]), [Predicate("robot", [Variable("X")]), Predicate("robot", [Variable("Y")]), NotEqualConstraint("X", "Y")]))

    engine = InferenceEngine(kb)
    
    # Test DomainConstraint
    results = engine.query(Predicate("robot_valid", ["r1"]))
    assert len(results) == 1
    
    results = engine.query(Predicate("robot_valid", ["r3"]))
    assert len(results) == 0
    
    # Test combination of rule and DomainConstraint
    results = engine.query(Predicate("alarm", ["r1"]))
    assert len(results) == 1
    
    results = engine.query(Predicate("alarm", ["r3"]))
    assert len(results) == 0
    
    # Test NotEqualConstraint
    results = engine.query(Predicate("pair_different", ["r1", "r2"]))
    assert len(results) == 1
    
    results = engine.query(Predicate("pair_different", ["r1", "r1"]))
    assert len(results) == 0


def test_simple_fact_query():
    """Test querying a simple fact that exists in the KB"""
    kb = KnowledgeBase()
    kb.add_fact(Predicate("parent", ["john", "mary"]))
    kb.add_fact(Predicate("parent", ["mary", "sue"]))
    
    engine = InferenceEngine(kb)
    
    # Query exact fact - should succeed
    results = engine.query(Predicate("parent", ["john", "mary"]))
    assert len(results) == 1
    
    # Query non-existent fact - should fail
    results = engine.query(Predicate("parent", ["john", "sue"]))
    assert len(results) == 0


def test_rules_proving_ground_query():
    """Test rules to prove a ground query (no variables)"""
    kb = KnowledgeBase()
    
    # Facts
    kb.add_fact(Predicate("parent", ["john", "mary"]))
    kb.add_fact(Predicate("parent", ["mary", "sue"]))
    
    # Rule: grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
    kb.add_rule(Rule(
        Predicate("grandparent", [Variable("X"), Variable("Z")]),
        [Predicate("parent", [Variable("X"), Variable("Y")]), 
         Predicate("parent", [Variable("Y"), Variable("Z")])]
    ))
    
    engine = InferenceEngine(kb)
    
    # Query with ground terms (no variables) - should prove true
    results = engine.query(Predicate("grandparent", ["john", "sue"]))
    assert len(results) == 1
    
    # Query false ground query - should fail
    results = engine.query(Predicate("grandparent", ["mary", "john"]))
    assert len(results) == 0