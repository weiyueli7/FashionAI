import re
import pandas as pd
from io import BytesIO, StringIO
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, secretmanager
from pinecone import Pinecone, ServerlessSpec
from helper_functions import get_clip_vector
import json
import os 

# Initialize global constants
PROJECT_ID = os.getenv("PROJECT_ID")
PINECONE_SECRET_NAME = os.getenv("PINECONE_SECRET_NAME")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
VECTOR_DIM_MODEL = os.getenv("VECTOR_DIM_MODEL")
BASE_BUCKET = os.getenv("BASE_BUCKET")


# Initialize global GCP storage client
storage_client = storage.Client(PROJECT_ID)


# Helper Functions

def get_pinecone_api_key(secret_name):
    """Retrieve Pinecone API key from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode("UTF-8")


def initialize_pinecone(index_name, vector_dim, api_key):
    """Initialize Pinecone index, creating it if it doesn't exist."""
    pc = Pinecone(api_key=api_key)
    if index_name not in [item["name"] for item in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=vector_dim,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)


def load_file_from_bucket(bucket_name, blob_name, file_type="json"):
    """Load a file from a GCP bucket."""
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=blob_name))

    file_blob = next(
        (blob for blob in blobs if blob.name.endswith(f'.{file_type}')), None)
    if not file_blob:
        raise ValueError(
            f"No {file_type} file found under blob prefix: {blob_name}")

    print(f"Reading file: {file_blob.name} from bucket: {bucket_name}")
    content = file_blob.download_as_text()

    return json.loads(content) if file_type == "json" else content


def parse_metadata(metadata_text):
    """Parse metadata CSV into a pandas DataFrame."""
    return pd.read_csv(StringIO(metadata_text))


def get_image_data(bucket_name, blob_path):
    """Download image data from a GCP bucket."""
    bucket = storage_client.bucket(bucket_name)
    image_blob = bucket.blob(blob_path)
    if not image_blob.exists():
        raise FileNotFoundError(f"Image not found in bucket: {blob_path}")
    return Image.open(BytesIO(image_blob.download_as_bytes())).convert("RGB")


# Processing Functions

def process_image_metadata(caption_entry, metadata_df, topic, data_name, image_bucket, pinecone_index):
    """Process and upload an image and its metadata to Pinecone."""
    image_name = caption_entry["image"]
    caption = caption_entry["caption"]

    # Find metadata entry
    image_id = int(re.search(r'\d+', image_name).group())
    metadata_entry = metadata_df.loc[metadata_df["source/id"] == image_id]

    if metadata_entry.empty:
        print(f"No metadata found for image: {image_name}")
        return None

    # Extract metadata fields

    # Convert to a series for easy access
    metadata_entry = metadata_entry.iloc[0]
    brand = metadata_entry.get("brand", "")
    image_url = metadata_entry.get("medias/0/url", "")
    gender = metadata_entry.get("categories/0", "")
    item_type = metadata_entry.get("categories/1", "")
    item_sub_type = metadata_entry.get("categories/2", "")
    item_url = metadata_entry.get("source/crawlUrl", "")
    image_description = metadata_entry.get("medias/0/alt", "")

    # Get image data and generate vector
    image_path = f"scrapped_data/{topic}/{data_name}{image_name}"
    try:
        image = get_image_data(image_bucket, image_path)
        vector = get_clip_vector(image, is_image=True)
    except FileNotFoundError:
        print(f"Image not found: {image_name}")
        return None

    # Prepare metadata for Pinecone
    pinecone_metadata = {
        "image_name": image_description,
        "brand": brand,
        "gender": gender,
        "item_type": item_type,
        "item_sub_type": item_sub_type,
        "image_url": image_url,
        "caption": caption,
        "item_url": item_url
    }

    # Upload to Pinecone
    pinecone_index.upsert([
        {
            "id": f"{topic} {image_name}",
            "values": vector.tolist(),
            "metadata": pinecone_metadata
        }
    ])
    return image_name


def process_and_upload_topic_parallel(topic, base_bucket, pinecone_index, data_name, max_workers=10):
    """Process and upload data for a specific topic in parallel."""
    caption_path = f"captioned_data/{topic}/{data_name}"
    metadata_path = f"metadata/{topic}/{data_name}"
    image_bucket = base_bucket

    # Load captions and metadata
    caption_data = load_file_from_bucket(
        base_bucket, caption_path, file_type="json")
    metadata_text = load_file_from_bucket(
        base_bucket, metadata_path, file_type="csv")
    metadata_df = parse_metadata(metadata_text)

    uploaded_items = []

    def process_entry(caption_entry):
        """Process a single caption entry."""
        return process_image_metadata(
            caption_entry, metadata_df, topic, data_name, image_bucket, pinecone_index
        )

    # Parallelize processing with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(process_entry, caption_data), total=len(
            caption_data), desc=f"Processing {topic}"))

    # Collect successful uploads
    uploaded_items = [item for item in results if item]
    print(f"Uploaded {len(uploaded_items)} items for topic: {topic}")


# Main Execution

if __name__ == "__main__":
    pinecone_api_key = get_pinecone_api_key(PINECONE_SECRET_NAME)
    pinecone_index = initialize_pinecone(
        PINECONE_INDEX_NAME, int(VECTOR_DIM_MODEL), pinecone_api_key)

    # Load topics from CSV
    data_buckets = pd.read_csv("data_buckets.csv")

    for _, row in data_buckets.iterrows():
        topic = row["bucket"]
        data_name = row["name"]
        print(f"Processing topic: {topic}")
        process_and_upload_topic_parallel(
            topic, BASE_BUCKET, pinecone_index, data_name)
