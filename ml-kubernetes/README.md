# ML on Kubernetes with KServe

This directory contains files to deploy and test a machine learning model on Kubernetes using KServe.

## Prerequisites

- A running Kubernetes cluster (e.g., Minikube).
- `kubectl` configured to connect to your cluster.
- KServe installed on your cluster.
- Istio installed on your cluster.
- A namespace `mlflow-kserve-test` created.

## Building the Docker Image

The `InferenceService` requires a Docker image containing the trained model.

1.  **Train a model:**
    First, you need to train a model and log it to MLflow. The `training.py` script can be used for this.
    Make sure you have an MLflow tracking server running. You can start one with:
    ```bash
    mlflow ui --port 5000
    ```
    Then run the training script:
    ```bash
    python ml-kubernetes/training.py
    ```

2.  **Get the Model URI:**
    After the training run is complete, go to the MLflow UI (usually at `http://127.0.0.1:5000`), find your run, and copy the model URI. It will look something like `models:/<model_name>/<version>`.

3.  **Build the Docker image:**
    Use the `mlflow models build-docker` command to build the image. Replace `<MODEL_URI>` with the URI you copied from the MLflow UI, and `<IMAGE_NAME>` with your Docker Hub username and image name.

    ```bash
    mlflow models build-docker -m <MODEL_URI> -n <IMAGE_NAME> --enable-mlserver
    ```
    For example:
    ```bash
    mlflow models build-docker -m models:/m-43392140bf9e42388adc05630f24731a -n ldiegoflores/mlflow-wine-classifier --enable-mlserver
    ```

4.  **Push the Docker image:**
    Push the image to a container registry (e.g., Docker Hub).

    ```bash
    docker push <IMAGE_NAME>:latest
    ```
    For example:
    ```bash
    docker push ldiegoflores/mlflow-wine-classifier:latest
    ```

5.  **Update the manifest:**
    Make sure the `image` field in `ml-kubernetes/ml-wine-clf.yaml` points to the image you just pushed.

## Deployment

1.  **Deploy the InferenceService:**
    Apply the `ml-wine-clf.yaml` manifest to deploy the model.

    ```bash
    kubectl apply -f ml-kubernetes/ml-wine-clf.yaml
    ```

    This will create an `InferenceService` named `mlflow-wine-classifier` in the `mlflow-kserve-test` namespace.

## Testing the Service

To test the deployed model, you can use the provided `Makefile`.

1.  **Run the prediction:**
    Execute the following command from the root of the project:

    ```bash
    make -C ml-kubernetes predict
    ```

    This command will:
    1.  Create a temporary tunnel to the service using `minikube service`.
    2.  Get the service hostname.
    3.  Send a prediction request to the model using `curl` with the test data from `test-input.json`.

    You should see the output from `curl` including the prediction result from the model.
