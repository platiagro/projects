# -*- coding: utf-8 -*-
"""Functions that access MinIO object storage."""
from os import getenv

from minio import Minio
from minio.error import S3Error

BUCKET_NAME = "anonymous"

MINIO_ENDPOINT = getenv("MINIO_ENDPOINT", "minio-service.platiagro:9000")
MINIO_ACCESS_KEY = getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = getenv("MINIO_SECRET_KEY", "minio123")
MINIO_REGION_NAME = getenv("MINIO_REGION_NAME", "us-east-1")
MINIO_CLIENT = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    region=MINIO_REGION_NAME,
    secure=False,
)


def make_bucket(name):
    """
    Creates the bucket in MinIO. Ignores exception if bucket already exists.

    Parameters
    ----------
    name : str
        The bucket name.
    """
    try:
        MINIO_CLIENT.make_bucket(name)
    except S3Error as err:
        if not err.code == "BucketAlreadyOwnedByYou":
            raise


def list_objects(prefix):
    """
    Get objects from MinIO.

    Parameters
    ----------
    prefix : str
        String specifying objects returned must begin with.

    Returns
    -------
    list
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET_NAME)

    objects = MINIO_CLIENT.list_objects(
        bucket_name=BUCKET_NAME,
        prefix=prefix,
        recursive=True,
    )

    return objects


def get_object(object_name):
    """
    Get data from object in MinIO.

    Parameters
    ----------
    object_name : str

    Returns
    -------
    bytes
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET_NAME)

    object_data = MINIO_CLIENT.get_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
    ).data

    return object_data


def remove_object(object_name):
    """
    Remove object from MinIO.

    Parameters
    ----------
    object_name : str
        Name of object to remove.
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET_NAME)

    MINIO_CLIENT.remove_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
    )


def remove_objects(prefix):
    """
    Remove objects from MinIO that starts with a prefix.

    Parameters
    ----------
    prefix : str
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET_NAME)

    for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
        MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)
