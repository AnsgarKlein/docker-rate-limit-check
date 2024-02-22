#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
cd "$PROJECT_ROOT"

PYTHON_MOD='docker_rate_limit'

mypy $PYTHON_MOD

pylint --rcfile .pylintrc.toml $PYTHON_MOD

pydoclint $PYTHON_MOD

pytype $PYTHON_MOD
