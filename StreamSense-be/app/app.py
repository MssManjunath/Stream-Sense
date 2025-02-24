from flask import Flask, request, jsonify
import json
from config.redis_config import redis_client
from config.db_config import connect_to_db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REDIS_QUEUE = "event_logs"

db = connect_to_db()
ANALYTICS_COLLECTION = db["analytics"]


@app.route("/api/event", methods=["POST"])
def capture_event():
    """API endpoint to capture events and push them to the Redis queue."""
    event_data = request.json
    redis_client.lpush(REDIS_QUEUE, json.dumps({"event_data": event_data}))
    return jsonify({"status": 200, "data": event_data})


@app.route("/api/queue", methods=["GET"])
def queue():
    """Retrieve all queued events from Redis."""
    queue = redis_client.lrange(REDIS_QUEUE, 0, -1)
    serialized_queue = [item.decode('utf-8', errors='replace') for item in queue]
    return jsonify({'queue': serialized_queue}), 200


@app.route("/api/analytics/user/<string:user_id>", methods=["GET"])
def get_analytics_by_user(user_id):
    """Retrieve analytics based on user ID."""
    analytics = list(ANALYTICS_COLLECTION.find({"user_id": user_id}, {"_id": 0}))
    if analytics:
        return jsonify({"status": 200, "analytics": analytics})
    else:
        return jsonify({"status": 404, "message": "No analytics found for this user."}), 404


@app.route("/api/analytics/video/<string:video_id>", methods=["GET"])
def get_analytics_by_video(video_id):
    """Retrieve analytics based on video ID."""
    analytics = list(ANALYTICS_COLLECTION.find({"video_id": video_id}, {"_id": 0}))
    if analytics:
        return jsonify({"status": 200, "analytics": analytics})
    else:
        return jsonify({"status": 404, "message": "No analytics found for this video."}), 404


@app.route("/api/analytics/video/<string:video_id>/summary", methods=["GET"])
def get_video_summary(video_id):
    """Summarize analytics for a specific video, including highest pause points, play points, etc."""
    analytics = list(ANALYTICS_COLLECTION.find({"video_id": video_id}, {"_id": 0}))

    if not analytics:
        return jsonify({"status": 404, "message": "No analytics found for this video."}), 404

    pause_points = []
    play_points = []
    mute_points = []
    total_pause_duration = 0
    total_play_duration = 0
    total_muted_duration = 0

    for session in analytics:
        pause_points.extend(session.get("pause_positions", []))
        play_points.extend(session.get("play_positions", []))
        mute_points.extend(session.get("mute_positions", []))
        total_pause_duration += session.get("total_pause_duration", 0)
        total_play_duration += session.get("total_play_duration", 0)
        total_muted_duration += session.get("total_muted_duration", 0)

    summary = {
        "video_id": video_id,
        "total_pause_duration": total_pause_duration,
        "total_play_duration": total_play_duration,
        "total_muted_duration": total_muted_duration,
        "pause_points": pause_points,
        "play_points": play_points,
        "mute_points": mute_points,
        "highest_pause_point": max(pause_points, default=None),
        "highest_play_point": max(play_points, default=None),
        "highest_mute_point": max(mute_points, default=None),
    }

    return jsonify({"status": 200, "summary": summary})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

