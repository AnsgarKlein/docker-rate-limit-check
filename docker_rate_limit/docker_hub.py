#!/usr/bin/env python3

from dataclasses import dataclass
import json
import re
import sys

from typing import Dict
from typing import Optional
from typing import Union

import requests
from requests.exceptions import RequestException
import yaml

from .output_format import RateLimitOutputFormat


TOKEN_RECEIVE_ENDPOINT = 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull'
RATE_LIMIT_ENDPOINT = 'https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest'


@dataclass
class DockerRateLimit():
    """Contains information about Docker Hub rate limiting"""

    rate_limit_max: int
    rate_limit_remaining: int
    ip: Optional[str]=None

    @property
    def rate_limit_used(self) -> int:  # pylint: disable=missing-function-docstring
        return self.rate_limit_max - self.rate_limit_remaining

    def asdict(self) -> Dict[str, Union[Optional[str], int]]:
        """
        Return attributes of this object as dictionary.

        :return: Dictionary representation of this object
        """

        attrs = [
            'rate_limit_max',
            'rate_limit_remaining',
            'ip',
            'rate_limit_used'
        ]
        return {a: getattr(self, a) for a in attrs}

    def to_output_format(self, output_format: RateLimitOutputFormat) -> str:
        """
        Return attributes of this object in the requested format

        :param output_format: Format of output
        :return: Attributes of this object formatted in requested format
        """

        if output_format == RateLimitOutputFormat.JSON:
            return self.to_json()
        if output_format == RateLimitOutputFormat.YAML:
            return self.to_yaml()

        return None  # type: ignore

    def to_json(self, indent: int=4) -> str:
        """
        Return attributes of this object as JSON string

        :param indent: Number of spaces for indentation
        :return: JSON formatted string representation of this object
        """

        dict_representation = self.asdict()
        return json.dumps(dict_representation, indent=indent)

    def to_yaml(self) -> str:
        """
        Return attributes of this object as YAML string

        :return: YAML formatted string representation of this object
        """

        dict_representation = self.asdict()
        yaml_repr = yaml.safe_dump(dict_representation, explicit_start=True)
        yaml_repr = yaml_repr.strip()
        return yaml_repr

def request_token(user: Optional[str]=None, password: Optional[str]=None) -> str:
    """
    Request token to authorize to Docker Hub with

    :param user: User to request token for.
        None for anonymous token.
    :param password: Password for user to request token for.
        None for anonymous token.
    :raises KeyError: If JSON returned by Docker Hub is malformed and
        does not contain expected keys.
    :raises RequestException: If Docker Hub does not respond with status code
        HTTP-200.
    :return: Token for given user or anonymous token to authorize to Docker
        Hub with
    """

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
    """
    Returns information about Docker Hub rate limiting

    :param token: Token to authenticate to Docker Hub with.
        Set to None to use an anonymous token.
    :raises KeyError: If JSON returned by Docker Hub is missing malformed and
        does not contain expected keys.
    :raises RequestException: If Docker Hub does not respond with status code
        HTTP-200 or HTTP-429.
    :return: Information about rate limit returned by Docker Hub
    """

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
