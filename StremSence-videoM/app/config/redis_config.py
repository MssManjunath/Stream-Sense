import os
import redis

def get_redis_client():
    """We will create a redis Client by calling this 
    function"""
    REDIS_HOST = os.getenv("REDIS_HOST","localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    return redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)

redis_client = get_redis_client()