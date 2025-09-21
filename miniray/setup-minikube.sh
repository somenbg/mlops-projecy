#!/bin/bash

# Setup script for minikube with Kuberay for local ML training
# This script sets up a local Kubernetes cluster with Ray for distributed ML training

set -e

echo "🚀 Setting up minikube with Kuberay for local ML training..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed. Please install minikube first:"
    echo "   https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first:"
    echo "   https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed. Please install helm first:"
    echo "   https://helm.sh/docs/intro/install/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start minikube with sufficient resources for ML workloads
echo "🔧 Starting minikube with ML-optimized configuration..."
minikube start \
    --memory=4096 \
    --cpus=4 \
    --disk-size=20g \
    --driver=docker \
    --kubernetes-version=v1.28.0

# Wait for cluster to be ready before enabling addons
echo "⏳ Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Wait for API server to be responsive
echo "⏳ Waiting for API server to be responsive..."
for i in {1..30}; do
    if kubectl get nodes &> /dev/null; then
        echo "✅ API server is responsive"
        break
    fi
    echo "⏳ Waiting for API server... ($i/30)"
    sleep 10
done

# Wait a bit more for all components to be fully initialized
echo "⏳ Waiting for all components to initialize..."
sleep 30

# Enable required addons
echo "🔌 Enabling required minikube addons..."
minikube addons enable metrics-server || echo "⚠️  metrics-server addon failed, continuing..."
minikube addons enable dashboard || echo "⚠️  dashboard addon failed, continuing..."

# Add Kuberay Helm repository
echo "📦 Adding Kuberay Helm repository..."
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# Install Kuberay operator
echo "🚀 Installing Kuberay operator..."
helm install kuberay-operator kuberay/kuberay-operator --namespace kuberay-system --create-namespace

# Wait for operator to be ready
echo "⏳ Waiting for Kuberay operator to be ready..."
kubectl wait --for=condition=Available deployment/kuberay-operator -n kuberay-system --timeout=300s

echo "✅ Minikube setup with Kuberay completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy Ray cluster: ./deploy-ray-cluster.sh"
echo "2. Submit ML training job: ./submit-training-job.sh"
echo "3. Monitor cluster: kubectl get rayclusters -n ray-system"
echo ""
echo "🔍 Useful commands:"
echo "- View cluster status: kubectl get nodes"
echo "- View Ray clusters: kubectl get rayclusters -n ray-system"
echo "- Access Ray dashboard: kubectl port-forward service/ray-dashboard -n ray-system 8265:8265"
echo "- Stop minikube: minikube stop"
echo "- Delete minikube: minikube delete"
