#!/usr/bin/env python3
"""
Logic Inference Engine with Prolog-like syntax
Supports facts, rules, queries, and unification
"""

import cmd
import os
from typing import Any, List
from knowledge_base import KnowledgeBase
from entailment_engine import EntailmentEngine
from core_parser import CoreParser
from core import Variable, Atom


class LogicREPL(cmd.Cmd):
    """REPL for the logic inference engine"""
    intro = "Logic Inference Engine REPL. Use 'KB fact.' for facts, 'KB rule.' for rules, 'ENTAIL query' for queries.\n"
    prompt = "> "
    command_prefix = '/'
    
    def __init__(self):
        super().__init__()
        self.kb = KnowledgeBase()
        self.engine = EntailmentEngine(self.kb)
        self.kb_input_mode = False
        self.kb_buffer = []
    
    def onecmd(self, line):
        # Only process as commands if line starts with prefix
        if line.startswith(self.command_prefix):
            # Strip prefix and let cmd.Cmd handle it normally
            line = line[len(self.command_prefix):]
            return super().onecmd(line)
        else:
            # No prefix - send to default() for custom handling
            return self.default(line)
    
    def default(self, line: str):
        """Handle fact assertions, rules, queries, and KB input mode"""
        line = line.strip()
        
        if not line:
            return
        
        # Handle KB input mode
        if self.kb_input_mode:
            if line == "END KB":
                self._process_kb_buffer()
                self.kb_input_mode = False
                return
            else:
                self.kb_buffer.append(line)
                return
        
        # Check if it's a BEGIN KB command
        if line == "BEGIN KB":
            self.kb_input_mode = True
            self.kb_buffer = []
            print("Entering KB input mode. Type 'END KB' to finish.")
            return
        
        # Check if it's a LOAD KB command
        if line.startswith('LOAD KB '):
            filename = line[8:].strip()
            self._load_kb_file(filename)
            return
        
        # Check if it's a labeling query (starts with LABEL)
        if line.startswith('LABEL '):
            self._handle_label(line[9:].strip())
            return
        
        # Check if it's a query (starts with ENTAIL)
        if line.startswith('ENTAIL '):
            self._handle_query(line[7:].strip())
            return
        
        # Check if it's knowledge base addition (starts with KB)
        if line.startswith('KB '):
            kb_line = line[3:].strip()
            if ':-' in kb_line:
                self._handle_rule(kb_line)
            else:
                self._handle_fact(kb_line)
            return
        
        # Invalid syntax
        print("Invalid syntax. Use 'KB fact.' for facts, 'KB rule.' for rules, 'ENTAIL query' for queries, 'LABEL ...' for labeling.")

    
    def _handle_fact(self, line: str):
        """Handle fact assertion"""
        fact = CoreParser.parse_fact(line)
        
        if fact:
            if self.kb.add_fact(fact):
                print(f"✓ Added fact: {fact}")
            else:
                print(f"⚠ Fact already exists: {fact}")
        else:
            print(f"✗ Parse error: Could not parse '{line}'")
    
    def _handle_rule(self, line: str):
        """Handle rule assertion"""
        rule = CoreParser.parse_rule(line)
        
        if rule:
            self.kb.add_rule(rule)
            print(f"✓ Added rule: {rule}")
        else:
            print(f"✗ Parse error: Could not parse rule '{line}'")
    
    def _handle_query(self, line: str):
        """Handle query (can be single or multiple goals)"""
        # Try to parse as a potentially multi-goal query
        goals = CoreParser.parse_query(line)
        
        if goals is None:
            print(f"✗ Parse error: Could not parse query '{line}'")
            return
        
        # If only one goal, pass it directly; otherwise pass the list
        query_goal = goals[0] if len(goals) == 1 else goals
        
        print(f"Query: {', '.join(str(g) for g in goals)}")
        results = self.engine.query(query_goal)
        
        if not results:
            print("false.")
        else:
            # Extract variables from query goals
            query_vars = []
            for goal in goals:
                query_vars.extend(self._extract_variables(goal))
            # Remove duplicates while preserving order
            seen = set()
            query_vars = [v for v in query_vars if not (str(v) in seen or seen.add(str(v)))]
            
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
    
    def _process_kb_buffer(self):
        """Process all lines accumulated in KB input mode"""
        if not self.kb_buffer:
            print("No KB entries provided.")
            return
        
        for line in self.kb_buffer:
            if ':-' in line:
                self._handle_rule(line)
            else:
                self._handle_fact(line)
        
        print(f"✓ Processed {len(self.kb_buffer)} KB entry/entries")
    
    def _load_kb_file(self, filename: str):
        """Load facts and rules from a file"""
        if not os.path.exists(filename):
            print(f"✗ File not found: {filename}")
            return
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            count = 0
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('%'):
                    continue
                
                if ':-' in line:
                    self._handle_rule(line)
                else:
                    self._handle_fact(line)
                count += 1
            
            print(f"✓ Loaded {count} entry/entries from {filename}")
        except Exception as e:
            print(f"✗ Error loading file: {e}")
    
    def _handle_label(self, line: str):
        """Handle labeling query: LABEL query SUBJECT TO constraints"""
        # Parse syntax: query SUBJECT TO constraint1, constraint2, ...
        if ' SUBJECT TO ' not in line:
            print(f"✗ Labeling syntax: LABEL vars SUBJECT TO constraints")
            return
        
        parts = line.split(' SUBJECT TO ', 1)
        var_str = parts[0].strip()
        constraints_str = parts[1].strip()
        
        # Parse variable names (comma-separated)
        var_names = [v.strip() for v in var_str.split(',')]
        variables = [Variable(name) for name in var_names]
        
        # Parse constraint strings
        constraint_items = [c.strip() for c in constraints_str.split(',')]
        constraints = []
        domains = {}
        
        # Initialize domains for all variables (default: empty means unconstrained)
        for var in variables:
            domains[str(var)] = None
        
        # Parse each constraint
        for constraint_item in constraint_items:
            # Try to parse as domain constraint (X in range or X in {values})
            domain_constraint = CoreParser.parse_domain_constraint(constraint_item)
            if domain_constraint:
                var_name = str(domain_constraint.variable)
                domains[var_name] = domain_constraint.values
                continue
            
            # Try to parse as not-equal constraint (X != Y)
            not_equal_constraint = CoreParser.parse_constraint(constraint_item)
            if not_equal_constraint:
                constraints.append(not_equal_constraint)
                continue
            
            # Otherwise try to parse as an atom goal (for use in labeling query)
            goal = CoreParser.parse_fact(constraint_item)
            if goal:
                # This is an atom goal that should be satisfied
                # We'll add it as a soft constraint via the labeling query
                pass
            else:
                print(f"⚠ Warning: Could not parse constraint '{constraint_item}'")
        
        # Convert None domains to empty lists
        domain_dict = {}
        for var in variables:
            var_name = str(var)
            if domains[var_name] is not None:
                domain_dict[var_name] = domains[var_name]
        
        print(f"Variables: {', '.join(str(v) for v in variables)}")
        print(f"Domains: {domain_dict}")
        print(f"Constraints: {len(constraints)} constraint(s)")
        
        # Call the labeling function from the inference engine
        try:
            # Default objective: return 0 for all assignments (for pure constraint satisfaction)
            objective = lambda assignment: 0
            
            results = self.engine.label_variables(
                domains=domain_dict,
                constraints=constraints,
                objective=objective
            )
            
            if not results:
                print("No solution found.")
            else:
                print(f"\nFound {len(results)} solution(s):")
                for i, solution in enumerate(results[:10], 1):  # Show first 10
                    print(f"\n  Solution {i}:")
                    for var in variables:
                        var_name = str(var)
                        if var_name in solution:
                            print(f"    {var_name} = {solution[var_name]}")
                
                if len(results) > 10:
                    print(f"\n  ... and {len(results) - 10} more solution(s)")
        except Exception as e:
            print(f"✗ Error during labeling: {e}")
    
    def _extract_variables(self, term: Any) -> List[Variable]:
        """Extract all variables from a term"""
        variables = []
        
        if isinstance(term, Variable):
            variables.append(term)
        elif isinstance(term, Atom):
            for arg in term.arguments:
                variables.extend(self._extract_variables(arg))
        
        return variables
    
    def do_facts(self, arg: str):
        """List all facts or facts matching a predicate. Usage: facts [predicate]"""
        predicate = arg.strip() if arg.strip() else None
        facts = self.kb.get_facts(predicate)
        
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
        rules = self.kb.get_rules(predicate)
        
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
        fact_count, rule_count = self.kb.count()
        self.kb.clear()
        print(f"✓ Cleared {fact_count} fact(s) and {rule_count} rule(s)")
    
    def do_count(self, arg: str):
        """Show the number of facts and rules in the database"""
        fact_count, rule_count = self.kb.count()
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
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Starting REPL...\n")
    LogicREPL().cmdloop()
