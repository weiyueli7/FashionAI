from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import numpy as np
import os
from pinecone import Pinecone
from google.cloud import secretmanager

# Load environment variables
APP_HOST = os.getenv("APP_HOST")
APP_PORT_PINECONE = int(os.getenv("APP_PORT_PINECONE"))
PINECONE_SECRET_NAME = os.getenv("PINECONE_SECRET_NAME")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

app = FastAPI()

def get_index():
    """
    Dynamically initialize and return the Pinecone index.
    This function retrieves the Pinecone API key from Google Secret Manager
    and uses it to connect to the Pinecone service.
    """
    # Get secret
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": PINECONE_SECRET_NAME})
    secret_value = response.payload.data.decode("UTF-8")

    # Initialize Pinecone client and return the index
    pc = Pinecone(api_key=secret_value)
    return pc.Index(PINECONE_INDEX_NAME)


class SearchRequest(BaseModel):
    vector: list
    top_k: int


@app.post("/search")
async def search(request: SearchRequest, index=Depends(get_index)):
    """
    Perform a vector-based search in the Pinecone index.
    """
    try:
        results = index.query(
            vector=np.array(request.vector, dtype=np.float32).tolist(),
            top_k=request.top_k,
            include_values=True,
            include_metadata=True,
        )
        matches = results.get("matches", [])

        # Format the search results
        formatted_matches = [
            {
                "rank": idx + 1,
                "id": match["id"],
                "score": match["score"],
                "metadata": match.get("metadata", {}),
            }
            for idx, match in enumerate(matches)
        ]
        return formatted_matches

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Pinecone: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Simple test to check if the index is accessible
        index = get_index()
        index.describe_index_stats()  # Call a lightweight Pinecone API
        return {"status": "ok", "message": "Pinecone service is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT_PINECONE, reload=True)
