import os

import redis

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")

redis_store = redis.Redis(
    host=redis_host, port=redis_port, password=redis_password, decode_responses=True
)
