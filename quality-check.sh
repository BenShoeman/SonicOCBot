#!/bin/bash

cd $(dirname "${BASH_SOURCE[0]}")

# Unit tests
echo "--- Unit tests ---"
python3 -m unittest discover tests -p "Test*"
unittest_exit_code=$?
echo

# MyPy type checking
echo "--- MyPy type checking ---"
mypy --ignore-missing-imports --disallow-untyped-defs --disallow-incomplete-defs -p src -p main -p train -p tests -p utils
mypy_exit_code=$?
echo

# Unimport unused import checking
echo "--- Unimport unused import checking ---"
python -m unimport --ignore-init src main.py train.py tests utils
unimport_exit_code=$?
echo

# Black format checking
echo "--- Black format checking ---"
black --check --line-length 160 src main.py train.py tests utils/**/*.py
black_exit_code=$?
echo

if [ $(echo $unittest_exit_code + $mypy_exit_code + $unimport_exit_code + $black_exit_code | bc) -ne 0 ]; then
  if [ $unittest_exit_code -ne 0 ]; then echo "Unit tests failed."                     ; fi
  if [     $mypy_exit_code -ne 0 ]; then echo "MyPy type checking failed."             ; fi
  if [ $unimport_exit_code -ne 0 ]; then echo "Unimport unused import checking failed."; fi
  if [    $black_exit_code -ne 0 ]; then echo "Black format checking failed."          ; fi
  exit 1
else
  echo "All checks passed."
fi

exit 0
