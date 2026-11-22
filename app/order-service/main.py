import os
from decimal import Decimal

import httpx
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="ShopSphere Order Service", version="1.1.0")

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL", "http://product-service:8000"
)


class OrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


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


def serialize_order(row):
    return {
        "order_id": row["order_id"],
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "quantity": row["quantity"],
        "unit_price": float(row["unit_price"]),
        "total_amount": float(row["total_amount"]),
        "status": row["status"],
        "created_at": row["created_at"].isoformat(),
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "order-service"}


@app.post("/orders", status_code=201)
async def create_order(request: OrderRequest):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{PRODUCT_SERVICE_URL}/products/{request.product_id}"
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(
            status_code=502, detail="Product Service returned an error"
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503, detail="Product Service unavailable"
        )

    product = response.json()

    if request.quantity > product["stock"]:
        raise HTTPException(
            status_code=400, detail="Insufficient product stock"
        )

    unit_price = Decimal(str(product["price"]))
    total_amount = unit_price * request.quantity

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO orders
                        (product_id, product_name, quantity,
                         unit_price, total_amount, status)
                    VALUES (%s, %s, %s, %s, %s, 'CREATED')
                    RETURNING order_id, product_id, product_name,
                              quantity, unit_price, total_amount,
                              status, created_at
                    """,
                    (
                        request.product_id,
                        product["name"],
                        request.quantity,
                        unit_price,
                        total_amount,
                    ),
                )
                return serialize_order(cur.fetchone())
    except psycopg.Error:
        raise HTTPException(
            status_code=503, detail="Database unavailable"
        )


@app.get("/orders")
def get_orders():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT order_id, product_id, product_name,
                           quantity, unit_price, total_amount,
                           status, created_at
                    FROM orders
                    ORDER BY order_id
                    """
                )
                return [serialize_order(row) for row in cur.fetchall()]
    except psycopg.Error:
        raise HTTPException(
            status_code=503, detail="Database unavailable"
        )


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT order_id, product_id, product_name,
                           quantity, unit_price, total_amount,
                           status, created_at
                    FROM orders
                    WHERE order_id = %s
                    """,
                    (order_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=404, detail="Order not found"
                    )
                return serialize_order(row)
    except psycopg.Error:
        raise HTTPException(
            status_code=503, detail="Database unavailable"
        )
