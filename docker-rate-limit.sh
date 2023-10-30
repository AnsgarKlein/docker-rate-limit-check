#!/bin/bash

# Receive anonymous token
TOKEN=$(curl -sSL "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq -r .token)

# Get current rate limit using token
curl -XHEAD --head -H "Authorization: Bearer $TOKEN" -sSL --output /dev/null --dump-header - https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest

exit 0
