from typing import Dict, Any, Optional
from core import Variable, Atom


class Substitution:
    """Represents variable bindings"""
    
    def __init__(self, bindings: Optional[Dict[str, Any]] = None):
        self.bindings = bindings or {}
    
    def bind(self, var: str, value: Any) -> 'Substitution':
        """Create a new substitution with an additional binding"""
        new_bindings = self.bindings.copy()
        new_bindings[var] = value
        return Substitution(new_bindings)
    
    def lookup(self, var: str) -> Any:
        """Look up a variable's binding, following variable chains"""
        val = self.bindings.get(var)
        if val is None:
            return None
        if isinstance(val, Variable):
            return self.lookup(val.name)
        return val
    
    def apply(self, term: Any) -> Any:
        """Apply substitution to a term"""
        if isinstance(term, Variable):
            val = self.lookup(term.name)
            if val is not None:
                return self.apply(val)  # Follow chains
            return term
        elif isinstance(term, Atom):
            new_args = [self.apply(arg) for arg in term.arguments]
            return Atom(term.predicate, new_args)
        elif isinstance(term, list):
            return [self.apply(item) for item in term]
        else:
            return term
    
    def __str__(self):
        if not self.bindings:
            return "{}"
        items = [f"{k}={v}" for k, v in self.bindings.items()]
        return "{" + ", ".join(items) + "}"
    
    def __repr__(self):
        return self.__str__()


class Unifier:
    """Handles unification of terms"""
    
    @staticmethod
    def unify(term1: Any, term2: Any, subst: Optional[Substitution] = None) -> Optional[Substitution]:
        """
        Unify two terms, returning a substitution if successful, None otherwise
        """
        if subst is None:
            subst = Substitution()
        
        # Apply current substitution
        term1 = subst.apply(term1)
        term2 = subst.apply(term2)
        
        # Same term
        if term1 == term2:
            return subst
        
        # Variable unification
        if isinstance(term1, Variable):
            return subst.bind(term1.name, term2)
        
        if isinstance(term2, Variable):
            return subst.bind(term2.name, term1)
        
        # Atom unification
        if isinstance(term1, Atom) and isinstance(term2, Atom):
            if term1.predicate != term2.predicate:
                return None
            
            if len(term1.arguments) != len(term2.arguments):
                return None
            
            # Unify arguments pairwise
            for arg1, arg2 in zip(term1.arguments, term2.arguments):
                subst = Unifier.unify(arg1, arg2, subst)
                if subst is None:
                    return None
            
            return subst
        
        # Can't unify
        return None