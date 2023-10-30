#!/bin/bash

PYTHON_FILES='*.py'

mypy $PYTHON_FILES

pylint $PYTHON_FILES

pydoclint $PYTHON_FILES

pytype $PYTHON_FILES
