# Load environment variables from the .env file
export $(grep -v '^#' .env | xargs)


# Check if the image already exists
if ! docker images $IMAGE_NAME | awk '{ print $1 }' | grep -q $IMAGE_NAME; then
    echo "Image does not exist. Building..."
    docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .
else
    echo "Image already exists. Skipping build..."
fi

# Run the scraper container and redirect output to a log file
docker run --rm --name $IMAGE_NAME \
    -v $(realpath ${SECRETS_PATH}${SECRET_FILE_NAME}):/secrets/$SECRET_FILE_NAME:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/$SECRET_FILE_NAME" \
    $IMAGE_NAME

CONTAINER_EXIT_CODE=$?