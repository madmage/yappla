#!/bin/bash
# Quick start guide for running the induction engine tests

echo "=== Rule Induction Engine - Test Suite ==="
echo ""
echo "Running all 11 pytest tests..."
echo ""

cd /home/calisi/personal/shared/dropbox-madmage/private/devel/yappla/src/yappla/experiments/induction

# Run with timeout to prevent hanging
timeout 30 python3 -m pytest test_induction11.py -v

echo ""
echo "=== Test Results Summary ==="
echo ""
echo "Test Categories:"
echo "  1. Entailment Checker Tests (3 tests)"
echo "     - Simple fact entailment"
echo "     - Rule entailment with conjunctions"
echo "     - Grandparent rule with intermediate variables"
echo ""
echo "  2. Top-Down Inducer Tests (3 tests)"  
echo "     - Learns at least one rule"
echo "     - Learned rules cover all positives"
echo "     - Learned rules reject all negatives"
echo ""
echo "  3. Inverse Entailment Inducer Tests (3 tests)"
echo "     - Learns at least one rule"
echo "     - Learned rules cover all positives"
echo "     - Learned rules reject all negatives"
echo ""
echo "  4. Bottom-Up Inducer Tests (2 tests)"
echo "     - Returns rules or empty list"
echo "     - Learned rules don't cover negatives (if any learned)"
echo ""
echo "Total: 11 tests"
echo "Expected Result: ALL PASSED ✓"
