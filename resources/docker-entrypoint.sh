#!/bin/bash


DOCKER_RATE_LIMIT_USER=${DOCKER_RATE_LIMIT_USER:-''}
DOCKER_RATE_LIMIT_PASS=${DOCKER_RATE_LIMIT_PASS:-''}
DOCKER_RATE_LIMIT_CACHE_TTL=${DOCKER_RATE_LIMIT_CACHE_TTL:-''}
DOCKER_RATE_LIMIT_DEFAULT_FORMAT=${DOCKER_RATE_LIMIT_DEFAULT_FORMAT:-''}


if [[ "$1" == "docker_rate_limit_check" ]]; then
    # Put together exec string
    CMD=('python' '-m' 'docker_rate_limit_check' 'http' '--port' '8080')

    # Add user/pass if provided
    if [[ -n "$DOCKER_RATE_LIMIT_USER" ]] && [[ -n "$DOCKER_RATE_LIMIT_PASS" ]]; then
        CMD+=('--user')
        CMD+=("$DOCKER_RATE_LIMIT_USER")
        CMD+=('--pass')
        CMD+=("$DOCKER_RATE_LIMIT_PASS")
    fi

    # Specify cache TTL if provided
    if [[ -n "$DOCKER_RATE_LIMIT_CACHE_TTL" ]]; then
        CMD+=('--cache-ttl')
        CMD+=("$DOCKER_RATE_LIMIT_CACHE_TTL")
    fi

    exec "${CMD[@]}"
fi

# Execute different command
exec "$@"
