#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define constants
export IMAGE_NAME="pinecone-service"
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

# Load the APP_PORT_PINECONE from the .env file
APP_PORT_PINECONE=$(grep APP_PORT_PINECONE "$ENV_FILE_PATH" | cut -d '=' -f2)

# Ensure APP_PORT_PINECONE is set
if [ -z "$APP_PORT_PINECONE" ]; then
    echo "Error: APP_PORT_PINECONE not set in $ENV_FILE_PATH"
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
    -p "$APP_PORT_PINECONE":"$APP_PORT_PINECONE" \
    "$IMAGE_NAME" $CMD
