# Nginx Server Deployment

This directory contains the Kubernetes manifest files for deploying an Nginx server.

## How to run

To deploy the Nginx server on your Kubernetes cluster, follow these steps:

1.  **Apply the Deployment:**
    ```bash
    kubectl apply -f nginx-server/nginx-deployment.yaml
    ```

2.  **Apply the Service:**
    ```bash
    kubectl apply -f nginx-server/nginx-service.yaml
    ```

3.  **Verify the Deployment:**
    You can check the status of your deployment and pods using:
    ```bash
    kubectl get deployments
    kubectl get pods
    kubectl get services
    ```

4.  **Access Nginx:**
    Depending on your Kubernetes environment and service type, you can access the Nginx server. If using `NodePort` or `LoadBalancer`, you can find the external IP or port using `kubectl get services`.

## Accessing with NodePort on Minikube

When running on Minikube, especially on macOS or Windows, you might need to take extra steps to access a `NodePort` service.

1.  **Set Service Type to NodePort:**
    Ensure your service YAML file (e.g., `nginx-server/nginx-service.yaml`) has the `spec.type` set to `NodePort`:
    ```yaml
    spec:
      type: NodePort
      ports:
        - port: 80
          targetPort: 80
          # The nodePort field is optional, Kubernetes will assign one if not specified.
    ```

2.  **Get Minikube IP and Service Port:**
    You can get the IP of your Minikube cluster and the assigned `NodePort` for your service:
    ```bash
    minikube ip
    kubectl get services
    ```

3.  **Create a Tunnel (if direct access fails):**
    On some systems (like macOS with the Docker driver), you may not be able to directly access `http://<minikube-ip>:<node-port>`. In this case, use the `minikube service` command to create a tunnel:
    ```bash
    minikube service nginx-service
    ```
    This command will open the service in your default browser or provide a URL you can use.
