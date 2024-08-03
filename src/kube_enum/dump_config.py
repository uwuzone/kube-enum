"""
Kubernetes Cluster Configuration Dumper

This script connects to a specified Kubernetes API URL and dumps the entire
accessible configuration as JSON. It's designed for internal security audits
and potential integration into automated security processes.

The script retrieves information about:
- Namespaces
- Pods
- Services
- Deployments
- Secrets (without decoding values)
- ConfigMaps
- Roles
- RoleBindings
- ClusterRoles
- ClusterRoleBindings

Usage:
    python script_name.py <kubernetes-api-url>

Note: This script is intended for authorized internal security audits only.
The information retrieved is highly sensitive and should be handled with extreme care.
Ensure proper authorization before use and securely handle the output.

CAUTION: This script disables SSL verification. Use only in controlled, internal environments.
"""

import json

from datetime import datetime

from kubernetes import client


class KubeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


def dump_cluster_config(api_url):
    configuration = client.Configuration()
    configuration.host = api_url
    configuration.verify_ssl = False  # Only for controlled testing environments
    api_client = client.ApiClient(configuration)

    v1 = client.CoreV1Api(api_client)
    apps_v1 = client.AppsV1Api(api_client)
    rbac_v1 = client.RbacAuthorizationV1Api(api_client)

    cluster_config = {
        "namespaces": [],
        "pods": [],
        "services": [],
        "deployments": [],
        "secrets": [],
        "configmaps": [],
        "roles": [],
        "rolebindings": [],
        "clusterroles": [],
        "clusterrolebindings": [],
    }

    # Namespaces
    namespaces = v1.list_namespace()
    cluster_config["namespaces"] = [ns.to_dict() for ns in namespaces.items]

    # Pods
    pods = v1.list_pod_for_all_namespaces()
    cluster_config["pods"] = [pod.to_dict() for pod in pods.items]

    # Services
    services = v1.list_service_for_all_namespaces()
    cluster_config["services"] = [svc.to_dict() for svc in services.items]

    # Deployments
    deployments = apps_v1.list_deployment_for_all_namespaces()
    cluster_config["deployments"] = [dep.to_dict() for dep in deployments.items]

    # Secrets (without decoding values)
    secrets = v1.list_secret_for_all_namespaces()
    cluster_config["secrets"] = [secret.to_dict() for secret in secrets.items]

    # ConfigMaps
    config_maps = v1.list_config_map_for_all_namespaces()
    cluster_config["configmaps"] = [cm.to_dict() for cm in config_maps.items]

    # Roles
    roles = rbac_v1.list_role_for_all_namespaces()
    cluster_config["roles"] = [role.to_dict() for role in roles.items]

    # RoleBindings
    role_bindings = rbac_v1.list_role_binding_for_all_namespaces()
    cluster_config["rolebindings"] = [rb.to_dict() for rb in role_bindings.items]

    # ClusterRoles
    cluster_roles = rbac_v1.list_cluster_role()
    cluster_config["clusterroles"] = [cr.to_dict() for cr in cluster_roles.items]

    # ClusterRoleBindings
    cluster_role_bindings = rbac_v1.list_cluster_role_binding()
    cluster_config["clusterrolebindings"] = [
        crb.to_dict() for crb in cluster_role_bindings.items
    ]

    return json.dumps(cluster_config, indent=2, cls=KubeJSONEncoder)
