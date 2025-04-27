import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app, get_index

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    # Mock the SecretManagerServiceClient
    monkeypatch.setattr(
        "main.secretmanager.SecretManagerServiceClient", lambda: MockSecretManagerClient()
    )

    # Mock the Pinecone Index
    mock_index = MagicMock()
    mock_index.query.return_value = {
        "matches": [
            {"id": "item1", "score": 0.95, "metadata": {"label": "label1"}},
            {"id": "item2", "score": 0.89, "metadata": {"label": "label2"}},
        ]
    }
    monkeypatch.setattr("main.get_index", lambda: mock_index)
    

class MockSecretManagerClient:
    def access_secret_version(self, request):
        if request["name"] == "projects/1087474666309/secrets/pincone/versions/latest":
            return MockSecretManagerResponse()
        raise ValueError("Invalid secret name")


class MockSecretManagerResponse:
    class Payload:
        def __init__(self):
            self.data = b"mocked-api-key"

    def __init__(self):
        self.payload = self.Payload()


def test_search_success(mock_external_services):
    payload = {
        "vector": [0.1] * 512,
        "top_k": 2
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("Response JSON:", data)
    assert len(data) == 2
    assert data[0]["id"] == "item1"
    assert data[1]["id"] == "item2"


def test_search_internal_error(monkeypatch):
    def mock_failing_index():
        mock_index = MagicMock()
        mock_index.query.side_effect = Exception("Mocked internal error")
        return mock_index

    monkeypatch.setattr("main.get_index", mock_failing_index)

    payload = {
        "vector": [0.1] * 512,
        "top_k": 2
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 500
    assert "Error querying Pinecone: Mocked internal error" in response.json()["detail"]
