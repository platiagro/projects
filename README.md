# PlatIAgro Projects

[![Build Status](https://github.com/platiagro/projects/workflows/Python%20application/badge.svg)](https://github.com/platiagro/projects/actions?query=workflow%3A%22Python+application%22)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=platiagro_projects&metric=alert_status)](https://sonarcloud.io/dashboard?id=platiagro_projects)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Gitter](https://badges.gitter.im/platiagro/community.svg)](https://gitter.im/platiagro/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Known Vulnerabilities](https://snyk.io/test/github/platiagro/projects/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/platiagro/projects?targetFile=requirements.txt)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.6](https://www.python.org/downloads/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Quick Start

Make sure you have all requirements installed on your computer. Then, you may start the server using either a [Docker container](#run-using-docker) or in your [local machine](#run-local).

### Run using Docker

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
```

(Optional) Start a MySQL server instance:

```bash
docker run -d -p 3306:3306 \
  --name mysql \
  --env "MYSQL_DATABASE=$MYSQL_DB_NAME" \
  --env "MYSQL_ROOT_PASSWORD=$MYSQL_DB_PASSWORD" \
  --env "MYSQL_ALLOW_EMPTY_PASSWORD=yes" \
  mysql:5.7
```

(Optional) Start a Jupyter Notebook instance:

```bash
docker run -d -p 8888:8888 \
  --name jupyter \
  jupyter/base-notebook \
  start-notebook.sh --NotebookApp.token=''
```

Then, build a docker image that launches the API server:

```bash
docker build -t platiagro/projects:0.0.2 .
```

Finally, start the API server:

```bash
docker run -it -p 8080:8080 \
  --name projects \
  --env "MINIO_ENDPOINT=$MINIO_ENDPOINT" \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  --env "MYSQL_DB_HOST=$MYSQL_DB_HOST" \
  --env "MYSQL_DB_NAME=$MYSQL_DB_NAME" \
  --env "MYSQL_DB_USER=$MYSQL_DB_USER" \
  --env "MYSQL_DB_PASSWORD=$MYSQL_DB_PASSWORD" \
  --env "JUPYTER_ENDPOINT=$JUPYTER_ENDPOINT" \
  platiagro/projects:0.0.2
```

### Run Local:

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
```

(Optional) Create a virtualenv:

```bash
virtualenv -p python3 venv
. venv/bin/activate
```

Install Python modules:

```bash
pip install .
```

(Optional) Initialize database:

```bash
platiagro-init-db
```

Then, start the API server:

```bash
python -m projects.api.main
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
```

Use the following command to run all tests:

```bash
pytest
```

Use the following command to run lint:

```bash
flake8
```

## API

See the [PlatIAgro Projects API doc](https://platiagro.github.io/projects/) for API specification.
