#!/bin/bash

set -e

export IMAGE_NAME=fashionclip-deployment-hf
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCP_PROJECT="fashion-ai-438801"
export GCS_MODELS_BUCKET_NAME="fashionai_training"
export HF_REPO_NAME="weiyueli7/fashionclip"



# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/secret.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_MODELS_BUCKET_NAME=$GCS_MODELS_BUCKET_NAME \
-e HUGGINGFACE_KEY=$HUGGINGFACE_KEY \
-e HF_REPO_NAME=$HF_REPO_NAME \
$IMAGE_NAME