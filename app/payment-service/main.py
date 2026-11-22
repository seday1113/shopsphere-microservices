import os
from decimal import Decimal

import httpx
import psycopg
from psycopg import errors
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="ShopSphere Payment Service",
    version="1.1.0"
)

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL", "http://order-service:8000"
)


class PaymentRequest(BaseModel):
    order_id: int = Field(gt=0)


def get_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "shopsphere"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=5,
        row_factory=dict_row,
    )


def serialize_payment(row):
    return {
        "payment_id": row["payment_id"],
        "order_id": row["order_id"],
        "amount": float(row["amount"]),
        "currency": row["currency"],
        "status": row["status"],
        "payment_method": row["payment_method"],
        "processed_at": row["processed_at"].isoformat(),
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "payment-service"
    }


@app.post("/payments", status_code=201)
async def create_payment(request: PaymentRequest):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{ORDER_SERVICE_URL}/orders/{request.order_id}"
            )
            response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        raise HTTPException(
            status_code=502,
            detail="Order Service returned an error"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Order Service unavailable"
        )

    order = response.json()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO payments
                        (order_id, amount, currency,
                         status, payment_method)
                    VALUES (%s, %s, 'USD', 'SUCCESS', 'MOCK')
                    RETURNING payment_id, order_id, amount,
                              currency, status, payment_method,
                              processed_at
                    """,
                    (
                        request.order_id,
                        Decimal(str(order["total_amount"])),
                    ),
                )
                return serialize_payment(cur.fetchone())

    except errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Payment already processed for this order"
        )
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/payments")
def get_payments():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT payment_id, order_id, amount,
                           currency, status, payment_method,
                           processed_at
                    FROM payments
                    ORDER BY payment_id
                    """
                )
                return [
                    serialize_payment(row)
                    for row in cur.fetchall()
                ]
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/payments/{payment_id}")
def get_payment(payment_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT payment_id, order_id, amount,
                           currency, status, payment_method,
                           processed_at
                    FROM payments
                    WHERE payment_id = %s
                    """,
                    (payment_id,),
                )
                row = cur.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Payment not found"
                    )

                return serialize_payment(row)

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )
