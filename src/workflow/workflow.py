import os
from kfp import dsl
from kfp import compiler
import google.cloud.aiplatform as aip
from dotenv import load_dotenv
import uuid

# Load and set up environment variables
load_dotenv()
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
BUCKET_URI = f"gs://{GCS_BUCKET_NAME}"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root"
GCP_PROJECT = os.getenv("GCP_PROJECT")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print(f"Using credentials at: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")

def generate_uuid():
    """Generate a unique job ID."""
    return str(uuid.uuid4())[:8]

# Data Captioning
DATA_CAPTIONING_IMAGE = os.getenv("DATA_CAPTIONING_IMAGE")

# Data Captioning
def data_captioning():
    print("data_captioning()")

    # Define a Container Component
    @dsl.container_component
    def data_captioning():
        container_spec = dsl.ContainerSpec(
            image=DATA_CAPTIONING_IMAGE,
            command=[],
            args=[],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def data_captioning_pipeline():
        data_captioning()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        data_captioning_pipeline, package_path="data_captioning.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "caption-app-data-captioning-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="data_captioning.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account="fashion-ai-service@fashion-ai-438801.iam.gserviceaccount.com")

# Model Training
from model import model_training as model_training_job
def model_training():
    print("model_training()")

    # Define a Pipeline
    @dsl.pipeline
    def model_training_pipeline():
        model_training_job()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        model_training_pipeline, package_path="model_training.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "app-model-training-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="model_training.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account="fashion-ai-service@fashion-ai-438801.iam.gserviceaccount.com")

# Model Deployment
MODEL_DEPLOYMENT_IMAGE = os.getenv("MODEL_DEPLOYMENT_IMAGE")

def model_deploying():
    print("model_deploying()")

    # Define a Container Component
    @dsl.container_component
    def model_deploying():
        container_spec = dsl.ContainerSpec(
            image=MODEL_DEPLOYMENT_IMAGE,
            command=[],
            args=["cli.py"],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def model_deploying_pipeline():
        model_deploying()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        model_deploying_pipeline, package_path="model_deploying.yaml"
    )
    
    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "model_deploying-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="model_deploying.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account="fashion-ai-service@fashion-ai-438801.iam.gserviceaccount.com")

if __name__ == "__main__":
    data_captioning()
    model_training()
    model_deploying()
