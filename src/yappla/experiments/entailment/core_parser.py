import re
from typing import List, Any, Optional, Union
from core import Atom, Rule, Variable
from constraints import NotEqualConstraint, DomainConstraint


class CoreParser:
    """Parser for Prolog-like facts, rules, and queries"""
    
    @staticmethod
    def parse_fact(fact_str: str) -> Optional[Atom]:
        """Parse a fact string into an Atom object"""
        fact_str = fact_str.strip()
        
        if fact_str.endswith('.'):
            fact_str = fact_str[:-1].strip()
        
        pattern = r'^([a-z_][a-zA-Z0-9_]*)\s*\((.*)\)$'
        match = re.match(pattern, fact_str)
        
        if not match:
            return None
        
        predicate_name = match.group(1)
        args_str = match.group(2).strip()
        
        if not args_str:
            return Atom(predicate_name, [])
        
        arguments = CoreParser._parse_arguments(args_str)
        return Atom(predicate_name, arguments)

    @staticmethod
    def parse_constraint(constraint_str: str) -> Optional[NotEqualConstraint]:
        """Parse a constraint string like 'X != Y' into a NotEqualConstraint object"""
        constraint_str = constraint_str.strip()
        
        if constraint_str.endswith('.'):
            constraint_str = constraint_str[:-1].strip()
        
        # Match pattern: arg1 != arg2
        pattern = r'^(.+?)\s*!=\s*(.+)$'
        match = re.match(pattern, constraint_str)
        
        if not match:
            return None
        
        arg1 = match.group(1).strip()
        arg2 = match.group(2).strip()
        
        # Both arguments should be variables or atoms
        if arg1 and arg2:
            return NotEqualConstraint(arg1, arg2)
        
        return None

    @staticmethod
    def parse_domain_constraint(constraint_str: str) -> Optional[DomainConstraint]:
        """Parse a domain constraint in the form 'X in 1..4' or 'X in {a, b, c}'"""
        constraint_str = constraint_str.strip()
        
        if constraint_str.endswith('.'):
            constraint_str = constraint_str[:-1].strip()
        
        # Match pattern: var in ...
        pattern = r'^(\w+)\s+in\s+(.+)$'
        match = re.match(pattern, constraint_str)
        
        if not match:
            return None
        
        var = match.group(1).strip()
        domain_str = match.group(2).strip()
        
        # Try to parse as a range: 1..4
        range_match = re.match(r'^(\d+)\.\.(\d+)$', domain_str)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            values = list(range(start, end + 1))
            return DomainConstraint(var, values)
        
        # Try to parse as a set: {a, b, c}
        set_match = re.match(r'^\{(.+)\}$', domain_str)
        if set_match:
            items_str = set_match.group(1)
            # Parse comma-separated items
            items = [item.strip() for item in items_str.split(',')]
            # Convert to appropriate types (try int, then string)
            values = []
            for item in items:
                try:
                    values.append(int(item))
                except ValueError:
                    values.append(item)
            return DomainConstraint(var, values)
        
        return None
    
    @staticmethod
    def parse_rule(rule_str: str) -> Optional[Rule]:
        """Parse a rule string: head :- body1, body2, ..."""
        rule_str = rule_str.strip()
        
        if rule_str.endswith('.'):
            rule_str = rule_str[:-1].strip()
        
        # Split on :-
        if ':-' not in rule_str:
            return None
        
        parts = rule_str.split(':-', 1)
        if len(parts) != 2:
            return None
        
        head_str = parts[0].strip()
        body_str = parts[1].strip()
        
        # Parse head
        head = CoreParser.parse_fact(head_str)
        if head is None:
            return None
        
        # Parse body (comma-separated facts and constraints)
        body_facts = []
        for item_str in CoreParser._split_body(body_str):
            item_str = item_str.strip()
            
            # Try to parse as a != constraint
            if '!=' in item_str:
                constraint = CoreParser.parse_constraint(item_str)
                if constraint is not None:
                    body_facts.append(constraint)
                    continue
                else:
                    # If constraint parsing failed, it's an error
                    return None
            
            # Try to parse as a domain constraint (with 'in' keyword)
            if ' in ' in item_str:
                domain_constraint = CoreParser.parse_domain_constraint(item_str)
                if domain_constraint is not None:
                    body_facts.append(domain_constraint)
                    continue
                else:
                    # If constraint parsing failed, it's an error
                    return None
            
            # Try to parse as a regular fact
            fact = CoreParser.parse_fact(item_str)
            if fact is None:
                return None
            body_facts.append(fact)
        
        return Rule(head, body_facts)
    
    @staticmethod
    def _split_body(body_str: str) -> List[str]:
        """Split body of rule on commas, respecting parentheses and braces"""
        parts = []
        current = ""
        paren_depth = 0
        brace_depth = 0
        
        for char in body_str:
            if char == '(':
                paren_depth += 1
                current += char
            elif char == ')':
                paren_depth -= 1
                current += char
            elif char == '{':
                brace_depth += 1
                current += char
            elif char == '}':
                brace_depth -= 1
                current += char
            elif char == ',' and paren_depth == 0 and brace_depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            parts.append(current.strip())
        
        return parts
    
    @staticmethod
    def _parse_arguments(args_str: str) -> List[Any]:
        """Parse comma-separated arguments"""
        arguments = []
        current_arg = ""
        paren_depth = 0
        in_string = False
        string_char = None
        
        for char in args_str:
            if in_string:
                current_arg += char
                if char == string_char and (len(current_arg) < 2 or current_arg[-2] != '\\'):
                    in_string = False
            elif char in ('"', "'"):
                in_string = True
                string_char = char
                current_arg += char
            elif char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                arguments.append(CoreParser._parse_single_argument(current_arg.strip()))
                current_arg = ""
            else:
                current_arg += char
        
        if current_arg.strip():
            arguments.append(CoreParser._parse_single_argument(current_arg.strip()))
        
        return arguments
    
    @staticmethod
    def _parse_single_argument(arg: str) -> Any:
        """Parse a single argument into its appropriate type"""
        arg = arg.strip()
        
        # String literals
        if (arg.startswith('"') and arg.endswith('"')) or \
           (arg.startswith("'") and arg.endswith("'")):
            return arg[1:-1]
        
        # Numbers
        try:
            if '.' in arg:
                return float(arg)
            else:
                return int(arg)
        except ValueError:
            pass
        
        # Nested facts
        if '(' in arg and arg.endswith(')'):
            nested_fact = CoreParser.parse_fact(arg)
            if nested_fact:
                return nested_fact
        
        # Variables (uppercase) or atoms (lowercase)
        if arg and arg[0].isupper():
            return Variable(arg)
        
        return arg

    @staticmethod
    def parse_query(query_str: str) -> Optional[List[Any]]:
        """Parse a query string which can be a conjunction of goals: goal1, goal2, ...
        
        Returns a list of goals (predicates and/or constraints) or None if parsing fails.
        """
        query_str = query_str.strip()
        
        if query_str.endswith('.'):
            query_str = query_str[:-1].strip()
        
        if not query_str:
            return None
        
        # Split on commas, respecting parentheses and braces
        goals = []
        for goal_str in CoreParser._split_body(query_str):
            goal_str = goal_str.strip()
            
            # Try to parse as a != constraint
            if '!=' in goal_str:
                constraint = CoreParser.parse_constraint(goal_str)
                if constraint is not None:
                    goals.append(constraint)
                    continue
                else:
                    return None
            
            # Try to parse as a domain constraint (with 'in' keyword)
            if ' in ' in goal_str:
                domain_constraint = CoreParser.parse_domain_constraint(goal_str)
                if domain_constraint is not None:
                    goals.append(domain_constraint)
                    continue
                else:
                    return None
            
            # Try to parse as a regular fact
            fact = CoreParser.parse_fact(goal_str)
            if fact is None:
                return None
            goals.append(fact)
        
        return goals if goals else None
