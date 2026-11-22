
import importlib.util
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient


service_file = Path(__file__).resolve().parents[1] / "main.py"

spec = importlib.util.spec_from_file_location(
    "order_service_main", service_file
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "order-service",
    }


def test_invalid_product_id():
    response = client.post(
        "/orders",
        json={"product_id": 0, "quantity": 2},
    )

    assert response.status_code == 422


def test_invalid_quantity():
    response = client.post(
        "/orders",
        json={"product_id": 1, "quantity": 0},
    )

    assert response.status_code == 422


def test_order_serialization():
    created_at = datetime(
        2026, 11, 22, 10, 0, tzinfo=timezone.utc
    )

    row = {
        "order_id": 101,
        "product_id": 1,
        "product_name": "Laptop",
        "quantity": 2,
        "unit_price": Decimal("999.99"),
        "total_amount": Decimal("1999.98"),
        "status": "CREATED",
        "created_at": created_at,
    }

    result = module.serialize_order(row)

    assert result == {
        "order_id": 101,
        "product_id": 1,
        "product_name": "Laptop",
        "quantity": 2,
        "unit_price": 999.99,
        "total_amount": 1999.98,
        "status": "CREATED",
        "created_at": created_at.isoformat(),
    }
