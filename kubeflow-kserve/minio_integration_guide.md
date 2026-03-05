# Minio Integration Guide for Kubeflow & KServe

This guide explains how to configure your Kubeflow pipeline and KServe InferenceService to work with the internal Minio instance.

## Prerequisites

- Kubeflow installed (includes Minio)
- KServe installed
- `kubectl` configured to access the cluster

## Step 1: Create S3 Secret

Kubeflow's Minio usually runs with default credentials `minio` / `minio123` (or `minio` / `minio12345678`).

Create a secret that will be used by the pipeline and KServe to access Minio.

```bash
kubectl create secret generic s3-secret \
  --from-literal=aws-access-key-id=minio \
  --from-literal=aws-secret-access-key=minio123 \
  --namespace kubeflow-user-example-com
```

*Note: Adjust the namespace if you are running the pipeline in a different namespace.*

## Step 2: Create Service Account for KServe

KServe needs a Service Account with the S3 secret attached to read the model for the inference service.

1. Create a file named `sa-s3.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: sa-s3-1
  namespace: kserve-test  # Configure this to the namespace where you deploy the InferenceService
  annotations:
    serving.kserve.io/s3-endpoint: minio-service.kubeflow.svc.cluster.local:9000
    serving.kserve.io/s3-use-https: "0"
    serving.kserve.io/s3-verifyssl: "0"
    serving.kserve.io/s3-region: "us-east-1"
secrets:
  - name: s3-secret
```

2. Apply it:

```bash
kubectl apply -f sa-s3.yaml
```

3. Ensure the secret exists in `kserve-test` namespace as well (if different from pipeline namespace):

```bash
kubectl create secret generic s3-secret \
  --from-literal=aws-access-key-id=minio \
  --from-literal=aws-secret-access-key=minio123 \
  --namespace kserve-test
```

4. Annotate the Service Account to use the S3 secret for storage access (serving.kserve.io/s3-secret):

```bash
kubectl patch serviceaccount sa-s3-1 \
  -n kserve-test \
  -p '{"secrets": [{"name": "s3-secret"}]}'
```

*Wait, KServe actually uses a specific annotation or a ServingRuntime with secrets. For simple cases, linking the secret to the Service Account used by the InferenceService is sufficient if using the default storage initializers.*

## Step 3: Run the Pipeline

Compile and run the pipeline (`pipeline.py`). It is configured to use:

- Endpoint: `http://minio-service.kubeflow.svc.cluster.local:9000`
- Bucket: `kubeflow-bucket-sjju`
- Key: `models/iris`

The model will be saved to `s3://kubeflow-bucket-sjju/models/iris`.

## Step 4: Deploy Inference Service

The `inferenceservice.yaml` is already configured to use `sa-s3-1` and point to the correct path.

```bash
kubectl apply -f inferenceservice.yaml -n kserve-test
```

## Step 5: Test

Follow the existing instructions in `README.md` to test the prediction endpoint.
