"""
Analysis of expected outputs for abduction03.py tests

Based on abductive reasoning principles:
1. An explanation must make all observations entailed from the KB
2. The explanation should be minimal (least cost, fewest hypotheses)
3. The explanation should be consistent (no contradictions)

TEST 1: Medical Diagnosis
Observations: not_working(alice), irritable(alice)
KB Rules:
  - not_working(X) :- sick(X)
  - not_working(X) :- tired(X)
  - not_working(X) :- injured(X)
  - irritable(X) :- stressed(X)
  - irritable(X) :- tired(X)
  - irritable(X) :- sick(X)

Abducibles: sick (cost 2.0), tired (cost 1.0), stressed (cost 1.5), injured (cost 3.0)

Analysis:
- To explain not_working(alice): need one of {sick, tired, injured}
- To explain irritable(alice): need one of {stressed, tired, sick}
- Optimal: tired(alice) covers both with cost 1.0
  ✓ tired(alice) => not_working(alice) ✓
  ✓ tired(alice) => irritable(alice) ✓
- Alternative: sick(alice) also covers both but costs 2.0
- Alternative: stressed(alice) + tired/sick/injured for not_working

EXPECTED FOR TEST 1:
- Greedy Coverage: {tired(alice)}, coverage=2, cost=1.0
- Branch and Bound: {tired(alice)}, coverage=2, cost=1.0 (optimal)
- Beam Search: {tired(alice)}, coverage=2, cost=1.0


TEST 2a: Animal Classification (tweety)
Observations: has_feathers(tweety), flies(tweety)
KB Rules:
  - flies(X) :- bird(X), not abnormal(X)
  - has_feathers(X) :- bird(X)
  - lays_eggs(X) :- bird(X)
  - swims(X) :- penguin(X)
  - bird(X) :- penguin(X)
  - abnormal(X) :- penguin(X)

Abducibles: bird, penguin, abnormal

Analysis:
- To explain has_feathers(tweety): need bird(tweety)
- To explain flies(tweety): need bird(tweety) AND not abnormal(tweety)
  - So we need bird(tweety) and must NOT have abnormal(tweety)
  - Since abnormal is an abducible, we just don't abduce it
- Optimal: {bird(tweety)}, coverage=2, cost=1.0 (or 0 if no cost specified)

EXPECTED FOR TEST 2a:
- {bird(tweety)}, coverage=2, cost=1.0


TEST 2b: Animal Classification (opus - non-flying bird)
Observations: has_feathers(opus), not flies(opus)
KB Rules: (same as above)

Analysis:
- To explain has_feathers(opus): need bird(opus)
- To explain not flies(opus): need either:
  a) NOT bird(opus) - contradicts first observation
  b) bird(opus) AND abnormal(opus) - need both bird and abnormal
- Optimal: {bird(opus), abnormal(opus)}, coverage=2, cost=2.0
- Current result shows: {bird(opus)}, coverage=1, cost=1.0
  This only covers has_feathers, NOT the negation

⚠️ This test result appears INCORRECT - it doesn't fully explain not flies(opus)

EXPECTED FOR TEST 2b:
- {bird(opus), abnormal(opus)}, coverage=2, cost=2.0


TEST 3: Technical Support (Two symptoms)
Observations: no_display(laptop1), no_boot(laptop1)
KB Rules:
  - no_display(X) :- power_issue(X)
  - no_display(X) :- broken_screen(X)
  - no_boot(X) :- power_issue(X)
  - no_boot(X) :- hard_drive_failure(X)
  - slow_performance(X) :- insufficient_ram(X)
  - slow_performance(X) :- malware(X)
  - overheating(X) :- dust_buildup(X)
  - overheating(X) :- fan_failure(X)

Costs: power_issue=2.0, broken_screen=5.0, hard_drive_failure=4.0, 
       insufficient_ram=1.5, malware=1.0, dust_buildup=1.0, fan_failure=3.0

Analysis:
- To explain no_display: power_issue(2.0) OR broken_screen(5.0)
- To explain no_boot: power_issue(2.0) OR hard_drive_failure(4.0)
- Optimal: power_issue(laptop1) covers both with cost 2.0
- Sub-optimal: broken_screen + hard_drive_failure = cost 9.0
- Current results show: {power_issue(laptop1)}, coverage=2, cost=2.0 ✓

EXPECTED FOR TEST 3:
- Branch and Bound: {power_issue(laptop1)}, coverage=2, cost=2.0 ✓
- Greedy Coverage: {power_issue(laptop1)}, coverage=2, cost=2.0 ✓


TEST 4: Technical Support (Three symptoms)
Observations: no_display(laptop1), no_boot(laptop1), slow_performance(laptop1)
Same KB as TEST 3

Analysis:
- Explain no_display: power_issue OR broken_screen
- Explain no_boot: power_issue OR hard_drive_failure  
- Explain slow_performance: insufficient_ram OR malware
- Optimal strategy:
  a) power_issue(2.0) covers first two, need one of {insufficient_ram(1.5), malware(1.0)}
     - power_issue + malware = 2.0 + 1.0 = 3.0 ✓ BEST
     - power_issue + insufficient_ram = 2.0 + 1.5 = 3.5
  b) broken_screen(5.0) + hard_drive_failure(4.0) + malware(1.0) = 10.0
- Current Greedy result: {malware(laptop1), power_issue(laptop1)}, coverage=3, cost=3.0 ✓

EXPECTED FOR TEST 4:
- Greedy Coverage: {power_issue(laptop1), malware(laptop1)}, coverage=3, cost=3.0 ✓
- Branch and Bound: {power_issue(laptop1), malware(laptop1)}, coverage=3, cost=3.0 ✓
- Beam Search: {power_issue(laptop1), malware(laptop1)}, coverage=3, cost=3.0 ✓
"""

print(__doc__)
