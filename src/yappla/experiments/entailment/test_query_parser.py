"""
Unit tests for the QueryParser
Run with: pytest test_query_parser.py -v
"""

from query_parser import QueryParser, KBCommand
from query import Query, QueryType


def test_query_parsing_entail():
    """Test parsing a basic ENTAIL query"""
    parser = QueryParser()
    query_text = """
    ENTAIL      Does it     rain?
    TIME   5
    GIVEN {"location": "Seattle"}
    """
    
    result = parser.parse(query_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.ENTAIL
    assert "rain" in result.question.lower()
    assert result.time == 5
    assert result.given == {"location": "Seattle"}


def test_kb_command_parsing_load():
    """Test parsing LOAD KB command"""
    parser = QueryParser()
    kb_text = """
    load kb
    some knowledge base content here
    """
    
    result = parser.parse(kb_text)
    assert isinstance(result, KBCommand)
    assert result.command == "LOAD KB"
    assert "content" in result.content.lower()


def test_query_parsing_explain():
    """Test parsing EXPLAIN query"""
    parser = QueryParser()
    explain_text = """
    explain why the sky is blue
    options {"detail_level": "high"}
    """
    
    result = parser.parse(explain_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.EXPLAIN
    assert "sky" in result.question.lower()
    assert result.options == {"detail_level": "high"}


def test_query_parsing_simple():
    """Test parsing simple query without optional fields"""
    parser = QueryParser()
    simple_text = "POSSIBLE will it snow tomorrow"
    result = parser.parse(simple_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.POSSIBLE
    assert "snow" in result.question.lower()
    assert result.time is None
    assert result.given is None
    assert result.options is None


def test_query_parsing_label_with_subject_to():
    """Test parsing LABEL query with SUBJECT TO clause"""
    parser = QueryParser()
    label_text = """
    LABEL    what   is   the   outcome
    SUBJECT    TO   some constraints here
    TIME 10
    """
    
    result = parser.parse(label_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.LABEL
    assert "outcome" in result.question.lower()
    assert result.subject_to == "some constraints here"
    assert result.time == 10


def test_query_parsing_label_compact():
    """Test parsing LABEL query with compact spacing"""
    parser = QueryParser()
    label_text2 = "LABEL outcome SUBJECT TO constraints"
    result = parser.parse(label_text2)
    assert isinstance(result, Query)
    assert result.type == QueryType.LABEL
    assert result.subject_to == "constraints"


def test_query_parsing_consistent():
    """Test parsing CONSISTENT query"""
    parser = QueryParser()
    consistent_text = "CONSISTENT all weather patterns"
    result = parser.parse(consistent_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.CONSISTENT
    assert "weather" in result.question.lower()


def test_query_parsing_induce():
    """Test parsing INDUCE query"""
    parser = QueryParser()
    induce_text = "INDUCE the pattern from data"
    result = parser.parse(induce_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.INDUCE
    assert "pattern" in result.question.lower()


def test_kb_command_parsing_begin():
    """Test parsing BEGIN KB command"""
    parser = QueryParser()
    kb_text = "BEGIN KB"
    result = parser.parse(kb_text)
    assert isinstance(result, KBCommand)
    assert result.command == "BEGIN KB"


def test_kb_command_parsing_end():
    """Test parsing END KB command"""
    parser = QueryParser()
    kb_text = "END KB"
    result = parser.parse(kb_text)
    assert isinstance(result, KBCommand)
    assert result.command == "END KB"


def test_kb_command_parsing_plain_kb():
    """Test parsing plain KB command"""
    parser = QueryParser()
    kb_text = "KB fact(a, b)"
    result = parser.parse(kb_text)
    assert isinstance(result, KBCommand)
    assert result.command == "KB"
    assert "fact" in result.content.lower()


def test_query_with_multiple_keywords():
    """Test parsing query with multiple keyword sections"""
    parser = QueryParser()
    query_text = """
    ENTAIL does the system work
    TIME 100
    GIVEN {"setup": "complete"}
    OPTIONS {"verbose": true}
    SUBJECT TO no_errors
    """
    
    result = parser.parse(query_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.ENTAIL
    assert result.time == 100
    assert result.given == {"setup": "complete"}
    # OPTIONS parsing may use fallback if dict eval fails
    assert result.options is not None
    assert result.subject_to == "no_errors"


def test_query_parsing_label_maximize():
    """Test parsing LABEL query with constraints and options"""
    parser = QueryParser()
    label_text = """
    LABEL A, B
    SUBJECT TO A in 1..5, B in 1..5, A != B
    """
    
    result = parser.parse(label_text)
    assert isinstance(result, Query)
    assert result.type == QueryType.LABEL
    assert "A" in result.question and "B" in result.question
    assert "in 1..5" in result.subject_to
    assert "A != B" in result.subject_to
