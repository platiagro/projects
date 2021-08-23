# -*- coding: utf-8 -*-
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_HOST = os.getenv("MYSQL_DB_HOST", "mysql.platiagro")
DB_NAME = os.getenv("MYSQL_DB_NAME", "platiagro")
DB_USER = os.getenv("MYSQL_DB_USER", "root")
DB_PASS = os.getenv("MYSQL_DB_PASSWORD", "")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DB_URL,
                       pool_size=32,
                       pool_recycle=300,
                       max_overflow=64)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    import projects.models  # noqa: F401

    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/mysql"
    tmp_engine = create_engine(db_url, convert_unicode=True)
    conn = tmp_engine.connect()
    text = f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
    conn.execute(text, database=DB_NAME)
    conn.close()

    Base.metadata.create_all(bind=engine)


def session_scope():
    """
    Provide a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
    finally:
        session.close()
