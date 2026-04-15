# AlmaLinux base for consistency with ACSys/Xpra images.

# ============================================================================
# Build arguments for version management
# Override at build time with: docker build --build-arg PYTHON_VERSION=3.13
# ============================================================================
ARG ALMALINUX_VERSION=9-base
ARG PYTHON_VERSION=3.12
ARG PYQT_VERSION="PyQt6~=6.10"

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
# Xpra-base stage: Adds Xpra server for web-based GUI access
# Base for xpra-runtime deployment with HTML5 client
# ============================================================================
FROM base AS xpra-base

USER root

# Enable EPEL and Xpra repositories, then install Xpra server
RUN dnf install -y \
      'dnf-command(config-manager)' \
 && dnf config-manager --set-enabled crb \
 && dnf install -y epel-release \
 && curl -L -o /etc/yum.repos.d/xpra.repo \
      https://raw.githubusercontent.com/Xpra-org/xpra/master/packaging/repos/almalinux/xpra.repo \
 && dnf makecache \
 && dnf install -y xpra \
 && dnf clean all

# Install curl for start.sh readiness checks and healthchecks
RUN dnf install -y --allowerasing curl && dnf clean all

# Install GUI runtime libraries (python already present from `base`)
RUN dnf install -y \
      libxcb \
      libxkbcommon \
      libxkbcommon-x11 \
      xcb-util \
      xcb-util-image \
      xcb-util-keysyms \
      xcb-util-renderutil \
      xcb-util-wm \
      xcb-util-cursor

# Install D-Bus and configure machine ID for Xpra
RUN dnf install -y dbus && dnf clean all
RUN rm -f /etc/machine-id && dbus-uuidgen --ensure=/etc/machine-id

# Create runtime directories for Xpra with proper permissions
# User already created in `base` stage
RUN mkdir -p /run/user/1000 /tmp/runtime-pyuser /tmp/.X11-unix /run/xpra \
 && chown -R pyuser:pygroup /run/user/1000 /tmp/runtime-pyuser /run/xpra \
 && chmod 700 /run/user/1000 /tmp/runtime-pyuser /run/xpra \
 && chmod 1777 /tmp/.X11-unix

# ============================================================================
# Xpra-builder stage: Build Python venv with PyQt for Xpra deployment
# ============================================================================
FROM xpra-base AS xpra-builder

# Re-declare args for use in this stage
ARG PYQT_VERSION

WORKDIR /install

# Install build tools needed for compiling Python packages
RUN dnf install -y gcc gcc-c++ make krb5-devel && dnf clean all

# Install uv (fast Python package manager) from astral.sh
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv venv /usr/local/.venv \
 && uv pip install --python /usr/local/.venv/bin/python --no-cache-dir . \
 && uv pip install --python /usr/local/.venv/bin/python --no-cache-dir "${PYQT_VERSION}"

# ============================================================================
# Xpra-runtime stage: Web-based GUI deployment via Xpra HTML5 client
# Exposes GUI on port 14500, accessible via web browser
# ============================================================================
FROM xpra-base AS xpra-runtime

# OCI labels for better metadata and discoverability
LABEL org.opencontainers.image.source="https://github.com/fermi-ad/ap-python-template"
LABEL org.opencontainers.image.description="Python application template (Xpra GUI runtime)"
LABEL org.opencontainers.image.title="ap-python-template-xpra"

COPY --from=xpra-builder /usr/local /usr/local
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

WORKDIR /app

# Switch to non-root user for runtime security
USER pyuser:pygroup

# Add venv to PATH for Python package access
ENV PATH="/usr/local/.venv/bin:${PATH}"

# Enable Xpra HTML5 client for web browser access
ENV XPRA_HTML=on
EXPOSE 14500

# Default to integrated package GUI in Xpra deployment via the main entrypoint
ENV APP_CMD="python -m ap_python_starter_kit.main --gui"

# Health check to verify Xpra server is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:14500/ || exit 1

# Start Xpra server with configured application
ENTRYPOINT ["/usr/local/bin/start.sh"]
