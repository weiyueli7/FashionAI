from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
    "torch",
    "torchvision",
    "transformers",
    "Pillow==9.2.0",
    "wandb",
    "annoy",
    "fashion-clip",
    "google-cloud-secret-manager",
    "huggingface_hub",
    "google-cloud-aiplatform"

]

setup(
    name="fashion-ai-trainer",
    version="0.0.1",
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    description="FashionAI Trainer Application",
)
