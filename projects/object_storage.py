# -*- coding: utf-8 -*-
from io import BytesIO
from os import getenv

from minio import Minio
from minio.error import BucketAlreadyOwnedByYou

BUCKET_NAME = "anonymous"

MINIO_CLIENT = Minio(
    endpoint=getenv("MINIO_ENDPOINT", "minio-service.kubeflow:9000"),
    access_key=getenv("MINIO_ACCESS_KEY", "minio"),
    secret_key=getenv("MINIO_SECRET_KEY", "minio123"),
    region=getenv("MINIO_REGION_NAME", "us-east-1"),
    secure=False,
)


def make_bucket(name):
    """Creates the bucket in MinIO. Ignores exception if bucket already exists.

    Args:
        name (str): the bucket name
    """
    try:
        MINIO_CLIENT.make_bucket(name)
    except BucketAlreadyOwnedByYou:
        pass


def put_object(name, data):
    """Puts an object into MinIO.

    Args:
        name (str): the object name
        data (bytes): the content of the object.
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET_NAME)

    stream = BytesIO(data)

    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=name,
        data=stream,
        length=len(data),
    )
