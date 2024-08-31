import yaml
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
        self.policy_v1 = client.PolicyV1Api()

        # Load thresholds from YAML file
        with open("thresholds.yaml", 'r') as stream:
            self.thresholds = yaml.safe_load(stream)

    def diagnose_cluster(self):
        print("[K8S Troubleshooter] Starting full cluster diagnostic...\n")
        self.cluster_overview()
        critical_issues = self.check_critical_issues()
        performance_warnings = self.check_performance_warnings()
        security_issues = self.scan_security_vulnerabilities()
        self.network_diagnostics()
        self.storage_checks()
        self.pod_disruption_checks()
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

        # Pod in CrashLoopBackOff or Failed state
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

        # Nodes under MemoryPressure or DiskPressure
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
                        print(f"     - Disk usage is high on node {node.metadata.name}. Consider freeing up space or redistributing workloads.\n")
        except ApiException as e:
            print(f"Error fetching nodes: {e}\n")

        # Deployments with unavailable replicas
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

        # High resource usage cluster-wide
        try:
            nodes = self.core_v1.list_node().items
            for node in nodes:
                node_cpu = node.status.allocatable['cpu']
                node_memory = node.status.allocatable['memory']
                usage_cpu = self.core_v1.read_node_status(node.metadata.name).status.capacity['cpu']
                usage_memory = self.core_v1.read_node_status(node.metadata.name).status.capacity['memory']

                cpu_usage_percentage = (int(usage_cpu.strip('m')) / int(node_cpu.strip('m'))) * 100
                memory_usage_percentage = (int(usage_memory.strip('Ki')) / int(node_memory.strip('Ki'))) * 100

                if cpu_usage_percentage > self.thresholds['cpu_usage_threshold']:
                    print(f"1. **Node: {node.metadata.name}**")
                    print(f"   - Warning: CPU usage is high ({cpu_usage_percentage:.2f}%).")
                    print("   - Suggested Action:")
                    print("     - Consider redistributing workloads or scaling up resources.\n")
                    performance_warnings.append({
                        'node': node.metadata.name,
                        'cpu_usage': cpu_usage_percentage
                    })

                if memory_usage_percentage > self.thresholds['memory_usage_threshold']:
                    print(f"1. **Node: {node.metadata.name}**")
                    print(f"   - Warning: Memory usage is high ({memory_usage_percentage:.2f}%).")
                    print("   - Suggested Action:")
                    print("     - Consider redistributing workloads or scaling up resources.\n")
                    performance_warnings.append({
                        'node': node.metadata.name,
                        'memory_usage': memory_usage_percentage
                    })

        except ApiException as e:
            print(f"Error fetching node resource usage: {e}\n")

        # Long pod scheduling time
        try:
            all_pods = self.core_v1.list_pod_for_all_namespaces().items
            for pod in all_pods:
                if pod.status.phase == "Pending" and pod.status.start_time:
                    # Calculate the time the pod has been in the pending state
                    time_in_pending = (client.V1Time.now() - pod.status.start_time).total_seconds()

                    if time_in_pending > self.thresholds['pod_scheduling_delay_threshold']:
                        print(f"2. **Namespace: {pod.metadata.namespace}**")
                        print(f"   - Issue: Pod \"{pod.metadata.name}\" has been pending for {time_in_pending / 60:.2f} minutes.")
                        print("   - Suggested Action:")
                        print("     - Check if there are sufficient resources available for scheduling.")
                        print("     - Investigate potential resource quotas, node affinity, or taints/tolerations that might be causing delays.\n")
                        performance_warnings.append({
                            'namespace': pod.metadata.namespace,
                            'pod': pod.metadata.name,
                            'issue': 'Extended pending state',
                            'time_in_pending': time_in_pending / 60  # Convert seconds to minutes
                        })
        except ApiException as e:
            print(f"Error fetching pod scheduling information: {e}\n")

        return performance_warnings

    def scan_security_vulnerabilities(self):
        security_issues = []
        print("Security Scan Results:")

        try:
            # Example security vulnerability detection logic
            all_pods = self.core_v1.list_pod_for_all_namespaces().items
            for pod in all_pods:
                for container in pod.spec.containers:
                    image_name = container.image
                    # Placeholder logic for checking image vulnerabilities
                    if "nginx" in image_name:
                        print(f"1. **Namespace: {pod.metadata.namespace}**")
                        print(f"   - Issue: Security vulnerability found in image \"{image_name}\".")
                        print("   - Suggested Action:")
                        print("     - Update the image to the latest secure version.")
                        print("     - Review image security policies and ensure regular vulnerability scans.\n")
                        security_issues.append({
                            'namespace': pod.metadata.namespace,
                            'image': image_name,
                            'vulnerability': 'Example vulnerability'
                        })

                    # Add similar checks for other images or custom vulnerability logic
        except ApiException as e:
            print(f"Error performing security scans: {e}\n")

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

            # Example for checking pod connectivity
            all_pods = self.core_v1.list_pod_for_all_namespaces().items
            for pod in all_pods:
                if pod.status.pod_ip is None:
                    print(f"- Warning: Pod {pod.metadata.name} in namespace {pod.metadata.namespace} has no IP address assigned.")
                    print("  - Suggested Action:")
                    print("    - Ensure the CNI plugin is functioning correctly.")
                    print("    - Investigate network policy or security group configurations.\n")

                # Check if any pods have DNS resolution issues
                if pod.status.phase == "Running":
                    dns_policy = pod.spec.dns_policy
                    if dns_policy and dns_policy != "ClusterFirst":
                        print(f"- Warning: Pod {pod.metadata.name} in namespace {pod.metadata.namespace} is not using the recommended DNS policy.")
                        print("  - Suggested Action:")
                        print("    - Consider setting the DNS policy to 'ClusterFirst' for optimal internal DNS resolution.\n")
        except ApiException as e:
            print(f"Error performing network diagnostics: {e}\n")

    def storage_checks(self):
        print("Storage Diagnostics:")

        try:
            persistent_volumes = self.core_v1.list_persistent_volume().items
            for pv in persistent_volumes:
                if pv.status.phase != "Bound":
                    print(f"- Warning: PersistentVolume {pv.metadata.name} is in {pv.status.phase} state.")
                    print("  - Suggested Action:")
                    print("    - Ensure the PersistentVolumeClaim is correctly configured and is bound to the PV.")
                    print("    - Check the storage class and availability of storage resources.\n")
        except ApiException as e:
            print(f"Error performing storage checks: {e}\n")

    def pod_disruption_checks(self):
        print("Pod Disruption Budget Diagnostics:")

        try:
            pdbs = self.policy_v1.list_pod_disruption_budget_for_all_namespaces().items
            for pdb in pdbs:
                if pdb.status.current_healthy < pdb.status.desired_healthy:
                    print(f"- Warning: PodDisruptionBudget {pdb.metadata.name} in namespace {pdb.metadata.namespace} has fewer healthy pods than desired.")
                    print("  - Suggested Action:")
                    print("    - Investigate if there are ongoing disruptions or issues affecting the pods.")
                    print("    - Ensure there are sufficient resources and pod replicas to meet the disruption budget requirements.\n")
        except ApiException as e:
            print(f"Error performing PodDisruptionBudget checks: {e}\n")

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
        print("5. Ensure PersistentVolumes are correctly bound and storage resources are available.")
        print("6. Verify PodDisruptionBudgets are maintained to ensure service availability.")

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