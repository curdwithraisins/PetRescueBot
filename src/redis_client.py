#!/usr/bin/env python3

import redis
from utils import get_env

class RedisClient(redis.Redis):
    def __init__(self):
        host = get_env("REDIS_HOST")
        password = get_env("REDIS_PASSWORD")
        super().__init__(host, port='6379', db='0', password=password)

    def get_users(self):
            length = super().llen('users')
            val = super().lrange('users', 0, length)
            return val
