from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import CLIPProcessor, CLIPModel
import os

# Get environment variables directly from Docker
APP_HOST = os.getenv("APP_HOST")  # Default to 127.0.0.1
APP_PORT_VECTOR = int(os.getenv("APP_PORT_VECTOR"))    # Default to 8001
MODEL_NAME = os.getenv("MODEL_NAME")
PROCESSOR_NAME = os.getenv("PROCESSOR_NAME")

app = FastAPI()

# Load CLIP model and processor
model = CLIPModel.from_pretrained(MODEL_NAME)
processor = CLIPProcessor.from_pretrained(PROCESSOR_NAME)


class VectorRequest(BaseModel):
    text: str


@app.post("/get_vector")
async def get_vector(request: VectorRequest):
    """
    Endpoint to generate vector embeddings for a given text input.
    - Accepts a JSON request with a 'text' field.
    - Returns a flattened vector representing the text.
    """
    try:
        # Preprocess the input text using the CLIP processor
        inputs = processor(text=[request.text],
                           return_tensors="pt", padding=True)
        # Generate text features using the CLIP model
        outputs = model.get_text_features(**inputs)
        # Convert the output tensor to a flattened list
        vector = outputs.detach().numpy().flatten().tolist()
        return {"vector": vector}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating vector: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Simple test to check if the model and processor are loaded
        test_inputs = processor(text=["health check"], return_tensors="pt", padding=True)
        test_output = model.get_text_features(**test_inputs)
        if test_output is not None:
            return {"status": "ok", "message": "CLIP service is running"}
        else:
            raise Exception("Model or processor not functional")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# Add this block to run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT_VECTOR, reload=True)
