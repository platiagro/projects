# -*- coding: utf-8 -*-
"""Utility functions."""


def search_for_pod_info(details, operator_id):
    """
    Get operator pod info, such as: name, status and message error (if failed).

    Parameters
    ----------
    details : dict
        Workflow manifest from pipeline runtime.
    operator_id : str

    Returns
    -------
    dict
        Pod informations.
    """
    info = {}

    try:
        if "nodes" in details["status"]:
            for node in [*details["status"]["nodes"].values()]:
                if node["displayName"] == operator_id:
                    info = {"name": node["id"], "status": node["phase"], "message": node["message"]}
    except KeyError:
        pass

    return info
