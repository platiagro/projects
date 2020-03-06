# -*- coding: utf-8 -*-
from io import BytesIO
from os import getenv, SEEK_SET

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


def duplicate_object(source, destination):
    """Makes a copy of an object in MinIO.

    Args:
        source (str): the path to source object.
        destination (str): the destination path.
    """
    data = MINIO_CLIENT.get_object(
        bucket_name=BUCKET_NAME,
        object_name=source,
    )

    buffer = BytesIO()
    for d in data.stream(32*1024):
        buffer.write(d)
    length = buffer.tell()
    buffer.seek(0, SEEK_SET)

    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=destination,
        data=buffer,
        length=length,
    )
