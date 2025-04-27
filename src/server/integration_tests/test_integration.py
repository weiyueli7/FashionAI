import pytest
import httpx
import numpy as np

# Base URLs for services
BASE_BACKEND_URL = "http://localhost:8000"
BASE_VECTOR_URL = "http://localhost:8001"
BASE_PINECONE_URL = "http://localhost:8002"


@pytest.mark.asyncio
async def test_vector_service():
    """Test the Vector Service independently."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_VECTOR_URL}/get_vector", json={"text": "Find a casual shirt"})
        assert response.status_code == 200
        data = response.json()
        
        # Assert the vector exists and is 512-dimensional
        assert "vector" in data
        assert isinstance(data["vector"], list)
        assert len(data["vector"]) == 512


@pytest.mark.asyncio
async def test_pinecone_service():
    """Test the Pinecone Service independently with a 512-dimensional vector."""
    # Create a 512-dimensional mock vector
    dummy_vector = np.random.rand(512).tolist()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_PINECONE_URL}/search", json={"vector": dummy_vector, "top_k": 3})
        assert response.status_code == 200
        data = response.json()
        
        # Assert the response is a list of results
        assert isinstance(data, list)
        if data:  # If there are results, validate structure
            first_result = data[0]
            assert "rank" in first_result
            assert "score" in first_result
            assert "metadata" in first_result


@pytest.mark.asyncio
async def test_backend_integration():
    """Test the backend's integration with the Vector and Pinecone services."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_BACKEND_URL}/search",
            json={"queryText": "Find a casual shirt", "top_k": 3}
        )
        assert response.status_code == 200
        data = response.json()

        # Assert the backend provides the expected structure
        assert "description" in data
        assert "items" in data
        assert isinstance(data["items"], list)

        if data["items"]:  # If there are items, validate structure
            first_item = data["items"][0]
            assert "item_name" in first_item
            assert "item_brand" in first_item
            assert "item_url" in first_item
            assert "image_url" in first_item
            assert "score" in first_item
