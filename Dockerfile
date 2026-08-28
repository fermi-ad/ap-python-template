# AlmaLinux base for consistency with ACSys/Xpra images.

# ============================================================================
# Build arguments for version management
# Override at build time with: docker build --build-arg PYTHON_VERSION=3.13
# ============================================================================
ARG ALMALINUX_VERSION=9-base
ARG PYTHON_VERSION=3.12

# ============================================================================
# Base stage: Minimal runtime dependencies
# Shared by all deployment variants (CLI, GUI, Xpra)
# ============================================================================
FROM almalinux/${ALMALINUX_VERSION} AS base

# Re-declare args for use in this stage
ARG PYTHON_VERSION

USER root

# Install system dependencies and create non-root user
# Combined into single layer to reduce image size
RUN dnf install -y \
      krb5-libs \
      krb5-workstation \
      shadow-utils \
      python${PYTHON_VERSION} \
      python${PYTHON_VERSION}-devel \
      git \
      ca-certificates \
 && dnf clean all \
 && groupadd -g 1000 pygroup \
 && useradd -m -u 1000 -g pygroup pyuser

COPY --chmod=644 .kerberos/krb5.conf /etc/krb5.conf

# ============================================================================
# Builder stage: Compile dependencies and build Python venv
# ============================================================================
FROM base AS builder
WORKDIR /install

# Install build tools needed for compiling Python packages
RUN dnf install -y gcc gcc-c++ make krb5-devel \
 && dnf clean all

# Install uv (fast Python package manager) from astral.sh
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv venv /usr/local/.venv \
 && uv pip install --python /usr/local/.venv/bin/python --no-cache-dir .

# ============================================================================
# Runtime stage: Minimal CLI deployment target
# Runs the template package entrypoint
# ============================================================================
FROM base AS runtime

# OCI labels for better metadata and discoverability
LABEL org.opencontainers.image.source="https://github.com/fermi-ad/ap-python-template"
LABEL org.opencontainers.image.description="Python application template (CLI runtime)"
LABEL org.opencontainers.image.title="ap-python-template-cli"

COPY --from=builder /usr/local /usr/local

WORKDIR /app

USER pyuser:pygroup

ENV PATH="/usr/local/.venv/bin:${PATH}"
ENV APP_CMD="python -m ap_python_starter_kit.main"

# Default (CLI) container just runs the app command.
ENTRYPOINT ["/bin/bash", "-lc", "python -m ap_python_starter_kit.main"]

# ============================================================================
# Xpra-builder stage: Build Python venv with PyQt for Xpra deployment
# ============================================================================
FROM adregistry.fnal.gov/dev-containers/ap-python-xpra-base AS xpra-builder

WORKDIR /install

COPY pyproject.toml README.md ./
COPY src ./src

ENV PATH="/root/.local/bin:${PATH}"

# Install build tools needed for compiling Python packages
# Install uv (fast Python package manager) from astral.sh
RUN dnf install -y gcc gcc-c++ make krb5-devel \
 && dnf clean all \
 && curl -LsSf https://astral.sh/uv/install.sh | sh \
 && uv venv /usr/local/.venv \
 && uv pip install --python /usr/local/.venv/bin/python --no-cache-dir .

# ============================================================================
# Xpra-runtime stage: Web-based GUI deployment via Xpra HTML5 client
# Exposes GUI on port 14500, accessible via web browser
# ============================================================================
FROM adregistry.fnal.gov/dev-containers/ap-python-xpra-base AS xpra-runtime

# OCI labels for better metadata and discoverability
LABEL org.opencontainers.image.source="https://github.com/fermi-ad/ap-python-template"
LABEL org.opencontainers.image.description="Python application template (Xpra GUI runtime)"
LABEL org.opencontainers.image.title="ap-python-template-xpra"

# Copy built venv from xpra-builder stage
COPY --from=xpra-builder /usr/local /usr/local

# Copy Xpra startup script with execute permissions
COPY --chmod=755 docker/start.sh /usr/local/bin/start.sh

# Run from user's home dir so Xpra's file upload/download dialog opens to the 
# same dir as the app's generated files 
WORKDIR /home/pyuser

# Switch to non-root user for runtime security
USER pyuser:pygroup

# Add venv to PATH for Python package access
ENV PATH="/usr/local/.venv/bin:${PATH}"

# Enable Xpra HTML5 client for web browser access
ENV XPRA_HTML=on XCURSOR_SIZE=24

EXPOSE 14500

# Health check to verify Xpra server is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:14500/ || exit 1

# Start Xpra server with configured application
ENTRYPOINT ["/usr/local/bin/start.sh"]
