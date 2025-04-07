
[![CI](https://github.com/AnsgarKlein/docker-rate-limit-check/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AnsgarKlein/docker-rate-limit-check/actions/workflows/ci.yml)

Check current rate limit for pulling images on [Docker Hub](https://hub.docker.com/).


## Execution modes

Tool can work as a command line tool and query the current Docker Hub rate
limit one time or run as an HTTP server and expose the current rate limit on
an easily accessible endpoint in Prometheus, JSON or YAML format for your
monitoring system. (It can act as a **Prometheus exporter**)

It can be used to query the rate limit for anonymous pulls or, when given
credentials check the rate limit for an authenticated user.

### Command-line mode

To query the current Docker Hub rate limit a single time, execute the tool in
command line mode:

```
python -m docker_rate_limit_check query
```

See `--help` for how to pass credentials or specify output format.

When using the tool in command-line mode it might be helpful to pack the
entire tool in a single file. See _Zipapp_ below.

### HTTP server mode

Execute HTTP server that exposes rate limit for Docker Hub on port 8080 in JSON
format:

```
python -m docker_rate_limit_check http --format json --port 8080
```

See `--help` for more options like passing credentials for Docker Hub.

The format given as command line argument specifies the default format for the
`/` endpoint:

```
curl 'http://127.0.0.1:8080'
{
    "rate_limit_max": 100,
    "rate_limit_remaining": 80,
    "identifier": "www.xxx.yyy.zzz",
    "rate_limit_used": 20
}
```

A different format can however still be requested:

```
curl 'http://127.0.0.1:8080?format=yaml'
---
identifier: www.xxx.yyy.zzz
rate_limit_max: 100
rate_limit_remaining: 80
rate_limit_used: 20
```

The `/metrics` endpoint will always default to serving metrics in Prometheus
format. (but different formats can still be explicitly requested)

The rate limit received from Docker Hub can be cached for a configurable
amount of time. Use `--cache-ttl` option to configure how long to cache
rate limit for. Subsequent request to the tool will only receive the cached
rate limit without requesting a current rate limit for Docker Hub.  
Set to `0` to disable caching.

## Docker

Container listens on port 8080 by default. Expose port to a port of your liking,
for example make it listen on port 9090 on your host:

```
docker run -p 9090:8080 -d ansgarklein/docker-rate-limit-check
```

Pass Docker Hub credentials using environment variables:

```
docker run -p 9090:8080 -d -e DOCKER_RATE_LIMIT_USER=login-user -e DOCKER_RATE_LIMIT_PASS=my-password ansgarklein/docker-rate-limit-check
```

**Environment variables**:

- `DOCKER_RATE_LIMIT_USER`:
  User name to use for authenticating to Docker Hub.
- `DOCKER_RATE_LIMIT_PASS`:
  User password (or
  [personal access token](https://docs.docker.com/security/for-developers/access-tokens/))
  to use for authenticating to Docker Hub.
- `DOCKER_RATE_LIMIT_CACHE_TTL`:
  Time in seconds for how long to cache retrieved rate limit before querying
  Docker Hub again.
- `DOCKER_RATE_LIMIT_DEFAULT_FORMAT`:
  Default output format for `/` (`/metrics` endpoint always defaults to
  Prometheus metrics)


## Development

Most development tasks have a shortcut using a Makefile.  
To get an overview simply cd to the root of this project and run `make`.

### Dependencies

Dependencies for this project are managed using [pip-tools](https://pip-tools.readthedocs.io).

Create and activate Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install pip and pip-tools:

```
python3 -m pip install -U pip
python3 -m pip install -U pip-tools
```

Install runtime and development dependencies:

```
pip-sync requirements.txt requirements-dev.txt
```

This will uninstall everything not listed in the requirements file from the
current virtual environment.

Update package versions in `requirements.txt` and `requirements-dev.txt` files
using constraints from `pyproject.toml`:

```
pip-compile --upgrade --allow-unsafe -o 'requirements.txt'
pip-compile --upgrade --allow-unsafe --extra dev -o 'requirements-dev.txt'
```

or run:

```
make update-requirements
```

### Tests

Run tests:

```
scripts/test.sh
```

or run:

```
make test
```

### Linting

Run linters:

```
scripts/lint.sh
```

or run:

```
make lint
```

### Single file (zipapp)

Especially, when using the tool in command-line mode it might be helpful to
pack the entire tool in a single file.  
This can be achieved using the built-in Python
[zipapp library](https://docs.python.org/3/library/zipapp.html).

The resulting file is a zip archive that can be executed directly using any
modern Python interpreter.

```
make zipfile
```

To make it possible to execute the file directly a Unix shebang will be added
by default. The resulting file thus cannot be easily read by a zip archive
tool.  
By default, the best shebang value is automatically detected from the
environment, but the shebang value can also be set explicitly:

```
export PYTHON_SHEBANG=/usr/bin/python3
make zipfile
```

Or adding of the shebang value can be disabled entirely:

```
export ADD_PYTHON_SHEBANG=true
make zipfile
```

for more information run:

```
make
```
