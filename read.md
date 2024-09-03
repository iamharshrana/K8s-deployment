# **Deployment Guide for Flask Application and MongoDB on Kind Kubernetes Cluster**

## **Introduction**

This guide provides detailed steps to deploy a Flask application and MongoDB using StatefulSet on a Kind (Kubernetes in Docker) cluster, including setting up Horizontal Pod Autoscaling (HPA) for the Flask application.

## **Prerequisites**

- **Docker:** Ensure Docker is installed and running.
- **Kind:** Install Kind (Kubernetes in Docker).
- **Kubectl:** Install `kubectl` to interact with your Kubernetes cluster.
- **Metrics Server:** Install the Kubernetes metrics server to enable HPA.

## **1. Set Up Kind Cluster**

1. **Create a Kind Cluster:**
   ```bash
   kind create cluster --name flask-mongo-cluster
   ```

2. **Verify Cluster Creation:**
   ```bash
   kubectl cluster-info --context kind-flask-mongo-cluster
   ```

## **2. Deploy MongoDB**

1. **Create MongoDB StatefulSet:**

   Save the following YAML content as `mongodb-statefulset.yaml`:

   ```yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: mongodb
   spec:
     serviceName: "mongodb"
     replicas: 1
     selector:
       matchLabels:
         app: mongodb
     template:
       metadata:
         labels:
           app: mongodb
       spec:
         containers:
         - name: mongodb
           image: mongo:latest
           ports:
           - containerPort: 27017
           volumeMounts:
           - name: mongo-persistent-storage
             mountPath: /data/db
           env:
           - name: MONGO_INITDB_ROOT_USERNAME
             value: root
           - name: MONGO_INITDB_ROOT_PASSWORD
             value: password
     volumeClaimTemplates:
     - metadata:
         name: mongo-persistent-storage
       spec:
         accessModes: [ "ReadWriteOnce" ]
         storageClassName: manual
         resources:
           requests:
             storage: 1Gi
   ```

2. **Create MongoDB Service:**

   Save the following YAML content as `mongodb-service.yaml`:

   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: mongodb
   spec:
     ports:
       - port: 27017
         targetPort: 27017
     selector:
       app: mongodb
     clusterIP: None  # Required for StatefulSet
   ```

3. **Apply MongoDB StatefulSet and Service:**

   ```bash
   kubectl apply -f mongodb-statefulset.yaml
   kubectl apply -f mongodb-service.yaml
   ```

## **3. Deploy Flask Application**

1. **Create Flask Deployment:**

   Save the following YAML content as `flask-app.yaml`:

   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: flask-app
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: flask-app
     template:
       metadata:
         labels:
           app: flask-app
       spec:
         containers:
         - name: flask-app
           image: flask-mongo-app:latest
           imagePullPolicy: IfNotPresent
           ports:
           - containerPort: 5000
           env:
           - name: MONGODB_URI
             value: "mongodb://mongodb:27017/"
           resources:
             requests:
               memory: "250Mi"
               cpu: "200m"
             limits:
               memory: "500Mi"
               cpu: "500m"
   ```

2. **Create Flask Service:**

   Save the following YAML content as `flask-app-service.yaml`:

   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: flask-app-service
   spec:
     type: ClusterIP
     selector:
       app: flask-app
     ports:
       - protocol: TCP
         port: 80
         targetPort: 5000
   ```

3. **Apply Flask Deployment and Service:**

   ```bash
   kubectl apply -f flask-app.yaml
   kubectl apply -f flask-app-service.yaml
   ```

## **4. Configure Horizontal Pod Autoscaler (HPA)**

1. **Create HPA Configuration:**

   Save the following YAML content as `flask-app-hpa.yaml`:

   ```yaml
   apiVersion: autoscaling/v2beta2
   kind: HorizontalPodAutoscaler
   metadata:
     name: flask-app-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: flask-app
     minReplicas: 2
     maxReplicas: 5
     metrics:
       - type: Resource
         resource:
           name: cpu
           target:
             type: Utilization
             averageUtilization: 50
   ```

2. **Apply HPA Configuration:**

   ```bash
   kubectl apply -f flask-app-hpa.yaml
   ```

3. **Verify HPA:**

   ```bash
   kubectl get hpa
   ```

## **5. Verify Deployments**

1. **Check Pods Status:**

   ```bash
   kubectl get pods
   ```

2. **Check Services:**

   ```bash
   kubectl get services
   ```

   The Flask service will be of type `ClusterIP`, so it is accessible within the cluster. Use port-forwarding to access it from your local machine:

   ```bash
   kubectl port-forward service/flask-app-service 8080:80
   ```

   Access the Flask application at `http://localhost:8080` in your browser.

## **6. Cleanup**

To delete the Flask application, MongoDB resources, and Kind cluster:

1. **Delete Flask Deployment, Service, and HPA:**

   ```bash
   kubectl delete -f flask-app-service.yaml
   kubectl delete -f flask-app.yaml
   kubectl delete -f flask-app-hpa.yaml
   ```

2. **Delete MongoDB StatefulSet and Service:**

   ```bash
   kubectl delete -f mongodb-service.yaml
   kubectl delete -f mongodb-statefulset.yaml
   ```

3. **Delete Kind Cluster:**

   ```bash
   kind delete cluster --name flask-mongo-cluster
   ```

## **Conclusion**

You have successfully deployed both the Flask application and MongoDB on a Kind Kubernetes cluster, with Horizontal Pod Autoscaling configured for the Flask application. You can now test and interact with your applications.

---

Adjust the resource requests, limits, and HPA configurations as needed based on your application’s requirements.