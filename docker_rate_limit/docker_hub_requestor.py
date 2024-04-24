#!/usr/bin/env python3

import datetime
import re
import sys

from typing import Optional

import requests
from requests.exceptions import RequestException

from .docker_rate_limit import DockerRateLimit


TOKEN_RECEIVE_ENDPOINT = 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull'
RATE_LIMIT_ENDPOINT = 'https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest'


class DockerHubRequestor():
    """
    Requestor that queries Docker Hub for the current rate limit.

    :param user: User to request token for.
        None for anonymous token.
    :param password: Password for user to request token for.
        None for anonymous token.
    :param cache_ttl: Number of seconds information should be cached
        before querying Docker Hub for fresh information.
    """

    def __init__(self,
            user: Optional[str]=None,
            password: Optional[str]=None,
            cache_ttl: int=0):

        self.user = user
        self.password = password
        self.rate_limit = DockerRateLimit(
            rate_limit_max=0,
            rate_limit_remaining=0)
        self.cache_ttl = cache_ttl
        self.cache_last_refresh = datetime.datetime.fromisoformat('1970-01-01T00:00:00')

    def get_rate_limit(self) -> DockerRateLimit:
        """
        Returns information about Docker Hub rate limiting.
        If cached information is fresh return information from cache.
        If cache is stale request current rate limit from Docker Hub,
        store information in cache and return it.

        :return: Information about rate limit
        """

        # Check age of cache
        now = datetime.datetime.now()
        cache_age = (now - self.cache_last_refresh) / datetime.timedelta(seconds=1)

        # If cache is stale then refresh information
        if cache_age > self.cache_ttl:
            self.rate_limit = self.get_rate_limit_from_docker_hub()
            self.cache_last_refresh = datetime.datetime.now()

        # Return information from cache
        return self.rate_limit

    def request_token(self) -> str:
        """
        Request token to authorize to Docker Hub with

        :raises KeyError: If JSON returned by Docker Hub is malformed and
            does not contain expected keys.
        :raises RequestException: If Docker Hub does not respond with status code
            HTTP-200.
        :return: Token for given user or anonymous token to authorize to Docker
            Hub with
        """

        if self.user is not None and self.password is not None:
            req = requests.get(TOKEN_RECEIVE_ENDPOINT, timeout=10, auth=(self.user, self.password))
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

    def get_rate_limit_from_docker_hub(self) -> DockerRateLimit:
        """
        Returns information about Docker Hub rate limiting by actively
        querying Docker Hub for that information.

        :raises KeyError: If JSON returned by Docker Hub is missing malformed and
            does not contain expected keys.
        :raises RequestException: If Docker Hub does not respond with status code
            HTTP-200 or HTTP-429.
        :return: Information about rate limit returned by Docker Hub
        """

        token = self.request_token()

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
