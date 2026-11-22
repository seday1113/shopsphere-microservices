import os

import psycopg
from psycopg import errors
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="ShopSphere User Service",
    version="1.1.0"
)


class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(min_length=5)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


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


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "user-service"
    }


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (name, email)
                    VALUES (%s, %s)
                    RETURNING id, name, email
                    """,
                    (user.name, user.email),
                )
                return cur.fetchone()
    except errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/users", response_model=list[UserResponse])
def get_users():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, email FROM users ORDER BY id"
                )
                return cur.fetchall()
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, email
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="User not found"
                    )

                return row
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )
