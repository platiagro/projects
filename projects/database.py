# -*- coding: utf-8 -*-
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_HOST = getenv("MYSQL_DB_HOST", "mysql.kubeflow")
DB_NAME = getenv("MYSQL_DB_NAME", "platiagro")
DB_USER = getenv("MYSQL_DB_USER", "root")
DB_PASS = getenv("MYSQL_DB_PASSWORD", "")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DB_URL,
                       convert_unicode=True,
                       pool_size=20,
                       pool_recycle=300)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    import projects.models

    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/mysql"
    tmp_engine = create_engine(db_url, convert_unicode=True)
    conn = tmp_engine.connect()
    text = f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
    conn.execute(text, database=DB_NAME)
    conn.close()

    Base.metadata.create_all(bind=engine)
