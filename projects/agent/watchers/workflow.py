import dateutil.parser
import logging
import http
import re
import uuid

from kubernetes import watch
from kubernetes.client.rest import ApiException

from projects import models
from projects.agent.logger import DEFAULT_LOG_LEVEL
from projects.agent.utils import list_resource_version
from projects.kfp import KF_PIPELINES_NAMESPACE

GROUP = "argoproj.io"
VERSION = "v1alpha1"
PLURAL = "workflows"

RECURRENT_MESSAGES = ["ContainerCreating", ]


def watch_workflows(api, session, **kwargs):
    """
    Watch workflows events and save data in database.

    Parameters
    ----------
    api : kubernetes.client.apis.custom_objects_api.CustomObjectsApi
    session : sqlalchemy.orm.session.Session
    """
    w = watch.Watch()

    log_level = kwargs.get("log_level", DEFAULT_LOG_LEVEL)
    logging.basicConfig(level=log_level)

    # When retrieving a collection of resources the response from the server
    # will contain a resourceVersion value that can be used to initiate a watch
    # against the server.
    resource_version = list_resource_version(
        group=GROUP,
        version=VERSION,
        namespace=KF_PIPELINES_NAMESPACE,
        plural=PLURAL,
    )

    while True:

        stream = w.stream(
            api.list_namespaced_custom_object,
            group=GROUP,
            version=VERSION,
            namespace=KF_PIPELINES_NAMESPACE,
            plural=PLURAL,
            resource_version=resource_version,
        )

        try:
            for workflow_manifest in stream:
                logging.info("Event: %s %s " % (workflow_manifest["type"],
                             workflow_manifest["object"]["metadata"]["name"]))

                update_status(workflow_manifest, session)
        except ApiException as e:
            # When the requested watch operations fail because the historical version
            # of that resource is not available, clients must handle the case by
            # recognizing the status code 410 Gone, clearing their local cache,
            # performing a list operation, and starting the watch from the resourceVersion returned by that new list operation.
            # See: https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes
            if e.status == http.HTTPStatus.GONE:
                resource_version = list_resource_version(
                    group=GROUP,
                    version=VERSION,
                    namespace=KF_PIPELINES_NAMESPACE,
                    plural=PLURAL,
                )


def update_status(workflow_manifest, session):
    """
    Parses workflow manifest and sets operators status in database.
    If workflow is a deployment update deployment in database.

    Parameters
    ----------
    workflow_manifest : dict
    session : sqlalchemy.orm.session.Session
    """
    # First, we set the status for operators that are unlisted in object.status.nodes.
    # Obs: the workflow manifest contains only the nodes that are ready to run (whose dependencies succeeded)

    # if the workflow is pending/running, then unlisted_operators_status = "Pending"
    # if the workflow succeeded/failed, then unlisted_operators_status = "Unset/Setted Up"
    workflow_status = workflow_manifest["object"]["status"].get("phase")
    if workflow_status in {"Pending", "Running"}:
        unlisted_operators_status = "Pending"
    else:
        unlisted_operators_status = "Unset"

    match = re.search(r"(experiment|deployment)-(.*)-\w+", workflow_manifest["object"]["metadata"]["name"])
    if match:
        key = match.group(1)
        id_ = match.group(2)
        session.query(models.Operator) \
            .filter_by(**{f"{key}_id": id_}) \
            .update({"status": unlisted_operators_status})

        # check if this workflow is a deployment
        if key == "deployment":
            update_seldon_deployment(
                deployment_id=id_,
                status=workflow_status,
                created_at_str=workflow_manifest["object"]["status"].get("startedAt"),
                session=session
            )

    # Then, we set the status for operators that are listed in object.status.nodes
    for node in workflow_manifest["object"]["status"].get("nodes", {}).values():
        try:
            operator_id = uuid.UUID(node["displayName"])
        except ValueError:
            continue

        status_message = str(node.get("message")) if node.get("message") else None
        # if workflow was interrupted, then status = "Terminated"
        if str(node.get("message")) == "terminated":
            status = "Terminated"
            status_message = None
        else:
            status = str(node["phase"])

        if status_message not in RECURRENT_MESSAGES:
            session.query(models.Operator) \
                .filter_by(uuid=operator_id) \
                .update({"status": status, "status_message": status_message})

    session.commit()


def update_seldon_deployment(deployment_id, status, created_at_str, session):
    """
    Sets deployment status and deployed_at in database.

    Parameters
    ----------
    deployment_id : str
    status : str
    created_at_str : str
    """
    if created_at_str is not None:
        deployed_at = dateutil.parser.isoparse(created_at_str)
    else:
        deployed_at = created_at_str

    if status in (None, "Running"):
        status = "Pending"

    session.query(models.Deployment) \
        .filter_by(uuid=deployment_id) \
        .update({"status": status, "deployed_at": deployed_at})

    session.commit()
