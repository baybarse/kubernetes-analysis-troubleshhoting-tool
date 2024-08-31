# Kubernetes Troubleshooting Tool

Kubernetes Troubleshooting Tool is an open-source command-line tool designed to help Kubernetes administrators and DevOps engineers diagnose and resolve issues within their Kubernetes clusters. It provides a comprehensive cluster overview, detects critical issues, performance warnings, and security vulnerabilities, and offers actionable suggestions based on customizable thresholds.

## Features

- **Cluster Overview:** Provides a snapshot of your cluster's health, including node statuses, namespaces, and pod states.
- **Critical Issue Detection:** Identifies pods in `CrashLoopBackOff` or `Failed` states, nodes under `MemoryPressure` or `DiskPressure`, and deployments with unavailable replicas.
- **Performance Warnings:** Detects high resource usage and long pod scheduling times based on configurable thresholds.
- **Security Scan:** Identifies security vulnerabilities in container images.
- **Network Diagnostics:** Checks for service endpoint availability and pod connectivity.
- **Storage Checks:** Ensures PersistentVolumes are correctly bound and storage resources are available.
- **Pod Disruption Budget Checks:** Monitors PodDisruptionBudgets to ensure they meet the desired healthy pod count.

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Automatic Installation via Bash Script](#automatic-installation-via-bash-script)
  - [Manual Installation](#manual-installation)
- [Usage](#usage)
  - [Running the Tool](#running-the-tool)
  - [Example Output](#example-output)
- [Configuration](#configuration)
  - [Thresholds](#thresholds)
- [Important Notes](#important-notes)
- [Contribution](#contribution)
- [License](#license)

## Installation

### Prerequisites

Before installing the Kubernetes Troubleshooting Tool, ensure that your environment meets the following requirements:

- **Python 3.6+**: The tool is built using Python and requires Python 3.6 or higher.
- **Kubernetes API Access**: The tool requires access to the Kubernetes API via a valid `kubeconfig` file or by running within a Kubernetes cluster.

### Automatic Installation via Bash Script

You can easily install the Kubernetes Troubleshooting Tool using the provided `install.sh` script:

#### Step 1: Download and run the installation script

```bash
curl -O https://github.com/baybarse/kubernetes-analysis-troubleshhoting-tool/main/main/install.sh
chmod +x install.sh
./install.sh
```

This script will:
- Install Python 3 and pip3 if they are not already installed.
- Install the Kubernetes Python client and PyYAML.
- Download the `k8s_troubleshooter.py` script and `thresholds.yaml` configuration file.
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
pip3 install kubernetes pyyaml
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
     - Check for port conflicts and DNS configuration issues.

Performance Warnings:
1. **Node: node-1**
   - Warning: CPU usage is high (85.00%).
   - Suggested Action:
     - Consider redistributing workloads or scaling up resources.

Security Scan Results:
- Vulnerabilities Detected: 1 (High Severity)
  - High Severity: CVE-2024-5678 found in image "nginx:1.19.0" used by "web-app" deployment.
  - Suggested Action:
    - Update the "nginx" image to the latest secure version.
    - Review image security policies.

Network Diagnostics:
- Warning: Service "my-service" in namespace "default" has no active endpoints.
  - Suggested Action:
    - Check if the associated pods are running and ready.
    - Verify the service selector matches the pod labels correctly.

Summary:
- 1 Critical issue detected.
- 1 Performance warning.
- 1 Security vulnerability identified.

Suggested Next Steps:
1. Address the critical issues in the identified namespaces and nodes.
2. Investigate and optimize resource usage on high-demand nodes.
3. Review security vulnerabilities and update affected images.
```

## Configuration

### Thresholds

The tool uses a configuration file, `thresholds.yaml`, to define threshold values for generating warnings and suggestions. These thresholds can be customized to suit your specific environment.

#### Example `thresholds.yaml`:

```yaml
cpu_usage_threshold: 75  # CPU usage threshold in percentage
memory_usage_threshold: 80  # Memory usage threshold in percentage
latency_threshold_ms: 100  # Service latency threshold in milliseconds
pod_scheduling_delay_threshold: 300  # Pod scheduling delay threshold in seconds
disk_pressure_threshold: 90  # Disk usage threshold in percentage
```

### Customizing Thresholds

To customize the thresholds, simply edit the `thresholds.yaml` file in the project directory. For example, to increase the CPU usage threshold to 85%, change the `cpu_usage_threshold` value:

```yaml
cpu_usage_threshold: 85
```

## Important Notes

- **Permissions:** Ensure the user or service account running the tool has sufficient permissions to access Kubernetes API resources like nodes, pods, services, deployments, etc.
- **Resource Consumption:** Running full diagnostics on large clusters may take time and consume resources; consider scheduling it during low-traffic periods.
- **Security Considerations:** Ensure that the tool is run in a secure environment, especially when dealing with sensitive data like kubeconfig files or API tokens. Regularly update the tool and its dependencies to address any potential security vulnerabilities.

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
- Ensure your code is clean, well-organized, and properly tested.


