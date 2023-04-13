#!/bin/sh

set -o errexit
set -o nounset
set -e

: "${cmd:=run_all_tests}"

run_pytest () {
  echo "Run pytest"
  PYTHONPATH=. pytest
}

run_fmt_check () {
  echo "Run formatting (isort and black) check"
  isort --check-only --diff app tests
  black . --check
}

run_flake8 () {
  echo "Run flake8 check"
  flake8 .
}

run_code_quality () {
  echo "Running code-quality check"
  xenon --max-absolute A --max-modules A --max-average A app
}

run_all_tests () {
  run_fmt_check
  run_flake8
  run_code_quality
  run_pytest
}

if [ $# -eq 0 ]; then
  echo "run all checks and tests"
  run_all_tests
else
  echo "called $*"
  "$@"
fi