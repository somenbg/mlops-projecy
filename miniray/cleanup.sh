#!/bin/bash

# Cleanup script for minikube and Ray cluster
# This script removes all resources created for the ML training environment

set -e

echo "🧹 Cleaning up ML training environment..."

# Delete RayJobs
echo "🗑️  Deleting RayJobs..."
kubectl delete rayjob ray-job-single -n ray-system --ignore-not-found=true
kubectl delete rayjob ray-job-multi -n ray-system --ignore-not-found=true
kubectl delete rayjob ray-job-workflow-complete -n ray-system --ignore-not-found=true

# Delete Ray clusters
echo "🗑️  Deleting Ray clusters..."
kubectl delete raycluster ray-cluster-single -n ray-system --ignore-not-found=true
kubectl delete raycluster ray-cluster-multi -n ray-system --ignore-not-found=true

# Delete configmaps
echo "🗑️  Deleting configmaps..."
kubectl delete configmap ml-training-script -n ray-system --ignore-not-found=true
kubectl delete configmap workflow-scripts -n ray-system --ignore-not-found=true

# Uninstall Kuberay operator
echo "🗑️  Uninstalling Kuberay operator..."
helm uninstall kuberay-operator -n kuberay-system --ignore-not-found=true

# Delete namespaces
echo "🗑️  Deleting namespaces..."
kubectl delete namespace ray-system --ignore-not-found=true
kubectl delete namespace kuberay-system --ignore-not-found=true

# Stop minikube
echo "🛑 Stopping minikube..."
minikube stop

echo "✅ Cleanup completed successfully!"
echo ""
echo "💡 To completely remove minikube and all data:"
echo "   minikube delete"
