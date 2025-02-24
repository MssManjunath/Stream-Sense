import os
import boto3
from dotenv import load_dotenv
from minio import Minio

load_dotenv()

# MinIO configurations
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')


# Initialize the S3 client
# s3_client = boto3.client(
#     's3',
#     endpoint_url=MINIO_ENDPOINT,
#     aws_access_key_id=MINIO_ACCESS_KEY,
#     aws_secret_access_key=MINIO_SECRET_KEY
# )

minio_client = Minio(
    minio_endpoint,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


# minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
# minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'rootuser')
# minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'rootpass123')
# redis_host = os.getenv('REDIS_HOST', 'localhost')

# print(f"MinIO Endpoint: {minio_endpoint}")
# print(f"MinIO Access Key: {minio_access_key}")
# print(f"Redis Host: {redis_host}")

# # Set up Redis client
# redis_client = redis.StrictRedis(host=redis_host, port=6379, db=0)

# # Set up MinIO client
# minio_client = Minio(
#     minio_endpoint,
#     access_key=minio_access_key,
#     secret_key=minio_secret_key,
#     secure=False
# )