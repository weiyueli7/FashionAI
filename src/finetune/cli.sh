
# List of prebuilt containers for training
# https://cloud.google.com/vertex-ai/docs/training/pre-built-containers

export UUID=$(openssl rand -hex 6)
export DISPLAY_NAME="fashionclip_training_job_$UUID"
export MACHINE_TYPE="n1-standard-4"
export REPLICA_COUNT=1
export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-3.py310:latest"
export PYTHON_PACKAGE_URI=$GCS_BUCKET_URI/trainer.tar.gz
export PYTHON_MODULE="trainer.task"
# export ACCELERATOR_TYPE="NVIDIA_TESLA_T4"
# export ACCELERATOR_COUNT=1
export GCP_REGION="us-central1" # Adjust region based on you approved quotas for GPUs

echo $GCS_DATA_BUCKET_URI

# To train the model:
export CMDARGS="--output_dir=$GCS_BUCKET_URI/test_fclip/,--n_samples=100"
# Run training with No GPU
export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-3.py310:latest"
gcloud ai custom-jobs create \
  --region=$GCP_REGION \
  --display-name=$DISPLAY_NAME \
  --python-package-uris=$PYTHON_PACKAGE_URI \
  --worker-pool-spec=machine-type=$MACHINE_TYPE,replica-count=$REPLICA_COUNT,executor-image-uri=$EXECUTOR_IMAGE_URI,python-module=$PYTHON_MODULE \
  --args=$CMDARGS



# To deploy the model:

# export PYTHON_MODULE="trainer.deploy"
# export CMDARGS="--hf_repo_name=weiyueli7/test2"
# export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-3.py310:latest"
# gcloud ai custom-jobs create \
#   --region=$GCP_REGION \
#   --display-name=$DISPLAY_NAME \
#   --python-package-uris=$PYTHON_PACKAGE_URI \
#   --worker-pool-spec=machine-type=$MACHINE_TYPE,replica-count=$REPLICA_COUNT,executor-image-uri=$EXECUTOR_IMAGE_URI,python-module=$PYTHON_MODULE \
#   --args=$CMDARGS