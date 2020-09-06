#!/usr/bin/env python3

from redis_client import redis_client
from igramscraper.instagram import Instagram

instagram = Instagram()

def scrap():
    return instagram.get_medias('curdwithraisins', 10)