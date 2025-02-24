import json
import time
from config.redis_config import redis_client
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from enum import Enum
from config.db_config import connect_to_db

# Configuration
REDIS_QUEUE = "event_logs"
POLLING_INTERVAL = 5  # Poll every 5 seconds
EVENTS_COLLECTION_NAME = "events"
ANALYTICS_COLLECTION_NAME = "analytics"


# Define Enum for Event Types
class EventType(Enum):
    PLAYED = "played"
    PAUSED = "paused"
    MUTED = "muted"
    UNMUTED = "unmuted"
    EXITED = "exited"



def parse_timestamp(timestamp_str):
    """Parse ISO 8601 timestamp string with milliseconds into a datetime object."""
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")


def save_event(collection, event):
    """Save the raw event to MongoDB."""
    collection.insert_one(event)
    print(f"Saved event for session {event['session_id']}")

def update_analytics(collection, event):
    """Update the analytics document for the given session."""
    session_id = event["session_id"]
    event_type = event["event_type"]
    timestamp = parse_timestamp(event["timestamp"])
    video_timestamp = event.get("video_timestamp")

    # Find the existing analytics document or create a new one
    analytics = collection.find_one({"session_id": session_id})

    if not analytics:
        analytics = {
            "session_id": session_id,
            "user_id": event["userid"],
            "video_id": event["video_id"],
            "total_pause_duration": 0,
            "paused_and_never_resumed": False,
            "total_play_duration": 0,
            "total_muted_duration": 0,
            "play_positions": [],
            "pause_positions": [],
            "mute_positions": [],
            "exit_time": None,
            "last_pause_time": None,
            "last_play_time": None,
            "last_mute_time": None,
        }

    # Handle event types using the Enum
    if event_type == EventType.PAUSED.value:
        if analytics["last_play_time"]:
            play_duration = (timestamp - analytics["last_play_time"]).total_seconds()
            analytics["total_play_duration"] += play_duration
            analytics["last_play_time"] = None  # Reset last_play_time after calculating play duration
        analytics["last_pause_time"] = timestamp
        analytics["pause_positions"].append(video_timestamp)

    elif event_type == EventType.PLAYED.value:
        analytics["last_play_time"] = timestamp
        analytics["play_positions"].append(video_timestamp)

    elif event_type == EventType.MUTED.value:
        analytics["last_mute_time"] = timestamp
        analytics["mute_positions"].append(video_timestamp)

    elif event_type == EventType.UNMUTED.value:
        if analytics["last_mute_time"]:
            mute_duration = (timestamp - analytics["last_mute_time"]).total_seconds()
            analytics["total_muted_duration"] += mute_duration
            analytics["last_mute_time"] = None

    elif event_type == EventType.EXITED.value:
        analytics["exit_time"] = timestamp
        if analytics["last_play_time"]:
            play_duration = (timestamp - analytics["last_play_time"]).total_seconds()
            analytics["total_play_duration"] += play_duration
            analytics["last_play_time"] = None
        if analytics["last_mute_time"]:
            mute_duration = (timestamp - analytics["last_mute_time"]).total_seconds()
            analytics["total_muted_duration"] += mute_duration
            analytics["last_mute_time"] = None

    # Check if paused and never resumed
    if analytics["last_pause_time"]:
        analytics["paused_and_never_resumed"] = True

    # Save updated analytics back to MongoDB
    collection.replace_one({"session_id": session_id}, analytics, upsert=True)
    print(f"Updated analytics for session {session_id}")


def consume_events(events_collection, analytics_collection):
    """Continuously consume events from the Redis queue and process them."""
    print("Starting event consumer...")

    while True:
        event_json = redis_client.rpop(REDIS_QUEUE)

        if event_json:
            try:
                event = json.loads(event_json)["event_data"]
                event_type = event["event_type"]

                # Validate event type
                if event_type not in [etype.value for etype in EventType]:
                    print(f"Invalid event type: {event_type}")
                    continue

                print(f"Processing event: {event}")

                # Save the raw event
                save_event(events_collection, event)

                # Update analytics
                update_analytics(analytics_collection, event)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing event: {e}")
        else:
            print("No events in the queue. Waiting...")
            time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    db = connect_to_db()
    events_collection = db[EVENTS_COLLECTION_NAME]
    analytics_collection = db[ANALYTICS_COLLECTION_NAME]
    consume_events(events_collection, analytics_collection)
