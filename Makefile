IMAGE_NAME ?= __template_project_name__
IMAGE_NAME_GUI ?= $(IMAGE_NAME)-gui
CONTAINER_NAME ?= __template_project_name__

.PHONY: help build build-gui build-no-cache run run-gui shell shell-gui clean

help:
	@echo "Available targets:"
	@echo "  make build                                   Build CLI Docker image ($(IMAGE_NAME))"
	@echo "  make build-gui                               Build GUI Docker image ($(IMAGE_NAME_GUI))"
	@echo "  make build-no-cache                          Build CLI Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run [APP_CMD=...]                       Run CLI container (defaults to template CLI)"
	@echo "  make run-gui [APP_CMD=...]                   Run GUI container (defaults to PyQt scaffold)"
	@echo "  make shell                                   Open an interactive shell in CLI container"
	@echo "  make shell-gui                               Open an interactive shell in GUI container"
	@echo "  make clean                                   Remove Docker images ($(IMAGE_NAME), $(IMAGE_NAME_GUI))"

build:
	docker build --target runtime -t $(IMAGE_NAME) .

build-gui:
	docker build --target runtime-gui -t $(IMAGE_NAME_GUI) .

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

shell:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME)

shell-gui:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME_GUI)

clean:
	docker image rm -f $(IMAGE_NAME) $(IMAGE_NAME_GUI)
