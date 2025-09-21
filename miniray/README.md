# MiniRay - Local Ray Training Environment

A setup for running Ray clusters and jobs locally using minikube and Kuberay.

## 🎯 What This Provides

Four working Ray scenarios:
- **Single-Node RayCluster** - 1 head node, 2 CPUs, 2GB memory
- **Multi-Node RayCluster** - 1 head + 1 worker, 4 CPUs, 4GB memory  
- **Single-Node RayJob** - ML training job on single node
- **Multi-Node RayJob** - ML training job on multi-node cluster

## 🤖 Ray Jobs

Ray Jobs are the recommended way to run ML workloads on Ray clusters. They provide automatic cluster management, job lifecycle handling, and resource cleanup.

### Ray Job Types

#### 1. Single-Node RayJob
**File**: `ray-job-single.yaml`
- **Resources**: 1 head node, 2 CPUs, 2GB memory
- **Use Case**: Simple ML training tasks
- **Features**: Automatic cleanup, package installation

#### 2. Multi-Node RayJob  
**File**: `ray-job-multi.yaml`
- **Resources**: 1 head + 1 worker, 4 CPUs total, 4GB memory
- **Use Case**: Distributed ML training
- **Features**: Horizontal scaling, distributed processing

#### 3. Complete ML Workflow
**File**: `ray-job-workflow-complete.yaml`
- **Process**: Data processing → ML training
- **Features**: End-to-end pipeline, shared volumes

### Ray Job Features

- **Automatic Cleanup**: `shutdownAfterJobFinishes: true`
- **Job Timeout**: `activeDeadlineSeconds: 600` (10 minutes)
- **TTL Management**: `ttlSecondsAfterFinished: 60`
- **Package Installation**: Automatic pandas, scikit-learn, joblib
- **Volume Mounting**: ConfigMap for scripts, emptyDir for models
- **Resource Management**: CPU/memory limits and requests

### Quick Start
```bash
# Run complete ML workflow
kubectl apply -f ray-job-workflow-complete.yaml

# Run single-node ML training
kubectl create configmap ml-training-script --from-file=simple-ml-training.py -n ray-system
kubectl apply -f ray-job-single.yaml

# Run multi-node ML training  
kubectl apply -f ray-job-multi.yaml
```

## 📁 Project Structure

```
miniray/
├── ray-cluster-single.yaml    # Single-node RayCluster
├── ray-cluster-multi.yaml     # Multi-node RayCluster
├── ray-job-single.yaml        # Single-node RayJob
├── ray-job-multi.yaml         # Multi-node RayJob
├── ray-job-workflow-complete.yaml # Complete ML workflow RayJob
├── data-processing.py         # Data processing script
├── ml-training-workflow.py    # ML training script
├── simple-ml-training.py      # Simple ML training script
├── test-ray.py               # Ray functionality test
├── setup-minikube.sh         # Environment setup
├── access-dashboard.sh       # Ray dashboard access
├── cleanup.sh               # Resource cleanup
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   ./setup-minikube.sh
   ```

2. **Test Single-Node RayCluster**:
   ```bash
   kubectl apply -f ray-cluster-single.yaml
   kubectl wait --for=condition=Ready pod -l app=ray-head -n ray-system --timeout=300s
   kubectl cp test-ray.py ray-system/$(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}'):/tmp/test-ray.py
   kubectl exec -it $(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}') -n ray-system -- python /tmp/test-ray.py
   ```

3. **Test Multi-Node RayCluster**:
   ```bash
   kubectl delete raycluster ray-cluster-single -n ray-system
   kubectl apply -f ray-cluster-multi.yaml
   kubectl wait --for=condition=Ready pod -l app=ray-head -n ray-system --timeout=300s
   kubectl wait --for=condition=Ready pod -l app=ray-worker -n ray-system --timeout=300s
   kubectl cp test-ray.py ray-system/$(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}'):/tmp/test-ray.py
   kubectl exec -it $(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}') -n ray-system -- python /tmp/test-ray.py
   ```

4. **Test RayJobs**:
   ```bash
   # Create ConfigMap for ML training script
   kubectl create configmap ml-training-script --from-file=simple-ml-training.py -n ray-system
   
   # Run single-node RayJob
   kubectl apply -f ray-job-single.yaml
   kubectl get rayjobs -n ray-system -w
   
   # Run multi-node RayJob
   kubectl apply -f ray-job-multi.yaml
   kubectl get rayjobs -n ray-system -w
   
   # Run complete ML workflow
   kubectl create configmap workflow-scripts --from-file=data-processing.py --from-file=ml-training-workflow.py -n ray-system
   kubectl apply -f ray-job-workflow-complete.yaml
   kubectl get rayjobs -n ray-system -w
   ```

## 🔍 Monitoring & Troubleshooting

### Ray Job Status
```bash
# View all RayJobs
kubectl get rayjobs -n ray-system

# Watch RayJob status changes
kubectl get rayjobs -n ray-system -w

# Get detailed RayJob information
kubectl describe rayjob <rayjob-name> -n ray-system
```

### Ray Job Logs
```bash
# View RayJob submitter pod logs
kubectl logs -l job-name=<rayjob-name> -n ray-system

# View Ray cluster head pod logs
kubectl logs -l app=ray-head -n ray-system

# Follow logs in real-time
kubectl logs -l job-name=<rayjob-name> -n ray-system -f
```

### Ray Cluster Status
```bash
# View Ray clusters
kubectl get rayclusters -n ray-system

# View all pods
kubectl get pods -n ray-system

# Access Ray dashboard
./access-dashboard.sh
```

### Common Issues

**RayJob Stuck in Pending**:
```bash
kubectl describe rayjob <rayjob-name> -n ray-system
kubectl get events -n ray-system --sort-by='.lastTimestamp'
```

**RayJob Failed**:
```bash
kubectl logs -l job-name=<rayjob-name> -n ray-system
kubectl describe pod <submitter-pod-name> -n ray-system
```

**Resource Issues**:
```bash
kubectl top pods -n ray-system
kubectl describe nodes
```

## 🧹 Cleanup

```bash
./cleanup.sh  # Clean up everything
```

## ⚙️ Ray Job Configuration

### Key Configuration Options

```yaml
spec:
  entrypoint: "python /workspace/script.py"  # Command to execute
  shutdownAfterJobFinishes: true             # Auto-cleanup cluster
  ttlSecondsAfterFinished: 60                # TTL after completion
  activeDeadlineSeconds: 600                 # Job timeout (10 min)
  rayClusterSpec:
    rayVersion: '2.49.0'                     # Ray version
    headGroupSpec:
      rayStartParams:
        num-cpus: '2'                        # CPU allocation
        memory: '2000000000'                 # Memory allocation (2GB)
      template:
        spec:
          containers:
          - name: ray-head
            resources:
              limits:
                cpu: "2"
                memory: 2Gi
              requests:
                cpu: "1"
                memory: 1Gi
```

### Customization Examples

**Increase Resources**:
```yaml
rayStartParams:
  num-cpus: '4'
  memory: '4000000000'  # 4GB
resources:
  limits:
    cpu: "4"
    memory: 4Gi
```

**Add Environment Variables**:
```yaml
env:
- name: MY_VAR
  value: "my_value"
- name: RAY_DISABLE_IMPORT_WARNING
  value: "1"
```

**Mount Additional Volumes**:
```yaml
volumeMounts:
- name: data-volume
  mountPath: /data
- name: model-cache
  mountPath: /models
volumes:
- name: data-volume
  persistentVolumeClaim:
    claimName: my-data-pvc
```

## 📊 Features

- **Ray 2.49.0** - Latest stable version
- **Resource Management** - Proper CPU/memory limits
- **Package Installation** - Automatic pandas, scikit-learn, joblib
- **Volume Mounting** - ConfigMap for scripts, emptyDir for models
- **Service Discovery** - Automatic head node discovery
- **Dashboard Access** - Ray dashboard on port 8265
- **Automatic Cleanup** - Self-managing job lifecycle
- **Timeout Management** - Configurable job timeouts

## 🎉 Success!

All scenarios are working and ready for production use:
- ✅ Single-node RayCluster
- ✅ Multi-node RayCluster  
- ✅ Single-node RayJob
- ✅ Multi-node RayJob
- ✅ Complete ML Workflow (Data Processing + Training)
