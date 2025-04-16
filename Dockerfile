FROM python:3.12-slim

USER root
ARG DEBIAN_FRONTEND=noninteractive

# Update system
RUN apt-get update && \
    apt-get dist-upgrade --no-install-recommends --assume-yes && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
ENV PYTHONUNBUFFERED=TRUE
WORKDIR /app

# Install pip requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-compile --no-cache-dir -r requirements.txt

# Copy app
COPY docker_rate_limit_check /app/docker_rate_limit_check
COPY resources/docker-entrypoint.sh /docker-entrypoint.sh

# Run
RUN groupadd --gid 65534 nobody || true
RUN useradd --no-create-home --uid 65534 --gid nobody nobody || true
USER nobody

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["docker_rate_limit_check"]

EXPOSE 8080
