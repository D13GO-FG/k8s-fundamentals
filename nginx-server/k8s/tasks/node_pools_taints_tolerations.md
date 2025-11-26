# Node Pools, Taints, and Tolerations Task

## Goal

Understand how to use Node Pools (simulated in Minikube), Taints, and Tolerations to control Pod scheduling. We will deploy the Nginx application to a specific custom node that is tainted to reject ordinary pods.

## Concepts

* **Node Pools**: Groups of nodes with similar configuration. In Minikube, we simulate this by adding extra nodes and labeling them.
* **Taints**: Applied to a Node to repel Pods. Only Pods with a matching Toleration can be scheduled on a tainted Node.
* **Tolerations**: Applied to a Pod to allow it to schedule on a matching tainted Node.

## 1. Setup Multi-Node Cluster with CNI

**Crucial Step**: For multi-node clusters in Minikube to function correctly (specifically pod-to-pod networking across nodes), you **must** use a CNI (Container Network Interface) plugin. Without it, pods on worker nodes may fail to start or communicate.

We will recreate the cluster with 2 nodes and the Calico CNI.

```bash
# Delete the existing cluster (if any)
minikube delete

# Start a new cluster with 2 nodes and Calico CNI
minikube start --nodes 2 --cni calico
```

Verify the nodes:

```bash
kubectl get nodes
```

You should see `minikube` and `minikube-m02` in a `Ready` state (it might take a moment for the CNI to initialize).

## 2. Simulate a Custom Node Pool (Labeling)

We will treat `minikube-m02` as our "custom" node pool.

```bash
# Label the new node
kubectl label node minikube-m02 node-pool=custom-nginx
```

## 3. Apply Taint to the Node

Now, we taint the node so that no pods can be scheduled on it unless they tolerate the taint.

```bash
# Taint the node
kubectl taint nodes minikube-m02 dedicated=custom-nginx:NoSchedule
```

* **Key**: `dedicated`
* **Value**: `custom-nginx`
* **Effect**: `NoSchedule` (Pods won't be scheduled unless they tolerate this)

## 4. Modify the Deployment

We need to update the `nginx-deployment.yaml` (or create a new one) to include:

1. **Node Affinity/Selector**: To ensure it *prefers* or *requires* this node.
2. **Toleration**: To ensure it is *allowed* on this tainted node.

Create a new file `nginx-deployment-custom.yaml` or update the existing one with the following `spec.template.spec` additions:

```yaml
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        # ... (other container settings)
      # Add these sections:
      nodeSelector:
        node-pool: custom-nginx
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "custom-nginx"
        effect: "NoSchedule"
```

## 5. Deploy and Verify

Apply the new configuration:

```bash
kubectl apply -f ../nginx-deployment-custom.yaml
```

Check where the pods are running:

```bash
kubectl get pods -o wide
```

You should see the Nginx pod running on `minikube-m02`.

## 6. Access the Application

You do **not** need a new Service YAML. The existing `nginx-service.yaml` selects pods based on the label `app: nginx`. Since our custom deployment uses this same label, the service will automatically route traffic to our new pod, even though it's on a different node.

1. **Apply the Service** (if not already done):

    ```bash
    kubectl apply -f ../nginx-service.yaml
    ```

2. **Access via Minikube**:
    Minikube provides a helper command to open the service in your default browser or display the URL. This handles the routing to the correct node automatically.

    ```bash
    minikube service nginx-service
    ```

    Or to just get the URL:

    ```bash
    minikube service nginx-service --url
    ```

## 7. Cleanup

To clean up the resources created in this task, run the following commands:

  ```bash
  kubectl delete -f ../nginx-deployment-custom.yaml
  kubectl delete -f ../nginx-service.yaml
  minikube node delete minikube-m02
  ```
