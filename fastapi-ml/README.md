# FastAPI ML Application

This project demonstrates a production-ready end-to-end Machine Learning workflow using FastAPI, Docker, and Kubernetes. It serves a Logistic Regression model trained on the Iris dataset and includes a simple HTML/JS frontend.

## Directory Structure

```
fastapi-ml/
├── backend/             # Python FastAPI Application
│   ├── main.py          # API Entrypoint
│   ├── model.py         # ML Model Logic
│   └── schemas.py       # Pydantic Models
├── frontend/            # HTML/CSS/JS Client
│   ├── index.html
│   ├── style.css
│   └── app.js
├── k8s/                 # Kubernetes Manifests
├── Dockerfile           # Multi-stage Docker build
├── Makefile             # Automation scripts
└── requirements.txt     # Python dependencies
```

## Architecture

The application consists of a FastAPI server running inside a Docker container, orchestrated by Kubernetes, and a static frontend.

```text
+------+      +----------------+      +-------------+      +----------+
| User |      | K8s Service    |      | FastAPI Pod |      | ML Model |
+--+---+      +-------+--------+      +------+------+      +-----+----+
   |                  |                      |                   |
   | POST /predict    |                      |                   |
   +----------------->|   Forward Request    |                   |
   |                  +--------------------->|                   |
   |                  |                      | predict(features) |
   |                  |                      +------------------>|
   |                  |                      |                   |
   |                  |                      | class, prob       |
   |                  |                      |<------------------+
   |                  |    JSON Response     |                   |
   |                  |<---------------------+                   |
   |  JSON Response   |                      |                   |
   |<-----------------+                      |                   |
   |                  |                      |                   |
```

## Development Workflow

```text
[Dev: Write Code] -> [Docker: Build Image] -> [Minikube: Load Image]
                                                      |
                                                      v
[Verify: Test Endpoints] <---------------- [Kubernetes: Apply Manifests]
```

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Health check for K8s probes |
| `POST` | `/predict` | Get model prediction |

## How to Run

### Prerequisites

- Docker
- Minikube
- `kubectl`

### Using Makefile (Recommended)

We have provided a `Makefile` to automate common tasks.

1. **Build the Docker Image:**

    ```bash
    make build
    ```

2. **Load Image into Minikube:**
    *Required because Minikube cannot see local Docker images by default.*

    ```bash
    make minikube-load
    ```

3. **Deploy to Kubernetes:**

    ```bash
    make deploy
    ```

4. **Run the Frontend:**

    First, get the backend URL:

    ```bash
    make service-url
    ```

    Then, open `frontend/index.html` in your browser, paste the URL, and click "Predict Species".

5. **Clean Up:**

    ```bash
    make clean
    ```
