IMAGE_NAME ?= __template_project_name__
CONTAINER_NAME ?= __template_project_name__

.PHONY: help build build-no-cache run shell clean

help:
	@echo "Available targets:"
	@echo "  make build                        Build Docker image ($(IMAGE_NAME))"
	@echo "  make build-no-cache               Build Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run [APP_CMD=...]            Run container (CLI default)"
	@echo "  make shell                        Open an interactive shell in container"
	@echo "  make clean                        Remove Docker image ($(IMAGE_NAME))"

build:
	docker build -t $(IMAGE_NAME) .

build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME) .

run:
	@docker run --rm --name $(CONTAINER_NAME) \
		$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
		$(IMAGE_NAME)

shell:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME)

clean:
	docker image rm -f $(IMAGE_NAME)
