╔════════════════════════════════════════════════════════════════════════════╗
║                         QUICK REFERENCE - PYTEST                            ║
╚════════════════════════════════════════════════════════════════════════════╝

FILE: test_abduction03.py (21 KB, 553 lines)
TESTS: 23 total | 23 passing | 0 failing | ~0.06 seconds

═════════════════════════════════════════════════════════════════════════════

BASIC COMMANDS:
───────────────

# Run all tests with verbose output
pytest test_abduction03.py -v

# Run quietly (just summary)
pytest test_abduction03.py -q

# Run specific test class
pytest test_abduction03.py::TestMedicalDiagnosis -v

# Run specific test
pytest test_abduction03.py::TestMedicalDiagnosis::test_greedy_coverage_strategy

# Run tests matching keyword
pytest test_abduction03.py -k "medical" -v
pytest test_abduction03.py -k "greedy" -v
pytest test_abduction03.py -k "branch_and_bound" -v

═════════════════════════════════════════════════════════════════════════════

PYTEST OPTIONS:
────────────────

-v, --verbose          Show test names and results
-q, --quiet            Minimal output
-x, --exitfirst        Stop after first failure
-s, --capture=no       Show print statements
--tb=short             Brief traceback
--tb=long              Full traceback
--tb=no                No traceback
-k EXPRESSION          Select tests by keyword
--co                   Collect tests without running
--lf                   Run last failed
--ff                   Failed first, then other
--maxfail=N            Stop after N failures

═════════════════════════════════════════════════════════════════════════════

COMMON WORKFLOWS:
─────────────────

# Development workflow
pytest test_abduction03.py -v

# CI/CD pipeline
pytest test_abduction03.py -v --tb=short

# Debug single test
pytest test_abduction03.py::TestName::test_name -vv -s

# Run until first failure
pytest test_abduction03.py -x

# Run only failed tests
pytest test_abduction03.py --lf

# Generate coverage report
pytest test_abduction03.py --cov=abduction03 --cov-report=html

═════════════════════════════════════════════════════════════════════════════

TEST CATEGORIES:
────────────────

MEDICAL DIAGNOSIS:
  pytest test_abduction03.py::TestMedicalDiagnosis -v

ANIMAL CLASSIFICATION:
  pytest test_abduction03.py::TestAnimalClassification -v

TECH SUPPORT (2 observations):
  pytest test_abduction03.py::TestTechSupportTwoObservations -v

TECH SUPPORT (3 observations):
  pytest test_abduction03.py::TestTechSupportThreeObservations -v

INTEGRATION TESTS:
  pytest test_abduction03.py::TestIntegration -v

EDGE CASES:
  pytest test_abduction03.py::TestEdgeCases -v

═════════════════════════════════════════════════════════════════════════════

STRATEGY TESTS:
────────────────

GREEDY COVERAGE:
  pytest test_abduction03.py -k "greedy" -v

BRANCH AND BOUND:
  pytest test_abduction03.py -k "branch_and_bound" -v

BEAM SEARCH:
  pytest test_abduction03.py -k "beam_search" -v

═════════════════════════════════════════════════════════════════════════════

EXPECTED OUTPUT:
─────────────────

$ pytest test_abduction03.py -v

collected 23 items

test_abduction03.py::TestMedicalDiagnosis::test_greedy_coverage_strategy ✓
test_abduction03.py::TestMedicalDiagnosis::test_branch_and_bound_strategy ✓
test_abduction03.py::TestMedicalDiagnosis::test_beam_search_strategy ✓
test_abduction03.py::TestAnimalClassification::test_normal_bird_classification ✓
test_abduction03.py::TestAnimalClassification::test_penguin_classification_with_negation ✓
test_abduction03.py::TestTechSupportTwoObservations::test_optimal_diagnosis_branch_and_bound ✓
test_abduction03.py::TestTechSupportTwoObservations::test_optimal_diagnosis_greedy ✓
test_abduction03.py::TestTechSupportThreeObservations::test_complex_diagnosis_greedy ✓
test_abduction03.py::TestTechSupportThreeObservations::test_complex_diagnosis_branch_and_bound ✓
test_abduction03.py::TestTechSupportThreeObservations::test_complex_diagnosis_beam_search ✓
test_abduction03.py::TestIntegration::test_entailment_engine_ground_facts ✓
test_abduction03.py::TestIntegration::test_entailment_engine_with_rules ✓
test_abduction03.py::TestIntegration::test_negation_as_failure ✓
test_abduction03.py::test_all_strategies_find_explanations[greedy_coverage] ✓
test_abduction03.py::test_all_strategies_find_explanations[branch_and_bound] ✓
test_abduction03.py::test_all_strategies_find_explanations[beam_search] ✓
test_abduction03.py::test_greedy_respects_cost_hierarchy[1.0] ✓
test_abduction03.py::test_greedy_respects_cost_hierarchy[2.0] ✓
test_abduction03.py::test_greedy_respects_cost_hierarchy[3.0] ✓
test_abduction03.py::TestEdgeCases::test_already_explained_observations ✓
test_abduction03.py::TestEdgeCases::test_impossible_to_explain ✓
test_abduction03.py::TestEdgeCases::test_single_observation ✓
test_abduction03.py::TestEdgeCases::test_multiple_equivalent_hypotheses ✓

========================== 23 passed in 0.06s ===========================

═════════════════════════════════════════════════════════════════════════════

KEY TEST NAMES:
────────────────

TestMedicalDiagnosis::
  - test_greedy_coverage_strategy
  - test_branch_and_bound_strategy
  - test_beam_search_strategy

TestAnimalClassification::
  - test_normal_bird_classification
  - test_penguin_classification_with_negation

TestTechSupportTwoObservations::
  - test_optimal_diagnosis_branch_and_bound
  - test_optimal_diagnosis_greedy

TestTechSupportThreeObservations::
  - test_complex_diagnosis_greedy
  - test_complex_diagnosis_branch_and_bound
  - test_complex_diagnosis_beam_search

TestIntegration::
  - test_entailment_engine_ground_facts
  - test_entailment_engine_with_rules
  - test_negation_as_failure

TestEdgeCases::
  - test_already_explained_observations
  - test_impossible_to_explain
  - test_single_observation
  - test_multiple_equivalent_hypotheses

Parametrized::
  - test_all_strategies_find_explanations[strategy]
  - test_greedy_respects_cost_hierarchy[cost]

═════════════════════════════════════════════════════════════════════════════

FIXTURE SETUP:
───────────────

# Medical
@pytest.fixture
def medical_kb():
    # Returns knowledge base with medical rules

@pytest.fixture
def medical_abducer(medical_kb):
    # Returns abducer with cost declarations

# Animal
@pytest.fixture
def animal_kb():
    # Returns animal classification KB

@pytest.fixture
def animal_abducer(animal_kb):
    # Returns animal abducer

# Tech Support
@pytest.fixture
def tech_support_kb():
    # Returns tech support KB

@pytest.fixture
def tech_support_abducer(tech_support_kb):
    # Returns tech support abducer with costs

═════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING:
─────────────────

pytest not found:
  $ python3 -m pytest test_abduction03.py -v

Import error:
  Make sure abduction03.py is in same directory

Test fails unexpectedly:
  $ pytest test_abduction03.py -vv --tb=long

Show print statements:
  $ pytest test_abduction03.py -s

Debug specific test:
  $ pytest test_abduction03.py::TestName::test_name -vv --pdb

═════════════════════════════════════════════════════════════════════════════

DOCUMENTATION:
────────────────

For detailed information, see:
- TEST_GUIDE.md - Comprehensive test guide
- PYTEST_SUMMARY.md - Detailed summary
- test_abduction03.py - Well-commented source code

═════════════════════════════════════════════════════════════════════════════
