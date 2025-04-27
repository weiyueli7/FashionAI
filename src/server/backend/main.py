import httpx
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to limit the origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
APP_PORT_BACKEND = int(os.getenv("APP_PORT_BACKEND"))
APP_HOST = os.getenv("APP_HOST")
PINECONE_SERVICE_HOST = os.getenv("PINECONE_SERVICE_HOST", "localhost")
VECTOR_SERVICE_HOST = os.getenv("VECTOR_SERVICE_HOST", "localhost")

class SearchQuery(BaseModel):
    queryText: str
    top_k: int = 5

@app.post("/search")
async def search(query: SearchQuery):
    """
    Handles search requests. 
    Communicates with a vector service to retrieve query vectors and
    with a Pinecone service for retrieving the top-k search results.
    """
    query_text = query.queryText
    top_k = query.top_k

    async with httpx.AsyncClient() as client:
        try:
            # Call the vector service to convert text into a vector
            vector_service_url = f"http://{VECTOR_SERVICE_HOST}:8001/get_vector"
            response = await client.post(vector_service_url, json={"text": query_text}, timeout=10)
            response.raise_for_status()

            # Parse the vector from the response
            query_vector = response.json().get("vector")
            if not query_vector:
                raise ValueError("No vector returned from vector service.")

            # Call the Pinecone service for retrieving search results
            pinecone_service_url = f"http://{PINECONE_SERVICE_HOST}:8002/search"
            pinecone_response = await client.post(
                pinecone_service_url,
                json={"vector": query_vector, "top_k": top_k},
                timeout=10
            )
            pinecone_response.raise_for_status()

            # Parse the search results
            search_results = pinecone_response.json()
            items = [
                {
                    "item_name": result["metadata"].get("image_name", "Unknown Name"),
                    "item_brand": result["metadata"].get("brand", "Unknown Name"),
                    "item_gender": result["metadata"].get("gender", "Unknown Name"),
                    "item_type": result["metadata"].get("item_type", "Unknown Name"),
                    "item_sub_type": result["metadata"].get("item_sub_type", "Unknown Name"),
                    "item_url": result["metadata"].get("item_url", "Unknown URL"),
                    "image_url": result["metadata"].get("image_url", "Unknown URL"),
                    "item_caption": result["metadata"].get("caption", "No caption available"),
                    "rank": result.get("rank", "N/A"),
                    "score": result.get("score", "N/A"),
                }
                for result in search_results if "metadata" in result
            ]

            return {"description": f"Search results for '{query_text}'", "items": items}

        except httpx.RequestError as req_exc:
            raise HTTPException(
                status_code=500, detail=f"Request error: {req_exc}")

        except ValueError as val_exc:
            raise HTTPException(
                status_code=501, detail=f"Value error: {val_exc}")

        except KeyError as key_exc:
            raise HTTPException(
                status_code=502, detail=f"Key error: {key_exc}")

        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Unexpected error: {e}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "Backend service is running"}


# Add this block to run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT_BACKEND, reload=True)
