import sqlite3
from contextlib import contextmanager

import psycopg2


@contextmanager
def sqlite_conn(path: str):
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


@contextmanager
def pg_conn(dsn: str):
    conn = psycopg2.connect(dsn)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
