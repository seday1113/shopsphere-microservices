# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# Stage 2: Production Runtime
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed Python dependencies
COPY --from=builder /install /usr/local

# Copy application code
COPY main.py .

# Create non-root user
RUN useradd --create-home --uid 10001 appuser

USER appuser

EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
