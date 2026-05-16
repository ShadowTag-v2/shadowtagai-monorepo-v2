.PHONY: build test run clean

# Image name
IMAGE_NAME = shadowtag-app
PYTHON_VERSION = 3.11-slim

build:
	docker build --build-arg PYTHON_VERSION=$(PYTHON_VERSION) -t $(IMAGE_NAME) .

test:
	docker build --build-arg PYTHON_VERSION=$(PYTHON_VERSION) --target builder -t $(IMAGE_NAME)-test .
	docker run --rm $(IMAGE_NAME)-test pytest

run:
	docker run -p 8080:8080 $(IMAGE_NAME)

clean:
	docker rmi $(IMAGE_NAME) $(IMAGE_NAME)-test || true
