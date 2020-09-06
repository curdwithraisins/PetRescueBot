#!/usr/bin/env python3

from redis_client import RedisClient
from igramscraper.instagram import Instagram

redis_client = RedisClient()
instagram = Instagram()

def scrap():
    print(redis_client.get_users())
    return instagram.get_medias('curdwithraisins', 10)