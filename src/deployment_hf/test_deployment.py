import pytest
from unittest.mock import patch, MagicMock, call
import os
import json
import argparse
from cli import main, get_secret, prepare, deploy


# Mock the GCP Secret Manager get_secret function
@patch("cli.secretmanager.SecretManagerServiceClient")
def test_get_secret(mock_secret_manager_client):
    # Setup mock response
    mock_client_instance = MagicMock()
    mock_secret_manager_client.return_value = mock_client_instance
    mock_response = MagicMock()
    mock_response.payload.data.decode.return_value = "fake_hf_token"
    mock_client_instance.access_secret_version.return_value = mock_response

    # Call the function
    secret_value = get_secret("projects/123/secrets/fake_secret/versions/latest")

    # Assertions
    mock_client_instance.access_secret_version.assert_called_once_with(
        request={"name": "projects/123/secrets/fake_secret/versions/latest"}
    )
    assert secret_value == "fake_hf_token"


# Mock the GCP Storage prepare function
@patch("cli.storage.Client")
def test_prepare(mock_storage_client):
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "finetuned-fashionclip/model.bin"
    mock_bucket.list_blobs.return_value = [mock_blob]

    mock_client_instance = MagicMock()
    mock_client_instance.bucket.return_value = mock_bucket
    mock_storage_client.return_value = mock_client_instance

    # Call the function
    prepare(
        model_path="finetuned-fashionclip",
        gcp_project="fake_project",
        gcs_bucket_name="fake_bucket",
        local_artifact_path="./fake_artifacts",
    )

    # Assertions
    mock_storage_client.assert_called_once_with(project="fake_project")
    mock_client_instance.bucket.assert_called_once_with("fake_bucket")
    mock_bucket.list_blobs.assert_called_once_with(prefix="finetuned-fashionclip")


@patch("cli.list_repo_files", return_value=["README.md"])
@patch("cli.delete_file")
@patch("cli.upload_folder")
@patch("cli.login")
def test_deploy(mock_login, mock_upload_folder, mock_delete_file, mock_list_repo_files):
    # Setup
    mock_local_path = "./fake_artifacts"
    mock_hf_token = "fake_hf_token"
    mock_hf_repo_name = "fake_repo"
    os.makedirs(mock_local_path, exist_ok=True)
    
    # Create a mock test_results.json file
    test_results_path = os.path.join(mock_local_path, "test_results.json")
    with open(test_results_path, "w") as f:
        json.dump({"accuracy": 0.9}, f)

    try:
        # Call the function
        deploy(
            local_artifact_path=mock_local_path,
            hf_token=mock_hf_token,
            hf_repo_name=mock_hf_repo_name,
        )

        # Assertions
        mock_login.assert_called_once_with(token="fake_hf_token")
        mock_list_repo_files.assert_called_once_with(repo_id="fake_repo", token="fake_hf_token")
        mock_delete_file.assert_not_called()  # Only README.md exists, which is preserved
        mock_upload_folder.assert_called_once_with(
            folder_path=mock_local_path,
            repo_id=mock_hf_repo_name,
            token=mock_hf_token,
            commit_message="Updated upload after cleanup",
        )
    finally:
        # Clean up the created file
        if os.path.exists(test_results_path):
            os.remove(test_results_path)


@patch("cli.get_secret", return_value="fake_hf_token")
@patch("cli.prepare")
@patch("cli.deploy")
def test_main(mock_deploy, mock_prepare, mock_get_secret):
    # Mock arguments
    args = argparse.Namespace(
        prepare=True,
        deploy=False,
        model_path="finetuned-fashionclip",
        gcp_project="fake_project",
        gcs_bucket_name="fake_bucket",
        local_artifact_path="./fake_artifacts",
        hf_token="fake_hf_secret",
        hf_repo_name="fake_repo",
    )

    # Call the main function
    main(args)

    # Assertions
    mock_get_secret.assert_called_once_with("fake_hf_secret")
    mock_prepare.assert_called_once_with(
        "finetuned-fashionclip",
        "fake_project",
        "fake_bucket",
        "./fake_artifacts",
    )
    mock_deploy.assert_not_called()
