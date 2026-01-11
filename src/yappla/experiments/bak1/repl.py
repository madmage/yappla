#!/usr/bin/env python3
"""
Logic Inference Engine with Prolog-like syntax
Supports facts, rules, queries, and unification
"""

import cmd
from typing import Any, List
from database import FactDatabase
from inference import InferenceEngine
from parser import LogicParser
from terms import Variable, Fact, Rule
from substitution import Substitution, Unifier


class LogicREPL(cmd.Cmd):
    """REPL for the logic inference engine"""
    
    intro = "Logic Inference Engine REPL. Type 'help' for commands.\n"
    prompt = "?- "
    
    def __init__(self):
        super().__init__()
        self.db = FactDatabase()
        self.engine = InferenceEngine(self.db)
    
    def default(self, line: str):
        """Handle fact assertions, rules, or queries"""
        line = line.strip()
        
        if not line:
            return
        
        # Check if it's a query (starts with ?)
        if line.startswith('?'):
            self._handle_query(line[1:].strip())
            return
        
        # Check if it's a rule (contains :-)
        if ':-' in line:
            self._handle_rule(line)
            return
        
        # Otherwise, treat as a fact
        self._handle_fact(line)
    
    def _handle_fact(self, line: str):
        """Handle fact assertion"""
        fact = LogicParser.parse_fact(line)
        
        if fact:
            if self.db.add_fact(fact):
                print(f"✓ Added fact: {fact}")
            else:
                print(f"⚠ Fact already exists: {fact}")
        else:
            print(f"✗ Parse error: Could not parse '{line}'")
    
    def _handle_rule(self, line: str):
        """Handle rule assertion"""
        rule = LogicParser.parse_rule(line)
        
        if rule:
            self.db.add_rule(rule)
            print(f"✓ Added rule: {rule}")
        else:
            print(f"✗ Parse error: Could not parse rule '{line}'")
    
    def _handle_query(self, line: str):
        """Handle query"""
        query = LogicParser.parse_fact(line)
        
        if query is None:
            print(f"✗ Parse error: Could not parse query '{line}'")
            return
        
        print(f"Query: {query}")
        results = self.engine.query(query)
        
        if not results:
            print("false.")
        else:
            # Extract variables from query
            query_vars = self._extract_variables(query)
            
            if not query_vars:
                print("true.")
            else:
                for i, subst in enumerate(results, 1):
                    bindings = []
                    for var in query_vars:
                        value = subst.apply(var)
                        bindings.append(f"{var} = {value}")
                    
                    print(f"  {' ,'.join(bindings)}")
                
                print(f"\n({len(results)} solution(s))")
    
    def _extract_variables(self, term: Any) -> List[Variable]:
        """Extract all variables from a term"""
        variables = []
        
        if isinstance(term, Variable):
            variables.append(term)
        elif isinstance(term, Fact):
            for arg in term.arguments:
                variables.extend(self._extract_variables(arg))
        
        return variables
    
    def do_facts(self, arg: str):
        """List all facts or facts matching a predicate. Usage: facts [predicate]"""
        predicate = arg.strip() if arg.strip() else None
        facts = self.db.get_facts(predicate)
        
        if not facts:
            if predicate:
                print(f"No facts found for predicate '{predicate}'")
            else:
                print("No facts in database")
        else:
            print(f"\n{len(facts)} fact(s):")
            for fact in facts:
                print(f"  {fact}")
            print()
    
    def do_rules(self, arg: str):
        """List all rules or rules matching a predicate. Usage: rules [predicate]"""
        predicate = arg.strip() if arg.strip() else None
        rules = self.db.get_rules(predicate)
        
        if not rules:
            if predicate:
                print(f"No rules found for predicate '{predicate}'")
            else:
                print("No rules in database")
        else:
            print(f"\n{len(rules)} rule(s):")
            for rule in rules:
                print(f"  {rule}")
            print()
    
    def do_clear(self, arg: str):
        """Clear all facts and rules from the database"""
        fact_count, rule_count = self.db.count()
        self.db.clear()
        print(f"✓ Cleared {fact_count} fact(s) and {rule_count} rule(s)")
    
    def do_count(self, arg: str):
        """Show the number of facts and rules in the database"""
        fact_count, rule_count = self.db.count()
        print(f"Database contains {fact_count} fact(s) and {rule_count} rule(s)")
    
    def do_exit(self, arg: str):
        """Exit the REPL"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg: str):
        """Exit the REPL"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg: str):
        """Exit on Ctrl+D"""
        print()
        return self.do_exit(arg)


# ============================================================================
# UNIT TESTS
# ============================================================================

# Tests moved to test_logic.py for pytest compatibility


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Starting REPL...\n")
    LogicREPL().cmdloop()
