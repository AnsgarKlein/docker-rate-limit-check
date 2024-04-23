#!/usr/bin/env python3

from functools import partial
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import sys
from urllib.parse import parse_qs
from urllib.parse import urlparse

from typing import Any
from typing import Optional

from .docker_hub_requestor import DockerHubRequestor
from .output_format import RateLimitOutputFormat

class DockerRateLimitHTTPServer(HTTPServer):
    """
    Basic HTTP server answering GET request with the current Docker Hub
    rate limit.

    :param port: Port to listen on
    :param default_format: Default output format if not specified using
        query parameter ?format=XYZ in GET request.
    :param docker_hub_requestor: Requestor for querying Docker Hub.
    :param host: Host string to bind on (default=0.0.0.0)
    """

    def __init__(
            self,
            port: int,
            default_format: RateLimitOutputFormat,
            docker_hub_requestor: DockerHubRequestor,
            host: str='0.0.0.0') -> None:

        # Prepare request handler
        request_handler = partial(
                DockerRateLimitRequestHandler,
                default_format,
                docker_hub_requestor)

        # Call parent init
        conn = (host, port)
        super().__init__(conn, request_handler)

class DockerRateLimitRequestHandler(BaseHTTPRequestHandler):
    """
    Request handler for basic HTTP server.
    Answers with the current Docker Hub rate limit to GET requests.

    :param default_format: Default output format if not specified using
        query parameter ?format=XYZ in GET request.
    :param docker_hub_requestor: Requestor for querying Docker Hub.
    :param *args: Arguments for parent class
    :param **kwargs: Arguments for parent class
    """

    def __init__(
            self,
            default_format: RateLimitOutputFormat,
            docker_hub_requestor: DockerHubRequestor,
            *args: Any,
            **kwargs: Any) -> None:

        # Set default output format if not specified in request
        self.default_format = default_format

        self.docker_hub_requestor = docker_hub_requestor

        # Set content of "Server" response header
        self.server_version = __name__
        self.sys_version = f'Python {sys.version_info.major}.{sys.version_info.minor}'

        super().__init__(*args, **kwargs)

    def send_http_error_message(self, code: int, message: str) -> None:
        """
        Send HTTP error message

        :param code: HTTP error code to send
        :param message: Plaintext message to include in body of response
        """
        # End message with newline character
        if len(message) > 0 and message[-1] != '\n':
            message += '\n'

        self.protocol_version = 'HTTP/1.1'
        self.send_response(code)
        self.send_header('Content-Length', str(len(message)))
        self.end_headers()
        self.wfile.write(bytes(message, 'utf-8'))

    def send_rate_limit_response(
            self,
            output_format: Optional[RateLimitOutputFormat]=None) -> None:
        """
        Send HTTP response with docker rate limit in specified format.

        :param output_format: Format in which to respond
        """

        # If not specified use default format
        if output_format is None:
            output_format = self.default_format

        # Get rate limit
        rate_limit = self.docker_hub_requestor.get_rate_limit()
        payload = rate_limit.to_output_format(output_format)

        # End payload with newline character
        if len(payload) > 0 and payload[-1] != '\n':
            payload += '\n'

        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Length', str(len(payload)))

        # Set Content-Type header accordingly
        if output_format is RateLimitOutputFormat.JSON:
            self.send_header('Content-Type', 'application/json')
        if output_format is RateLimitOutputFormat.YAML:
            self.send_header('Content-Type', 'application/yaml')

        self.end_headers()
        self.wfile.write(bytes(payload, 'utf-8'))

    # pylint: disable=invalid-name
    def do_GET(self) -> None:
        """
        Handle GET request to HTTP server
        """

        # Parse request
        urltuple = urlparse(self.path)
        path = urltuple.path
        arguments = parse_qs(urltuple.query)

        # Return HTTP-404 for every location but /
        if path != '/':
            self.protocol_version = 'HTTP/1.1'
            self.send_response(404)
            self.end_headers()
            return

        # Check for unexpected arguments
        supported_args = {'format'}
        for arg in arguments:
            if arg not in supported_args:
                message = f'Error: Unknown query string "{arg}"'
                self.send_http_error_message(400, message)
                return

        # Extract format from request
        format_enum = None
        if 'format' in arguments:
            if len(arguments['format']) > 1:
                message = 'Error: Expected exactly one value for parameter "format"'
                self.send_http_error_message(400, message)
                return

            format_str = arguments['format'][0].lower()
            try:
                format_enum = RateLimitOutputFormat(format_str)
            except ValueError:
                message = f'Error: Unsupported format \"{format_str}\"'
                self.send_http_error_message(400, message)
                return

        self.send_rate_limit_response(format_enum)
        return
