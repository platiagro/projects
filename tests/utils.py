from io import BytesIO
from json import dumps

from minio.error import BucketAlreadyOwnedByYou

from projects.object_storage import BUCKET_NAME, MINIO_CLIENT


def creates_boston_metadata(dataset_name):
    """Create boston metadata into which the model will import.

    Args:
        dataset_name (str): name the model will search for in Minio.
    """
    try:
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
    except BucketAlreadyOwnedByYou:
        pass

    metadata = {"columns": ["crim", "zn", "indus", "chas", "nox", "rm", "age", "dis",
                            "rad", "tax", "ptratio", "black", "lstat", "medv"],
                "featuretypes": ["Numerical", "Numerical", "Numerical", "Numerical",
                                 "Numerical", "Numerical", "Numerical", "Numerical", "Numerical",
                                 "Numerical", "Numerical", "Numerical", "Numerical", "Numerical"],
                "filename": "boston.metadata"}

    buffer = BytesIO(dumps(metadata).encode())
    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f"datasets/{dataset_name}/{dataset_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_iris_metadata(dataset_name):
    """Create iris metadata into which the model will import.

    Args:
        dataset_name (str): name the model will search for in Minio.
    """
    try:
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
    except BucketAlreadyOwnedByYou:
        pass

    metadata = {"columns": ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm",
                            "PetalWidthCm", "Species"],
                "featuretypes": ["Numerical", "Numerical", "Numerical", "Numerical",
                                 "Categorical"],
                "filename": "iris_mock.metadata"}

    buffer = BytesIO(dumps(metadata).encode())
    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f"datasets/{dataset_name}/{dataset_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_titanic_metadata(dataset_name):
    """Create titanic metadata into which the model will import.

    Args:
        dataset_name (str): name the model will search for in Minio.
    """
    try:
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
    except BucketAlreadyOwnedByYou:
        pass

    metadata = {"columns": ["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp",
                            "Parch", "Ticket", "Fare", "Cabin", "Embarked"],
                "featuretypes": ["Numerical", "Numerical", "Numerical", "Categorical", "Categorical",
                                 "Numerical", "Numerical", "Numerical", "Categorical", "Numerical",
                                 "Categorical", "Categorical"],
                "filename": "iris_mock.metadata"}

    buffer = BytesIO(dumps(metadata).encode())
    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f"datasets/{dataset_name}/{dataset_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_mock_dataset(name, content):
    """Create a mock dataset to be used in unit test.

    Args:
        name (str): dataset name.
        content (bytes): data of the dataset.
    """
    try:
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
    except BucketAlreadyOwnedByYou:
        pass

    file = BytesIO(content)
    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f"datasets/{name}/{name}",
        data=file,
        length=file.getbuffer().nbytes,
    )


def delete_mock_dataset(name):
    """Delete a mock dataset from Minio.

    Args:
        name (str): dataset name.
    """
    for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=f"datasets/{name}", recursive=True):
        MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)
