# Use Python base image
FROM python:3.9-slim

# Define the packages to be installed
ARG DEBIAN_PACKAGES="build-essential git screen vim"
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PYENV_SHELL=/bin/bash
ENV PYTHONUNBUFFERED=1

# Disable GPG signature verification and install dependencies
RUN set -ex; \
    # Disable GPG verification
    echo "Acquire::AllowInsecureRepositories \"true\";" > /etc/apt/apt.conf.d/99insecure-repos && \
    echo "Acquire::AllowDowngradeToInsecureRepositories \"true\";" >> /etc/apt/apt.conf.d/99insecure-repos && \
    echo "Acquire::Gpgv::Options::=--ignore-time-conflict;" >> /etc/apt/apt.conf.d/99insecure-repos && \
    echo "Acquire::Check-Valid-Until \"false\";" >> /etc/apt/apt.conf.d/99insecure-repos && \
    # Update package sources and install necessary dependencies
    apt-get update && \
    apt-get upgrade -y --allow-unauthenticated && \
    apt-get install -y --no-install-recommends gnupg curl ca-certificates $DEBIAN_PACKAGES --allow-unauthenticated && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Install pipenv for managing Python dependencies
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    # Create a non-root user and set up application directory
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app

# Set working directory
WORKDIR /app

# Copy Pipfile first to leverage Docker caching
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy application code
COPY . .

# Expose the application port (default is 8001)
EXPOSE 8001

# Run the application using Uvicorn, dynamically setting host and port
CMD ["sh", "-c", "pipenv run uvicorn main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT_VECTOR:-8001}"]
