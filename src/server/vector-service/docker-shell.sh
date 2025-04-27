#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define constants
export IMAGE_NAME="vector-service"
export BASE_DIR=$(pwd)
export ENV_FILE_PATH=$(realpath "../.env")  # Path to the .env file
export GOOGLE_CREDENTIALS_PATH=$(realpath "../../../../secrets")  # Adjust as needed

# Check if the credentials file exists
if [ ! -f "$GOOGLE_CREDENTIALS_PATH/secret.json" ]; then
    echo "Error: Credentials file not found at $GOOGLE_CREDENTIALS_PATH/secret.json"
    exit 1
fi

# Ensure the .env file exists
if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "Error: .env file not found at $ENV_FILE_PATH"
    exit 1
fi

# Load APP_PORT_VECTOR from the .env file
APP_PORT_VECTOR=$(grep APP_PORT_VECTOR "$ENV_FILE_PATH" | cut -d '=' -f2)

# Ensure APP_PORT_VECTOR is set
if [ -z "$APP_PORT_VECTOR" ]; then
    echo "Error: APP_PORT_VECTOR not set in $ENV_FILE_PATH"
    exit 1
fi

# Build the Docker image
docker build -t $IMAGE_NAME -f Dockerfile .

# Determine if /bin/bash is passed as an argument
if [ "$1" == "/bin/bash" ]; then
    CMD="/bin/bash"
else
    CMD=""
fi

# Run the Docker container
docker run --rm --name "${IMAGE_NAME}-container" -ti \
    --env-file "$ENV_FILE_PATH" \
    -v "$BASE_DIR":/app \
    -v "$GOOGLE_CREDENTIALS_PATH":/secrets \
    -p "$APP_PORT_VECTOR":"$APP_PORT_VECTOR" \
    "$IMAGE_NAME" $CMD
