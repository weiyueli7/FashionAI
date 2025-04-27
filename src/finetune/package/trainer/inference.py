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
