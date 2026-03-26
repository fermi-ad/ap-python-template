IMAGE_NAME ?= ap-python-starter-kit
IMAGE_NAME_GUI ?= $(IMAGE_NAME)-gui
IMAGE_NAME_XPRA ?= $(IMAGE_NAME)-xpra

CONTAINER_NAME ?= ap-python-starter-kit

XPRA_PORT ?= 14500
XPRA_BIND_HOST ?= 0.0.0.0

.PHONY: help build build-gui build-xpra build-no-cache run run-gui run-xpra shell shell-gui shell-xpra clean

help:
	@echo "Available targets:"
	@echo "  make build                                   Build CLI Docker image ($(IMAGE_NAME))"
	@echo "  make build-gui                               Build GUI Docker image ($(IMAGE_NAME_GUI))"
	@echo "  make build-xpra                              Build Xpra (HTML) Docker image ($(IMAGE_NAME_XPRA))"
	@echo "  make build-no-cache                          Build CLI Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run [APP_CMD=...]                       Run CLI container (defaults to template CLI)"
	@echo "  make run-gui [APP_CMD=...]                   Run GUI container (defaults to PyQt scaffold)"
	@echo "  make run-xpra [XPRA_PORT=14500] [APP_CMD=...] Run Xpra HTML container (defaults to PyQt scaffold)"
	@echo "  make shell                                   Open an interactive shell in CLI container"
	@echo "  make shell-gui                               Open an interactive shell in GUI container"
	@echo "  make shell-xpra                              Open an interactive shell in Xpra container"
	@echo "  make clean                                   Remove Docker images ($(IMAGE_NAME), $(IMAGE_NAME_GUI), $(IMAGE_NAME_XPRA))"

build:
	docker build --target runtime -t $(IMAGE_NAME) .

build-gui:
	docker build --target runtime-gui -t $(IMAGE_NAME_GUI) .

build-xpra:
	docker build --target xpra-runtime -t $(IMAGE_NAME_XPRA) .

build-no-cache:
	docker build --no-cache --target runtime -t $(IMAGE_NAME) .

run:
	@docker run --rm --name $(CONTAINER_NAME) \
		$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
		$(IMAGE_NAME)

run-gui:
	@docker run --rm --name $(CONTAINER_NAME)-gui \
		-e DISPLAY="$(DISPLAY)" \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
		$(IMAGE_NAME_GUI)

run-xpra:
	@docker run --rm --name $(CONTAINER_NAME)-xpra \
		-p $(XPRA_PORT):14500 \
		-e XPRA_BIND_HOST="$(XPRA_BIND_HOST)" \
		$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
		$(IMAGE_NAME_XPRA)
	@echo "Xpra HTML is served at: http://localhost:$(XPRA_PORT)/"

shell:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME)

shell-gui:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME_GUI)

shell-xpra:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME_XPRA)

clean:
	docker image rm -f $(IMAGE_NAME) $(IMAGE_NAME_GUI) $(IMAGE_NAME_XPRA)
