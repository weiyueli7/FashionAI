# FashionAI

## Overview

FashionAI is a full-stack, AI-driven platform that consolidates fashion products from multiple brands, enabling users to efficiently discover matching items without extensive searching. With this application, users can submit queries such as "find me a classic dress for attending a summer wedding" and receive clothing recommendations that semantically match their criteria.

See our blog post [here](https://medium.com/@michelleqtan/natural-language-based-ai-fashion-stylist-efe337e72270).

### Developers:

<div style="display: flex; justify-content: space-around; align-items: center;">
    <div><a href="mailto:yushuqiu@g.harvard.edu"><strong>Yushu Qiu</strong></a></div>
    <div><a href="mailto:weiyueli@g.harvard.edu"><strong>Weiyue Li</strong></a></div>
    <div><a href="mailto:dnurieli@g.harvard.edu"><strong>Daniel Nurieli</strong></a></div>
    <div><a href="mailto:mtan@mba2025.hbs.edu"><strong>Michelle Tan</strong></a></div>
</div>

## Prerequisites and Setup Instructions

FashionAI uses Google Cloud Platform (GCP) for model training and app deployment. All source code in the [`src`](src) folder for the machine learning workflow and app deployment is containerized with Docker, eliminating the need to install dependencies manually. Follow these steps to get started:

1. Clone this repository.
2. Create a GCP project and set up a service account with the following permissions: `AI Platform Admin`, `Compute Admin`, `Project IAM Admin`, `Secret Manager Secret Accessor`, `Service Usage Admin`, `Service Usage Consumer`, `Storage Admin`, and `Vertex AI Administrator`. Save the service account key as `secret.json` in a `secrets` folder (`secrets/secret.json`) at the same level as the project.
3. Create two [Secret Manager](https://cloud.google.com/security/products/secret-manager?hl=en) entries to store API keys for [WandB](https://wandb.ai/home) and [Hugging Face](https://huggingface.co/). WandB is used for tracking model training, and Hugging Face is used for model deployment.

## Deployment Instructions

### ML Workflow

FashionAI includes a production-ready ML workflow hosted on GCP. Below is an overview of the workflow components and instructions for running it.

#### Overview of Workflow Components

The ML workflow includes three main stages:
1. **Data Captioning**: Processes images and generates captions for training.
2. **Model Training**: Fine-tunes the Fashion-CLIP model with the generated data.
3. **Model Deployment**: Deploys the trained model to Hugging Face for inference.

The workflow uses Kubeflow Pipelines to orchestrate the steps and Vertex AI to execute them. This setup provides scalability, efficient workload distribution, and seamless integration with GCP services.

To run the workflow:
```bash
cd src/workflow
sh docker-shell.sh
```

The shell script builds and runs a Docker image, automatically submitting the captioning, training, and deployment jobs to Vertex AI step by step through pulling the corresponding docker images.

We also set up a CI/CD pipeline to allow automatic running of the workflow. The workflow will automatically run once we add "/run-ml-workflow" in our commit message.

**Note:** To reproduce this workflow, you must update the GCP project name, bucket name, and other configurations in the `docker-shell.sh` scripts located in each subfolder of [`src`](src). Then, follow the instructions to run each container individually and push the image to the Artifact Registry so that `secret.json` has proper access.

---

#### 1. Data Captioning

- **Objective:** Generate human-like captions for training images, as the scraped images lack captions.
- **Solution:** Utilize the Gemini 1.5 Flash multimodal model to generate captions. This model was chosen for its reliable performance, cost-effectiveness, and fast processing speed.
- **Process:**
  - During the scraping process, images are stored in GCS buckets.
  - The captioning Docker image, registered in the GCP Artifact Registry, retrieves images from GCS, invokes the Gemini API to generate captions, and saves the resulting JSON files to a separate GCS bucket for further processing.
  - After captioning, the workflow moves to the model training stage.

---

#### 2. Model Training (and Evaluation)

- **Objective:** Fine-tune the Fashion-CLIP model to handle fashion-specific queries effectively.
- **Process:**
  - The training Docker image retrieves image-caption data from GCS buckets and fine-tunes the Fashion-CLIP model using PyTorch and WandB.
  - Fine-tuned models are saved to a GCS bucket.
- **Evaluation:**
  - Inference is performed on a test set of 100 captions.
  - The top 5 matching images for each caption are evaluated; if the correct image is among the top 5, the result is marked as correct.
  - Accuracy is calculated as the number of correct matches divided by 100.
  - Evaluation results, saved as a JSON file, ensure that only models meeting the performance threshold proceed to deployment.

---

#### 3. Model Deployment

- **Objective:** Deploy the fine-tuned model for real-world use.
- **Deployment Target:** Hugging Face was chosen for its cost-effectiveness compared to GCP. Its lower fees for deployment and inference make it a sustainable long-term solution.
- **Process:**
  - The deployment Docker image downloads the fine-tuned model and evaluation results from GCS.
  - The model’s accuracy is checked against a defined threshold (default: 0.8). If it meets or exceeds the threshold, the workflow uploads the model to a Hugging Face repository using the Hugging Face API.
      -  Our final deployed model has an accuracy of 90% on our test bench.
  - An endpoint is generated for integration with the frontend and backend systems to provide real-time inference capabilities for user queries.


### App Deployment

The application has a CI/CD pipeline set up in GitHub Actions that automatically triggers the deployment process whenever a commit is made with "/deploy-app" in the commit name. This pipeline is configured to use GCP secrets and Kubernetes configuration details that have been pre-defined in the project's src/ansible/vars/main.yml file. Before the deployment process, you need to revise the variable values in this file to set up details like your GCP projects and your GCP regions.

The deployment pipeline:

* Sets up a Kubernetes cluster, including nodes and a static IP address. This Kubernetes environment is accessible at the URL http://34.56.234.182.sslip.io.
* Configures the necessary environment variables and secrets that the application's Docker images will use when running in the Kubernetes cluster.
* Builds and pushes the Docker images to a container registry.
* Deploys the Kubernetes resources required for the application, including an Nginx ingress controller and the deployments and services defined in the src/server/kubernetes folder. These Kubernetes files help set up and deploy front end, back end, and vectorrerized database.

To run:
```ansible-playbook -i src/ansible/inventory.ini src/ansible/playbook.yml```
However, the deployment should not be run locally, but rather should be executed as part of the CI/CD pipeline.

Overall, this deployment process is fully automated, leveraging a CI/CD pipeline to handle the provisioning of the Kubernetes infrastructure, building and deploying the application's Docker images, and configuring the necessary networking and service resources in the target Kubernetes environment.

The application is now fully hosted on GCP. The frontend, backend, and vectorized database components are integrated and working together seamlessly on GCP.


## Usage details and examples

### Usage Guidelines

#### Frontend Usage

- **Navigating the Application**: Use the navigation buttons on the home page to access different sections.
- **Interacting with the Stylist**: On the Stylist page, describe your occasion and style preferences to receive personalized recommendations.
- **Viewing the Gallery**: The Gallery page allows browsing through various fashion items. Click on any item for more details.

#### User Journey Showcase
- **Get Recommendation**:

    1. Click "Get Started Here" to access the AI Stylist page and receive personalized clothing recommendations.
    ![image](https://github.com/user-attachments/assets/7fc22823-04ee-4d5f-9d72-bbf13f5df2e6)

    2. Enter a query based on your preferences, such as "I want a pair of shoes."
    ![image](https://github.com/user-attachments/assets/5bf4ead4-2017-4cff-8464-fe5af095058d)

    3. The AI Assistant will provide a selection of shoe images tailored to your preferences, along with brand details and a brief description for each item.
    ![image](https://github.com/user-attachments/assets/a627ca5a-3692-415a-b565-6cf95d92524d)

    4. Click on the recommended image, and you will be redirected to the shopping link on Farfetch.
    ![image](https://github.com/user-attachments/assets/d1173bd0-084f-4ba1-9a82-545e7d33dcaf)

    
    
- **Explore Fashion Gallery**:

    1. Click on "Fashion Gallery" to explore a curated selection of clothing recommendations organized by category.
    ![image](https://github.com/user-attachments/assets/c49d5ef5-0d81-4374-8e4e-b282f70c08dc)

    2. For instance, if you're looking for Business Professional attire, navigate to the corresponding section to view tailored recommendations.
    ![image](https://github.com/user-attachments/assets/178684c4-5826-43e0-bdb8-8bdead870627)

    3. Click on any recommended image to be redirected to the shopping link on Farfetch.
    ![image](https://github.com/user-attachments/assets/c39ea621-00cc-4a7d-8b43-f1cee60b1913)



## Known Issues and Limitations

Here are several current limitations of our app:

1. **Lack of support for specific brands**  
   - *Issue:* The app is unable to return results for specific brands.  
   - *Future fix:* Implement an LLM agent to process user queries, extract meaningful information, and enable image matching within a subset of our image dataset.

2. **Difficulty understanding edge cases**  
   - *Issue:* The model struggles with edge cases, such as "Southeast Asian wedding," due to a lack of diverse captions during the model fine-tuning process.  
   - *Future fix:* Gather a more diverse set of images and ensure that captions capture a wider variety of styles and occasions.

3. **Inability to filter unethical or harmful input**  
   - *Issue:* The app cannot detect or prevent unethical or hate-based input.  
   - *Future fix:* Implement an LLM agent to process user queries, identify harmful content, and halt execution immediately if necessary.








