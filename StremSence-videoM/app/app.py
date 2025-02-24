from flask import Flask, request, jsonify, redirect
from config.minio_config import minio_client, BUCKET_NAME
from config.db_config import db, videos_collection
import datetime
from datetime import timedelta
from flask_cors import CORS
import redis
from celery import Celery

app = Flask(__name__)
CORS(app)

# Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Celery configuration
celery = Celery(__name__, broker='redis://localhost:6379/0')

# Helper function to generate a signed URL
def generate_presigned_url(bucket_name, filename, expiry=timedelta(days=1)):
    return minio_client.presigned_get_object(bucket_name, filename, expires=expiry)

# Celery task to generate and cache signed URL
@celery.task
def cache_signed_url(bucket_name, filename):
    try:
        url = generate_presigned_url(bucket_name, filename)
        redis_client.setex(filename, timedelta(hours=1), url)
        print(f"Cached signed URL for {filename}")
    except Exception as e:
        print(f"Failed to cache signed URL: {str(e)}")

# Route to upload a video
@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Upload file to MinIO
        file_length = len(file.read())
        file.seek(0)
        minio_client.put_object(BUCKET_NAME, file.filename, file, file_length)

        # Save metadata to MongoDB
        video_metadata = {
            "filename": file.filename,
            "upload_time": datetime.datetime.utcnow()
        }
        videos_collection.insert_one(video_metadata)

        # Trigger asynchronous task to cache signed URL
        cache_signed_url.delay(BUCKET_NAME, file.filename)

        return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to stream a video using cached signed URL
@app.route("/stream/<filename>", methods=["GET"])
def stream_video(filename):
    try:
        # Check if URL is cached
        cached_url = redis_client.get(filename)
        if cached_url:
            print("Returning cached signed URL.")
            return redirect(cached_url.decode("utf-8"))

        # If not cached, generate a new signed URL and cache it
        print(f"Generating signed URL for file: {filename}")
        url = generate_presigned_url(BUCKET_NAME, filename)
        redis_client.setex(filename, timedelta(hours=1), url)
        return redirect(url)

    except Exception as e:
        print(f"Error generating signed URL: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
# Route to list all uploaded videos
@app.route("/videos", methods=["GET"])
def list_videos():
    """Retrieves a list of all uploaded videos from MongoDB."""
    try:
        videos = list(videos_collection.find({}, {"_id": 0, "filename": 1, "upload_time": 1}))
        return jsonify({"videos": videos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Health check route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Video upload and streaming service is running."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
