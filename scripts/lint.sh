#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
cd "$PROJECT_ROOT"

PYTHON_MOD='docker_rate_limit_check'

echo 'Running mypy...'
mypy $PYTHON_MOD
echo ''
echo ''

echo 'Running pylint...'
pylint $PYTHON_MOD
echo ''
echo ''

echo 'Running pydoclint...'
pydoclint $PYTHON_MOD
echo ''
echo ''

echo 'Running pytype...'
pytype $PYTHON_MOD
