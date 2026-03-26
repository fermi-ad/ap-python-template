FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
WORKDIR /install

COPY pyproject.toml ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Build a venv containing the editable project with CLI-only deps.
RUN uv venv .venv \
    && uv pip install -e .

FROM base AS runtime
WORKDIR /app

COPY --from=builder /install/.venv /opt/venv
COPY src /app/src
COPY scaffolds /app/scaffolds
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

ENV PATH="/opt/venv/bin:${PATH}"
ENV APP_CMD="python -m __template_module__.main"

ENTRYPOINT ["/usr/local/bin/start.sh"]

# Optional GUI runtime target. Builds a separate image that includes minimal Qt runtime libs
# and installs the `gui-pyqt` extra from pyproject.
FROM runtime AS runtime-gui

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      libgl1 \
      libxkbcommon0 \
      libxcb1 \
      libxcb-icccm4 \
      libxcb-image0 \
      libxcb-keysyms1 \
      libxcb-randr0 \
      libxcb-render0 \
      libxcb-render-util0 \
      libxcb-shape0 \
      libxcb-shm0 \
      libxcb-sync1 \
      libxcb-xfixes0 \
      libxcb-xinerama0 \
      libxcb-xkb1 \
      libxrender1 \
      libxext6 \
      libx11-6 \
      libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install the optional GUI extras into the existing venv.
RUN /opt/venv/bin/python -m pip install --no-cache-dir "PyQt6>=6.7"

ENV APP_CMD="python /app/scaffolds/pyqt/app.py"
