#!/usr/bin/env python3

from enum import Enum


class RateLimitOutputFormat(str, Enum):
    """Format for outputting Docker Hub rate limit"""

    JSON = 'json'
    YAML = 'yaml'

    def __str__(self) -> str:
        return self.value
