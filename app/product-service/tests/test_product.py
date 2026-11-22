
import importlib.util
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient


service_file = Path(__file__).resolve().parents[1] / "main.py"

spec = importlib.util.spec_from_file_location(
    "product_service_main", service_file
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "product-service",
    }


def test_product_serialization():
    row = {
        "id": 1,
        "name": "Laptop",
        "price": Decimal("999.99"),
        "stock": 10,
    }

    result = module.serialize_product(row)

    assert result == {
        "id": 1,
        "name": "Laptop",
        "price": 999.99,
        "stock": 10,
    }


def test_invalid_product_id():
    response = client.get("/products/invalid")

    assert response.status_code == 422
