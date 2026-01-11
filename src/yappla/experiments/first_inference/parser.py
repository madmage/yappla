import re
from typing import List, Any, Optional
from terms import Fact, Rule, Variable


class LogicParser:
    """Parser for Prolog-like facts, rules, and queries"""
    
    @staticmethod
    def parse_fact(fact_str: str) -> Optional[Fact]:
        """Parse a fact string into a Fact object"""
        fact_str = fact_str.strip()
        
        if fact_str.endswith('.'):
            fact_str = fact_str[:-1].strip()
        
        pattern = r'^([a-z_][a-zA-Z0-9_]*)\s*\((.*)\)$'
        match = re.match(pattern, fact_str)
        
        if not match:
            return None
        
        predicate = match.group(1)
        args_str = match.group(2).strip()
        
        if not args_str:
            return Fact(predicate, [])
        
        arguments = LogicParser._parse_arguments(args_str)
        return Fact(predicate, arguments)
    
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
        head = LogicParser.parse_fact(head_str)
        if head is None:
            return None
        
        # Parse body (comma-separated facts)
        body_facts = []
        for fact_str in LogicParser._split_body(body_str):
            fact = LogicParser.parse_fact(fact_str.strip())
            if fact is None:
                return None
            body_facts.append(fact)
        
        return Rule(head, body_facts)
    
    @staticmethod
    def _split_body(body_str: str) -> List[str]:
        """Split body of rule on commas, respecting parentheses"""
        parts = []
        current = ""
        depth = 0
        
        for char in body_str:
            if char == '(':
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
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
                arguments.append(LogicParser._parse_single_argument(current_arg.strip()))
                current_arg = ""
            else:
                current_arg += char
        
        if current_arg.strip():
            arguments.append(LogicParser._parse_single_argument(current_arg.strip()))
        
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
            nested_fact = LogicParser.parse_fact(arg)
            if nested_fact:
                return nested_fact
        
        # Variables (uppercase) or atoms (lowercase)
        if arg and arg[0].isupper():
            return Variable(arg)
        
        return arg