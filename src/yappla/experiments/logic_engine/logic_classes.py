from dataclasses import dataclass
from typing import List, Any

@dataclass
class Predicate:
    """Represents a logical predicate with a name and arguments"""
    name: str
    arguments: List[Any]
    
    def __str__(self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.name == other.name and self.arguments == other.arguments
    
    def __hash__(self):
        return hash((self.name, tuple(str(a) for a in self.arguments)))


@dataclass
class Rule:
    """Represents a logical rule: head :- body"""
    head: Predicate
    body: List[Predicate]
    
    def __str__(self):
        body_str = ', '.join(str(fact) for fact in self.body)
        return f"{self.head} :- {body_str}"
    
    def __repr__(self):
        return self.__str__()


@dataclass
class Variable:
    """Represents a logical variable"""
    name: str
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Var({self.name})"
    
    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
