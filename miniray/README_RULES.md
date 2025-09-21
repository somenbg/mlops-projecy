# README_RULES.md - Agent Guidelines for Ray Project

This document provides comprehensive guidelines for AI agents to continue working on this Ray ML training project.

## 🎯 Project Overview

**Project Name**: MiniRay - Local Ray Training Environment  
**Purpose**: A clean, focused setup for running Ray clusters and jobs locally using minikube and Kuberay  
**Location**: `/Users/somenbag/projects/mlops-projecy/miniray/`

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
├── README.md                # Main documentation
└── README_RULES.md          # This file (agent guidelines)
```

## ✅ Working Scenarios

### 1. Ray Clusters
- **Single-Node RayCluster**: `ray-cluster-single.yaml` - 1 head node, 2 CPUs, 2GB memory
- **Multi-Node RayCluster**: `ray-cluster-multi.yaml` - 1 head + 1 worker, 4 CPUs, 4GB memory

### 2. Ray Jobs
- **Single-Node RayJob**: `ray-job-single.yaml` - ML training on single node
- **Multi-Node RayJob**: `ray-job-multi.yaml` - Distributed ML training
- **Complete ML Workflow**: `ray-job-workflow-complete.yaml` - Data processing + ML training

### 3. Test Scripts
- **Ray Functionality Test**: `test-ray.py` - Tests basic Ray cluster functionality
- **Simple ML Training**: `simple-ml-training.py` - Basic ML training example
- **Data Processing**: `data-processing.py` - Data generation, cleaning, feature engineering
- **ML Training Workflow**: `ml-training-workflow.py` - Advanced ML training with multiple models

## 🚀 Quick Commands

### Setup Environment
```bash
./setup-minikube.sh
```

### Test Ray Clusters
```bash
# Single-node
kubectl apply -f ray-cluster-single.yaml
kubectl wait --for=condition=Ready pod -l app=ray-head -n ray-system --timeout=300s
kubectl cp test-ray.py ray-system/$(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}'):/tmp/test-ray.py
kubectl exec -it $(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}') -n ray-system -- python /tmp/test-ray.py

# Multi-node
kubectl delete raycluster ray-cluster-single -n ray-system
kubectl apply -f ray-cluster-multi.yaml
kubectl wait --for=condition=Ready pod -l app=ray-head -n ray-system --timeout=300s
kubectl wait --for=condition=Ready pod -l app=ray-worker -n ray-system --timeout=300s
kubectl cp test-ray.py ray-system/$(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}'):/tmp/test-ray.py
kubectl exec -it $(kubectl get pods -l app=ray-head -n ray-system -o jsonpath='{.items[0].metadata.name}') -n ray-system -- python /tmp/test-ray.py
```

### Test Ray Jobs
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

### Monitor Resources
```bash
# View RayJobs
kubectl get rayjobs -n ray-system

# View Ray clusters
kubectl get rayclusters -n ray-system

# View pods
kubectl get pods -n ray-system

# Access Ray dashboard
./access-dashboard.sh
```

### Cleanup
```bash
./cleanup.sh
```

## 🔧 Technical Specifications

### Ray Version
- **Ray Version**: 2.49.0 (latest stable)
- **Python Version**: 3.11
- **Base Image**: `rayproject/ray:2.49.0-py311-cpu`

### Resource Allocations
- **Single-Node**: 2 CPUs, 2GB memory
- **Multi-Node**: 4 CPUs total (2 head + 2 worker), 4GB memory total
- **Minikube Memory**: 4GB (configured in setup script)

### Key Dependencies
- **pandas**: Data processing
- **scikit-learn**: ML algorithms
- **joblib**: Model serialization
- **numpy**: Numerical operations

### Ray Job Configuration
```yaml
spec:
  entrypoint: "python /workspace/script.py"
  shutdownAfterJobFinishes: true
  ttlSecondsAfterFinished: 60
  activeDeadlineSeconds: 600
```

## 🐛 Common Issues & Solutions

### 1. RayJob Stuck in Pending
```bash
kubectl describe rayjob <rayjob-name> -n ray-system
kubectl get events -n ray-system --sort-by='.lastTimestamp'
```

### 2. RayJob Failed
```bash
kubectl logs -l job-name=<rayjob-name> -n ray-system
kubectl describe pod <submitter-pod-name> -n ray-system
```

### 3. Resource Issues
```bash
kubectl top pods -n ray-system
kubectl describe nodes
```

### 4. Cleanup Stuck
```bash
# Force delete stuck resources
kubectl patch rayjob <name> -n ray-system -p '{"metadata":{"finalizers":null}}' --type=merge
kubectl patch raycluster <name> -n ray-system -p '{"metadata":{"finalizers":null}}' --type=merge
```

### 5. Minikube Issues
```bash
# Reset minikube
minikube delete
minikube start
```

## 📊 Performance Benchmarks

### ML Workflow Results
- **Data Processing**: 10,000 records with 16 engineered features
- **Model Accuracy**: 99.1% R² score (Random Forest)
- **Training Time**: ~1-2 minutes for complete workflow
- **Models Trained**: Random Forest, Gradient Boosting, Linear Regression

### Resource Usage
- **Memory Usage**: ~2GB for single-node, ~4GB for multi-node
- **CPU Usage**: 2-4 CPUs depending on configuration
- **Storage**: Minimal (emptyDir volumes)

## 🔄 Workflow Patterns

### 1. Single RayJob Workflow
- **File**: `ray-job-workflow-complete.yaml`
- **Process**: Data processing → ML training in single RayJob
- **Pros**: Simple, shared volumes, single point of management
- **Cons**: Less flexible, harder to scale individual steps

### 2. Chained RayJobs
- **Files**: Separate RayJobs for each step
- **Process**: Data processing RayJob → ML training RayJob
- **Pros**: Modular, scalable, better error isolation
- **Cons**: Requires external orchestration, complex data sharing

## 🛠️ Development Guidelines

### Adding New Ray Jobs
1. **Create YAML file** following existing patterns
2. **Use Ray 2.49.0** and Python 3.11
3. **Include proper resource limits** and requests
4. **Add timeout and cleanup settings**
5. **Test with both single and multi-node configurations**

### Adding New Scripts
1. **Follow existing naming conventions**
2. **Include proper error handling** and logging
3. **Add command-line arguments** for flexibility
4. **Update ConfigMaps** if needed
5. **Test with Ray Jobs**

### Modifying Existing Files
1. **Test changes thoroughly** before committing
2. **Update documentation** if needed
3. **Maintain backward compatibility** when possible
4. **Follow existing code patterns** and style

## 📝 File Update Rules

### README_RULES.md Updates
- **ONLY update when explicitly asked** by the user
- **This is a one-time activity** document
- **Do not modify** unless specifically requested
- **Use this file** as reference for project guidelines

### Other Files
- **README.md**: Update when adding new features or fixing issues
- **YAML files**: Update when modifying Ray configurations
- **Python scripts**: Update when adding new functionality
- **Shell scripts**: Update when changing setup/cleanup procedures

## 🎯 Success Criteria

### Ray Clusters
- ✅ Pods start successfully
- ✅ Ray dashboard accessible
- ✅ Test script runs without errors
- ✅ Resources properly allocated

### Ray Jobs
- ✅ Jobs complete successfully
- ✅ ML training produces results
- ✅ Automatic cleanup works
- ✅ Logs show proper execution

### Workflows
- ✅ Data processing completes
- ✅ ML training produces models
- ✅ Results saved properly
- ✅ End-to-end execution successful

## 🚨 Important Notes

1. **Always test changes** before considering them complete
2. **Use existing patterns** when adding new functionality
3. **Maintain clean project structure** - avoid unnecessary files
4. **Document changes** in README.md when significant
5. **Follow the established workflow** for setup → test → cleanup
6. **Respect the project's focus** on simplicity and functionality

## 📞 Troubleshooting Commands

### Check System Status
```bash
minikube status
kubectl get nodes
kubectl get namespaces
```

### Check Ray Resources
```bash
kubectl get rayclusters -n ray-system
kubectl get rayjobs -n ray-system
kubectl get pods -n ray-system
```

### Check Logs
```bash
kubectl logs -l app=ray-head -n ray-system
kubectl logs -l job-name=<rayjob-name> -n ray-system
```

### Force Cleanup
```bash
kubectl delete rayjobs --all -n ray-system
kubectl delete rayclusters --all -n ray-system
kubectl delete namespace ray-system
```

---

**Last Updated**: September 21, 2025  
**Project Status**: ✅ All scenarios working  
**Maintainer**: AI Assistant  
**Next Review**: When explicitly requested
