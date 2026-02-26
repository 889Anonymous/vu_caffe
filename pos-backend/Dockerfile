# syntax=docker/dockerfile:1
# ==============================================================================
# Build Stage - Using UV for ultra-fast dependency management
# ==============================================================================
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim@sha256:6b8ac7bb76766ffe9f6cc20f56789755d539e8d0e605d8983131227c5c8b87a1 AS builder

ENV UV_LINK_MODE=copy
WORKDIR /build

# Copy project files for dependency installation
COPY pyproject.toml ./
# If uv.lock doesn't exist, uv will create it. 
# We don't use --frozen here because we are generating it inside the container for the first time.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev --no-editable

# Copy source code
COPY src/ ./src/

# Collect necessary shared libraries (libc, libm, libz, libssl, libcrypto, etc.)
RUN mkdir -p /lib/multi-arch && \
    ldd /usr/local/bin/python3.13 | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v '{}' /lib/multi-arch/ && \
    find /usr/local/lib/python3.13/lib-dynload -name "*.so" -exec ldd {} \; | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v -n '{}' /lib/multi-arch/

# ==============================================================================
# Production Stage - Using Distroless for security and minimal size
# ==============================================================================
FROM gcr.io/distroless/cc-debian12:nonroot AS runtime

LABEL image.description="Secure, minimal Python POS Backend using UV and Distroless"

WORKDIR /app

# Copy Python binary, libraries and virtual environment from builder stage
COPY --from=builder /lib/multi-arch/ /lib/
COPY --from=builder /usr/local/lib/libpython3.13.so.1.0 /usr/local/lib/libpython3.13.so.1.0
COPY --from=builder /usr/local/lib/python3.13/ /usr/local/lib/python3.13/
COPY --from=builder /usr/local/bin/python3.13 /usr/local/bin/python

COPY --from=builder /build/.venv/ /app/.venv/
COPY --from=builder /build/src/ /app/src/

# SQLite DB file should be persistent, we'll map it via volume in docker-compose
ENV PATH="/app/.venv/bin/:$PATH" \
    PYTHONPATH="/app/src/" \
    LD_LIBRARY_PATH="/lib" \
    LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    WORKERS=2

EXPOSE 8000

# Run the application
ENTRYPOINT ["python", "-m", "uvicorn", "pos.main:app", "--host", "0.0.0.0", "--port", "8000"]
