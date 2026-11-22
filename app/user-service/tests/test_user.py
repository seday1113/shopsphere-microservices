
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


service_file = Path(__file__).resolve().parents[1] / "main.py"

spec = importlib.util.spec_from_file_location(
    "user_service_main", service_file
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "user-service",
    }


def test_invalid_user_payload():
    response = client.post(
        "/users",
        json={"name": "A", "email": "a"},
    )

    assert response.status_code == 422
