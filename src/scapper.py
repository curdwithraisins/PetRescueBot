#!/usr/bin/env python3

from redis_client import redis_client
from igramscraper.instagram import Instagram

instagram = Instagram()

def scrap(city):
    accounts = redis_client.get_accounts()
    updates = []
    for acc_idx, account in enumerate(accounts):
        if account['city'] == city:
            print(account)
            posts = instagram.get_medias(account['name'], 10)

            for post_idx, post in enumerate(posts):
                post.city = account['city']
                if account['timestamp'] == post.created_time:
                    posts = posts[:post_idx]
                    break

            updates.extend(posts)
            if (len(posts)):
                account['timestamp'] = posts[0].created_time
            redis_client.update_account(acc_idx, account)
    
    return updates