"""
Module to deploy a Hugging Face model (FashionCLIP) on HuggingFace.
"""

import os
import argparse
from google.cloud import storage
from huggingface_hub import login, HfApi, delete_file, upload_folder, list_repo_files
from google.cloud import secretmanager


# # uncomment for local testing
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../../../secrets/secret.json"


def get_secret(secret):
    client = secretmanager.SecretManagerServiceClient()
    print("-----\nFetching Key\n-----")
    response = client.access_secret_version(request={"name": secret})
    secret_value = response.payload.data.decode("UTF-8")
    print("-----\nKey Fetched\n-----")
    return secret_value


def prepare(model_path, gcp_project, gcs_bucket_name, local_artifact_path):
    """
    Downloads all files from a specific folder in a GCP bucket
    and saves them locally, preserving the folder structure.
    """
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(gcs_bucket_name)

    # List all blobs in the specified folder
    blobs = bucket.list_blobs(prefix=model_path)

    for blob in blobs:
        # Remove the folder prefix to get the relative path
        relative_path = blob.name[len(model_path) + 1:]

        # Skip folder paths
        if not relative_path:
            continue

        # Define the local file path
        local_file_path = os.path.join(local_artifact_path, relative_path)

        # Ensure the local directory exists
        local_dir = os.path.dirname(local_file_path)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        # Download the file
        print(f"Downloading {blob.name} to {local_file_path}...")
        blob.download_to_filename(local_file_path)

    print(
        f"All files from {model_path} have been downloaded to {local_artifact_path}")


def deploy(local_artifact_path, hf_token, hf_repo_name):
    login(token=hf_token)

    # Initialize API
    api = HfApi()

    # Check if the repository exists
    try:
        repo_files = list_repo_files(repo_id=hf_repo_name, token=hf_token)
        print(f"Repository {hf_repo_name} found. Proceeding with upload.")
    except Exception as e:
        print(f"Repository {hf_repo_name} does not exist. Creating a new repository.")
        api.create_repo(repo_id=hf_repo_name, token=hf_token, repo_type="model", exist_ok=True)
        repo_files = []  # Empty repository, no files to list

    # Files to preserve
    files_to_preserve = [".gitattributes", "README.md"]

    # Delete files not in the preserve list
    for file_path in repo_files:
        if file_path not in files_to_preserve:
            delete_file(path_in_repo=file_path,
                        repo_id=hf_repo_name, token=hf_token)
            print(f"Deleted: {file_path}")

    # Upload all files from the local folder
    upload_folder(
        folder_path=local_artifact_path,
        repo_id=hf_repo_name,
        token=hf_token,
        commit_message="Updated upload after cleanup"
    )

    print("Upload complete.")


def main(args):
    print("Starting FashionCLIP deployment...")
    secret = get_secret(args.hf_token)
    if args.prepare:
        print("Preparing model...")
        prepare(args.model_path, args.gcp_project, args.gcs_bucket_name, args.local_artifact_path)

    elif args.deploy:
        print("Deploying model...")
        deploy(args.local_artifact_path, secret, args.hf_repo_name)
    else:
        print("Preparing model...")
        prepare(args.model_path, args.gcp_project, args.gcs_bucket_name, args.local_artifact_path)
        print("Deploying model...")
        deploy(args.local_artifact_path, secret, args.hf_repo_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FashionCLIP Deployment CLI")

    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Prepare the FashionCLIP model and processor for Vertex AI.",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy the FashionCLIP model to Vertex AI.",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="finetuned-fashionclip",
        help="Path to the model in the GCS bucket.",
    )
    parser.add_argument(
        "--gcp_project",
        type=str,
        default="fashion-ai-438801",
        help="Google Cloud Project ID.",
    )
    parser.add_argument(
        "--gcs_bucket_name",
        type=str,
        default="vertexai_train",
        help="Name of the GCS bucket containing the model.",
    )
    parser.add_argument(
        "--local_artifact_path",
        type=str,
        default="./artifacts",
        help="Local path to save downloaded artifacts.",
    )
    parser.add_argument(
        "--hf_token",
        type=str,
        default="projects/1087474666309/secrets/HF_API/versions/latest",
        help="Hugging Face API token.",
    )
    parser.add_argument(
        "--hf_repo_name",
        type=str,
        default="weiyueli7/test2",
        help="Name of the Hugging Face model repository.",
    )

    args = parser.parse_args()
    main(args)
