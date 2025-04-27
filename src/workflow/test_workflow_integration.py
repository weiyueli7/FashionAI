import pytest
import os
from unittest.mock import patch, MagicMock, ANY

@patch.dict(os.environ, {"GCP_PROJECT": "your-test-project", "GCS_BUCKET_NAME": "your-test-bucket"}, clear=True)
@patch("google.auth.default")
@patch("google.cloud.aiplatform.init")
@patch("google.cloud.aiplatform.PipelineJob")
def test_data_captioning(mock_pipeline_job, mock_aip_init, mock_google_auth):
    # Mock Google authentication
    mock_google_auth.return_value = (MagicMock(), "test-project-id")

    # Mock the behavior of aip.init
    mock_aip_init.return_value = None

    # Mock the PipelineJob class
    mock_pipeline_instance = MagicMock()
    mock_pipeline_job.return_value = mock_pipeline_instance

    from workflow import data_captioning
    data_captioning()

    # Assertions
    mock_aip_init.assert_called_once_with(
        project="your-test-project", staging_bucket="gs://your-test-bucket"
    )
    mock_pipeline_job.assert_called_once_with(
        display_name=ANY,  # Ignore the dynamically generated display_name
        template_path="data_captioning.yaml",
        pipeline_root="gs://your-test-bucket/pipeline_root",
        enable_caching=False,
    )
    mock_pipeline_instance.run.assert_called_once()


@patch("google.auth.default")
@patch("google.cloud.aiplatform.init")
@patch("google.cloud.aiplatform.PipelineJob")
def test_model_training(mock_pipeline_job, mock_aip_init, mock_google_auth):
    # Mock Google authentication
    mock_google_auth.return_value = (MagicMock(), "test-project-id")
    
    # Mock dependencies
    mock_aip_init.return_value = None
    mock_pipeline_instance = MagicMock()
    mock_pipeline_job.return_value = mock_pipeline_instance

    from workflow import model_training
    model_training()

    # Assertions
    mock_aip_init.assert_called_once()
    mock_pipeline_job.assert_called_once()
    mock_pipeline_instance.run.assert_called_once()

@patch("google.auth.default")
@patch("google.cloud.aiplatform.init")
@patch("google.cloud.aiplatform.PipelineJob")
def test_model_deploying(mock_pipeline_job, mock_aip_init, mock_google_auth):
    # Mock Google authentication
    mock_google_auth.return_value = (MagicMock(), "test-project-id")
    
    # Mock dependencies
    mock_aip_init.return_value = None
    mock_pipeline_instance = MagicMock()
    mock_pipeline_job.return_value = mock_pipeline_instance

    from workflow import model_deploying
    model_deploying()

    # Assertions
    mock_aip_init.assert_called_once()
    mock_pipeline_job.assert_called_once()
    mock_pipeline_instance.run.assert_called_once()
