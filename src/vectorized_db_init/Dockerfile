# Use Python base image
FROM python:3.9-slim

ARG DEBIAN_PACKAGES="build-essential git"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Disable Python buffering
ENV PYTHONUNBUFFERED=1

# Ensure we have an up-to-date baseline, install dependencies, and create a user
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    chown app:app /persistent && \
    chown app:app /app

# Set working directory
WORKDIR /app

# Copy only Pipfile first to leverage Docker caching
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . .

# Run the application or open a shell
CMD ["pipenv", "run", "python", "main.py"]
