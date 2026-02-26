# syntax=docker/dockerfile:1.7
# ==============================================================================
# Build Stage - Using Node Alpine for minimal size
# ==============================================================================
FROM node:22.21.1-alpine3.21@sha256:af8023ec879993821f6d5b21382ed915622a1b0f1cc03dbeb6804afaf01f8885 AS builder

# Install pnpm with specific version from package.json and gzip for pre-compression
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable && \
  corepack prepare pnpm --activate

WORKDIR /app

# Copy package files for dependency installation (optimized layer caching)
COPY package.json pnpm-lock.yaml ./

# Install dependencies with cache mount for faster rebuilds
# Installs all dependencies (including devDependencies needed for build: typescript, vite, tailwindcss, etc.)
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
  pnpm install --frozen-lockfile

# Copy only necessary source files (exclude tests, docs, config files not needed for build)
COPY tsconfig.json tsconfig.node.json vite.config.ts tailwind.config.ts postcss.config.js ./
COPY index.html ./
COPY public ./public
COPY src ./src

# Build the application
RUN pnpm run build && \
  # Verify build output exists
  test -d dist && test -f dist/index.html && \
  # Remove bundle visualizer output (not needed in production, saves ~100KB compressed)
  rm -f dist/stats.html && \
  # Create a minimal health check endpoint (1 byte file for ultra-fast response)
  echo "OK" > dist/health && \
  # Pre-compress all static files with gzip (level 9 = maximum compression)
  find dist -type f \( \
  -name "*.html" -o \
  -name "*.css" -o \
  -name "*.js" -o \
  -name "*.json" -o \
  -name "*.xml" -o \
  -name "*.txt" -o \
  -name "*.svg" \
  \) -exec sh -c 'gzip -9 "{}"' \;

# ==============================================================================
# Production Stage - Using lipanski/docker-static-website for extreme minimal footprint (92.5 KB base)
# ==============================================================================
FROM lipanski/docker-static-website:latest AS production

# Add OCI labels for metadata
LABEL org.opencontainers.image.title="Vite React Template" \
  org.opencontainers.image.description="Production-ready Vite React application with extreme minimal footprint" \
  org.opencontainers.image.version="0.4.0" \
  org.opencontainers.image.licenses="MIT OR Apache-2.0" \
  org.opencontainers.image.base.name="lipanski/docker-static-website:latest"

# Copy built assets from builder stage
# lipanski/docker-static-website serves from /home/static
COPY --from=builder /app/dist /home/static

# Expose port (BusyBox httpd uses port 3000 by default)
EXPOSE 3000

# The base image already has CMD set to run BusyBox httpd
# It automatically serves .gz files when Accept-Encoding: gzip is present
# No additional configuration needed - inherited from base image