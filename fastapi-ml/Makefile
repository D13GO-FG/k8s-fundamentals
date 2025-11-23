IMAGE_NAME = fastapi-ml
TAG = v1
FULL_IMAGE_NAME = $(IMAGE_NAME):$(TAG)

.PHONY: build run-docker minikube-load deploy service-url clean test-api

build:
	docker build -t $(FULL_IMAGE_NAME) .

run-docker:
	docker run -p 8000:8000 $(FULL_IMAGE_NAME)

minikube-load:
	minikube image load $(FULL_IMAGE_NAME)

deploy:
	kubectl apply -f k8s/

service-url:
	minikube service fastapi-ml-service --url

clean:
	kubectl delete -f k8s/ || true
	docker stop $$(docker ps -q --filter ancestor=$(FULL_IMAGE_NAME)) || true

test-api:
	@echo "Starting port forwarding in background..."
	@kubectl port-forward service/fastapi-ml-service 8080:80 > /dev/null 2>&1 & \
	PID=$$!; \
	echo "Waiting for port forwarding..."; \
	sleep 5; \
	echo "Testing API..."; \
	curl -s -X POST http://localhost:8080/predict \
		-H "Content-Type: application/json" \
		-d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}' || true; \
	echo "\nStopping port forwarding..."; \
	kill $$PID

run-frontend:
	@echo "To run the frontend:"
	@echo "1. Run 'make service-url' to get the backend URL."
	@echo "2. Open 'frontend/index.html' in your browser."
	@echo "3. Paste the URL and start predicting!"
