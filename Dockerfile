FROM python:3.6-buster

LABEL maintainer="fabiol@cpqd.com.br"

# Stamps the commit SHA into the labels and ENV vars
ARG BRANCH="master"
ARG COMMIT=""
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}
ENV COMMIT=${COMMIT}
ENV BRANCH=${BRANCH}

RUN apt-get update && \
    apt-get install wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./projects /app/projects
COPY ./setup.py /app/setup.py

RUN pip install /app/

RUN wget https://github.com/platiagro/tasks/archive/v0.1.0.zip && \
    unzip v0.1.0.zip && \
    mv tasks-0.1.0/tasks /samples && \
    mv tasks-0.1.0/config.json /samples && \
    rm -rf v0.1.0.zip tasks-0.1.0/

WORKDIR /app/

EXPOSE 8080

ENTRYPOINT ["python", "-m", "projects.api.main"]
CMD ["--init-db", "--samples-config", "/samples/config.json"]
