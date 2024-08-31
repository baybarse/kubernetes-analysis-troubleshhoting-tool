#!/bin/bash

# Kubernetes Troubleshooting Tool Installation Script

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update and install Python3 and pip3
echo "Updating package lists..."
sudo apt-get update -y

echo "Installing Python3 and pip3..."
sudo apt-get install -y python3 python3-pip

# Check if Python and pip are installed
if ! command_exists python3 || ! command_exists pip3; then
    echo "Python3 or pip3 could not be installed. Please install them manually."
    exit 1
fi

# Install Kubernetes Python Client
echo "Installing Kubernetes Python client..."
pip3 install kubernetes pyyaml

# Check if Kubernetes client was installed
if ! python3 -c "import kubernetes" >/dev/null 2>&1; then
    echo "Kubernetes client could not be installed. Please install it manually."
    exit 1
fi

# Download the k8s_troubleshooter.py script and thresholds.yaml
echo "Downloading the Kubernetes Troubleshooting Tool..."
wget -q https://github.com/baybarse/kubernetes-analysis-troubleshhoting-tool/main/k8s_troubleshooter.py -O k8s_troubleshooter.py
wget -q https://github.com/baybarse/kubernetes-analysis-troubleshhoting-tool/main/thresholds.yaml -O thresholds.yaml

# Ensure the script is executable
chmod +x k8s_troubleshooter.py

# Move script to /usr/local/bin to make it globally executable
sudo mv k8s_troubleshooter.py /usr/local/bin/k8s_troubleshooter

echo "Installation complete. You can now use the Kubernetes Troubleshooting Tool by running 'k8s_troubleshooter'."