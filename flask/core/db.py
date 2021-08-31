import datetime
import os
import traceback
import time
from contextlib import contextmanager

import redis
from dotenv import load_dotenv

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')

redis_store = redis.Redis(host=redis_host, port=redis_port, password=redis_password, 
                decode_responses=True)

