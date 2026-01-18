# Quick Reference: LABELING Queries

## Command Syntax
```
LABELING var1, var2, ... SUBJECT TO constraint1, constraint2, ...
```

## Quick Examples

### Example 1: Three Variables, All Different
```
LABELING X, Y, Z SUBJECT TO X in 1..3, Y in 1..3, Z in 1..3, X != Y, X != Z, Y != Z
```
**Result**: 6 solutions (all permutations of 1,2,3)

### Example 2: Two Variables, Different Time Slots
```
LABELING S1, S2 SUBJECT TO S1 in 0..5, S2 in 0..5, S1 != S2
```
**Result**: 30 solutions

### Example 3: Set-Based Domains
```
LABELING Color1, Color2 SUBJECT TO Color1 in {red, green, blue}, Color2 in {red, green, blue}, Color1 != Color2
```
**Result**: 6 solutions (different color pairs)

## Constraint Types

| Constraint | Syntax | Meaning |
|-----------|--------|---------|
| Range | `X in 1..10` | X is any integer from 1 to 10 |
| Set | `X in {a, b, c}` | X is one of: a, b, or c |
| Not-Equal | `X != Y` | X and Y must be different |

## REPL Commands for Context

| Command | Purpose |
|---------|---------|
| `LOAD KB file.kb` | Load knowledge base |
| `LABELING ... SUBJECT TO ...` | Find constraint-satisfying assignments |
| `ENTAIL goal1, goal2, ...` | Query with regular backward chaining |
| `facts` | List all facts |
| `rules` | List all rules |
| `count` | Show database statistics |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No solution found" | Check constraints aren't contradictory |
| Parse error | Ensure space after `SUBJECT TO` |
| All solutions same | Constraints might not bind variables |
| Takes too long | Reduce domain size or add more constraints |

## Performance Tips

1. **Smaller domains are faster**: Use `1..5` not `1..100`
2. **Add constraints early**: More filtering = faster search
3. **All-different constraints**: Very effective for search pruning
4. **Check results**: Verify solutions are sensible

## Files

- **repl.py**: Interactive command-line interface
- **inference.py**: Core labeling algorithm
- **constraints.py**: Constraint definitions and propagation
- **parser.py**: Syntax parsing for constraints
- **test_logic.py**: Comprehensive test suite (30 tests)
- **job_scheduling.kb**: Example domain
- **LABELING_GUIDE.md**: Full documentation

## Status

✅ **Production Ready** - All 30 tests pass, no known issues.
