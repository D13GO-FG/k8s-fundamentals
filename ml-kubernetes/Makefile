# Makefile for testing the KServe InferenceService

# --- Variables ---
# Get the service hostname for the Host header
SERVICE_HOSTNAME := $(shell kubectl get inferenceservice mlflow-wine-classifier -n mlflow-kserve-test -o jsonpath='{.status.url}' | cut -d "/" -f 3)
TEST_INPUT_FILE := ./test-input.json
MODEL_NAME := mlflow-model

# --- Test Target ---

## predict: Test the service using 'minikube service'
# This is often the most reliable method for local development as it creates a direct tunnel to the service.
predict:
	@echo "--- Testing with minikube service ---"
	@echo "Getting temporary service URL..."
	$(eval URL := $(shell minikube service mlflow-wine-classifier-predictor -n mlflow-kserve-test --url))
	@if [ -z "$(URL)" ]; then \
		echo "Error: Could not get service URL. Is minikube running and the service deployed?"; \
		exit 1; \
	fi
	@echo "Service URL: $(URL)"
	@echo "Service Hostname: $(SERVICE_HOSTNAME)"
	@echo "Sending prediction request..."
	@curl -v -H "Host: $(SERVICE_HOSTNAME)" \
		-H "Content-Type: application/json" \
		-d @$(TEST_INPUT_FILE) \
		"$(URL)/v2/models/$(MODEL_NAME)/infer"

.PHONY: predict

