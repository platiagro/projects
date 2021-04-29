from kubernetes import client

from projects.kubernetes.kube_config import load_kube_config


def list_resource_version(group, version, namespace, plural):
    """
    Determines the resource version the watcher should list from.

    Parameters
    ----------
    group : str
    version : str
    namespace : str
    plural : str

    Returns
    -------
    str
    """
    load_kube_config()
    api = client.CustomObjectsApi()

    r = api.list_namespaced_custom_object(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
    )
    return r["metadata"]["resourceVersion"]
