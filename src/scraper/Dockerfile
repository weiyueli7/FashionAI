FROM python:3.11-slim-bookworm

ARG DEBIAN_PACKAGES="build-essential git screen vim"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Tell pipenv where the shell is. This allows us to use "pipenv shell" as a
# container entry point.
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs.
ENV PYTHONUNBUFFERED=1

# Ensure we have an up to date baseline, install dependencies and
# create a user so we don't run the app as root
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    chown app:app /persistent && \
    chown app:app /app


# Create the /src directory inside the container
RUN mkdir -p /src

# Switch to the new user

WORKDIR /app

ADD --chown=app:app Pipfile Pipfile.lock /app/

RUN pipenv sync

# Set the default working directory for the Python app (mounted folder)
# We'll mount our project folder dynamically to this path during runtime
#WORKDIR /src

CMD ["pipenv", "run", "python", "/src/scraper.py"]
# Install python packages
#ADD --chown=app:app Pipfile Pipfile.lock /app/

#RUN pipenv sync

# Add the rest of the source code. This is done last so we don't invalidate all
# layers when we change a line of code.
#ADD --chown=app:app . /app

# Entry point
#ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]