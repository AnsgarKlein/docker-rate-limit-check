#!/bin/sh

USR_BIN_ENV_EXISTS='false'
PYTHON_INTERPRETER=''
PYTHON_INTERPRETER_PATH=''

# Check if /usr/bin/env helper exists
if [ -e '/usr/bin/env' ] && [ -x '/usr/bin/env' ]; then
    USR_BIN_ENV_EXISTS='true'
fi

# Check if "python3" exists in path
if [ "$PYTHON_INTERPRETER" = '' ]; then
    if command -v python3 > /dev/null 2> /dev/null; then
        PYTHON_INTERPRETER='python3'
    fi
fi

# Check if "python" exists in path
if [ "$PYTHON_INTERPRETER" = '' ]; then
    if command -v python > /dev/null 2> /dev/null; then
        PYTHON_INTERPRETER='python'
    fi
fi

# Fail if we did not find an interpreter in PATH
if [ "$PYTHON_INTERPRETER" = '' ]; then
    echo 'Could not find a valid python3 interpreter!'
    exit 1
fi

# Get absolute path of interpreter we detected
PYTHON_INTERPRETER_PATH="$(which "$PYTHON_INTERPRETER")"

# If /usr/bin/env does not exist we need to specify the full
# path, otherwise just the basename.
if [ "$USR_BIN_ENV_EXISTS" = 'true' ]; then
    echo "/usr/bin/env $PYTHON_INTERPRETER"
    exit 0
else
    echo "$PYTHON_INTERPRETER_PATH"
    exit 0
fi
