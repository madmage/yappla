"""
Unit tests for the Logic Inference Engine
Run with: pytest-3 test_logic.py
"""

from database import FactDatabase
from inference import InferenceEngine
from parser import LogicParser
from terms import Variable
from substitution import Unifier


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
    assert rule.head.predicate == "grandparent"
    assert len(rule.body) == 2


def test_simple_inference():
    """Test simple fact-based inference"""
    db = FactDatabase()
    db.add_fact(LogicParser.parse_fact("parent(john, mary)"))
    db.add_fact(LogicParser.parse_fact("parent(mary, sue)"))
    
    engine = InferenceEngine(db)
    query = LogicParser.parse_fact("parent(john, X)")
    results = engine.query(query)
    assert len(results) == 1
    assert results[0].lookup("X") == "mary"


def test_inference_with_rules():
    """Test inference using rules"""
    db = FactDatabase()
    db.add_fact(LogicParser.parse_fact("parent(john, mary)"))
    db.add_fact(LogicParser.parse_fact("parent(mary, sue)"))
    db.add_rule(LogicParser.parse_rule("grandparent(X, Z) :- parent(X, Y), parent(Y, Z)"))
    
    engine = InferenceEngine(db)
    query = LogicParser.parse_fact("grandparent(john, Z)")
    results = engine.query(query)
    assert len(results) == 1
    assert results[0].lookup("Z") == "sue"


def test_multiple_solutions():
    """Test queries with multiple solutions"""
    db = FactDatabase()
    db.add_fact(LogicParser.parse_fact("likes(john, pizza)"))
    db.add_fact(LogicParser.parse_fact("likes(john, pasta)"))
    db.add_fact(LogicParser.parse_fact("likes(mary, pizza)"))
    
    engine = InferenceEngine(db)
    query = LogicParser.parse_fact("likes(john, X)")
    results = engine.query(query)
    assert len(results) == 2
    values = [results[0].lookup("X"), results[1].lookup("X")]
    assert "pizza" in values and "pasta" in values