# -*- coding: utf-8 -*-
"""Experiments Results controller."""
import io
import re
import zipfile

from projects.exceptions import NotFound
from projects.kfp.runs import get_latest_run_id
from projects.object_storage import list_objects, get_object

class ResultController:
    def __init__(self, session):
        self.session = session

    def get_results(self, experiment_id: str, run_id: str):
        """
        Get results from experiment in a .zip file.

        Parameters
        ----------
        experiment_id: str
        run_id: str
            The run_id. If `run_id=latest`, then returns results from the latest run_id.

        Returns
        -------
        """
        if run_id == "latest":
            run_id = get_latest_run_id(experiment_id)

        zip_file = io.BytesIO()

        has_results = False
        path = f"experiments/{experiment_id}/operators/"
        objects = list_objects(path)

        with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as zipped:
            for object in objects:
                file = self._download_result(object.object_name, run_id)
                if file is not None:
                    filename = f'''{file["operatorId"]}/{file["filename"]}'''
                    zipped.writestr(filename, file["data"])
                    has_results = True

        if not has_results:
            raise NotFound("The specified run has no results")

        zip_file.seek(0)

        return zip_file
    
    def get_operator_results(self, experiment_id: str, run_id: str, operator_id: str):
        """
        Get results from a specific operator in a .zip file.

        Parameters
        ----------
        experiment_id: str
        run_id: str
            The run_id. If `run_id=latest`, then returns results from the latest run_id.
        operator_id: str

        Returns
        -------
        """
        if run_id == "latest":
            run_id = get_latest_run_id(experiment_id)

        zip_file = io.BytesIO()

        has_results = False
        path = f"experiments/{experiment_id}/operators/{operator_id}"
        objects = list_objects(path)

        with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as zipped:
            for object in objects:
                file = self._download_result(object.object_name, run_id)
                if file is not None:
                    zipped.writestr(file["filename"], file["data"])
                    has_results = True

        if not has_results:
            raise NotFound("The specified operator has no results")

        zip_file.seek(0)

        return zip_file

    def _download_result(self, object_name, run_id):
        # split and remove /experiments/{experiment_id}/operators/
        object_name_splitted = object_name.split("/")[3:]

        if object_name_splitted[1] == run_id:
            filename = object_name_splitted[2]
            filename_pattern = re.compile(r"figure-([0-9]{18})\.(png|html)")
            if filename_pattern.match(filename):
                return {"filename": filename,
                        "data": get_object(object_name),
                        "operatorId": object_name_splitted[0]}