#!/usr/bin/env python3

import redis
from json import dumps, loads
from utils import get_env

class RedisClient(redis.Redis):
    def __init__(self):
        host = get_env("REDIS_HOST")
        password = get_env("REDIS_PASSWORD")
        super().__init__(host, port='6379', db='0', password=password)

    def add_user(self, city, chat_id):
        super().sadd(city, chat_id)

    def get_users(self, city):
        return [ loads(i) for i in super().smembers(city) ]

    def get_cities(self):
        return [ i.decode('UTF-8') for i in super().lrange('cities', 0, super().llen('cities')) ]

    def get_accounts(self):
        return [ loads(i) for i in super().lrange('accounts', 0, super().llen('accounts')) ]

    def update_account(self, idx, data):
        super().lset('accounts', idx, dumps(data))

redis_client = RedisClient()