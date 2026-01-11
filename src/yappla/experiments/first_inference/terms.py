from dataclasses import dataclass
from typing import List, Any

# Term
# A term is the most general syntactic category in logic programming. Everything you write in a logic program is a term. Terms come in several varieties:
# Examples: 42 (a number), john (an atom), X (a variable), parent(mary, susan) (a compound term), [1, 2, 3] (a list, which is actually syntactic sugar for a compound term)
#
# Atom
# An atom is a constant symbol with no internal structure. Atoms are the simplest terms and represent themselves. They start with a lowercase letter or are enclosed in single quotes.
# Examples: john, mary, loves, 'New York' (atom with spaces, needs quotes), x (lowercase single letter is an atom, not a variable)
#
# Variable
# A variable is a placeholder that can be instantiated (bound) to any term. Variables start with an uppercase letter or an underscore.
# Examples: X, Person, _result, _ (the anonymous variable, used when you don't care about the value)
#
# Compound Term (or Structure)
# A compound term consists of a functor (an atom) and a fixed number of arguments (which are themselves terms). It has the form functor(arg1, arg2, ..., argN).
# Examples: parent(tom, bob) - functor is parent, arity is 2, date(2024, january, 8) - functor is date, arity is 3, point(X, Y) - arguments can be variables, likes(john, pizza) - functor is likes, arity is 2
#
# Functor
# The functor is the name of a compound term, often paired with its arity (number of arguments), written as name/arity.
# Examples: parent/2 (the functor parent with 2 arguments), append/3 (the functor append with 3 arguments), member/2
#
# Clause
# A clause is a basic statement in logic programming. There are two types: Fact and Rule
#
# Fact
# A fact is a clause with no conditions (a head with no body).
# Examples: parent(mary, john). likes(john, pizza).
#
# Rule
# A rule is a clause with conditions (a head and a body separated by :-).
# Examples: grandparent(X, Z) :- parent(X, Y), parent(Y, Z). sibling(X, Y) :- parent(P, X), parent(P, Y), X \= Y.
#
# Predicate
# A predicate is a collection of clauses that share the same functor and arity. It defines a relation.
#
# Goal (or Query)
# A goal is a term that you want the system to prove or satisfy. In Prolog, you write queries starting with ?-.
# Examples:
# ?- parent(mary, john). (is this true?)
# ?- parent(mary, X). (who are Mary's children?)
# ?- parent(X, Y), parent(Y, Z). (find all grandparent relationships)
#
# Term
# - Atom
# - Number
# - Variable
# - Compound Term

@dataclass
class Term:
    """Base class for terms (facts, variables, etc.)"""
    pass


@dataclass
class Fact(Term):
    """Represents a logical fact with a predicate and arguments"""
    predicate: str
    arguments: List[Any]
    
    def __str__(self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        return f"{self.predicate}({args_str})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Fact):
            return False
        return self.predicate == other.predicate and self.arguments == other.arguments
    
    def __hash__(self):
        return hash((self.predicate, tuple(str(a) for a in self.arguments)))


@dataclass
class Rule:
    """Represents a logical rule: head :- body"""
    head: Fact
    body: List[Fact]
    
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
