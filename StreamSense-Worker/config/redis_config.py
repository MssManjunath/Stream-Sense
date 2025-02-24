import os
import redis

def get_redis_client():
    """We will create a Redis Client by calling this function."""
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")

    # Check if REDIS_PORT is a URL and extract the port number
    if REDIS_PORT.startswith("tcp://"):
        # Remove the 'tcp://' part and split at ':'
        REDIS_PORT = REDIS_PORT[len("tcp://"):]
        REDIS_PORT = REDIS_PORT.split(":")[1]  # Get the port part

    REDIS_PORT = int(REDIS_PORT)  # Now it's safe to convert to int
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

redis_client = get_redis_client()
