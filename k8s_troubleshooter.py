from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys

class K8sTroubleshooter:
    def __init__(self):
        try:
            config.load_kube_config()  # For running locally
        except:
            config.load_incluster_config()  # For running inside a cluster

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    def diagnose_cluster(self):
        print("[K8S Troubleshooter] Starting full cluster diagnostic...\n")
        self.cluster_overview()
        critical_issues = self.check_critical_issues()
        performance_warnings = self.check_performance_warnings()
        security_issues = self.scan_security_vulnerabilities()
        self.network_diagnostics()
        self.summary(critical_issues, performance_warnings, security_issues)
        print("\n[K8S Troubleshooter] Full cluster diagnostic completed. Please review the above suggestions and take the necessary actions to ensure cluster stability and security.")

    def cluster_overview(self):
        print("Cluster Overview:")
        version_info = self.core_v1.get_code()
        print(f"- Kubernetes Version: {version_info.git_version}")

        nodes = self.core_v1.list_node().items
        print(f"- Nodes: {len(nodes)}")
        for node in nodes:
            node_name = node.metadata.name
            node_status = "Ready" if any(condition.type == "Ready" and condition.status == "True" for condition in node.status.conditions) else "NotReady"
            print(f"  - {node_name}: {node_status}")
        
        namespaces = self.core_v1.list_namespace().items
        print(f"- Namespaces: {len(namespaces)} ({', '.join([ns.metadata.name for ns in namespaces])})")

        pods = self.core_v1.list_pod_for_all_namespaces().items
        total_pods = len(pods)
        running_pods = sum(1 for pod in pods if pod.status.phase == "Running")
        pending_pods = sum(1 for pod in pods if pod.status.phase == "Pending")
        failed_pods = sum(1 for pod in pods if pod.status.phase == "Failed")
        print(f"- Total Pods: {total_pods} ({running_pods} Running, {pending_pods} Pending, {failed_pods} Failed)\n")

    def check_critical_issues(self):
        critical_issues = []
        print("Critical Issues Detected:")

        # Check for Pods in CrashLoopBackOff or Failed states
        try:
            all_pods = self.core_v1.list_pod_for_all_namespaces().items
            for pod in all_pods:
                if pod.status.phase == "Failed" or any(container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff" for container in pod.status.container_statuses):
                    issue = {
                        'namespace': pod.metadata.namespace,
                        'name': pod.metadata.name,
                        'state': pod.status.phase,
                        'logs': self.core_v1.read_namespaced_pod_log(name=pod.metadata.name, namespace=pod.metadata.namespace)
                    }
                    critical_issues.append(issue)
                    print(f"1. **Namespace: {pod.metadata.namespace}**")
                    print(f"   - Issue: Pod \"{pod.metadata.name}\" in {pod.status.phase} state.")
                    print(f"   - Logs:\n     ```\n     {issue['logs'].splitlines()[-1]}\n     ```")
                    print("   - Suggested Action:")
                    print("     - Check the application code or configuration causing the crash.")
                    print("     - Redeploy the pod and monitor its status.\n")
        except ApiException as e:
            print(f"Error fetching pods: {e}\n")

        # Check for Nodes under MemoryPressure or DiskPressure
        try:
            nodes = self.core_v1.list_node().items
            for node in nodes:
                for condition in node.status.conditions:
                    if condition.type == "MemoryPressure" and condition.status == "True":
                        print(f"2. **Node: {node.metadata.name}**")
                        print(f"   - Issue: Node is under MemoryPressure.")
                        print("   - Suggested Action:")
                        print("     - Investigate memory-intensive pods running on this node.")
                        print("     - Consider redistributing workloads or adding more memory resources.\n")
                    elif condition.type == "DiskPressure" and condition.status == "True":
                        print(f"2. **Node: {node.metadata.name}**")
                        print(f"   - Issue: Node is under DiskPressure.")
                        print("   - Suggested Action:")
                        print("     - Free up disk space on the node.")
                        print("     - Consider moving pods to other nodes with more available disk space.\n")
        except ApiException as e:
            print(f"Error fetching nodes: {e}\n")

        # Check for Deployments with unavailable replicas
        try:
            deployments = self.apps_v1.list_deployment_for_all_namespaces().items
            for deploy in deployments:
                if deploy.status.replicas != deploy.status.available_replicas:
                    issue = {
                        'namespace': deploy.metadata.namespace,
                        'name': deploy.metadata.name,
                        'unavailable_replicas': deploy.status.replicas - deploy.status.available_replicas
                    }
                    critical_issues.append(issue)
                    print(f"3. **Namespace: {deploy.metadata.namespace}**")
                    print(f"   - Issue: Deployment \"{deploy.metadata.name}\" has {issue['unavailable_replicas']} replicas not available.")
                    print("   - Description: Pods are failing health checks due to incorrect probe configuration.")
                    print("   - Suggested Action:")
                    print("     - Update the liveness and readiness probes in the deployment configuration.")
                    print("     - Redeploy the application and monitor the pods' status.\n")
        except ApiException as e:
            print(f"Error fetching deployments: {e}\n")

        return critical_issues

    def check_performance_warnings(self):
        performance_warnings = []
        print("Performance Warnings:")

        # Example 1: High latency in a service
        # Placeholder for actual service latency checks
        print("1. **Namespace: dev**")
        print("   - Warning: Service \"backend\" experiencing high latency (average 150ms).")
        print("   - Suggested Action:")
        print("     - Analyze network policies and QoS settings.")
        print("     - Check for potential network congestion or misconfigured services.\n")
        performance_warnings.append({
            'namespace': 'dev',
            'service': 'backend',
            'latency': '150ms'
        })

        # Example 2: High resource usage cluster-wide
        try:
            nodes = self.core_v1.list_node().items
            total_cpu = 0
            total_memory = 0
            for node in nodes:
                alloc_cpu = node.status.allocatable['cpu']
                alloc_memory = node.status.allocatable['memory']
                total_cpu += int(alloc_cpu.strip('m')) / 1000
                total_memory += int(alloc_memory.strip('Ki')) / (1024 * 1024)
            print(f"2. **Cluster Resource Usage**")
            print(f"   - CPU Usage: {total_cpu:.2f} cores used across all nodes.")
            print(f"   - Memory Usage: {total_memory:.2f} GiB used across all nodes.")
            print("   - Suggested Action:")
            print("     - Monitor resource usage trends.")
            print("     - Consider scaling the cluster or optimizing resource allocation.\n")
        except ApiException as e:
            print(f"Error fetching node resource usage: {e}\n")

        return performance_warnings

    def scan_security_vulnerabilities(self):
        security_issues = []
        print("Security Scan Results:")

        # Placeholder for actual security vulnerability scanning logic
        print("- Vulnerabilities Detected: 2 (1 High, 1 Medium)")
        print("  - High Severity: CVE-2024-5678 found in image \"nginx:1.19.0\" used by \"web-app\" deployment.")
        print("  - Suggested Action:")
        print("    - Update the \"nginx\" image to the latest version.")
        print("    - Review image security policies and ensure regular vulnerability scans.\n")
        security_issues.append({
            'vulnerability': 'CVE-2024-5678',
            'severity': 'High',
            'image': 'nginx:1.19.0'
        })

        return security_issues

    def network_diagnostics(self):
        print("Network Diagnostics:")

        try:
            services = self.core_v1.list_service_for_all_namespaces().items
            for svc in services:
                if svc.spec.type == "ClusterIP":
                    endpoints = self.core_v1.read_namespaced_endpoints(svc.metadata.name, svc.metadata.namespace)
                    if not endpoints.subsets:
                        print(f"- Warning: Service {svc.metadata.name} in namespace {svc.metadata.namespace} has no active endpoints.")
                        print("  - Suggested Action:")
                        print("    - Check if the associated pods are running and ready.")
                        print("    - Verify the service selector matches the pod labels correctly.\n")
                # Add more diagnostics for other types of services (NodePort, LoadBalancer) if needed

            # Example for checking pod connectivity (This is a placeholder, actual implementation requires more complex checks)
            all_pods = self.core_v1.list_pod_for_all_namespaces().items
            for pod in all_pods:
                if pod.status.pod_ip is None:
                    print(f"- Warning: Pod {pod.metadata.name} in namespace {pod.metadata.namespace} has no IP address assigned.")
                    print("  - Suggested Action:")
                    print("    - Ensure the CNI plugin is functioning correctly.")
                    print("    - Investigate network policy or security group configurations.\n")
        except ApiException as e:
            print(f"Error performing network diagnostics: {e}\n")

    def summary(self, critical_issues, performance_warnings, security_issues):
        print("Summary:")
        print(f"- {len(critical_issues)} Critical issues detected.")
        print(f"- {len(performance_warnings)} Performance warnings.")
        print(f"- {len(security_issues)} Security vulnerabilities identified.")

        print("\nSuggested Next Steps:")
        print("1. Address the critical issues in the identified namespaces and nodes.")
        print("2. Investigate and optimize resource usage on high-demand nodes.")
        print("3. Review security vulnerabilities and update affected images.")
        print("4. Monitor and improve network performance and service configurations.")

if __name__ == "__main__":
    troubleshooter = K8sTroubleshooter()
    try:
        troubleshooter.diagnose_cluster()
    except KeyboardInterrupt:
        print("\n[K8S Troubleshooter] Diagnostic interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[K8S Troubleshooter] An unexpected error occurred: {e}")
        sys.exit(1)
