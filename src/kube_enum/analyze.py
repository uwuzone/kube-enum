import json
import base64


def load_kube_config(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def should_skip_secret(value, skip_strings=[]):
    if skip_strings:
        return any(
            skip.lower() in value.lower() if value else False for skip in skip_strings
        )

    return False


def should_skip_ns(value, skip_ns=[]):
    if skip_ns:
        return any(skip in value for skip in skip_ns)


def show_secrets_and_env_vars(
    file_path, truncate_length=None, skip_strings=None, skip_namespaces=None
):
    config = load_kube_config(file_path)
    print("Secrets and Environment Variables:")
    print("==================================")

    # Process Secrets
    for secret in config.get("secrets", []):
        namespace = secret["metadata"]["namespace"]
        if should_skip_ns(namespace, skip_namespaces):
            continue

        print(f"\nSecret: {secret['metadata']['name']} (Namespace: {namespace})")
        if "data" in secret and secret["data"]:
            for key, value in secret["data"].items():
                decoded_value = base64.b64decode(value).decode(
                    "utf-8", errors="replace"
                )
                if not should_skip_secret(decoded_value, skip_strings):
                    if truncate_length and len(decoded_value) > truncate_length:
                        decoded_value = decoded_value[:truncate_length] + "..."
                    print(f"  {key}: {decoded_value}")

    # Process Environment Variables from Deployments
    for deployment in config.get("deployments", []):
        namespace = deployment["metadata"]["namespace"]
        if should_skip_ns(namespace, skip_namespaces):
            continue

        containers = deployment["spec"]["template"]["spec"]["containers"]
        has_env_vars = any(
            "env" in container and container["env"] for container in containers
        )
        if not has_env_vars:
            continue
        print(
            f"\nDeployment: {deployment['metadata']['name']} (Namespace: {namespace})"
        )
        for container in containers:
            if "env" in container and container["env"]:
                print(f"  Container: {container['name']}")
                for env in container["env"]:
                    value = env.get("value", "N/A")
                    if not should_skip_secret(value, skip_strings):
                        if truncate_length and value and len(value) > truncate_length:
                            value = value[:truncate_length] + "..."
                        print(f"    {env['name']}: {value}")


def log_none_values(file_path):
    config = load_kube_config(file_path)
    print("Instances of None values:")
    print("=========================")
    for resource_type, resources in config.items():
        for resource in resources:
            _recursive_none_check(
                resource, f"{resource_type}/{resource['metadata']['name']}"
            )


def _recursive_none_check(obj, path):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v is None:
                print(f"None value found: {path}/{k}")
            else:
                _recursive_none_check(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _recursive_none_check(v, f"{path}[{i}]")


def show_verbose_structure(file_path):
    config = load_kube_config(file_path)
    print("Verbose Structure of Resources:")
    print("===============================")
    for resource_type, resources in config.items():
        print(f"\n{resource_type.upper()}:")
        for resource in resources:
            print(f"  - Name: {resource['metadata']['name']}")
            print(f"    Namespace: {resource['metadata'].get('namespace', 'N/A')}")
            _print_structure(resource, 4)


def _print_structure(obj, indent=0):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ["metadata", "status"]:  # Skip these to keep output manageable
                continue
            print(f"{' ' * indent}{k}:")
            _print_structure(v, indent + 2)
    elif isinstance(obj, list):
        for item in obj:
            _print_structure(item, indent + 2)
    else:
        print(f"{' ' * indent}{obj}")


def check_unused_resources(file_path):
    config = load_kube_config(file_path)
    print("Unused Secrets and ConfigMaps:")
    print("==============================")

    used_resources = set()

    # Collect used resources
    for deployment in config.get("deployments", []):
        for container in deployment["spec"]["template"]["spec"]["containers"]:
            if "envFrom" in container:
                for env_from in container["envFrom"]:
                    if "configMapRef" in env_from:
                        used_resources.add(
                            f"ConfigMap/{env_from['configMapRef']['name']}"
                        )
                    elif "secretRef" in env_from:
                        used_resources.add(f"Secret/{env_from['secretRef']['name']}")

    # Check for unused Secrets
    for secret in config.get("secrets", []):
        name = secret["metadata"]["name"]
        if f"Secret/{name}" not in used_resources:
            print(f"Unused Secret: {name}")

    # Check for unused ConfigMaps
    for cm in config.get("configmaps", []):
        name = cm["metadata"]["name"]
        if f"ConfigMap/{name}" not in used_resources:
            print(f"Unused ConfigMap: {name}")
