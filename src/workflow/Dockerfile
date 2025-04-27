# Use Python 3.8 slim image
FROM python:3.8-slim-bookworm

# Argument for Debian packages to be installed
ARG DEBIAN_PACKAGES="build-essential git screen vim"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set UTF-8 locale for Python
ENV LANG=C.UTF-8

# Tell Python to disable buffering for logs
ENV PYTHONUNBUFFERED=1

# Ensure up-to-date baseline, install dependencies, and create user
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    chown app:app /persistent && \
    chown app:app /app

# Create the /src directory inside the container
RUN mkdir -p /src


# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install curl
RUN apt-get update && apt-get install -y curl

# Install pip (if not already installed)
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

# Switch to the new user

# Set PATH to include the local bin directory
ENV PATH=$PATH:/home/app/.local/bin

# Set the working directory to /app
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# # Copy the Python scripts (finetune.py and qa.py) into the container
# COPY --chown=app:app finetune.py qa.py /app/

# # copy everything from the current directory into the container
# COPY --chown=app:app . /app/

# Install any required dependencies
ADD --chown=app:app Pipfile Pipfile.lock /app/

# Install any required dependencies
RUN pipenv sync

# Set the default working directory for Python execution
WORKDIR /app

ADD . /src/

# # Use ENTRYPOINT to open bash and automatically start pipenv shell
# ENTRYPOINT ["/bin/bash", "-c", "pipenv shell && exec \"$@\"", "--"]

CMD ["pipenv", "run", "python", "/src/workflow.py"]