#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define environment variables
export IMAGE_NAME="frontend-app"
export BASE_DIR=$(pwd)
export ENV_FILE_PATH=$(realpath "../.env") 

# Build the Docker image
docker build -t $IMAGE_NAME -f Dockerfile .

# Determine if /bin/bash is passed as an argument
if [ "$1" == "/bin/bash" ]; then
    CMD="/bin/bash"
else
    CMD=""
fi

APP_PORT_FRONTEND=$(grep APP_PORT_FRONTEND "$ENV_FILE_PATH" | cut -d '=' -f2)

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
    -v "$BASE_DIR":/app \
    -p "$APP_PORT_FRONTEND":"$APP_PORT_FRONTEND" \
    $IMAGE_NAME $CMD
