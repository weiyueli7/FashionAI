import json
import os
import io
import argparse
from pathlib import Path
import pandas as pd
import google.generativeai as genai
import re
from google.cloud import secretmanager
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize the Secret Manager client and retrieve the Gemini API key
secret_manager_client = secretmanager.SecretManagerServiceClient()
secret_name = os.getenv("GEMINI_GCP_SECRET_ACCESS",
                        "projects/1087474666309/secrets/GeminiAPI/versions/1")
response = secret_manager_client.access_secret_version(
    request={"name": secret_name})
secret_value = response.payload.data.decode("UTF-8")


def download_image_from_local(image_path):
    """Loads an image from the local file system."""
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    image_name = Path(image_path).name
    image_file_io = io.BytesIO(image_bytes)
    image_file_io.name = image_name
    return image_file_io, image_name


def preprocess_text(text):
    cleaned_text = re.sub(r'(\\u[0-9A-Fa-f]{4}|\\n|\\t)', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


def generate_captions_with_gemini(image_path):
    """Generates captions for the given image using the Gemini client."""
    image_file, image_name = download_image_from_local(image_path)

    genai.configure(api_key=secret_value)

    if image_name.endswith(('.jpg', '.jpeg')):
        mime_type = 'image/jpeg'
    elif image_name.endswith('.png'):
        mime_type = 'image/png'
    else:
        raise ValueError("Unsupported image format.")

    myfile = genai.upload_file(image_file, mime_type=mime_type)
    model = genai.GenerativeModel("gemini-1.5-flash")

    result = model.generate_content(
        [myfile, "\n\n", "For this image, come up with a caption that has 4 parts, and uses short phrases to answer each of the four categories below: - the style - the occasions that it’s worn in - material used - texture and patterns. You don't need to list the four categories."]
    )

    caption = preprocess_text(result.text)
    prompt_token = result.usage_metadata.prompt_token_count
    candidate_token = result.usage_metadata.candidates_token_count
    total_token = result.usage_metadata.total_token_count

    return caption, prompt_token, candidate_token, total_token


def save_intermediate_results(csv_data, json_data, failed_images, intermediate_folder, csv_output, json_output, failed_csv_output, batch_num):
    """Save intermediate results locally."""
    csv_df = pd.DataFrame(csv_data)
    csv_batch_output = f"{intermediate_folder}/{csv_output}_batch_{batch_num}.csv"
    csv_df.to_csv(csv_batch_output, index=False)

    json_batch_output = f"{intermediate_folder}/{json_output}_batch_{batch_num}.json"
    with open(json_batch_output, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    if failed_images:
        failed_df = pd.DataFrame(failed_images)
        failed_batch_output = f"{intermediate_folder}/{failed_csv_output}_batch_{batch_num}.csv"
        failed_df.to_csv(failed_batch_output, index=False)


def wrapper_function():
    gemini_key_path = os.getenv("GEMINI_KEY_PATH")  # Environment variable set in Docker
    with open(gemini_key_path, 'r') as f:
        gemini_key_data = json.load(f)

    # Extract the API key
    gemini_key = gemini_key_data.get("api_key")
    if not gemini_key:
        raise ValueError("The API key is missing from the gemini_key.json file.")

    images_folder = "data"
    output_folder = "output"

    # Now you have the folder names for all the paths
    print(f"Images folder: {images_folder}")
    print(f"Output folder: {output_folder}")

    # Ensure directories exist
    os.makedirs(output_folder, exist_ok=True)

    csv_data = []
    json_data = []
    failed_images = []

    total_images = 0
    batch_num = 1

    # Iterate through images and generate captions
    image_files = Path(images_folder).glob('**/*')
    valid_image_extensions = ['.jpg', '.jpeg', '.png']

    for image_file in image_files:
        if image_file.suffix.lower() not in valid_image_extensions:
            continue

        total_images += 1
        print(f"Processing image {total_images}: {image_file.name}")

        try:
            caption, prompt_token, candidate_token, total_token = generate_captions_with_gemini(
                image_file)
            csv_data.append({
                'image_name': image_file.name,
                'prompt_token_count': prompt_token,
                'candidates_token_count': candidate_token,
                'total_token_count': total_token
            })
            json_data.append({'image': image_file.name, 'caption': caption})

        except Exception as e:
            failed_images.append(
                {'image_name': image_file.name, 'error': str(e)})

    # Print current working directory
    print("Current working directory (pwd):")
    print(os.getcwd())

    # List all folders and files in the current directory
    print("\nList of all files and folders in the current directory:")
    for item in os.listdir():
        print(item)

    # Check if 'output' folder exists and list its contents
    output_dir = 'output'

    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        print(f"\nContents of '{output_dir}' folder:")
        for item in os.listdir(output_dir):
            print(item)
    else:
        print(f"\n'{output_dir}' folder does not exist.")

    # Final output saving
    csv_df = pd.DataFrame(csv_data)
    output_path = f"/src/output/final_output.csv"
    csv_df.to_csv(output_path, index=False)

    with open(f"/src/output/final_output.json", 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(
        f"Total images: {total_images}, successfully processed: {len(csv_data)}, failed: {len(failed_images)}")

    print(f"File saved at: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    wrapper_function()
