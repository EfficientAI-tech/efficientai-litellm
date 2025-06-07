# Base image for building
ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/python:latest-dev

# Runtime image
ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/python:latest-dev

# Builder stage
FROM $LITELLM_BUILD_IMAGE AS builder

# Set the working directory to /app
WORKDIR /app

USER root

# Install build dependencies
RUN apk add --no-cache gcc python3-dev openssl openssl-dev

RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY pyproject.toml poetry.lock ./
COPY litellm/ litellm/
COPY README.md ./
COPY docker/ docker/

# Build Admin UI
RUN chmod +x docker/build_admin_ui.sh && ./docker/build_admin_ui.sh

# Install the package directly without building wheel
RUN pip install -e .

# ensure pyjwt is used, not jwt
RUN pip uninstall jwt -y || true
RUN pip uninstall PyJWT -y || true
RUN pip install PyJWT==2.9.0 --no-cache-dir

# Runtime stage
FROM $LITELLM_RUNTIME_IMAGE AS runtime

# Ensure runtime stage runs as root
USER root

# Install runtime dependencies
RUN apk add --no-cache openssl

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/lib/python3.13/site-packages/ /usr/lib/python3.13/site-packages/
COPY --from=builder /usr/bin/ /usr/bin/

# Copy the entire project
COPY . .
RUN ls -la /app

# Generate prisma client
RUN prisma generate || true
RUN chmod +x docker/entrypoint.sh
RUN chmod +x docker/prod_entrypoint.sh

EXPOSE 4000/tcp

ENTRYPOINT ["docker/prod_entrypoint.sh"]

# Append "--detailed_debug" to the end of CMD to view detailed debug logs 
CMD ["--port", "4000"]
