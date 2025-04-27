#!/bin/bash

export IMAGE_NAME=fashion_ai_training-cli
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCS_BUCKET_URI="gs://fashionai_training"
export GCS_DATA_BUCKET_URI="gs://fashion_ai_data"
export GCP_PROJECT="fashion-ai-438801"

# Check if the image already exists
if ! docker images $IMAGE_NAME | awk '{ print $1 }' | grep -q $IMAGE_NAME; then
    echo "Image does not exist. Building..."
    docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .
else
    echo "Image already exists. Skipping build..."
fi

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/secret.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_URI=$GCS_BUCKET_URI \
-e WANDB_KEY=$WANDB_KEY \
$IMAGE_NAME

CONTAINER_EXIT_CODE=$?

# Check if the container ran successfully
if [ $CONTAINER_EXIT_CODE -ne 0 ]; then
    echo "The finetune container encountered an issue. Checking logs..."
    
    exit 1
fi
