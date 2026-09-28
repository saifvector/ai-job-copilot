# ==============================================================================
# AI Job Copilot - Backend Production Dockerfile
# Base: Python 3.12 Slim Linux
# ==============================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies for C extensions (e.g. psycopg2 / asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime stage
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime PostgreSQL client library
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root unprivileged app user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed python wheels from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy source code
COPY . .

# Set proper permissions
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
