#!/usr/bin/env python
# Kyle Fitzsimmons, 2018
from datetime import date, datetime
import functools
import logging
import platform
import uuid
import time


logger = logging.getLogger(__name__)


# serialize types not handled by default by JSON library to string
def json_serialize(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    # extremely hacky way to naively serialize peewee objects
    if 'peewee.' in str(type(obj)):
        return str(obj)

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def os_is_windows():
    return platform.system() == 'Windows'


class UserNotFoundError(Exception):
    pass


# https://realpython.com/primer-on-python-decorators/#a-few-real-world-examples
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        value = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} completed in {end - start:.2f} s.")
        return value

    return wrapper