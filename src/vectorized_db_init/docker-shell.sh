#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define environment variables
export IMAGE_NAME="docker-shell"
export BASE_DIR=$(pwd)

# Dynamically convert the relative path to an absolute path for the secrets directory
export GOOGLE_CREDENTIALS_PATH=$(realpath "../../../secrets")
export ENV_FILE_PATH=$(realpath "../server/.env") # Path to the .env file in the env folder

# Check if the credentials file exists in the directory
if [ ! -f "$GOOGLE_CREDENTIALS_PATH/secret.json" ]; then
    echo "Error: Credentials file not found at $GOOGLE_CREDENTIALS_PATH/secret.json"
    exit 1
fi

# Ensure the .env file exists
if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "Error: .env file not found at $ENV_FILE_PATH"
    exit 1
fi

# Determine if /bin/bash is passed as an argument
if [ "$1" == "/bin/bash" ]; then
    CMD="/bin/bash"
else
    CMD=""
fi

# Build the Docker image
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the Docker container
docker run --rm --name "${IMAGE_NAME}-shell" -ti \
    --env-file "$ENV_FILE_PATH" \
    -v "$BASE_DIR":/app \
    -v "$GOOGLE_CREDENTIALS_PATH":/secrets \
    "$IMAGE_NAME" $CMD
