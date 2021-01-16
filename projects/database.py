# -*- coding: utf-8 -*-
import os
from functools import update_wrapper

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_HOST = os.getenv("MYSQL_DB_HOST", "mysql.platiagro")
DB_NAME = os.getenv("MYSQL_DB_NAME", "platiagro")
DB_USER = os.getenv("MYSQL_DB_USER", "root")
DB_PASS = os.getenv("MYSQL_DB_PASSWORD", "")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DB_URL,
                       pool_size=20,
                       pool_recycle=300)
Session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()
Base.query = Session.query_property()


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


def session_scope(func):
    """
    Provide a transactional scope around a series of operations.

    Parameters
    ----------
    func : function
    """
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
        except:
            session.rollback()
            Session.remove()
            raise
        else:
            Session.remove()
        return result
    return update_wrapper(wrapper, func)
