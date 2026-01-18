# Unit Tests for Logic Inference Engine
# This file contains REPL commands to run all unit tests

# Test 5: Simple inference
parent(john, mary)
parent(mary, sue)
? parent(john, X)

# Test 6: Inference with rules
clear
parent(john, mary)
parent(mary, sue)
grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
? grandparent(john, Z)

# Test 7: Multiple solutions
clear
likes(john, pizza)
likes(john, pasta)
likes(mary, pizza)
? likes(john, X)

# Test 8: Arithmetic evaluation
clear
? is(X, 1 + 2)
? is(Y, 5 - 2 * 1)

# Test 9: Rules with arithmetic
clear
sum(X, Y, Z) :- is(Z, X + Y)
? sum(1, 2, Z)