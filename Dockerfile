FROM python:3.12-slim

# Build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Metadata labels
LABEL org.opencontainers.image.title="Immich Google Photos Sync"
LABEL org.opencontainers.image.description="Synchronize Immich albums to Google Photos"
LABEL org.opencontainers.image.authors="Immich Google Sync Contributors"
LABEL org.opencontainers.image.vendor="Immich Google Sync"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/Unlink/immich-google-mirroring"
LABEL org.opencontainers.image.source="https://github.com/Unlink/immich-google-mirroring"
LABEL org.opencontainers.image.documentation="https://github.com/Unlink/immich-google-mirroring#readme"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.version="${VERSION}"

WORKDIR /app

# Install system dependencies and curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create data directory
RUN mkdir -p /data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
