#!/bin/bash

PYTHON_BIN='docker-rate-limit.py'
PYTHON_MOD='docker_rate_limit'

mypy $PYTHON_BIN $PYTHON_MOD

pylint $PYTHON_BIN $PYTHON_MOD

pydoclint $PYTHON_BIN $PYTHON_MOD

pytype $PYTHON_BIN $PYTHON_MOD
