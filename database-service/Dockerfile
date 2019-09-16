FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD 123
ENV MYSQL_DATABASE platia

RUN	mkdir /usr/sql
RUN	chmod 644 /usr/sql

COPY ./db.sql /docker-entrypoint-initdb.d/