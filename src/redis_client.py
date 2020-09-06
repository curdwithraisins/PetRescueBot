#!/usr/bin/env python3

import redis
from json import dumps, loads
from utils import get_env

class RedisClient(redis.Redis):
    def __init__(self):
        host = get_env("REDIS_HOST")
        password = get_env("REDIS_PASSWORD")
        super().__init__(host, port='6379', db='0', password=password)

    def add_user(self, user):
        super().lpush('users', dumps(user))

    def get_users(self):
            return [ loads(i) for i in super().lrange('users', 0, super().llen('users')) ]

redis_client = RedisClient()