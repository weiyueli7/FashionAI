import os
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from scraper import download_images  # Replace with your actual module name
import shutil

# Set up test environment variables
os.environ['SCRAPED_METADATA'] = './test_data/meta'
os.environ['SCRAPED_RAW_IMAGES'] = './test_data/images'
os.environ['MEN_FILE_NAME'] = 'men_test_metadata.csv'
os.environ['COLUMN_ID_NAME'] = 'id'
os.environ['URL_IMAGE'] = 'image_url'


@pytest.fixture(scope="module")
def setup_environment():
    """Sets up a test environment with dummy metadata and directories."""
    os.makedirs('./test_data/meta', exist_ok=True)
    os.makedirs('./test_data/images', exist_ok=True)

    # Dummy metadata for testing
    test_metadata = [
        {'id': 1, 'image_url': 'https://invalid-url.com'}
    ]
    metadata_path = Path('./test_data/meta') / 'invalid_urls.csv'
    pd.DataFrame(test_metadata).to_csv(metadata_path, index=False)

    yield

    # Cleanup after tests
    shutil.rmtree('./test_data', ignore_errors=True)


@pytest.mark.asyncio
async def test_download_images_with_invalid_urls(setup_environment):
    """Tests handling invalid image URLs."""
    metadata_path = Path('./test_data/meta') / 'invalid_urls.csv'
    urls_df = pd.read_csv(metadata_path)
    output_folder = Path('./test_data/images') / 'invalid_images'

    # Mock Actor.create_proxy_configuration and aiohttp.ClientSession.get
    async_mock_get = AsyncMock()
    async_mock_get.__aenter__.return_value.status = 404

    with patch('scraper.Actor.create_proxy_configuration', AsyncMock()) as mock_proxy_config:
        mock_proxy_config.return_value.new_url.return_value = 'http://mock-proxy-url'

        with patch('scraper.aiohttp.ClientSession.get', return_value=async_mock_get):
            bad_urls_df = await download_images(urls_df, output_folder)
            assert isinstance(
                bad_urls_df, pd.DataFrame), "Bad URLs output is not a DataFrame"
            assert len(
                bad_urls_df) == 1, "Expected one bad URL but got a different count"
