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
