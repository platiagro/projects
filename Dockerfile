FROM python:3.8-alpine3.11

RUN apk add --no-cache libstdc++ g++ git

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./projects /app/projects
COPY ./setup.py /app/setup.py

RUN pip install /app/

WORKDIR /app/

EXPOSE 8080

ENTRYPOINT ["python", "-m", "projects.api.main"]
CMD ["--init-db"]