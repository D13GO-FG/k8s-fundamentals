# ML on Kubernetes with KServe

This directory contains files to deploy and test a machine learning model on Kubernetes using KServe.

## Prerequisites

- A running Kubernetes cluster (e.g., Minikube).
- `kubectl` configured to connect to your cluster.
- KServe installed on your cluster.
- Istio installed on your cluster.
- A namespace `mlflow-kserve-test` created.

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
