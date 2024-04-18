#!/usr/bin/env python3

from typing_extensions import Annotated

import typer

from .docker_hub import get_rate_limit
from .http_server import DockerRateLimitHTTPServer
from .output_format import RateLimitOutputFormat


app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]})

@app.command(help='''
Query Docker Hub for rate limit''')
def query(
        output_format: Annotated[RateLimitOutputFormat, typer.Option(
            '--format', '-f',
            help='''
            Output format of rate limit information''')]=RateLimitOutputFormat.JSON
    ) -> None:
    """
    Query Docker Hub for rate limit

    :param output_format: Output format of rate limit information
    """

    # Get rate limit
    rate_limit = get_rate_limit()

    # Output in correct format
    output = rate_limit.to_output_format(output_format)
    print(output)

@app.command(help='''
Run HTTP server that responds with rate limit''')
def http(
        port: Annotated[int, typer.Option(
            '--port', '-p',
            metavar='PORT',
            help='''
            Port to listen on''')],
        host: Annotated[str, typer.Option(
            '--host',
            metavar='HOST',
            help='''
            Host to bind on''')]='0.0.0.0',
        output_format: Annotated[RateLimitOutputFormat, typer.Option(
            '--format', '-f',
            help='''
            Default output format if format is
            not specified in GET request.''')]=RateLimitOutputFormat.JSON
    ) -> None:
    """
    Run http server to abstract calls to Docker Hub

    :param port: Port to listen on
    :param host: Host to bind on
    :param output_format: Default output format if not specified in request
    """

    # Start server
    server = DockerRateLimitHTTPServer(
            host=host,
            port=port,
            default_format=output_format)
    server.serve_forever()

def main() -> None:
    """Main application entry point"""
    app()

if __name__ == '__main__':
    main()
