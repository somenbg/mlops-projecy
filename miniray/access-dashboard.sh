#!/bin/bash

# Access Ray Dashboard
# This script provides easy access to the Ray dashboard

set -e

echo "🌐 Accessing Ray Dashboard..."

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Please run ./setup-minikube.sh first"
    exit 1
fi

# Check if Ray cluster or RayJob exists
RAY_CLUSTER=$(kubectl get rayclusters -n ray-system -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
RAY_JOB=$(kubectl get rayjobs -n ray-system -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$RAY_CLUSTER" ] && [ -z "$RAY_JOB" ]; then
    echo "❌ No Ray cluster or RayJob found. Please run ./deploy-ray-cluster.sh or ./submit-rayjob.sh first"
    exit 1
fi

# Get the head pod name
HEAD_POD=$(kubectl get pods -n ray-system -l app=ray-head -o jsonpath='{.items[0].metadata.name}')

if [ -z "$HEAD_POD" ]; then
    echo "❌ Ray head pod not found"
    exit 1
fi

echo "📊 Ray cluster status:"
kubectl get pods -n ray-system

echo ""
echo "🚀 Starting port-forward to Ray dashboard..."
echo "📱 Dashboard will be available at: http://localhost:8265"
echo ""
echo "💡 Tips:"
echo "- If the dashboard doesn't load immediately, wait a few minutes for Ray to fully initialize"
echo "- Press Ctrl+C to stop the port-forward"
echo ""

# Start port-forward
kubectl port-forward pod/$HEAD_POD -n ray-system 8265:8265
