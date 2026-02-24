# Builder stage using uv for ultra-fast builds
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim@sha256:6b8ac7bb76766ffe9f6cc20f56789755d539e8d0e605d8983131227c5c8b87a1 AS builder
ENV UV_LINK_MODE=copy

WORKDIR /build

# Mount files for dependency installation without full copy
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev --no-editable

# Runtime stage using Google Distroless for security and minimal size
FROM gcr.io/distroless/python3-debian12:nonroot AS runtime

LABEL maintainer="Modern POS Team"
LABEL image.description="Secure, minimal POS app using UV and Distroless"

WORKDIR /app

# Copy virtual environment and source from builder
COPY --from=builder --chown=nonroot:nonroot /build/.venv/ /app/.venv/
COPY --chown=nonroot:nonroot src/ ./src/

# Config environments for low resource (Oracle Free Tier)
ENV PATH="/app/.venv/bin/:$PATH" \
    PYTHONPATH="/app/src/" \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    WORKERS=1 \
    LOGGING_LEVEL=INFO

EXPOSE 8000

# Entry point for FastAPI
ENTRYPOINT ["python", "-m", "uvicorn", "src.pos.main:app", "--host", "0.0.0.0", "--port", "8000"]
