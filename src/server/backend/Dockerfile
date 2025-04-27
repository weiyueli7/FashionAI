# Use Python base image
FROM python:3.9-slim

# Define the packages to be installed
ARG DEBIAN_PACKAGES="build-essential git screen vim"
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# Install necessary tools with signature verification disabled
RUN set -ex; \
    # Configure APT to disable GPG signature verification
    echo "Acquire::AllowInsecureRepositories \"true\";" > /etc/apt/apt.conf.d/99insecure-repos && \
    echo "Acquire::AllowDowngradeToInsecureRepositories \"true\";" >> /etc/apt/apt.conf.d/99insecure-repos && \
    echo "Acquire::Gpgv::Options::=--ignore-time-conflict;" >> /etc/apt/apt.conf.d/99insecure-repos && \
    echo "Acquire::Check-Valid-Until \"false\";" >> /etc/apt/apt.conf.d/99insecure-repos && \
    echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    # Update and install packages without signature verification
    apt-get update && \
    apt-get upgrade -y --allow-unauthenticated && \
    apt-get install -y --no-install-recommends gnupg curl ca-certificates $DEBIAN_PACKAGES --allow-unauthenticated && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Install pipenv for Python dependency management
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    # Create a non-root user and setup application directory
    useradd -ms /bin/bash app -d /home/app -u 1000 && \
    mkdir -p /app && \
    chown app:app /app

# Set the working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock for dependency installation
COPY Pipfile Pipfile.lock ./

# Install dependencies using Pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy application code into the container
COPY . .

# Expose the default application port
EXPOSE 8000

# Run the application with Uvicorn, dynamically using APP_PORT_BACKEND
CMD ["sh", "-c", "pipenv run uvicorn main:app --host 0.0.0.0 --port ${APP_PORT_BACKEND:-8000}"]