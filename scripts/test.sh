#!/bin/sh

# Directory of this script
SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"

# Root directory of the project
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"

# Directory of the tests
TEST_DIR="${PROJECT_ROOT}/tests"

# Whether or not an error occurred
errors=no


# Change directory to project root
cd "$PROJECT_ROOT" || exit 1


# Check if the tests directory exists
if [ ! -d "$TEST_DIR" ]; then
    echo "Error: Tests directory $TEST_DIR does not exist!" > /dev/stderr
    exit 1
fi

echo 'Running unit tests...'
if ! python -m unittest discover -v -s "$TEST_DIR" -p "*.py"; then
    echo 'Error: Unit tests failed!' > /dev/stderr
    errors='yes'
fi



# Return with error code if tests returned an error
if [ "$errors" = 'yes' ]; then
    exit 1
fi
