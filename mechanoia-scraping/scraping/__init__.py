from . import config
from . import mq

import psycopg2
from redis import StrictRedis


def get_redis_connection(**params):
    params = (params or config.redis_conn_params)
    return StrictRedis(**params)


def get_pg_connection(conn_str=None):
    return psycopg2.connect((conn_str or config.pgsql_conn_str))
