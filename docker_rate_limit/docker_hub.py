#!/usr/bin/env python3

# Copyright (c) 2023 Ansgar Klein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import dataclass
import re
import sys

from typing import Dict
from typing import Optional
from typing import Union

import requests
from requests.exceptions import RequestException


TOKEN_RECEIVE_ENDPOINT = 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull'
RATE_LIMIT_ENDPOINT = 'https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest'


@dataclass
class DockerRateLimit():
    """Contains information about Docker Hub rate limiting"""

    rate_limit_max: int
    rate_limit_remaining: int
    ip: Optional[str]=None

    @property
    def rate_limit_used(self) -> int:
        return self.rate_limit_max - self.rate_limit_remaining

    def asdict(self) -> Dict[str, Union[Optional[str], int]]:
        """Return attributes of this object as dictionary"""

        attrs = [
            'rate_limit_max',
            'rate_limit_remaining',
            'ip',
            'rate_limit_used'
        ]
        return {a: getattr(self, a) for a in attrs}

def request_token(user: Optional[str]=None, password: Optional[str]=None) -> str:
    """Request token to authorize to Docker Hub with"""

    if user is not None and password is not None:
        req = requests.get(TOKEN_RECEIVE_ENDPOINT, timeout=10, auth=(user, password))
    else:
        req = requests.get(TOKEN_RECEIVE_ENDPOINT, timeout=10)

    # Check for correct status code
    if req.status_code != 200:
        raise RequestException((
            'Error when requesting token. '
            f'Response code was {req.status_code} instead of 200.'))

    response_json = req.json()

    # Check for malformed json
    if 'token' not in response_json:
        raise KeyError((
            'Error when parsing response: '
            'Could not find "token" key in response.'))
    if not isinstance(response_json['token'], str):
        raise KeyError((
            'Error when parsing response: '
            '"token" key is not of type string.'))

    return str(response_json['token'])

def get_rate_limit(token: Optional[str]=None) -> DockerRateLimit:
    """Returns information about Docker Hub rate limiting"""

    if token is None:
        token = request_token()

    headers = {'Authorization': f'Bearer {token}'}
    req = requests.head(RATE_LIMIT_ENDPOINT, timeout=10, headers=headers)

    if req.status_code == 200:
        # Check that all required headers have been returned
        required_headers = [
            'ratelimit-limit',
            'ratelimit-remaining',
            'docker-ratelimit-source']
        for required_header in required_headers:
            try:
                _ = req.headers[required_header]
            except KeyError as err:
                print((
                    'Error: Response did not contain contain expected '
                    f'header "{required_header}"'),
                    file=sys.stderr)
                raise err

        # Extract response headers
        response_headers = {key: req.headers[key] for key in required_headers}

        # Extract relevant information from response headers
        rate_limit_max = int(
            re.sub(
                r'^(\d*);w=(.*)$', r'\1',
                response_headers['ratelimit-limit'])
            )
        rate_limit_remaining = int(
            re.sub(
                r'^(\d*);w=(.*)$', r'\1',
                response_headers['ratelimit-remaining'])
            )
        rate_limit_ip = response_headers['docker-ratelimit-source']

        return DockerRateLimit(
            rate_limit_max=rate_limit_max,
            rate_limit_remaining=rate_limit_remaining,
            ip=rate_limit_ip)

    if req.status_code == 429:
        return DockerRateLimit(
            rate_limit_max=0,
            rate_limit_remaining=0)

    raise RequestException((
        'Error when requesting rate limit. '
        f'Response code was {req.status_code} instead of 200 or 429.'))
