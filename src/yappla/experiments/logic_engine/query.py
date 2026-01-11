from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

class QueryType(Enum):
    ENTAIL = "entail"
    CONSISTENT = "consistent"
    EXPLAIN = "explain"
    POSSIBLE = "possible"
    INDUCE = "induce"

@dataclass
class Query:
    type: QueryType
    question: Any
    time: Optional[int] = None
    given: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

@dataclass
class Result:
    success: bool
    answer: Any = None
    explanation: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None