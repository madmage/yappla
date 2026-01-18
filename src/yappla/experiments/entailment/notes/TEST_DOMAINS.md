% Test Knowledge Base Domains
% ============================
% This directory contains 5 test domains for the Logic Inference Engine REPL.
% Each domain demonstrates different aspects of the logic engine.

% USAGE:
% 1. Start the REPL: python3 repl.py
% 2. Load a domain: LOAD KB family.kb (or any other .kb file)
% 3. Query the domain: ENTAIL grandparent(tom, ann)
% 4. List facts: facts
% 5. List rules: rules

% ============================================================================
% 1. family.kb - Basic Fact and Rule Reasoning
% ============================================================================
% Focus: Simple transitive relationships, multi-level inference
% Features:
%   - Basic facts (parent relationships)
%   - Simple rules (grandparent, sibling)
%   - Transitive rules (ancestor through recursion)
%   - Multi-level rule composition (greatgrandparent)
% 
% Example queries:
%   ENTAIL parent(tom, bob)
%   ENTAIL grandparent(tom, ann)
%   ENTAIL ancestor(tom, jim)
%   ENTAIL sibling(bob, liz)

% ============================================================================
% 2. robots.kb - Facts with Multiple Predicates
% ============================================================================
% Focus: Robot domain with locations and operational states
% Features:
%   - Multiple independent fact types (robot, location)
%   - Rules combining different facts
%   - Derived properties (operational, available)
%
% Example queries:
%   ENTAIL robot(r1)
%   ENTAIL location(r2, factory)
%   ENTAIL operational(r1)
%   ENTAIL in_warehouse(r1)

% ============================================================================
% 3. graph.kb - Path Finding and Graph Traversal
% ============================================================================
% Focus: Recursive rule application for path finding
% Features:
%   - Graph edges as facts
%   - Recursive path finding (single step + multi-step paths)
%   - Symmetric relations (connected in both directions)
%   - Complex multi-level queries
%
% Example queries:
%   ENTAIL edge(a, b)
%   ENTAIL path(a, c)
%   ENTAIL path(a, e) (finds paths through multiple edges)
%   ENTAIL connected(a, e)

% ============================================================================
% 4. university.kb - Complex Domain with Multiple Entity Types
% ============================================================================
% Focus: Real-world domain with students, courses, instructors
% Features:
%   - Multiple fact types (student, course, enrolled, instructor)
%   - Multi-argument rules
%   - Derived knowledge from multiple fact sources
%   - Practical reasoning examples
%
% Example queries:
%   ENTAIL student(alice)
%   ENTAIL enrolled(alice, algorithms)
%   ENTAIL taught_by(algorithms, dr_smith)
%   ENTAIL student_of(alice, dr_smith)
%   ENTAIL active_course(algorithms)

% ============================================================================
% 5. philosophy.kb - Self-Referential and Meta-Reasoning
% ============================================================================
% Focus: Meta-level reasoning and philosophical propositions
% Features:
%   - Self-referential facts (propositions about logic)
%   - Multiple inheritance (entity can be both human and philosopher)
%   - Abstract concepts
%   - Type-based reasoning
%
% Example queries:
%   ENTAIL human(socrates)
%   ENTAIL mortal(socrates)
%   ENTAIL philosopher(socrates)
%   ENTAIL entity(socrates)
%   ENTAIL historical_figure(plato)

% ============================================================================
% 6. example_kb.txt - Original Example Domain
% ============================================================================
% (Provided as reference - similar to family.kb but with different names)
