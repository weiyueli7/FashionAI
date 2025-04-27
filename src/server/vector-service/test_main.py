import pytest
from fastapi.testclient import TestClient
from main import app
import main
import torch

client = TestClient(app)


class MockModel:
    def get_text_features(self, **kwargs):
        return torch.tensor([[0.1, 0.2, 0.3]])


class MockProcessor:
    def __call__(self, text, return_tensors, padding):
        return {"input_ids": torch.tensor([[0]])}


@pytest.fixture(autouse=True)
def mock_clip_model(monkeypatch):
    monkeypatch.setattr(main, "model", MockModel())
    monkeypatch.setattr(main, "processor", MockProcessor())


def test_mock_setup():
    assert isinstance(main.model, MockModel)
    assert isinstance(main.processor, MockProcessor)


def test_get_vector_success():
    """
    Test that the /get_vector endpoint returns a valid vector response for valid input.
    """
    response = client.post("/get_vector", json={"text": "Test input"})
    assert response.status_code == 200
    data = response.json()
    assert "vector" in data
    assert isinstance(data["vector"], list)
    assert all(isinstance(x, float) for x in data["vector"])


def test_get_vector_empty_text():
    """
    Test that the /get_vector endpoint handles empty text input gracefully.
    """
    response = client.post("/get_vector", json={"text": ""})
    # Should still process the input, might return empty or similar.
    assert response.status_code == 200


def test_get_vector_invalid_payload():
    """
    Test that the /get_vector endpoint returns 422 for invalid payload.
    """
    response = client.post("/get_vector", json={"invalid_key": "Test input"})
    assert response.status_code == 422  # Unprocessable Entity


def test_get_vector_internal_error():
    """
    Test that the /get_vector endpoint handles internal errors gracefully.
    """

    def mock_error_function(*args, **kwargs):
        raise Exception("Mock error")

    main.model.get_text_features = mock_error_function

    response = client.post("/get_vector", json={"text": "Test input"})
    assert response.status_code == 500
    data = response.json()
    assert data["detail"].startswith("Error generating vector:")
