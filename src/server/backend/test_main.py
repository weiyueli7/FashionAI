import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app, SearchQuery

client = TestClient(app)


@pytest.fixture
def mock_vector_service():
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = lambda url, **kwargs: (
            AsyncMock(return_value=AsyncMock(
                status_code=200,
                json=AsyncMock(return_value={"vector": [0.1, 0.2, 0.3]}),
            ))
            if "get_vector" in url
            else None
        )
        yield mock_post


@pytest.fixture
def mock_pinecone_service():
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = lambda url, **kwargs: (
            AsyncMock(return_value=AsyncMock(
                status_code=200,
                json=AsyncMock(return_value=[
                    {
                        "metadata": {
                            "image_name": "Test Item",
                            "brand": "Test Brand",
                            "gender": "Unisex",
                            "item_type": "Shirt",
                            "item_sub_type": "Casual",
                            "item_url": "https://example.com/item",
                            "image_url": "https://example.com/image.jpg",
                            "caption": "A stylish shirt"
                        },
                        "rank": 1,
                        "score": 0.95
                    }
                ]),
            ))
            if "search" in url
            else None
        )
        yield mock_post


def test_search_success(mock_vector_service, mock_pinecone_service):
    """Test successful search endpoint with mocked services."""
    # Mock vector service response
    vector_response = {"vector": [0.1, 0.2, 0.3]}
    mock_vector_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=200, json=AsyncMock(return_value=vector_response)))]
    print(mock_vector_service.side_effect)
    # Mock Pinecone service response
    pinecone_response = [
        {
            "metadata": {
                "image_name": "Test Item",
                "brand": "Test Brand",
                "gender": "Unisex",
                "item_type": "Shirt",
                "item_sub_type": "Casual",
                "item_url": "https://example.com/item",
                "image_url": "https://example.com/image.jpg",
                "caption": "A stylish shirt"
            },
            "rank": 1,
            "score": 0.95
        }
    ]
    mock_pinecone_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=200, json=AsyncMock(return_value=pinecone_response)))]

    # Request payload
    query = {
        "queryText": "Find a casual shirt",
        "top_k": 3
    }

    # Make the request
    response = client.post("/search", json=query)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["item_name"] == "Test Item"
    assert data["items"][0]["item_brand"] == "Test Brand"
    assert data["items"][0]["item_url"] == "https://example.com/item"


def test_search_vector_service_error(mock_vector_service):
    """Test vector service failure."""
    mock_vector_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=500, text="Internal Server Error"))]

    query = {
        "queryText": "Find a casual shirt",
        "top_k": 3
    }

    response = client.post("/search", json=query)

    assert response.status_code == 500
    assert "Request error" in response.json()["detail"]


def test_search_no_vector(mock_vector_service):
    """Test vector service returning no vector."""
    vector_response = {"vector": None}
    mock_vector_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=200, json=AsyncMock(return_value=vector_response)))]

    query = {
        "queryText": "Find a casual shirt",
        "top_k": 3
    }

    response = client.post("/search", json=query)

    assert response.status_code == 501
    assert "No vector returned from vector service" in response.json()["detail"]


def test_search_pinecone_service_error(mock_vector_service, mock_pinecone_service):
    """Test Pinecone service failure."""
    vector_response = {"vector": [0.1, 0.2, 0.3]}
    mock_vector_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=200, json=AsyncMock(return_value=vector_response)))]

    mock_pinecone_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=500, text="Internal Server Error"))]

    query = {
        "queryText": "Find a casual shirt",
        "top_k": 3
    }

    response = client.post("/search", json=query)

    assert response.status_code == 500
    assert "Request error" in response.json()["detail"]


def test_search_invalid_payload():
    """Test invalid payload."""
    query = {
        "queryText": 123,  # Invalid type
        "top_k": "five"    # Invalid type
    }

    response = client.post("/search", json=query)

    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()


def test_search_empty_results(mock_vector_service, mock_pinecone_service):
    """Test empty results from Pinecone service."""
    vector_response = {"vector": [0.1, 0.2, 0.3]}
    mock_vector_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=200, json=AsyncMock(return_value=vector_response)))]

    mock_pinecone_service.side_effect = [AsyncMock(return_value=AsyncMock(
        status_code=200, json=AsyncMock(return_value=[])))]

    query = {
        "queryText": "Find a casual shirt",
        "top_k": 3
    }

    response = client.post("/search", json=query)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
