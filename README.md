# Kubernetes Troubleshooting Tool

Kubernetes Troubleshooting Tool is an open-source command-line tool designed to help Kubernetes administrators and DevOps engineers diagnose and resolve issues within their Kubernetes clusters. This tool performs a comprehensive analysis of your Kubernetes environment, detects critical issues, performance warnings, and security vulnerabilities, and offers actionable solutions to ensure your cluster runs smoothly.

## Features

- **Cluster Overview:** Provides a snapshot of your cluster's health, including node statuses, namespaces, and pod states.
- **Critical Issue Detection:** Identifies pods in `CrashLoopBackOff` or `Failed` states, nodes under `MemoryPressure` or `DiskPressure`, and deployments with unavailable replicas.
- **Performance Warnings:** Detects high latency in services and high resource usage across the cluster.
- **Security Scan:** Identifies security vulnerabilities in container images.
- **Network Diagnostics:** Ensures services have active endpoints and pods are correctly assigned IP addresses.

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Automatic Installation via Bash Script](#automatic-installation-via-bash-script)
  - [Manual Installation](#manual-installation)
- [Usage](#usage)
  - [Running the Tool](#running-the-tool)
  - [Example Output](#example-output)
- [Configuration](#configuration)
- [Important Notes](#important-notes)
- [Contribution](#contribution)
- [License](#license)

## Installation

### Prerequisites

Before installing the Kubernetes Troubleshooting Tool, ensure that your environment meets the following requirements:

- **Python 3.6+**: The tool is built using Python and requires Python 3.6 or higher.
- **Kubernetes API Access**: The tool requires access to the Kubernetes API via a valid `kubeconfig` file or by running within a Kubernetes cluster.

### Automatic Installation via Bash Script

You can easily install the Kubernetes Troubleshooting Tool using the provided `install.sh` script. This script handles everything from installing dependencies to setting up the tool for global use.

#### Step 1: Download and run the installation script

```bash
curl -O https://github.com/baybarse/kubernetes-analysis-troubleshhoting-tool/main/install.sh
chmod +x install.sh
./install.sh
```

This script will:
- Install Python 3 and pip3 if they are not already installed.
- Install the Kubernetes Python client (`kubernetes`).
- Download the `k8s_troubleshooter.py` script.
- Make the tool globally executable as `k8s_troubleshooter`.

### Manual Installation

If you prefer to manually install the tool, follow these steps:

#### Step 1: Clone the repository

```bash
git clone https://github.com/baybarse/kubernetes-analysis-troubleshhoting-tool.git
cd k8s-troubleshooter
```

#### Step 2: Install dependencies

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip -y
pip3 install kubernetes
```

#### Step 3: Make the script executable

```bash
chmod +x k8s_troubleshooter.py
sudo mv k8s_troubleshooter.py /usr/local/bin/k8s_troubleshooter
```

## Usage

Once installed, the Kubernetes Troubleshooting Tool is easy to use. Simply run the following command:

### Running the Tool

```bash
k8s_troubleshooter
```

The tool will perform a full cluster diagnostic and output the results directly to your terminal. The diagnostic includes:

- A cluster overview with Kubernetes version, node status, namespaces, and pod states.
- Identification of any critical issues, performance warnings, security vulnerabilities, and network diagnostics.
- Suggested actions to resolve detected issues.

### Example Output

Here’s an example of what the output looks like when you run the tool:

```plaintext
[K8S Troubleshooter] Starting full cluster diagnostic...

Cluster Overview:
- Kubernetes Version: v1.24.0
- Nodes: 3
  - node-1: Ready
  - node-2: Ready
  - node-3: Ready
- Namespaces: 5 (default, kube-system, kube-public, dev, prod)
- Total Pods: 120 (110 Running, 5 Pending, 5 Failed)

Critical Issues Detected:
1. **Namespace: kube-system**
   - Issue: Pod "kube-dns" in CrashLoopBackOff state.
   - Logs: 
     ```
     FATAL: Unable to start DNS server: address already in use.
     ```
   - Suggested Action:
     - Restart the DNS pod and ensure no conflicting services are using port 53.
     - Verify the DNS configuration in the kube-system namespace.

2. **Node: node-2**
   - Issue: Node is under MemoryPressure.
   - Suggested Action:
     - Investigate memory-intensive pods running on this node.
     - Consider redistributing workloads or adding more memory resources.

Performance Warnings:
1. **Namespace: dev**
   - Warning: Service "backend" experiencing high latency (average 150ms).
   - Suggested Action:
     - Analyze network policies and QoS settings.
     - Check for potential network congestion or misconfigured services.

Security Scan Results:
- Vulnerabilities Detected: 2 (1 High, 1 Medium)
  - High Severity: CVE-2024-5678 found in image "nginx:1.19.0" used by "web-app" deployment.
  - Suggested Action:
    - Update the "nginx" image to the latest version.
    - Review image security policies and ensure regular vulnerability scans.

Network Diagnostics:
- Warning: Service "my-service" in namespace "default" has no active endpoints.
  - Suggested Action:
    - Check if the associated pods are running and ready.
    - Verify the service selector matches the pod labels correctly.

Summary:
- 2 Critical issues detected.
- 1 Performance warnings.
- 2 Security vulnerabilities identified.

Suggested Next Steps:
1. Address the critical issues in the identified namespaces and nodes.
2. Investigate and optimize resource usage on high-demand nodes.
3. Review security vulnerabilities and update affected images.
4. Monitor and improve network performance and service configurations.

[K8S Troubleshooter] Full cluster diagnostic completed. Please review the above suggestions and take the necessary actions to ensure cluster stability and security.
```

## Configuration

### kubeconfig

To function correctly, the Kubernetes Troubleshooting Tool requires access to the Kubernetes API:

- **Locally**: The tool will use your default `kubeconfig` located at `~/.kube/config`.
- **In-Cluster**: If running within a Kubernetes cluster (e.g., as a pod), the tool will automatically use the in-cluster configuration provided by Kubernetes.

## Important Notes

- **Permissions**: Ensure the user or service account running the tool has sufficient permissions to access Kubernetes API resources like nodes, pods, services, deployments, etc.
- **Resource Consumption**: Running full diagnostics on large clusters may take time and consume resources; consider scheduling it during low-traffic periods.
- **Security Considerations**: Ensure that the tool is run in a secure environment, especially when dealing with sensitive data like kubeconfig files or API tokens.

## Contribution

We welcome contributions from the community! Whether it’s bug reports, feature requests, or pull requests, your input helps improve the project.

### How to Contribute

1. **Fork the Repository:** Create your own fork of the repository.
2. **Clone Your Fork:** Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/baybarse/kubernetes-analysis-troubleshhoting-tool.git
    ```
3. **Create a Branch:** Create a new branch for your changes.
    ```bash
    git checkout -b feature/your-feature-name
    ```
4. **Make Your Changes:** Implement your changes in your local branch.
5. **Commit Your Changes:** Commit your changes with a descriptive message.
    ```bash
    git add .
    git commit -m "Add feature: your feature name"
    ```
6. **Push Your Changes:** Push your changes to your forked repository.
    ```bash
    git push origin feature/your-feature-name
    ```
7. **Open a Pull Request:** Go to the original repository and open a pull request. Provide a detailed description of your changes and reference any related issues.

### Coding Style

Please follow the existing coding style and conventions in the project. This includes:

- Use descriptive variable and function names.
- Write comments to explain complex logic or decisions.
- Ensure your code is clean and well-organized.
