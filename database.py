# import sqlite3
import psycopg2
from psycopg2 import pool
from flask import g
from config import Config
from psycopg2.extras import RealDictCursor

connection_pool = None

def get_pool():
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,
            10,
            dsn=Config.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
    return connection_pool


def get_db():
    if 'db' not in g:
        g.db = get_pool().getconn()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        from database import get_pool
        get_pool().putconn(db)