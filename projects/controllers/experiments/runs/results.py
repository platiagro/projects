# -*- coding: utf-8 -*-
"""Experiments Results controller."""
import io
import re
import zipfile

from projects.kfp.runs import get_latest_run_id
from projects.object_storage import list_objects, get_object


class ResultController:
    def __init__(self, session):
        self.session = session

    def get_results(self, experiment_id: str, run_id: str, operator_id: str = None):
        """
        Write results from experiment in a .zip file.

        Parameters
        ----------
        experiment_id: str
        run_id: str
            The run_id. If `run_id=latest`, then returns results from the latest run_id.
        operator_id: str
            The operador_id. If `operator_id=None`, get results for all operators.

        Returns
        -------
        io.BytesIO
            Zip file of experiment results.
        """
        if run_id == "latest":
            run_id = get_latest_run_id(experiment_id)

        if operator_id:
            objects_path = f"experiments/{experiment_id}/operators/{operator_id}"
        else:
            objects_path = f"experiments/{experiment_id}/operators/"
        objects = list_objects(objects_path)

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, "a", zipfile.ZIP_DEFLATED) as z:
            for object in objects:
                file = self._download_result(object.object_name, run_id)
                if file is not None:
                    z.writestr(f"{file['operatorId']}/{file['filename']}", file["data"])

        zip_file.seek(0)

        return zip_file

    def _download_result(self, object_name, run_id):
        # split and remove /experiments/{experiment_id}/operators/
        # object_name_splitted = [{operator_id}, {run_id}, {filename}]
        object_name_splitted = object_name.split("/")[3:]

        if object_name_splitted[1] == run_id:
            filename = object_name_splitted[2]
            filename_pattern = re.compile(r"figure-([0-9]{18})\.(png|html)")
            if filename_pattern.match(filename):
                return {
                    "filename": filename,
                    "data": get_object(object_name),
                    "operatorId": object_name_splitted[0],
                }
        return None
