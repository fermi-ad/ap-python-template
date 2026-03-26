# AlmaLinux base for consistency with ACSys/Xpra images.

FROM almalinux/9-base AS base

USER root

RUN dnf install -y krb5-libs shadow-utils python3.12 python3.12-devel git curl \
 && dnf clean all

# uv expects a few basics during sync/install
RUN dnf install -y ca-certificates \
 && dnf clean all

# Match OpenShift/K8s-friendly non-root runtime user.
RUN groupadd -g 1000 pygroup && useradd -m -u 1000 -g pygroup pyuser

FROM base AS builder
WORKDIR /install

RUN dnf install -y gcc gcc-c++ make krb5-devel \
 && dnf clean all

COPY pyproject.toml ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Build a venv in /usr/local for simple runtime PATH.
RUN uv venv /usr/local/.venv \
 && /usr/local/.venv/bin/python -m pip install --no-cache-dir -e .

FROM base AS runtime

COPY --from=builder /usr/local /usr/local
COPY src /app/src
COPY scaffolds /app/scaffolds
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

WORKDIR /app

USER pyuser:pygroup

ENV PATH="/usr/local/.venv/bin:${PATH}"
ENV APP_CMD="python -m __template_module__.main"

ENTRYPOINT ["/usr/local/bin/start.sh"]

# Optional GUI runtime target for host X server usage.
FROM runtime AS runtime-gui

# Install GUI runtime libs + PyQt.
RUN dnf install -y \
      libxcb \
      libxkbcommon \
      libxkbcommon-x11 \
      xcb-util \
      xcb-util-image \
      xcb-util-keysyms \
      xcb-util-renderutil \
      xcb-util-wm \
      xcb-util-cursor \
      mesa-libGL \
      fontconfig \
 && dnf clean all

RUN /usr/local/.venv/bin/python -m pip install --no-cache-dir "PyQt6>=6.7"

ENV APP_CMD="python /app/scaffolds/pyqt/app.py"

# ---------------------------
# Optional deployment target: AlmaLinux + Xpra HTML
# ---------------------------
FROM base AS xpra-base

USER root

RUN dnf install -y \
      'dnf-command(config-manager)' \
 && dnf config-manager --set-enabled crb \
 && dnf install -y epel-release \
 && curl -L -o /etc/yum.repos.d/xpra.repo \
      https://raw.githubusercontent.com/Xpra-org/xpra/master/packaging/repos/almalinux/xpra.repo \
 && dnf makecache \
 && dnf install -y xpra \
 && dnf clean all

# (python is already present from `base`)
RUN dnf install -y python3.12-tkinter
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

RUN dnf install -y dbus && dnf clean all
RUN rm -f /etc/machine-id && dbus-uuidgen --ensure=/etc/machine-id

# user already created in `base`
RUN mkdir -p /run/user/1000 /tmp/runtime-pyuser /tmp/.X11-unix /run/xpra \
 && chown -R pyuser:pygroup /run/user/1000 /tmp/runtime-pyuser /run/xpra \
 && chmod 700 /run/user/1000 /tmp/runtime-pyuser /run/xpra \
 && chmod 1777 /tmp/.X11-unix

FROM xpra-base AS xpra-builder
WORKDIR /install

RUN dnf install -y gcc gcc-c++ make krb5-devel && dnf clean all

COPY pyproject.toml ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Create venv in /usr/local to simplify runtime PATH.
RUN uv venv /usr/local/.venv \
 && /usr/local/.venv/bin/python -m pip install --no-cache-dir -e . \
 && /usr/local/.venv/bin/python -m pip install --no-cache-dir "PyQt6>=6.7"

FROM xpra-base AS xpra-runtime

COPY --from=xpra-builder /usr/local /usr/local
COPY src /app/src
COPY scaffolds /app/scaffolds
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

WORKDIR /app

USER pyuser:pygroup

ENV PATH="/usr/local/.venv/bin:${PATH}"
ENV XDG_RUNTIME_DIR=/tmp/runtime-pyuser

# Xpra HTML on :14500 with no auth.
ENV XPRA_HTML=on
ENV XPRA_AUTH=none
EXPOSE 14500

# Default to PyQt scaffold in Xpra image.
ENV APP_CMD="python /app/scaffolds/pyqt/app.py"

ENTRYPOINT ["/usr/local/bin/start.sh"]
