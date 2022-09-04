#!/bin/bash

cd $(dirname "${BASH_SOURCE[0]}")

# MyPy type checking
echo "--- MyPy type checking ---"
mypy --ignore-missing-imports --disallow-untyped-defs --disallow-incomplete-defs -p src -p main
mypy_exit_code=$?
echo

# Unimport unused import checking
echo "--- Unimport unused import checking ---"
python -m unimport --ignore-init src main.py
unimport_exit_code=$?
echo

# Black format checking
echo "--- Black format checking ---"
black --check --line-length 160 src main.py
black_exit_code=$?
echo

if [ $(echo $mypy_exit_code + $unimport_exit_code + $black_exit_code | bc) -ne 0 ]; then
  if [     $mypy_exit_code -ne 0 ]; then echo "MyPy type checking failed."             ; fi
  if [ $unimport_exit_code -ne 0 ]; then echo "Unimport unused import checking failed."; fi
  if [    $black_exit_code -ne 0 ]; then echo "Black format checking failed."          ; fi
  exit 1
else
  echo "All checks passed."
fi

exit 0
