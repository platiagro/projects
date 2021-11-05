# -*- coding: utf-8 -*-
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_TENANT = os.getenv("DB_TENANT", "anonymous")
DB_HOST = os.getenv("MYSQL_DB_HOST", "mysql.platiagro")
DB_NAME = os.getenv("MYSQL_DB_NAME", "platiagro")
DB_USER = os.getenv("MYSQL_DB_USER", "root")
DB_PASS = os.getenv("MYSQL_DB_PASSWORD", "")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(
    DB_URL,
    connect_args={"connect_timeout": 10},
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def session_scope():
    """
    Provide a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
    finally:
        session.close()
