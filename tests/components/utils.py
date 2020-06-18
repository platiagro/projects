from io import BytesIO
from json import dumps

from minio.error import BucketAlreadyOwnedByYou, ResponseError

from projects.object_storage import BUCKET_NAME, MINIO_CLIENT


def creates_boston_metadata(dataset_object_name):
    """Create boston metadata into which the model will import.

    Args:
        dataset_object_name (str): name of the dataset that the Model will search in Minio.
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
        object_name=f"datasets/{dataset_object_name}/{dataset_object_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_iris_metadata(dataset_object_name):
    """Create iris metadata into which the model will import.

    Args:
        dataset_object_name (str): name of the dataset that the Model will search in Minio.
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
        object_name=f"datasets/{dataset_object_name}/{dataset_object_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_eucalyptus_metadata(dataset_object_name):
    """Create eucalyptus metadata into which the model will import.

    Args:
        dataset_object_name (str): name of the dataset that the Model will search in Minio.
    """
    try:
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
    except BucketAlreadyOwnedByYou:
        pass

    metadata = {"columns": ["Abbrev", "Rep", "Locality", "Map_Ref", "Latitude", "Altitude",
                            "Rainfall", "Frosts", "Year", "Sp", "PMCno", "DBH", "Ht", "Surv",
                            "Vig", "Ins_res", "Stem_Fm", "Crown_Fm", "Brnch_Fm", "Utility"],
                "featuretypes": ["Categorical", "Numerical", "Categorical", "Categorical", "Categorical",
                                 "Numerical", "Numerical", "Numerical", "Numerical", "Categorical",
                                 "Numerical", "Numerical", "Numerical", "Numerical", "Numerical",
                                 "Numerical", "Numerical", "Numerical", "Numerical", "Categorical"],
                "filename": "eucalyptus_mock.metadata"}
    buffer = BytesIO(dumps(metadata).encode())
    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f"datasets/{dataset_object_name}/{dataset_object_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_titanic_metadata(dataset_object_name):
    """Create titanic metadata into which the model will import.

    Args:
        dataset_object_name (str): name of the dataset that the Model will search in Minio.
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
        object_name=f"datasets/{dataset_object_name}/{dataset_object_name}.metadata",
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )


def creates_mock_dataset(object_name, object_content):
    """Create a mock dataset to be used in unit test.

    Args:
        object_name (str): dataset name.
        object_content (bytes): data of the dataset.
    """
    try:
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
    except BucketAlreadyOwnedByYou:
        pass

    file = BytesIO(object_content)
    MINIO_CLIENT.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f"datasets/{object_name}/{object_name}",
        data=file,
        length=file.getbuffer().nbytes,
    )


def delete_mock_dataset(obeject_name):
    """Delete a mock dataset from Minio.

    Args:
        obeject_name (str): dataset name.
    """
    try:
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=f"datasets/{obeject_name}", recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)
    except ResponseError as err:
        print(err)
