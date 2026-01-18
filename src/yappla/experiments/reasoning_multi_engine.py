from typing import Optional
try:
    from .query import Query, QueryType, Result
    from .entailment_engine import EntailmentEngine
except ImportError:
    from query import Query, QueryType, Result
    from entailment_engine import EntailmentEngine


class ReasoningMultiEngine:
    """
    Multi-engine reasoning system that dispatches queries to specialized engines
    based on the QueryType.
    """

    def __init__(self, 
                 entailment_engine: Optional[EntailmentEngine] = None,
                 induction_engine = None,
                 abduction_engine = None):
        """
        Initialize the ReasoningMultiEngine with optional engines.
        
        Args:
            entailment_engine: Engine for handling entailment queries (default: None)
            induction_engine: Engine for handling induction queries (default: None)
            abduction_engine: Engine for handling abduction queries (default: None)
        """
        self.entailment_engine = entailment_engine
        self.induction_engine = induction_engine
        self.abduction_engine = abduction_engine

    def query(self, q: Query) -> Result:
        """
        Dispatch a query to the appropriate engine based on its type.
        
        Args:
            q: A Query object with type, question, and optional parameters
            
        Returns:
            A Result object with success, answer, explanation, and metadata
            
        Raises:
            NotImplementedError: If the required engine is not available for the query type
        """
        dispatch = {
            QueryType.ENTAIL: self._entail,
            QueryType.CONSISTENT: self._consistent,
            QueryType.EXPLAIN: self._explain,
            QueryType.POSSIBLE: self._possible,
            QueryType.INDUCE: self._induce,
        }
        
        if q.type not in dispatch:
            return Result(
                success=False,
                answer=None,
                explanation=f"Unknown query type: {q.type}"
            )
        
        return dispatch[q.type](q)

    def _entail(self, q: Query) -> Result:
        """Handle entailment queries"""
        if self.entailment_engine is None:
            return Result(
                success=False,
                answer=None,
                explanation="Entailment engine not available"
            )
        
        try:
            results = self.entailment_engine.query(q.question)
            success = len(results) > 0
            return Result(
                success=success,
                answer=results if success else None,
                explanation="Query entailed" if success else "Query not entailed"
            )
        except Exception as e:
            return Result(
                success=False,
                answer=None,
                explanation=f"Error during entailment: {str(e)}"
            )

    def _consistent(self, q: Query) -> Result:
        """Handle consistency checking queries"""
        if self.entailment_engine is None:
            return Result(
                success=False,
                answer=None,
                explanation="Entailment engine not available"
            )
        
        try:
            # Consistency checking: check if the facts are consistent with KB
            results = self.entailment_engine.query(q.question)
            # If we can derive it from the KB, it's consistent
            is_consistent = len(results) > 0
            return Result(
                success=True,
                answer=is_consistent,
                explanation="Consistent" if is_consistent else "Inconsistent with KB"
            )
        except Exception as e:
            return Result(
                success=False,
                answer=None,
                explanation=f"Error during consistency check: {str(e)}"
            )

    def _explain(self, q: Query) -> Result:
        """Handle explanation queries"""
        if self.entailment_engine is None:
            return Result(
                success=False,
                answer=None,
                explanation="Entailment engine not available for explanations"
            )
        
        try:
            # Find all proofs/derivations for the query
            results = self.entailment_engine.query(q.question)
            if results:
                return Result(
                    success=True,
                    answer=results,
                    explanation="Derivations found"
                )
            else:
                return Result(
                    success=False,
                    answer=None,
                    explanation="No derivations found"
                )
        except Exception as e:
            return Result(
                success=False,
                answer=None,
                explanation=f"Error during explanation: {str(e)}"
            )

    def _possible(self, q: Query) -> Result:
        """Handle possibility queries"""
        if self.entailment_engine is None:
            return Result(
                success=False,
                answer=None,
                explanation="Entailment engine not available"
            )
        
        try:
            # Check if something is possible (derivable under some interpretation)
            results = self.entailment_engine.query(q.question)
            is_possible = len(results) > 0
            return Result(
                success=True,
                answer=is_possible,
                explanation="Possible" if is_possible else "Not possible"
            )
        except Exception as e:
            return Result(
                success=False,
                answer=None,
                explanation=f"Error during possibility check: {str(e)}"
            )

    def _induce(self, q: Query) -> Result:
        """Handle induction queries"""
        if self.induction_engine is None:
            return Result(
                success=False,
                answer=None,
                explanation="Induction engine not available"
            )
        
        try:
            # Delegate to induction engine
            return self.induction_engine.query(q)
        except Exception as e:
            return Result(
                success=False,
                answer=None,
                explanation=f"Error during induction: {str(e)}"
            )
