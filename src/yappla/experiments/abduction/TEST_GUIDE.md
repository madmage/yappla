# Pytest Test Suite for Abduction Logic Programming Engine

## Quick Start

Run all tests:
```bash
pytest test_abduction03.py -v
```

Run specific test class:
```bash
pytest test_abduction03.py::TestMedicalDiagnosis -v
```

Run specific test:
```bash
pytest test_abduction03.py::TestMedicalDiagnosis::test_greedy_coverage_strategy -v
```

Run with coverage report:
```bash
pytest test_abduction03.py --cov=abduction03 --cov-report=html
```

## Test Suite Overview

**Total Tests: 23**
**Pass Rate: 100%**

### Test Organization

1. **TestMedicalDiagnosis** (3 tests)
   - Medical diagnosis problem with multiple strategies
   - Tests: greedy_coverage, branch_and_bound, beam_search

2. **TestAnimalClassification** (2 tests)
   - Animal classification with positive and negative observations
   - Tests: normal bird case, penguin with negation

3. **TestTechSupportTwoObservations** (2 tests)
   - Technical support with 2 symptoms (no_display, no_boot)
   - Tests: branch_and_bound, greedy_coverage

4. **TestTechSupportThreeObservations** (3 tests)
   - Technical support with 3 symptoms (adds slow_performance)
   - Tests: greedy_coverage, branch_and_bound, beam_search

5. **TestIntegration** (3 tests)
   - Core engine functionality tests
   - Tests: ground facts, rule proving, negation-as-failure

6. **Parametrized Tests** (6 tests)
   - test_all_strategies_find_explanations (3 strategies)
   - test_greedy_respects_cost_hierarchy (3 cost thresholds)

7. **TestEdgeCases** (4 tests)
   - Edge cases and boundary conditions
   - Tests: already explained, impossible to explain, single observation, multiple hypotheses

### Test Coverage by Domain

| Domain | Observations | Tests |
|--------|--------------|-------|
| Medical | not_working, irritable | 3 |
| Animal (positive) | has_feathers, flies | 1 |
| Animal (negative) | has_feathers, NOT flies | 1 |
| Tech Support (2 obs) | no_display, no_boot | 2 |
| Tech Support (3 obs) | no_display, no_boot, slow_performance | 3 |
| Engine Core | Various | 3 |
| Parametrized | Various | 6 |
| Edge Cases | Various | 4 |

### Fixtures

The test suite uses pytest fixtures for knowledge bases and abducers:

- `medical_kb`: Medical diagnosis knowledge base
- `medical_abducer`: Medical abducer with cost declarations
- `animal_kb`: Animal classification knowledge base
- `animal_abducer`: Animal abducer with declarations
- `tech_support_kb`: Technical support knowledge base
- `tech_support_abducer`: Tech support abducer with costs

### Key Test Cases Explained

#### Medical Diagnosis
- **Greedy Coverage**: Should find tired (cost 1.0) as optimal
- **Branch & Bound**: Should find tired as optimal solution
- **Beam Search**: Tests beam search (may have suboptimal results)

#### Animal Classification
- **Normal Bird**: bird(tweety) alone explains has_feathers + flies
- **Penguin with Negation**: Documents known limitation with negations

#### Technical Support 2 Symptoms
- **Observations**: no_display + no_boot
- **Expected**: power_issue (cost 2.0) explains both

#### Technical Support 3 Symptoms
- **Observations**: no_display + no_boot + slow_performance
- **Expected**: power_issue (2.0) + malware (1.0) = 3.0 total cost

### What Each Test Verifies

1. **Correctness**: Does the engine find valid explanations?
2. **Optimality**: Does it find the cheapest explanation?
3. **Coverage**: Does it cover all observations?
4. **Robustness**: Does it handle edge cases gracefully?
5. **Strategy Comparison**: Do different strategies work?

### Known Limitations Tested

The test suite documents known limitations:

1. **Beam Search Suboptimality**
   - Test: `test_complex_diagnosis_beam_search`
   - Status: Currently returns suboptimal solutions

2. **Negation-as-Failure Handling**
   - Test: `test_penguin_classification_with_negation`
   - Status: Known limitation documented

### Running Specific Test Groups

By keyword:
```bash
pytest test_abduction03.py -k "medical" -v
pytest test_abduction03.py -k "beam_search" -v
pytest test_abduction03.py -k "greedy" -v
```

By marker:
```bash
pytest test_abduction03.py -m "not slow" -v
```

### Output Examples

Successful run:
```
======================== 23 passed in 0.07s ========================
```

With verbose output:
```
test_abduction03.py::TestMedicalDiagnosis::test_greedy_coverage_strategy PASSED [  4%]
test_abduction03.py::TestMedicalDiagnosis::test_branch_and_bound_strategy PASSED [  8%]
...
```

### Tips for Adding More Tests

1. Create a new fixture for your knowledge base
2. Add test class or test function
3. Use assertions to verify behavior:
   ```python
   assert len(explanations) > 0, "Should find explanation"
   assert best.cost == expected_cost, f"Expected {expected_cost}, got {best.cost}"
   assert len(best.covered_observations) == num_obs
   ```

### Integration with CI/CD

For GitHub Actions or other CI/CD:
```bash
pytest test_abduction03.py -v --junit-xml=test-results.xml
```

### Debugging Failed Tests

Run with detailed output:
```bash
pytest test_abduction03.py -vv --tb=long
```

Drop into debugger on failure:
```bash
pytest test_abduction03.py -vv --pdb
```

### Test Dependencies

- Python 3.6+
- pytest 4.6+
- abduction03.py (the engine being tested)

All dependencies are satisfied if the main abduction03.py file works.
