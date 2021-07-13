import http
import logging
import os

from kubernetes import watch
from kubernetes.client.rest import ApiException

from projects import models
from projects.agent.utils import list_resource_version
from projects.kfp import KF_PIPELINES_NAMESPACE

GROUP = "machinelearning.seldon.io"
VERSION = "v1"
PLURAL = "seldondeployments"


def watch_seldon_deployments(api, session):
    """
    Watch seldon deployment events and save data in database.

    Parameters
    ----------
    api : kubernetes.client.apis.custom_objects_api.CustomObjectsApi
    session : sqlalchemy.orm.session.Session
    """
    # When retrieving a collection of resources the response from the server
    # will contain a resourceVersion value that can be used to initiate a watch
    # against the server.
    resource_version = list_resource_version(
        group=GROUP,
        version=VERSION,
        namespace=KF_PIPELINES_NAMESPACE,
        plural=PLURAL,
    )

    while os.environ["STOP_THREADS"] == "0":
        logging.info("Watching deployments stream...")

        stream = watch.Watch().stream(
            api.list_namespaced_custom_object,
            group=GROUP,
            version=VERSION,
            namespace=KF_PIPELINES_NAMESPACE,
            plural=PLURAL,
            resource_version=resource_version,
            timeout_seconds=5,
        )

        try:
            for sdep_manifest in stream:
                logging.info("Event: %s %s " % (sdep_manifest["type"],
                             sdep_manifest["object"]["metadata"]["name"]))

                update_seldon_deployment(sdep_manifest, session)

            raise Exception("deployments stream ended.")
        except ApiException as e:
            logging.exception("kubernetes.client.rest.ApiException")
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
            else:
                raise e


def update_seldon_deployment(seldon_deployment_manifest, session):
    """
    Parses seldon deployment manifest and sets status in database.

    Parameters
    ----------
    seldon_deployment_manifest : dict
    session : sqlalchemy.orm.session.Session
    """
    deployment_id = seldon_deployment_manifest["object"]["metadata"]["name"]
    status = seldon_deployment_manifest["object"].get("status")

    if status is not None:
        state = status["state"]

        if state == "Available":
            state = "Succeeded"
        elif state == "Creating":
            state = "Pending"

        session.query(models.Deployment) \
            .filter_by(uuid=deployment_id) \
            .update({"status": state})

    session.commit()
