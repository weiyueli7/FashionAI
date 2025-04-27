from unittest.mock import Mock
import os
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from io import BytesIO, StringIO
from PIL import Image
import json
from main import (
    get_pinecone_api_key,
    initialize_pinecone,
    load_file_from_bucket,
    parse_metadata,
    get_image_data,
    process_image_metadata,
    process_and_upload_topic_parallel
)

# Mock environment variables
os.environ["PROJECT_ID"] = "fashion-ai"
os.environ["SECRET_NAME"] = "projects/1087474666309/secrets/pincone/versions/latest"
os.environ["BASE_BUCKET"] = "fashion_ai_data"

# Constants for tests
SECRET_NAME = os.environ["SECRET_NAME"]
BASE_BUCKET = os.environ["BASE_BUCKET"]
INDEX_NAME = "test-index"
VECTOR_DIM = 512
MOCK_API_KEY = "mock_pinecone_key"

# Fixtures for reusable test setup


@pytest.fixture
def mock_storage_client():
    with patch("main.storage.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_secret_manager():
    with patch("main.secretmanager.SecretManagerServiceClient") as mock_secret_manager:
        yield mock_secret_manager


@pytest.fixture
def mock_pinecone():
    with patch("main.Pinecone") as mock_pinecone:
        yield mock_pinecone

# Test cases


def test_get_pinecone_api_key(mock_secret_manager):
    """Test retrieving Pinecone API key from Google Secret Manager."""
    mock_secret_manager.return_value.access_secret_version.return_value.payload.data.decode.return_value = MOCK_API_KEY
    api_key = get_pinecone_api_key(SECRET_NAME)
    assert api_key == MOCK_API_KEY


def test_initialize_pinecone(mock_pinecone):
    """Test Pinecone index initialization."""
    mock_index = MagicMock()
    mock_pinecone.return_value.list_indexes.return_value = []
    mock_pinecone.return_value.create_index.return_value = mock_index
    mock_pinecone.return_value.Index.return_value = mock_index

    index = initialize_pinecone(INDEX_NAME, VECTOR_DIM, MOCK_API_KEY)
    mock_pinecone.return_value.create_index.assert_called_once()
    assert index == mock_index


def test_load_file_from_bucket(mock_storage_client):
    """Test loading a file from GCP bucket."""
    mock_blob = MagicMock()
    mock_blob.name = "test/file.json"  # Match the prefix 'test' and file type 'json'
    mock_blob.download_as_text.return_value = '{"key": "value"}'
    mock_bucket = MagicMock()
    mock_bucket.list_blobs.return_value = [mock_blob]
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    result = load_file_from_bucket(BASE_BUCKET, "test", "json")
    assert result == {"key": "value"}


def test_parse_metadata():
    """Test parsing metadata CSV."""
    csv_content = "source/id,brand,medias/0/url\n1,Brand A,https://example.com/image.jpg"
    result = parse_metadata(csv_content)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["brand"] == "Brand A"


def test_get_image_data(mock_storage_client):
    """Test downloading image data from GCP bucket."""
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True  # Simulate the image exists in the bucket
    mock_blob.download_as_bytes.return_value = BytesIO(
        b"fake_image_data").getvalue()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    with patch("main.Image.open") as mock_open:
        mock_open.return_value = Image.new("RGB", (100, 100))
        result = get_image_data(BASE_BUCKET, "path/to/image.jpg")
        assert result.mode == "RGB"


def test_process_image_metadata(mock_pinecone):
    """Test processing and uploading image metadata to Pinecone."""
    caption_entry = {"image": "1.jpg", "caption": "A great image"}
    metadata_df = pd.DataFrame([
        {"source/id": 1, "brand": "Brand A",
            "medias/0/url": "https://example.com/image.jpg"}
    ])
    mock_index = MagicMock()
    mock_pinecone.return_value.Index.return_value = mock_index

    with patch("main.get_image_data") as mock_get_image, \
            patch("main.get_clip_vector") as mock_get_vector:
        mock_get_image.return_value = Image.new("RGB", (100, 100))
        mock_get_vector.return_value = Mock(
            tolist=Mock(return_value=[0.1] * VECTOR_DIM))

        result = process_image_metadata(
            caption_entry, metadata_df, "test-topic", "test-data", BASE_BUCKET, mock_index
        )
        assert result == "1.jpg"
        mock_index.upsert.assert_called_once()


def test_process_and_upload_topic_parallel(mock_storage_client, mock_pinecone):
    """Test processing and uploading data for a topic in parallel."""
    caption_data = [{"image": "1.jpg", "caption": "A test caption"}]
    metadata_text = "source/id,brand,medias/0/url\n1,Brand A,https://example.com/image.jpg"
    metadata_df = pd.read_csv(StringIO(metadata_text))

    mock_bucket = MagicMock()
    mock_blob_caption = MagicMock()
    mock_blob_caption.download_as_text.return_value = json.dumps(caption_data)
    mock_blob_metadata = MagicMock()
    mock_blob_metadata.download_as_text.return_value = metadata_text

    mock_bucket.list_blobs.return_value = [
        mock_blob_caption, mock_blob_metadata]
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    mock_index = MagicMock()
    mock_pinecone.return_value.Index.return_value = mock_index

    with patch("main.get_image_data") as mock_get_image, \
            patch("main.get_clip_vector") as mock_get_vector:
        mock_get_image.return_value = Image.new("RGB", (100, 100))
        mock_get_vector.return_value = [0.1] * VECTOR_DIM

        process_and_upload_topic_parallel(
            "test-topic", BASE_BUCKET, mock_index, "test-data", max_workers=1
        )
        mock_index.upsert.assert_called_once()


test_get_image_data(mock_storage_client)
