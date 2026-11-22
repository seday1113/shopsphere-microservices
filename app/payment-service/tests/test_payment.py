
import importlib.util
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient


service_file = Path(__file__).resolve().parents[1] / "main.py"

spec = importlib.util.spec_from_file_location(
    "payment_service_main", service_file
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "payment-service",
    }


def test_invalid_order_id():
    response = client.post(
        "/payments",
        json={"order_id": 0},
    )

    assert response.status_code == 422


def test_missing_order_id():
    response = client.post(
        "/payments",
        json={},
    )

    assert response.status_code == 422


def test_payment_serialization():
    processed_at = datetime(
        2026, 11, 22, 10, 0, tzinfo=timezone.utc
    )

    row = {
        "payment_id": 101,
        "order_id": 201,
        "amount": Decimal("1999.98"),
        "currency": "USD",
        "status": "SUCCESS",
        "payment_method": "MOCK",
        "processed_at": processed_at,
    }

    result = module.serialize_payment(row)

    assert result == {
        "payment_id": 101,
        "order_id": 201,
        "amount": 1999.98,
        "currency": "USD",
        "status": "SUCCESS",
        "payment_method": "MOCK",
        "processed_at": processed_at.isoformat(),
    }
