IMAGE_NAME ?= ap-python-starter-kit
IMAGE_NAME_GUI ?= $(IMAGE_NAME)-gui

CONTAINER_NAME ?= ap-python-starter-kit

XPRA_PORT ?= 14500
XPRA_BIND_HOST ?= 0.0.0.0

.PHONY: help build build-gui build-no-cache docs-serve format lint rename-project run run-gui run-uv shell shell-gui test uv-sync clean

help:
	@echo "Available targets:"
	@echo "  make build                                   Build CLI Docker image ($(IMAGE_NAME))"
	@echo "  make build-gui                               Build GUI via Xpra (HTML) Docker image ($(IMAGE_NAME_GUI))"
	@echo "  make build-no-cache                          Build CLI Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make docs-serve                              Serve documentation from ./docs at http://localhost:8000/"
	@echo "  make format                                  Format code using ruff"
	@echo "  make lint                                    Lint code using ruff"
	@echo "  make rename-project                          Rename project (update template names in files and src/ package, and rename Docker images in Makefile)"
	@echo "  make run [APP_CMD=...]                       Run CLI container (defaults to template CLI launcher)"
	@echo "  make run-gui [XPRA_PORT=14500] [APP_CMD=...] Run GUI + Xpra HTML container (integrated PyQt app)"
	@echo "  make run-uv [APP_CMD=...]                    Run project locally using uv (defaults to template CLI launcher)"
	@echo "  make shell                                   Open an interactive shell in CLI container"
	@echo "  make shell-gui                               Open an interactive shell in GUI + Xpra container"
	@echo "  make test                                    Run tests using pytest"
	@echo "  make uv-sync                                 Update project dependencies and lockfile using uv"
	@echo "  make clean                                   Remove Docker images ($(IMAGE_NAME), $(IMAGE_NAME_GUI))"

build:
	docker build --target runtime -t $(IMAGE_NAME) .

build-gui:
	docker build --target xpra-runtime -t $(IMAGE_NAME_GUI) .

build-no-cache:
	docker build --no-cache --target runtime -t $(IMAGE_NAME) .

docs-serve:
	python -m http.server 8000 --directory docs

format:
	uv run ruff format .

lint:
	uv run ruff check .

rename-project:
	python3 scripts/rename_project.py

run:
	@docker run --rm --name $(CONTAINER_NAME) \
		$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
		$(IMAGE_NAME)

run-gui:
	@docker run --rm --name $(CONTAINER_NAME)-xpra \
		-p $(XPRA_PORT):14500 \
		-e XPRA_BIND_HOST="$(XPRA_BIND_HOST)" \
		$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
		$(IMAGE_NAME_GUI)
	@echo "Xpra HTML is served at: http://localhost:$(XPRA_PORT)/"

run-uv:
	uv run $(APP_CMD)

shell:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME)

shell-gui:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME_GUI)

test:
	uv run pytest

uv-sync:
	uv sync

clean:
	docker image rm -f $(IMAGE_NAME) $(IMAGE_NAME_GUI)
