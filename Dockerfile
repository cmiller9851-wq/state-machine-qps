# ==========================================
# Phase 1: Build-dependencies compiler stage
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system utilities needed to compile C-level extensions (e.g., psycopg2 dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Compile libraries to isolated locally cached path
RUN pip install --user --no-cache-dir -r requirements.txt


# ==========================================
# Phase 2: Lightweight runtime environment
# ==========================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Ensure runtime dependencies for libpq/postgres are installed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled dependencies and application code from builder
COPY --from=builder /root/.local /usr/local
COPY . .

# Enforce secure non-root execution permissions (Fargate Best Practice)
RUN useradd -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Server starts with 4 processes to leverage container-allocated multi-core CPUs
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
