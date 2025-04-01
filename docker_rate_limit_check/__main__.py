#!/usr/bin/env python3

from typing import Optional
from typing_extensions import Annotated

import rich
import typer

from .docker_hub_requestor import DockerHubRequestor
from .http_server import DockerRateLimitHTTPServer
from .output_format import RateLimitOutputFormat


app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False)

typer_user_option = typer.Option(
    '--user', '-u',
    metavar='USER',
    help='''
    User name to use for authentication to Docker Hub''',
    show_default=False)

typer_pass_option = typer.Option(
    '--pass',
    metavar='PASSWORD',
    help='''
    User password to use for authentication to Docker Hub''',
    show_default=False)


@app.command(help='''
Query Docker Hub for rate limit''')
# pylint: disable=too-many-arguments
def query(
        user: Annotated[Optional[str], typer_user_option]=None,
        password: Annotated[Optional[str], typer_pass_option]=None,
        output_format: Annotated[RateLimitOutputFormat, typer.Option(
            '--format', '-f',
            help='''
            Output format of rate limit information''')]=RateLimitOutputFormat.JSON
    ) -> None:
    """
    Query Docker Hub for rate limit

    :param user: User name to use for authentication to Docker Hub
    :param password: User password to use for authentication to Docker Hub
    :param output_format: Output format of rate limit information
    """

    # Get rate limit
    docker_hub_requestor = DockerHubRequestor(
        user=user,
        password=password)
    rate_limit = docker_hub_requestor.get_rate_limit()

    # Output in correct format
    output = rate_limit.to_output_format(output_format)

    # Output with or without syntax highlight (depending on format)
    if output_format in [RateLimitOutputFormat.JSON, RateLimitOutputFormat.YAML]:
        rich.print(output)
    else:
        print(output)

@app.command(help='''
Run HTTP server that responds with rate limit''')
# pylint: disable=too-many-arguments
def http(
        port: Annotated[int, typer.Option(
            '--port', '-p',
            metavar='PORT',
            help='''
            Port to listen on''',
            show_default=False)],
        host: Annotated[str, typer.Option(
            '--host',
            metavar='HOST',
            help='''
            Host to bind on''')]='0.0.0.0',
        user: Annotated[Optional[str], typer_user_option]=None,
        password: Annotated[Optional[str], typer_pass_option]=None,
        output_format: Annotated[RateLimitOutputFormat, typer.Option(
            '--format', '-f',
            help='''
            Default output format if format is
            not specified in GET request.''')]=RateLimitOutputFormat.JSON,
        cache_ttl: Annotated[int, typer.Option(
            '--cache-ttl', '-t',
            metavar='TTL',
            help='''
            Cache TTL in seconds. Response by Docker Hub will be cached for
            this many seconds. Subsequent requests will only be served the
            cached result until cache age exceeds given TTL.''')]=30
    ) -> None:
    """
    Run http server to abstract calls to Docker Hub

    :param port: Port to listen on
    :param host: Host to bind on
    :param user: User name to use for authentication to Docker Hub
    :param password: User password to use for authentication to Docker Hub
    :param output_format: Default output format if not specified in request
    :param cache_ttl: For how many seconds to cache response by Docker Hub
    """

    docker_hub_requestor = DockerHubRequestor(
        user=user,
        password=password,
        cache_ttl=cache_ttl)

    # Start server
    server = DockerRateLimitHTTPServer(
            host=host,
            port=port,
            default_format=output_format,
            docker_hub_requestor=docker_hub_requestor)
    server.serve_forever()

def main() -> None:
    """Main application entry point"""
    app()

if __name__ == '__main__':
    main()
