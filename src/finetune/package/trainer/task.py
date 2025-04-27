import os
import json
import argparse
from google.cloud import storage
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import torch
import wandb
from google.cloud import secretmanager
from tqdm import tqdm
# from inference import FashionDataset, test_model

## uncomment for local testing
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../../../secrets/secret.json"


def get_secret(secret):
    client = secretmanager.SecretManagerServiceClient()
    print("-----\nFetching Key\n-----")
    response = client.access_secret_version(request={"name": secret})
    secret_value = response.payload.data.decode("UTF-8")
    print("-----\nKey Fetched\n-----")
    return secret_value




# Function to download images and JSON file from GCS
def download_from_gcs(gcs_json_path, gcs_image_dir, local_json_path, local_image_dir, n_samples=None):
    client = storage.Client()

    # Download JSON file if it doesn't already exist locally
    if not os.path.exists(local_json_path):
        bucket_name, json_blob_path = gcs_json_path.replace(
            "gs://", "").split("/", 1)
        bucket = client.bucket(bucket_name)
        json_blob = bucket.blob(json_blob_path)
        json_blob.download_to_filename(local_json_path)
        print(f"Downloaded {json_blob_path} to {local_json_path}")
    else:
        print(f"JSON file already exists at {local_json_path}, skipping download.")

    # Load JSON and filter the first n items
    with open(local_json_path, 'r') as f:
        if n_samples:
            data = json.load(f)[:n_samples]
        else:
            data = json.load(f)

    # Prepare for image downloads
    bucket_name, image_blob_prefix = gcs_image_dir.replace(
        "gs://", "").split("/", 1)
    blobs = client.list_blobs(bucket_name, prefix=image_blob_prefix)
    os.makedirs(local_image_dir, exist_ok=True)

    # Download images if they do not already exist locally
    print("Downloading images...")
    for blob in blobs:
        for item in data:
            if blob.name.endswith(item['image']):
                local_path = os.path.join(
                    local_image_dir, os.path.basename(blob.name))
                # print(f"local_path: {local_path}")
                if not os.path.exists(local_path):
                    blob.download_to_filename(local_path)
                    # print(f"Downloaded {blob.name} to {local_path}")
                else:
                    # print(f"Image {local_path} already exists, skipping download.")
                    pass



# Function to upload model weights to GCS
def upload_to_gcs(local_path, gcs_path, bucket_name="vertexai_train"):
    client = storage.Client()
    # bucket_name, gcs_folder = gcs_path.replace("gs://", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    gcs_path = gcs_path[len(f"gs://{bucket_name}/"):]
    print(f"Uploading model to {gcs_path}...")

    for root, _, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            print(f"local_file_path: {local_file_path}")
            remote_path = os.path.relpath(local_file_path, local_path)
            remote_path = os.path.join(gcs_path, remote_path)
            print(f"remote_path: {remote_path}")
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file_path)
            print(f"Uploaded {local_file_path} to {gcs_path}/{remote_path}")

DIR_DICT = {
    "men_accessories": {
        "category": "men_accessories",
        "json_path": "gs://fashion_ai_data/captioned_data/men_accessories/2024-11-18_11-34-54/men_accessories.json",
        "image_dir": "gs://fashion_ai_data/scrapped_data/men_accessories/2024-11-18_11-34-54"
} ,
    
    "men_clothes":{
        "category": "men_clothes",
        "json_path": "gs://fashion_ai_data/captioned_data/men_clothes/2024-11-18_11-34-54/men_clothes.json",
        "image_dir": "gs://fashion_ai_data/scrapped_data/men_clothes/2024-11-18_11-34-54"
} ,
        
    "men_shoes":{   
        "category": "men_shoes",
        "json_path": "gs://fashion_ai_data/captioned_data/men_shoes/2024-11-18_11-34-54/men_shoes.json",
        "image_dir": "gs://fashion_ai_data/scrapped_data/men_shoes/2024-11-18_11-34-54"
} ,
        
    "women_accessories":{
        "category": "women_accessories",
        "json_path": "gs://fashion_ai_data/captioned_data/women_accessories/2024-11-18_11-34-54/women_accessories.json",
        "image_dir": "gs://fashion_ai_data/scrapped_data/women_accessories/2024-11-18_11-34-54"
} ,
            
    "women_clothes":{
        "category": "women_clothes",
        "json_path": "gs://fashion_ai_data/captioned_data/women_clothes/2024-11-18_11-34-54/women_clothes.json",
        "image_dir": "gs://fashion_ai_data/scrapped_data/women_clothes/2024-11-18_11-34-54"
} ,
                    
    "women_shoes":{
        "category": "women_shoes",
        "json_path": "gs://fashion_ai_data/captioned_data/women_shoes/2024-11-18_11-34-54/women_shoes.json",
        "image_dir": "gs://fashion_ai_data/scrapped_data/women_shoes/2024-11-18_11-34-54"
}
}


import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from tqdm import tqdm
import numpy as np

# Define dataset class
class FashionDataset(Dataset):
    def __init__(self, json_file, image_dir, transform=None):
        self.json_file = json_file
        with open(json_file, 'r') as f:
            # Use only the first 100 data points
            self.data = json.load(f)[:100]
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image_path = os.path.join(self.image_dir, item['image'])
        
        image = Image.open(image_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        text = item['caption']
        return image, text
    

class ImageDataset(Dataset):
    def __init__(self, total_test_cases, json_file, image_dir, transform=None):
        self.json_file = json_file  # Store the JSON file path
        with open(json_file, 'r') as f:
            self.data = json.load(f)[:100]#[:total_test_cases]  # First 100 data points
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image_path = os.path.join(self.image_dir, item['image'])
        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, image_path


def test_model(model, processor, dataset, local_model_dir, device, total_test_cases=10):
    print("\n\nModel evaluation started...\n\n")
    model.eval()
    correct_matches = 0
    test_data = dataset.data[:total_test_cases]

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        # transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    # transform = None


    # Use the original JSON file path for all images dataset
    all_images_dataset = ImageDataset(total_test_cases=total_test_cases, json_file=dataset.json_file, image_dir=dataset.image_dir, transform=transform)
    all_images_loader = DataLoader(all_images_dataset, batch_size=32, shuffle=False)

    for idx, test_item in enumerate(test_data):
        caption = test_item['caption']
        true_image_path = os.path.join(dataset.image_dir, test_item['image'])
        
        # Search for the best matching image
        best_image_path, _, top5_image_paths = search_similar_images(caption, all_images_loader, model, processor, device)

        print(f"True image: {true_image_path}")

        for i, img_path in enumerate(top5_image_paths):
            if os.path.basename(img_path) == os.path.basename(true_image_path):
                print(f"Matched path: {img_path}")
                print(f"caption: {caption}")
                correct_matches += 1
            
        # Check if the best match is correct
        # if os.path.basename(best_image_path) == os.path.basename(true_image_path):
        #     correct_matches += 1
        #     print("\n\n\nMatch found!\n\n\n")

    # Calculate accuracy
    accuracy = correct_matches / total_test_cases

    # Save accuracy to a JSON file
    result_file = os.path.join(local_model_dir, "test_results.json")
    with open(result_file, 'w') as f:
        json.dump({"accuracy": accuracy}, f)
    print(f"Testing completed. Accuracy: {accuracy}. Results saved to {result_file}")



def search_similar_images(text, image_loader, model, processor, device):
    all_probs = []
    all_image_paths = []
    
    for images, image_paths in image_loader:
        images = images.float().to(device)
        inputs = processor(text=[text], 
                           images=images, 
                           return_tensors="pt", 
                           padding=True, 
                           ).to(device)

        # Forward pass: get the similarity logits
        with torch.no_grad():
            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image  # Image-to-text similarity

        # Convert logits to probabilities (softmax over image logits)
        probs = logits_per_image.softmax(dim=0)  # Apply softmax over the last dimension

        # Store results for this batch
        all_probs.append(probs)
        all_image_paths.extend(image_paths)
    
    # Concatenate probabilities across all batches
    all_probs = torch.cat(all_probs, dim=0)
    
    # Find the most relevant image (best match)
    best_image_idx = all_probs.argmax(dim=0).item()  # Get the index of the best match

    # get indicies of top 5 matches
    top5_image_idxs = all_probs.argsort(descending=True, dim=0)[:5]
    # print(f"top5_image_idxs: {top5_image_idxs}")
    
    best_image_path = all_image_paths[best_image_idx]

    # get top 5 image paths
    top5_image_paths = [all_image_paths[i] for i in top5_image_idxs]
    return best_image_path, all_probs, top5_image_paths



# Parse arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="men_accessories", help="Category of the dataset.")
    parser.add_argument("--output_dir", type=str, default="finetuned-fashionclip",
                        help="GCS path to save the fine-tuned model.")
    parser.add_argument("--batch_size", type=int, default=32,
                        help="Training batch size.")
    parser.add_argument("--epochs", type=int, default=1,
                        help="Number of training epochs.")
    parser.add_argument("--learning_rate", type=float,
                        default=5e-6, help="Learning rate.")
    parser.add_argument("--wandb_key", dest="wandb_key",
                        default="projects/1087474666309/secrets/WandbAPI/versions/latest", type=str, help="WandB API Key Secret Name")
    parser.add_argument("--model_name", type=str, 
                        default="weiyueli7/fclip_men_accessories",
                        # default="patrickjohncyh/fashion-clip",
                        help="Name of the model to load.")
    parser.add_argument("--bucket_name", type=str, default="vertexai_train")
    parser.add_argument("--n_samples", type=int, default=None)
    parser.add_argument("--total_test_cases", type=int, default=10)
    return parser.parse_args()


def main():
    args = parse_args()



    json_path = DIR_DICT[args.category]["json_path"]
    image_dir = DIR_DICT[args.category]["image_dir"]

    # Local paths for data
    local_json_path = json_path.replace("gs://", "")
    local_image_dir = image_dir.replace("gs://", "")
    local_model_dir = "local_fine_tuned_model"

    # Create dedicated subfolder for the model in the output directory
    os.makedirs("/".join(local_json_path.split("/")[:-1]), exist_ok=True)
    os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(local_model_dir, exist_ok=True)

    # Download data from GCS
    download_from_gcs(json_path, image_dir,
                      local_json_path, local_image_dir, args.n_samples)

    # Dataset and DataLoader
    transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])



    # wandb.login(key=get_secret(args.wandb_key))
    # wandb.init(project=f"fashionclip_{args.category}", config=args)

    dataset = FashionDataset(json_file=local_json_path,
                             image_dir=local_image_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    # Model and processor
    processor = CLIPProcessor.from_pretrained(args.model_name)
    processor.image_processor.do_rescale = False
    model = CLIPModel.from_pretrained(args.model_name)
    print(f"model loaded from {args.model_name}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)

    # Training loop
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0
        progress_bar = tqdm(enumerate(dataloader), total=len(
            dataloader), desc=f"Epoch {epoch+1}/{args.epochs}")
        for batch_idx, (images, texts) in progress_bar:
            images = images.to(device)
            inputs = processor(
                text=texts,
                images=images,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77
            ).to(device)
            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image
            logits_per_text = outputs.logits_per_text
            loss_image = torch.nn.functional.cross_entropy(
                logits_per_image, torch.arange(len(images), device=device))
            loss_text = torch.nn.functional.cross_entropy(
                logits_per_text, torch.arange(len(texts), device=device))
            loss = (loss_image + loss_text) / 2
            total_loss += loss.item()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            progress_bar.set_postfix(loss=loss.item())
        #     wandb.log(
        #         {"epoch": epoch, "batch_idx": batch_idx, "loss": loss.item()})
        # wandb.log({"epoch": epoch, "average_loss": total_loss / len(dataloader)})

    # Save and upload the model
    model.save_pretrained(local_model_dir)
    processor.save_pretrained(local_model_dir)


    # add testing code here
    test_model(model, processor, dataset, local_model_dir, device, args.total_test_cases)

    upload_to_gcs(local_model_dir, args.output_dir, args.bucket_name)
    print("Training completed and model uploaded successfully.")


if __name__ == "__main__":
    main()
