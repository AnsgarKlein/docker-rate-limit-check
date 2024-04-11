#!/usr/bin/env python3

from enum import Enum

from typing_extensions import Annotated

import typer

from .docker_hub import get_rate_limit


app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]})

class OutputFormat(str, Enum):
    """Format for outputting Docker Hub rate limit"""

    JSON = 'json'
    YAML = 'yaml'

    def __str__(self) -> str:
        return self.value


@app.command(help='''
Query Docker Hub for rate limit''')
def query(
        output_format: Annotated[OutputFormat, typer.Option(
            '--format', '-f',
            help='''
            Output format of rate limit information''')]=OutputFormat.JSON
    ) -> None:
    """
    Query Docker Hub for rate limit

    :param output_format: Output format of rate limit information
    """

    # Get rate limit
    rate_limit = get_rate_limit()

    # Output in correct format
    if output_format is OutputFormat.JSON:
        output = rate_limit.to_json()
    elif output_format is OutputFormat.YAML:
        output = rate_limit.to_yaml()
    print(output)

@app.command(help='''
    not yet implemented''')
def http() -> None:
    """
    Run http server to abstract calls to Docker Hub
    (not yet implemented)

    :raises Exception: Not yet implemented
    """

    print('Not yet implemented')
    raise typer.Exit(code=1)

def main() -> None:
    """Main application entry point"""
    app()

if __name__ == '__main__':
    main()
