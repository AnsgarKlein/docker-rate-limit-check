#!/usr/bin/env python3

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import sys

from typing import Any

from .docker_hub import get_rate_limit

class DockerRateLimitHTTPServer(HTTPServer):
    """
    Basic HTTP server answering GET request with the current Docker Hub
    rate limit.

    :param port: Port to listen on
    :param host: Host string to bind on (default=0.0.0.0)
    """

    def __init__(self, port: int, host: str='0.0.0.0') -> None:
        conn = (host, port)
        super().__init__(conn, DockerRateLimitRequestHandler)

class DockerRateLimitRequestHandler(BaseHTTPRequestHandler):
    """
    Request handler for basic HTTP server.
    Answers with the current Docker Hub rate limit to GET requests.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Set content of "Server" response header
        self.server_version = __name__
        self.sys_version = f'Python {sys.version_info.major}.{sys.version_info.minor}'

        super().__init__(*args, **kwargs)

    # pylint: disable=invalid-name
    def do_GET(self) -> None:
        """
        Handle GET request to HTTP server
        """

        # Get rate limit
        rate_limit = get_rate_limit()
        payload = rate_limit.to_json()

        # Send response
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(payload, 'utf-8'))
