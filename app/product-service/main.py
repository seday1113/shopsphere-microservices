import os
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="ShopSphere Product Service",
    version="1.1.0"
)


class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int


def get_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "shopsphere"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=5,
        row_factory=dict_row
    )


def serialize_product(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "price": float(row["price"]),
        "stock": row["stock"]
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "product-service"}


@app.get("/products", response_model=list[Product])
def get_products():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, price, stock FROM products ORDER BY id"
                )
                return [serialize_product(row) for row in cur.fetchall()]
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, price, stock FROM products WHERE id = %s",
                    (product_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Product not found")
                return serialize_product(row)
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database unavailable")
