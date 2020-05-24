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


def get_object(source):
    """Get an object in MinIO.

    Args:
        source (str): the path to source object.

    Returns:
        bytes: the file contents as bytes.
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET_NAME)

    data = MINIO_CLIENT.get_object(
        bucket_name=BUCKET_NAME,
        object_name=source,
    )

    buffer = BytesIO()
    for d in data.stream(32*1024):
        buffer.write(d)
    buffer.seek(0, SEEK_SET)

    return buffer.read()


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
    MINIO_CLIENT.copy_object(
        bucket_name=BUCKET_NAME,
        object_name=destination,
        object_source=f"{BUCKET_NAME}/{source}"
    )


def list_objects(prefix):
    """Get objects from MinIO.

    Args:
        prefix (str): String specifying objects returned must begin with
    """

    objects = MINIO_CLIENT.list_objects(
        bucket_name=BUCKET_NAME,
        prefix=prefix,
        recursive=True,
    )

    return objects


def remove_object(object_name):
    """Remove object from MinIO.

    Args:
        object_name (str): Name of object to remove
    """

    MINIO_CLIENT.remove_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
    )


def remove_objects(prefix):
    """Remove objects from MinIO that starts with a prefix.

    Args:
        prefix (str): prefix.
    """
    for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
        MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)
