#!/bin/bash

PYTHON_MOD='docker_rate_limit'

mypy $PYTHON_MOD

pylint $PYTHON_MOD

pydoclint $PYTHON_MOD

pytype $PYTHON_MOD
