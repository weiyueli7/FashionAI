import pytest
from io import BytesIO
from pathlib import Path
from caption_generating import download_image_from_local

def test_download_image_from_local_1(tmp_path):
    # Create a temporary image file
    temp_image = tmp_path / "test_image.jpg"
    temp_image.write_bytes(b"fake image data")
    
    # Test valid image file
    image_file, image_name = download_image_from_local(temp_image)
    assert isinstance(image_file, BytesIO)
    assert image_name == "test_image.jpg"

def test_download_image_from_local_2(tmp_path):
    # Test invalid file
    with pytest.raises(FileNotFoundError):
        download_image_from_local("non_existent.jpg")

from caption_generating import preprocess_text

def test_preprocess_text_1():
    assert preprocess_text("Text with \\n newlines \\u1234") == "Text with newlines"

def test_preprocess_text_2():
    assert preprocess_text("  Extra   spaces  ") == "Extra spaces"
    assert preprocess_text("") == ""

from unittest.mock import patch, MagicMock
from caption_generating import generate_captions_with_gemini

@patch("caption_generating.genai")  # Mock the Gemini API client
def test_generate_captions_with_gemini(mock_genai, tmp_path):
    # Mock secret value
    secret_value = "mock_secret_value"

    # Create a mock image
    temp_image = tmp_path / "test_image.jpg"
    temp_image.write_bytes(b"fake image data")

    # Mock Gemini API response
    mock_model = MagicMock()
    mock_usage_metadata = MagicMock(
        prompt_token_count=10,
        candidates_token_count=5,
        total_token_count=15,
    )
    mock_result = MagicMock(
        text="Caption text",
        usage_metadata=mock_usage_metadata
    )
    mock_model.generate_content.return_value = mock_result
    mock_genai.GenerativeModel.return_value = mock_model

    # Call the function with the mock secret_value
    caption, prompt_token, candidate_token, total_token = generate_captions_with_gemini(temp_image, secret_value)

    # Assertions
    assert caption == "Caption text"
    assert prompt_token == 10
    assert candidate_token == 5
    assert total_token == 15


@patch("caption_generating.genai")  # Mock the Gemini API client
def test_generate_captions_with_gemini_2(mock_genai, tmp_path):
    # Mock secret value
    secret_value = "mock_secret_value"

    # Create a mock image
    temp_image = tmp_path / "test_image2.jpg"
    temp_image.write_bytes(b"fake image data")

    # Mock Gemini API response
    mock_model = MagicMock()
    mock_usage_metadata = MagicMock(
        prompt_token_count=20,
        candidates_token_count=10,
        total_token_count=30,
    )
    mock_result = MagicMock(
        text="Another caption text",
        usage_metadata=mock_usage_metadata
    )
    mock_model.generate_content.return_value = mock_result
    mock_genai.GenerativeModel.return_value = mock_model

    # Call the function with the mock secret_value
    caption, prompt_token, candidate_token, total_token = generate_captions_with_gemini(temp_image, secret_value)

    # Assertions
    assert caption == "Another caption text"
    assert prompt_token == 20
    assert candidate_token == 10
    assert total_token == 30



import pandas as pd
import json
from caption_generating import save_intermediate_results

def test_save_intermediate_results_1(tmp_path):
    csv_data = [{"image_name": "test.jpg", "token_count": 5}]
    json_data = [{"image": "test.jpg", "caption": "Sample caption"}]
    failed_images = [{"image_name": "failed.jpg", "error": "Error"}]

    save_intermediate_results(
        csv_data, json_data, failed_images, tmp_path, "csv_output", "json_output", "failed_output", 1
    )

    # Check CSV
    csv_file = tmp_path / "csv_output_batch_1.csv"
    assert csv_file.exists()
    assert pd.read_csv(csv_file).shape[0] == 1

    # Check JSON
    json_file = tmp_path / "json_output_batch_1.json"
    assert json_file.exists()
    with open(json_file) as f:
        data = json.load(f)
        assert len(data) == 1

    # Check failed CSV
    failed_file = tmp_path / "failed_output_batch_1.csv"
    assert failed_file.exists()
    assert pd.read_csv(failed_file).shape[0] == 1

import pandas as pd
import json
from caption_generating import save_intermediate_results

def test_save_intermediate_results_2(tmp_path):
    csv_data = [
        {"image_name": "image2.jpg", "token_count": 10},
        {"image_name": "image3.jpg", "token_count": 20},
    ]
    json_data = [
        {"image": "image2.jpg", "caption": "Caption for image2"},
        {"image": "image3.jpg", "caption": "Caption for image3"},
    ]
    failed_images = [
        {"image_name": "failed2.jpg", "error": "Some error"},
        {"image_name": "failed3.jpg", "error": "Another error"},
    ]

    save_intermediate_results(
        csv_data, json_data, failed_images, tmp_path, "csv_output", "json_output", "failed_output", 2
    )

    # Check CSV
    csv_file = tmp_path / "csv_output_batch_2.csv"
    assert csv_file.exists()
    assert pd.read_csv(csv_file).shape[0] == 2

    # Check JSON
    json_file = tmp_path / "json_output_batch_2.json"
    assert json_file.exists()
    with open(json_file) as f:
        data = json.load(f)
        assert len(data) == 2

    # Check failed CSV
    failed_file = tmp_path / "failed_output_batch_2.csv"
    assert failed_file.exists()
    assert pd.read_csv(failed_file).shape[0] == 2