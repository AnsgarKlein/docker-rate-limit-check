#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"

# Change directory to project root
cd "$PROJECT_ROOT" || exit 1

# Name of python package
PYTHON_PACKAGE='docker_rate_limit_check'

# Whether or not an error occurred
errors=no


if ! command -v mypy > /dev/null 2>&1; then
    echo 'Error: Can not run mypy!' > /dev/stderr
    echo 'mypy is not installed!' > /dev/stderr
else
    echo 'Running mypy...'
    if ! mypy $PYTHON_PACKAGE; then
        errors='yes'
    fi
fi
echo ''
echo ''


if ! command -v pylint > /dev/null 2>&1; then
    echo 'Error: Can not run pylint!' > /dev/stderr
    echo 'pylint is not installed!' > /dev/stderr
else
    echo 'Running pylint...'
    if ! pylint $PYTHON_PACKAGE; then
        errors='yes'
    fi
fi
echo ''
echo ''


if ! command -v pydoclint > /dev/null 2>&1; then
    echo 'Error: Can not run pydoclint!' > /dev/stderr
    echo 'pydoclint is not installed!' > /dev/stderr
else
    echo 'Running pydoclint...'
    if ! pydoclint $PYTHON_PACKAGE; then
        errors='yes'
    fi
fi
echo ''
echo ''


if ! command -v pytype > /dev/null 2>&1; then
    echo 'Error: Can not run pytype!' > /dev/stderr
    echo 'pytype is not installed!' > /dev/stderr
else
    echo 'Running pytype...'
    if ! pytype --jobs auto $PYTHON_PACKAGE; then
        errors='yes'
    fi
fi


# Return with error code if any linter returned an error
if [ "$errors" = 'yes' ]; then
    exit 1
fi
