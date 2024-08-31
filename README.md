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
- Nodes: 5
  - node-1: Ready
  - node-2: Ready
  - node-3: Ready
  - node-4: Ready
  - node-5: NotReady (DiskPressure)
- Namespaces: 8 (default, kube-system, kube-public, dev, prod, staging, monitoring, logging)
- Total Pods: 320 (290 Running, 10 Pending, 20 Failed)

Critical Issues Detected:
1. **Namespace: kube-system**
   - Issue: Pod "kube-dns" in CrashLoopBackOff state.
   - Logs: 
     ```
     FATAL: Unable to start DNS server: address already in use.
     ```
   - Suggested Action:
     - Check for port conflicts and DNS configuration issues.
     - Ensure no other processes are using port 53 on this node.
     - Restart the "kube-dns" pod and monitor its status.

2. **Node: node-5**
   - Issue: Node is under DiskPressure and marked as NotReady.
   - Disk Usage: 92% (Threshold: 90%)
   - Suggested Action:
     - Free up disk space on node-5 by cleaning up unused images, volumes, or logs.
     - Consider adding more disk capacity to node-5 or redistributing workloads.

3. **Namespace: prod**
   - Issue: Deployment "payment-service" has 3 replicas not available.
   - Description: Pods are failing liveness checks due to high memory usage.
   - Suggested Action:
     - Review and optimize memory usage in the payment-service application.
     - Increase memory limits in the deployment configuration.
     - Redeploy the application and monitor its status.

4. **Namespace: dev**
   - Issue: Pod "api-server" in Pending state for over 15 minutes.
   - Reason: Insufficient CPU resources available for scheduling.
   - Suggested Action:
     - Check if there are sufficient CPU resources available on the nodes.
     - Consider adjusting resource requests or scaling the cluster.
     - Investigate node taints or affinity/anti-affinity rules that might be affecting scheduling.

5. **Namespace: staging**
   - Issue: Pod "frontend-app" in Failed state due to OOMKilled (Out of Memory).
   - Logs:
     ```
     MemoryError: Unable to allocate memory.
     ```
   - Suggested Action:
     - Increase memory limits for the frontend-app deployment.
     - Optimize the application code to reduce memory consumption.
     - Monitor the pod's memory usage after redeployment.

Performance Warnings:
1. **Node: node-2**
   - Warning: CPU usage is high (87.00%).
   - Suggested Action:
     - Redistribute workloads to less utilized nodes.
     - Consider scaling up resources or adding more nodes to the cluster.

2. **Namespace: monitoring**
   - Warning: Service "prometheus" experiencing high latency (average 250ms).
   - Suggested Action:
     - Investigate network policies or QoS settings affecting Prometheus.
     - Check for network congestion or misconfigured services.
     - Optimize Prometheus resource allocation or sharding.

3. **Namespace: logging**
   - Warning: Fluentd pods experiencing high memory usage (95%).
   - Suggested Action:
     - Investigate the volume of logs being processed by Fluentd.
     - Optimize Fluentd configuration to reduce memory usage.
     - Consider increasing memory allocation or scaling the Fluentd deployment.

Security Scan Results:
- Vulnerabilities Detected: 2 (1 High, 1 Medium)
  - High Severity: CVE-2024-5678 found in image "nginx:1.19.0" used by "web-app" deployment (Namespace: prod).
  - Suggested Action:
    - Update the "nginx" image to the latest secure version.
    - Review image security policies and ensure regular vulnerability scans.
  
  - Medium Severity: CVE-2023-1234 found in image "redis:6.2.0" used by "cache-service" deployment (Namespace: dev).
  - Suggested Action:
    - Update the "redis" image to a secure version.
    - Implement automated image vulnerability scanning in your CI/CD pipeline.

Network Diagnostics:
1. **Namespace: default**
   - Issue: Service "internal-api" has no active endpoints.
   - Suggested Action:
     - Ensure that the associated pods are running and have passed readiness probes.
     - Verify that the service selector matches the pod labels correctly.
     - Check for any network policies that might be blocking traffic.

2. **Namespace: prod**
   - Issue: Pod "payment-gateway" is not using the recommended DNS policy ("ClusterFirst").
   - Suggested Action:
     - Update the DNS policy in the pod specification to "ClusterFirst".
     - Verify that internal DNS resolution is functioning correctly for this pod.

3. **Namespace: staging**
   - Issue: Pod "web-server" failed to establish connectivity to the "database" service.
   - Suggested Action:
     - Check the service and pod network configurations.
     - Ensure that network policies allow traffic between "web-server" and "database" pods.
     - Verify that the "database" service has active, ready endpoints.

Storage Diagnostics:
1. **PersistentVolume: pv-log-storage**
   - Issue: PersistentVolume is in Released state but not reused.
   - Suggested Action:
     - If the PersistentVolume is no longer needed, delete it to free up resources.
     - If it should be reused, ensure it is properly bound to a PersistentVolumeClaim.

2. **PersistentVolume: pv-backup-storage**
   - Issue: PersistentVolume is in Failed state.
   - Suggested Action:
     - Investigate the underlying storage system for issues.
     - Check if the PersistentVolumeClaim is correctly configured.
     - Consider deleting and recreating the PersistentVolume if the issue persists.

Pod Disruption Budget Diagnostics:
1. **Namespace: prod**
   - Issue: PodDisruptionBudget "payment-pdb" has fewer healthy pods than desired.
   - Current Healthy: 2, Desired Healthy: 4
   - Suggested Action:
     - Investigate disruptions or issues affecting the pods under this PDB.
     - Ensure sufficient resources and replicas are available to meet the disruption budget.

Summary:
- 5 Critical issues detected.
- 3 Performance warnings.
- 2 Security vulnerabilities identified.
- 3 Network diagnostics issues identified.
- 2 Storage issues identified.
- 1 PodDisruptionBudget issue detected.

Suggested Next Steps:
1. Address the critical issues in the kube-system, prod, dev, and staging namespaces.
2. Investigate and optimize resource usage on high-demand nodes (node-2 and node-5).
3. Review and mitigate security vulnerabilities in nginx and redis images.
4. Resolve network diagnostics issues in the default, prod, and staging namespaces.
5. Ensure PersistentVolumes are correctly bound and storage resources are available.
6. Verify PodDisruptionBudgets are maintained to ensure service availability.
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


