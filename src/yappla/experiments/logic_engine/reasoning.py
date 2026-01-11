from query import Query, QueryType, Result

class ReasoningEngine:

    def query(self, q: Query) -> Result:
        dispatch = {
            QueryType.ENTAIL: self._entail,
            QueryType.CONSISTENT: self._consistent,
            QueryType.EXPLAIN: self._explain,
            QueryType.POSSIBLE: self._possible,
            QueryType.INDUCE: self._induce,
        }
        return dispatch[q.type](q)