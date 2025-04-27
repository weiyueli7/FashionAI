import pytest
from unittest.mock import patch, MagicMock

# Mock the dsl.component decorator
@patch("kfp.dsl.component", lambda *args, **kwargs: lambda func: func)
@patch("google.cloud.aiplatform.init")
@patch("google.cloud.aiplatform.CustomPythonPackageTrainingJob")
def test_model_training(mock_training_job, mock_aip_init):
    # Mock `aip.init` to avoid actual initialization
    mock_aip_init.return_value = None

    # Mock the CustomPythonPackageTrainingJob class
    mock_job_instance = MagicMock()
    mock_training_job.return_value = mock_job_instance

    # Import and call the model_training function
    from model import model_training
    model_training()

    # Verify `aip.init` was called with expected arguments
    mock_aip_init.assert_called_once_with(
        project="fashion-ai-438801",
        location="us-central1",
        staging_bucket="gs://fashionai_training"
    )

    # Verify the CustomPythonPackageTrainingJob was created with expected arguments
    mock_training_job.assert_called_once_with(
        display_name="fashionclip_training_job",
        python_package_gcs_uri="gs://fashionai_training/trainer.tar.gz",
        python_module_name="trainer.task",
        container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-3.py310:latest",
        project="fashion-ai-438801",
    )

    # Verify the `run` method was called with expected arguments
    mock_job_instance.run.assert_called_once_with(
        args=[
            "--output_dir=gs://fashionai_training/finetuned-fashionclip/",
            "--n_samples=100",
            "--bucket_name=fashionai_training"
        ],
        replica_count=1,
        machine_type="n1-standard-4",
        sync=True,
    )
