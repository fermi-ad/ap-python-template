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
RUN uv venv .venv \
    && uv pip install -e .

FROM base AS runtime
WORKDIR /app

COPY --from=builder /install/.venv /opt/venv
COPY src /app/src
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

ENV PATH="/opt/venv/bin:${PATH}"
ENV APP_CMD="python -m __template_module__.main"

ENTRYPOINT ["/usr/local/bin/start.sh"]
