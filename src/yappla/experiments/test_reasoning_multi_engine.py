"""
Simple test to verify ReasoningMultiEngine works correctly
"""
from src.yappla.experiments.logic_engine.knowledge_base import KnowledgeBase
from src.yappla.experiments.logic_engine.entailment_engine import EntailmentEngine
from src.yappla.experiments.logic_engine.reasoning_multi_engine import ReasoningMultiEngine
from src.yappla.experiments.logic_engine.query import Query, QueryType
from src.yappla.experiments.logic_engine.parser import LogicParser


def test_reasoning_multi_engine_entailment():
    """Test ReasoningMultiEngine dispatching entailment queries"""
    # Create knowledge base
    kb = KnowledgeBase()
    kb.add_fact(LogicParser.parse_fact("parent(john, mary)"))
    kb.add_fact(LogicParser.parse_fact("parent(mary, sue)"))
    
    # Create entailment engine
    entailment_engine = EntailmentEngine(kb)
    
    # Create multi-engine reasoner
    reasoner = ReasoningMultiEngine(entailment_engine=entailment_engine)
    
    # Test entailment query
    query = Query(
        type=QueryType.ENTAIL,
        question=LogicParser.parse_fact("parent(john, mary)")
    )
    
    result = reasoner.query(query)
    assert result.success == True
    assert result.answer is not None
    print(f"✓ Entailment query succeeded: {result.explanation}")
    
    # Test false entailment
    query2 = Query(
        type=QueryType.ENTAIL,
        question=LogicParser.parse_fact("parent(john, sue)")
    )
    
    result2 = reasoner.query(query2)
    assert result2.success == False
    print(f"✓ False entailment query correctly failed: {result2.explanation}")


def test_reasoning_multi_engine_without_engine():
    """Test ReasoningMultiEngine handles missing engines gracefully"""
    reasoner = ReasoningMultiEngine()
    
    query = Query(
        type=QueryType.ENTAIL,
        question="test"
    )
    
    result = reasoner.query(query)
    assert result.success == False
    assert "not available" in result.explanation
    print(f"✓ Missing engine handled correctly: {result.explanation}")


def test_reasoning_multi_engine_consistency():
    """Test ReasoningMultiEngine handles consistency checks"""
    kb = KnowledgeBase()
    kb.add_fact(LogicParser.parse_fact("likes(john, pizza)"))
    
    entailment_engine = EntailmentEngine(kb)
    reasoner = ReasoningMultiEngine(entailment_engine=entailment_engine)
    
    query = Query(
        type=QueryType.CONSISTENT,
        question=LogicParser.parse_fact("likes(john, pizza)")
    )
    
    result = reasoner.query(query)
    assert result.success == True
    assert result.answer == True
    print(f"✓ Consistency check passed: {result.explanation}")


if __name__ == "__main__":
    print("Testing ReasoningMultiEngine...")
    test_reasoning_multi_engine_entailment()
    test_reasoning_multi_engine_without_engine()
    test_reasoning_multi_engine_consistency()
    print("\n✓ All ReasoningMultiEngine tests passed!")
