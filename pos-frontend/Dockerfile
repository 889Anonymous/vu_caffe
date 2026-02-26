# syntax=docker/dockerfile:1.7
# ==============================================================================
# Build Stage
FROM node:22-bookworm-slim AS builder

# Install pnpm 
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files for dependency installation
COPY package.json pnpm-lock.yaml* package-lock.json* ./

# Install dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm install; \
    else pnpm install; fi

# Copy source code and config
COPY . .

# Build the application
RUN npm run build && \
  # Verify build output exists (Standard check)
  [ -d dist ] && [ -f dist/index.html ] && \
  # Create health check
  echo "OK" > dist/health && \
  # Pre-compress all static files with gzip
  find dist -type f \( \
  -name "*.html" -o \
  -name "*.css" -o \
  -name "*.js" -o \
  -name "*.json" -o \
  -name "*.svg" \
  \) -exec gzip -9 -k "{}" \;

# ==============================================================================
# Production Stage - Using lipanski/docker-static-website for extreme minimal footprint
# ==============================================================================
FROM lipanski/docker-static-website:latest AS production

LABEL image.description="Original Vue POS Frontend with extreme minimal footprint"

# Copy built assets from builder stage
COPY --from=builder /app/dist /home/static

# Expose port (BusyBox httpd uses port 3000 by default)
EXPOSE 3000
