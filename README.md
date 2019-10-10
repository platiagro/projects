# PlatIAgro Projects

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [Run Docker](#run-docker)
  - [Run Local](#run-local)
- [Testing](#testing)
- [API](#api)

## Introduction

[![Build Status](https://travis-ci.com/platiagro/projects.svg?branch=master)](https://travis-ci.com/platiagro/projects)
[![codecov](https://codecov.io/gh/platiagro/projects/branch/master/graph/badge.svg)](https://codecov.io/gh/platiagro/projects)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Gitter](https://badges.gitter.im/platiagro/community.svg)](https://gitter.im/platiagro/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Known Vulnerabilities](https://snyk.io//test/github/platiagro/projects/badge.svg?targetFile=package.json)](https://snyk.io//test/github/platiagro/projects?targetFile=package.json)

PlatIAgro Projects management microservice.

## Requirements

The application can be run locally or in a docker container, the requirements for each setup are listed below.

### Local

- [Node.js](https://nodejs.org/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)
- [Docker-Compose](https://docs.docker.com/compose/install/)

## Quick Start

Make sure you have all requirements installed on your computer, then you can run the server in a [docker container](#run-docker) or in your [local machine](#run-local).<br>
**Firstly you need to create a .env file, see the .env.example.**

### Run Docker

Run it :

```bash
$ docker-compose up
```

_The default container port is 4000, you can change on docker-compose.yml_

### Run Local:

Run it :

```bash
$ npm install
$ npm run start
```

Or:

```bash
$ yarn
$ yarn start
```

## Testing

You can run the following command to test the project:

```bash
$ npm install
$ npm test
```

Or:

```bash
$ yarn
$ yarn test
```

To run tests with code coverage:

```bash
$ npm run test-coverage
```

Or:

```bash
$ yarn test-coverage
```

## API

API Reference with examples.

### Projects

**Get Project By Id:** <br>
url: /projects/:projectId

```
curl --location --request GET "localhost:3000/projects/a214d8fc-639f-4088-a9fb-c30ba2a69146"
```

**Get All Projects:** <br>
url: /projects

```
curl --location --request GET "localhost:3000/projects"
```

**Create Project:** <br>
url: /projects

```
curl --location --request POST "localhost:3000/projects" \
  --header "Content-Type: application/json" \
  --data "{
	\"name\": \"ML Example\"
}"
```

**Update Project:** <br>
url: /projects/:projectId

```
curl --location --request PATCH "localhost:3000/projects/a214d8fc-639f-4088-a9fb-c30ba2a69146" \
  --header "Content-Type: application/json" \
  --data "{
	\"name\": \"Machine Learning Example\"
}"
```

### Experiments

**Get Experiment By Id:** <br>
url: /projects/:projectId/experiments/:experimentId

```
curl --location --request GET "localhost:3000/projects/a214d8fc-639f-4088-a9fb-c30ba2a69146/experiments/33f56c0f-12f9-4cf0-889f-29b3b424fd4e"
```

**Get All Experiment:** <br>
url: /projects/:projectId/experiments/

```
curl --location --request GET "localhost:3000/projects/a214d8fc-639f-4088-a9fb-c30ba2a69146/experiments"
```

**Create Experiment:** <br>
url: /projects/:projectId/experiments/

```
curl --location --request POST "localhost:3000/projects/a214d8fc-639f-4088-a9fb-c30ba2a69146/experiments" \
  --header "Content-Type: application/json" \
  --data "{
	\"name\": \"ML Experiment\"
}"
```

**Update Experiment:** <br>
url: /projects/:projectId/experiments/:experimentId

```
curl --location --request PATCH "localhost:3000/projects/a214d8fc-639f-4088-a9fb-c30ba2a69146/experiments/33f56c0f-12f9-4cf0-889f-29b3b424fd4e" \
  --header "Content-Type: application/json" \
  --data "{
    \"name\": \"Auto-featuring Experiment\",
    \"pipelineIdTrain\": \"23266cfd-4ed6-43d6-b8a0-ca8440d251c6\",
    \"pipelineIdDeploy\": \"fe5205f5-7f76-4f57-84ca-ea6dd62670e8\",
    \"datasetId\": \"0a10c0ac-ff3b-42df-ab7a-dc2962a1750c\",
    \"headerId\": \"482b603f-23c1-4a10-9b79-8c5b91c6c0cb\",
    \"targetColumnId\": \"3191a035-97a6-4e29-90d4-034cb1f87237\",
    \"parameters\": \"{ price: 8, auto-featuring: true }\",
    \"position\": 1
}"
```
