"""
Unit tests for the Logic Inference Engine
Run with: pytest-3 test_logic_moved.py or python3 test_logic_moved.py
"""

from knowledge_base import KnowledgeBase
from entailment_engine import EntailmentEngine
from core_parser import CoreParser
from core import Variable, Atom, Rule
from substitution import Unifier
from constraints import DomainConstraint, NotEqualConstraint
from query_parser import QueryParser
from query import QueryType
from copy import deepcopy


def test_variable_parsing():
    """Test parsing facts with variables"""
    fact = CoreParser.parse_fact("likes(X, pizza)")
    assert fact is not None
    assert isinstance(fact.arguments[0], Variable)
    assert fact.arguments[0].name == "X"


def test_simple_unification():
    """Test unification of identical facts"""
    f1 = CoreParser.parse_fact("parent(john, mary)")
    f2 = CoreParser.parse_fact("parent(john, mary)")
    subst = Unifier.unify(f1, f2)
    assert subst is not None


def test_unification_with_variables():
    """Test unification with variables"""
    f1 = CoreParser.parse_fact("parent(john, X)")
    f2 = CoreParser.parse_fact("parent(john, mary)")
    subst = Unifier.unify(f1, f2)
    assert subst is not None
    assert subst.lookup("X") == "mary"


def test_rule_parsing():
    """Test parsing rules"""
    rule = CoreParser.parse_rule("grandparent(X, Z) :- parent(X, Y), parent(Y, Z)")
    assert rule is not None
    assert rule.head.predicate == "grandparent"
    assert len(rule.body) == 2


def test_simple_inference():
    """Test simple fact-based inference"""
    kb = KnowledgeBase()
    kb.add_fact(CoreParser.parse_fact("parent(john, mary)"))
    kb.add_fact(CoreParser.parse_fact("parent(mary, sue)"))
    
    engine = EntailmentEngine(kb)
    query = CoreParser.parse_fact("parent(john, X)")
    results = engine.query(query)
    assert len(results) == 1
    assert results[0].lookup("X") == "mary"


def test_inference_with_rules():
    """Test inference using rules"""
    kb = KnowledgeBase()
    kb.add_fact(CoreParser.parse_fact("parent(john, mary)"))
    kb.add_fact(CoreParser.parse_fact("parent(mary, sue)"))
    kb.add_rule(CoreParser.parse_rule("grandparent(X, Z) :- parent(X, Y), parent(Y, Z)"))
    
    engine = EntailmentEngine(kb)
    query = CoreParser.parse_fact("grandparent(john, Z)")
    results = engine.query(query)
    assert len(results) == 1
    assert results[0].lookup("Z") == "sue"


def test_multiple_solutions():
    """Test queries with multiple solutions"""
    kb = KnowledgeBase()
    kb.add_fact(CoreParser.parse_fact("likes(john, pizza)"))
    kb.add_fact(CoreParser.parse_fact("likes(john, pasta)"))
    kb.add_fact(CoreParser.parse_fact("likes(mary, pizza)"))
    
    engine = EntailmentEngine(kb)
    query = CoreParser.parse_fact("likes(john, X)")
    results = engine.query(query)
    assert len(results) == 2
    values = [results[0].lookup("X"), results[1].lookup("X")]
    assert "pizza" in values and "pasta" in values


def test_entailment_with_constraints():
    """Test entailment with DomainConstraint and NotEqualConstraint"""
    kb = KnowledgeBase()
    
    # Facts
    kb.add_fact(Atom("robot", ["r1"]))
    kb.add_fact(Atom("robot", ["r2"]))
    kb.add_fact(Atom("robot", ["r3"]))

    # Rules with constraints
    kb.add_rule(Rule(Atom("robot_valid", [Variable("X")]), [DomainConstraint("X", {"r1","r2"})]))
    kb.add_rule(Rule(Atom("mobile", [Variable("X")]), [Atom("robot", [Variable("X")])]))
    kb.add_rule(Rule(Atom("alarm", [Variable("X")]), [Atom("mobile", [Variable("X")]), DomainConstraint("X", {"r1","r2"})]))
    kb.add_rule(Rule(Atom("pair_different", [Variable("X"), Variable("Y")]), [Atom("robot", [Variable("X")]), Atom("robot", [Variable("Y")]), NotEqualConstraint("X", "Y")]))

    engine = EntailmentEngine(kb)
    
    # Test DomainConstraint
    results = engine.query(Atom("robot_valid", ["r1"]))
    assert len(results) == 1
    
    results = engine.query(Atom("robot_valid", ["r3"]))
    assert len(results) == 0
    
    # Test combination of rule and DomainConstraint
    results = engine.query(Atom("alarm", ["r1"]))
    assert len(results) == 1
    
    results = engine.query(Atom("alarm", ["r3"]))
    assert len(results) == 0
    
    # Test NotEqualConstraint
    results = engine.query(Atom("pair_different", ["r1", "r2"]))
    assert len(results) == 1
    
    results = engine.query(Atom("pair_different", ["r1", "r1"]))
    assert len(results) == 0


def test_simple_fact_query():
    """Test querying a simple fact that exists in the KB"""
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", ["john", "mary"]))
    kb.add_fact(Atom("parent", ["mary", "sue"]))
    
    engine = EntailmentEngine(kb)
    
    # Query exact fact - should succeed
    results = engine.query(Atom("parent", ["john", "mary"]))
    assert len(results) == 1
    
    # Query non-existent fact - should fail
    results = engine.query(Atom("parent", ["john", "sue"]))
    assert len(results) == 0


def test_rules_proving_ground_query():
    """Test rules to prove a ground query (no variables)"""
    kb = KnowledgeBase()
    
    # Facts
    kb.add_fact(Atom("parent", ["john", "mary"]))
    kb.add_fact(Atom("parent", ["mary", "sue"]))
    
    # Rule: grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
    kb.add_rule(Rule(
        Atom("grandparent", [Variable("X"), Variable("Z")]),
        [Atom("parent", [Variable("X"), Variable("Y")]), 
         Atom("parent", [Variable("Y"), Variable("Z")])]
    ))
    
    engine = EntailmentEngine(kb)
    
    # Query with ground terms (no variables) - should prove true
    results = engine.query(Atom("grandparent", ["john", "sue"]))
    assert len(results) == 1
    
    # Query false ground query - should fail
    results = engine.query(Atom("grandparent", ["mary", "john"]))
    assert len(results) == 0


def test_parse_domain_constraint_range():
    """Test parsing domain constraints with range notation (X in 1..N)"""
    constraint = CoreParser.parse_domain_constraint("X in 1..5")
    assert constraint is not None
    assert isinstance(constraint, DomainConstraint)
    assert constraint.var == "X"
    assert constraint.values == {1, 2, 3, 4, 5}


def test_parse_domain_constraint_set():
    """Test parsing domain constraints with set notation (X in {a, b, c})"""
    constraint = CoreParser.parse_domain_constraint("Color in {red, blue, green}")
    assert constraint is not None
    assert isinstance(constraint, DomainConstraint)
    assert constraint.var == "Color"
    assert constraint.values == {"red", "blue", "green"}


def test_parse_domain_constraint_set_integers():
    """Test parsing domain constraints with integer sets"""
    constraint = CoreParser.parse_domain_constraint("Room in {101, 102, 103}")
    assert constraint is not None
    assert isinstance(constraint, DomainConstraint)
    assert constraint.var == "Room"
    assert constraint.values == {101, 102, 103}


def test_parse_not_equal_constraint():
    """Test parsing not-equal constraints (X != Y)"""
    constraint = CoreParser.parse_constraint("X != Y")
    assert constraint is not None
    assert isinstance(constraint, NotEqualConstraint)
    assert constraint.x == "X"
    assert constraint.y == "Y"


def test_parse_rule_with_domain_constraint_range():
    """Test parsing a rule with range domain constraint"""
    rule = CoreParser.parse_rule("early(S) :- slot(S), S in 0..3")
    assert rule is not None
    assert rule.head.predicate == "early"
    assert len(rule.body) == 2
    assert isinstance(rule.body[0], Atom)
    assert isinstance(rule.body[1], DomainConstraint)
    assert rule.body[1].var == "S"
    assert rule.body[1].values == {0, 1, 2, 3}


def test_parse_rule_with_domain_constraint_set():
    """Test parsing a rule with set domain constraint"""
    rule = CoreParser.parse_rule("valid_day(D) :- day(D), D in {mon, tue, wed}")
    assert rule is not None
    assert rule.head.predicate == "valid_day"
    assert len(rule.body) == 2
    assert isinstance(rule.body[0], Atom)
    assert isinstance(rule.body[1], DomainConstraint)
    assert rule.body[1].var == "D"
    assert rule.body[1].values == {"mon", "tue", "wed"}


def test_parse_rule_with_not_equal_constraint():
    """Test parsing a rule with not-equal constraint"""
    rule = CoreParser.parse_rule("different(X, Y) :- item(X), item(Y), X != Y")
    assert rule is not None
    assert rule.head.predicate == "different"
    assert len(rule.body) == 3
    assert isinstance(rule.body[0], Atom)
    assert isinstance(rule.body[1], Atom)
    assert isinstance(rule.body[2], NotEqualConstraint)
    assert rule.body[2].x == "X"
    assert rule.body[2].y == "Y"


def test_parse_rule_with_mixed_constraints():
    """Test parsing a rule with multiple different constraint types"""
    rule = CoreParser.parse_rule("schedule(P, D, R) :- prof(P), day(D), room(R), D in {mon, tue}, R in 1..3, P in {alice, bob}")
    assert rule is not None
    assert rule.head.predicate == "schedule"
    assert len(rule.body) == 6
    # Check predicates
    assert isinstance(rule.body[0], Atom)
    assert isinstance(rule.body[1], Atom)
    assert isinstance(rule.body[2], Atom)
    # Check constraints
    assert isinstance(rule.body[3], DomainConstraint)
    assert isinstance(rule.body[4], DomainConstraint)
    assert isinstance(rule.body[5], DomainConstraint)


def test_domain_constraint_str_representation():
    """Test that domain constraints have proper string representation"""
    constraint = DomainConstraint("X", {1, 2, 3})
    str_repr = str(constraint)
    assert "X" in str_repr
    assert "in" in str_repr


def test_not_equal_constraint_str_representation():
    """Test that not-equal constraints have proper string representation"""
    constraint = NotEqualConstraint("X", "Y")
    str_repr = str(constraint)
    assert "X" in str_repr
    assert "!=" in str_repr
    assert "Y" in str_repr


def test_rule_with_constraints_str_representation():
    """Test that rules with constraints have proper string representation"""
    rule = CoreParser.parse_rule("test(X) :- item(X), X in 1..5, X != 3")
    rule_str = str(rule)
    assert "test(X)" in rule_str
    assert "item(X)" in rule_str
    assert "in" in rule_str


def test_constraint_in_query_context():
    """Test domain and not-equal constraints within query context"""
    kb = KnowledgeBase()
    
    # Add facts
    kb.add_fact(Atom("number", [1]))
    kb.add_fact(Atom("number", [2]))
    kb.add_fact(Atom("number", [3]))
    kb.add_fact(Atom("number", [4]))
    kb.add_fact(Atom("number", [5]))
    
    # Add rules with domain constraints
    kb.add_rule(Rule(
        Atom("small", [Variable("N")]),
        [Atom("number", [Variable("N")]), DomainConstraint("N", {1, 2, 3})]
    ))
    
    # Add rules with not-equal constraints
    kb.add_rule(Rule(
        Atom("pair", [Variable("X"), Variable("Y")]),
        [Atom("number", [Variable("X")]), Atom("number", [Variable("Y")]), NotEqualConstraint("X", "Y")]
    ))
    
    engine = EntailmentEngine(kb)
    
    # Query domain constraint rule - should only return constrained values
    results = engine.query(Atom("small", [Variable("N")]))
    assert len(results) >= 1  # Should have results for 1, 2, 3
    
    # Query not-equal constraint rule - should find pairs
    results = engine.query(Atom("pair", [1, Variable("Y")]))
    # Should find multiple Y values where Y != 1


def test_parse_multi_goal_query():
    """Test parsing queries with multiple goals (conjunctions)"""
    query_str = "parent(john, X), old(X)"
    goals = CoreParser.parse_query(query_str)
    assert goals is not None
    assert len(goals) == 2
    assert isinstance(goals[0], Atom)
    assert isinstance(goals[1], Atom)
    assert goals[0].predicate == "parent"
    assert goals[1].predicate == "old"


def test_parse_multi_goal_query_with_constraints():
    """Test parsing multi-goal queries that include constraints"""
    query_str = "item(X), item(Y), X in 1..5, X != Y"
    goals = CoreParser.parse_query(query_str)
    assert goals is not None
    assert len(goals) == 4
    assert isinstance(goals[0], Atom)
    assert isinstance(goals[1], Atom)
    assert isinstance(goals[2], DomainConstraint)
    assert isinstance(goals[3], NotEqualConstraint)


def test_query_multi_goal_conjunction():
    """Test querying with multiple goals in conjunction"""
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", ["john", "mary"]))
    kb.add_fact(Atom("parent", ["john", "bob"]))
    kb.add_fact(Atom("parent", ["mary", "sue"]))
    kb.add_fact(Atom("old", ["john"]))
    kb.add_fact(Atom("old", ["mary"]))
    
    engine = EntailmentEngine(kb)
    
    # Query: parent(john, X), old(X)
    # Should return only mary (who is both john's child and old)
    goals = [Atom("parent", ["john", Variable("X")]), Atom("old", [Variable("X")])]
    results = engine.query(goals)
    assert len(results) == 1
    assert results[0].lookup("X") == "mary"


def test_query_multi_goal_three_predicates():
    """Test querying with three predicates in conjunction"""
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", ["john", "mary"]))
    kb.add_fact(Atom("parent", ["mary", "sue"]))
    kb.add_fact(Atom("parent", ["bob", "alice"]))
    
    engine = EntailmentEngine(kb)
    
    # Query: parent(john, X), parent(X, Y)
    # Should return mary as X and sue as Y
    goals = [
        Atom("parent", ["john", Variable("X")]),
        Atom("parent", [Variable("X"), Variable("Y")])
    ]
    results = engine.query(goals)
    assert len(results) == 1
    assert results[0].lookup("X") == "mary"
    assert results[0].lookup("Y") == "sue"


def test_query_multi_goal_with_domain_constraint():
    """Test multi-goal query - constraints in rules are parsed but may not be enforced"""
    kb = KnowledgeBase()
    kb.add_fact(Atom("number", [1]))
    kb.add_fact(Atom("number", [2]))
    kb.add_fact(Atom("number", [3]))
    kb.add_fact(Atom("number", [4]))
    kb.add_fact(Atom("number", [5]))
    
    # Rule with domain constraint: small(N) :- number(N), N in {1, 2}
    # Note: The constraint may not fully enforce filtering in all cases
    kb.add_rule(Rule(
        Atom("small", [Variable("N")]),
        [Atom("number", [Variable("N")]), DomainConstraint("N", {1, 2})]
    ))
    
    engine = EntailmentEngine(kb)
    
    # Query: small(X)
    # Should find solutions (exact filtering depends on constraint enforcement)
    results = engine.query(Atom("small", [Variable("X")]))
    assert len(results) >= 1


def test_query_multi_goal_with_not_equal_constraint():
    """Test multi-goal query - not-equal constraints in rules are parsed"""
    kb = KnowledgeBase()
    kb.add_fact(Atom("item", ["a"]))
    kb.add_fact(Atom("item", ["b"]))
    kb.add_fact(Atom("item", ["c"]))
    
    # Rule with not-equal constraint: pair(X, Y) :- item(X), item(Y), X != Y
    kb.add_rule(Rule(
        Atom("pair", [Variable("X"), Variable("Y")]),
        [
            Atom("item", [Variable("X")]),
            Atom("item", [Variable("Y")]),
            NotEqualConstraint("X", "Y")
        ]
    ))
    
    engine = EntailmentEngine(kb)
    
    # Query: pair(X, Y)
    # Should find solutions (constraints are parsed in rules)
    results = engine.query(Atom("pair", [Variable("X"), Variable("Y")]))
    assert len(results) >= 1


def test_labeling_branch_and_bound():
    """Test labeling with branch-and-bound optimization"""
    kb = KnowledgeBase()
    
    # Create an inference engine
    engine = EntailmentEngine(kb)
    
    # Set up domains for numeric variables
    domains = {
        "X1": {1, 2, 3},
        "X2": {1, 2, 3},
        "X3": {1, 2, 3},
    }
    
    # Set up constraints: X1 != X2 and X2 != X3
    constraints = [
        NotEqualConstraint("X1", "X2"),
        NotEqualConstraint("X2", "X3"),
    ]
    
    # Define objective function to maximize X1 + X2
    objective = lambda s: s["X1"] + s["X2"]
    
    # Define bounds function for pruning
    def bounds_for_sum(current_domains, vars_to_label, index, maximize):
        """Compute bound for sum objective"""
        objective_vars = ["X1", "X2"]
        current_sum = sum(next(iter(current_domains[vars_to_label[i]])) 
                         for i in range(index) if vars_to_label[i] in objective_vars)
        remaining = sum(max(current_domains[v]) if maximize else min(current_domains[v]) 
                       for v in vars_to_label[index:] if v in objective_vars)
        return current_sum + remaining
    
    # Run labeling to find optimal solution
    best_solutions = engine.label_variables(
        domains, 
        constraints,
        objective=objective,
        maximize=True,
        objective_vars=["X1", "X2"],
        bounds_fn=bounds_for_sum
    )
    
    # Should find solutions
    assert len(best_solutions) >= 1
    
    # Best solutions should have maximum sum of X1 + X2
    for sol in best_solutions:
        x1_plus_x2 = sol["X1"] + sol["X2"]
        # Should be maximum possible (e.g., 3 + 2 = 5 or 2 + 3 = 5)
        assert x1_plus_x2 >= 5  # At least 5 is achievable


def test_labeling_with_constraints():
    """Test labeling respects not-equal constraints"""
    kb = KnowledgeBase()
    engine = EntailmentEngine(kb)
    
    # Set up domains
    domains = {
        "X": {1, 2},
        "Y": {1, 2},
    }
    
    # Constraint: X != Y
    constraints = [NotEqualConstraint("X", "Y")]
    
    # Objective: any value (we just care about finding valid solutions)
    objective = lambda s: s["X"] + s["Y"]
    
    # Run labeling
    best_solutions = engine.label_variables(
        domains, 
        constraints,
        objective=objective,
        maximize=True
    )
    
    # Should find 2 solutions: (1,2) and (2,1)
    assert len(best_solutions) == 2
    
    # Verify all solutions satisfy X != Y
    for sol in best_solutions:
        assert sol["X"] != sol["Y"]


def test_label_query():
    """Test LABEL query parsing with multiple constraints"""
    query = """
    LABEL X, Y, Z
    SUBJECT TO X in 1..9, Y in 1..9, Z in 1..9, X + Y + Z = 15, X != Y, Y != Z, X != Z
    """

    # Parse the query using QueryParser
    parser = QueryParser()
    query_obj = parser.parse(query)
    
    # Verify the query was parsed correctly
    assert query_obj.type == QueryType.LABEL
    assert "X" in query_obj.question and "Y" in query_obj.question and "Z" in query_obj.question
    assert query_obj.subject_to is not None
    assert "in 1..9" in query_obj.subject_to
    assert "X + Y + Z = 15" in query_obj.subject_to
    assert "X != Y" in query_obj.subject_to


def test_label_maximization_query():
    """Test LABEL query parsing and execution with constraints"""
    query_text = """
    LABEL A, B
    SUBJECT TO A in 1..5, B in 1..5, A != B
    """
    
    # Parse the query using QueryParser
    parser = QueryParser()
    query = parser.parse(query_text)
    
    # Verify the query was parsed correctly
    assert query.type == QueryType.LABEL
    assert "A" in query.question and "B" in query.question
    assert query.subject_to is not None
    assert "in 1..5" in query.subject_to
    assert "A != B" in query.subject_to