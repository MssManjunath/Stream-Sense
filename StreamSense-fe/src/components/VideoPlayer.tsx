import React, { useState, useRef } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

interface VideoPlayerProps {
  title: string | null;
  videoUrl: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ title, videoUrl }) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const sessionId = useRef<string>(uuidv4()); // Generate a unique session ID for the session

  const backendUrl = process.env.REACT_APP_BACKEND_URL || "/api";

  const sendEvent = async (eventType: string, videoTimestamp: number) => {
    try {
      const timestamp = new Date().toISOString();
      const eventData = {
        session_id: sessionId.current,
        userid: "user123", // Replace with actual user ID if available
        video_id: title,
        event_type: eventType,
        timestamp,
        video_timestamp: videoTimestamp,
      };

      await axios.post(`${backendUrl}/event`, eventData);
      console.log(`Event sent: ${eventType}`, eventData);
    } catch (error) {
      console.error("Error sending event:", error);
    }
  };

  const handlePlay = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    setIsPlaying(true);
    const videoElement = e.currentTarget;
    sendEvent("played", videoElement.currentTime);
  };

  const handlePause = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    setIsPlaying(false);
    const videoElement = e.currentTarget;
    sendEvent("paused", videoElement.currentTime);
  };

  const handleMute = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    const videoElement = e.currentTarget;
    if (videoElement.muted) {
      sendEvent("muted", videoElement.currentTime);
    } else {
      sendEvent("unmuted", videoElement.currentTime);
    }
  };

  const handleEnded = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    const videoElement = e.currentTarget;
    sendEvent("exited", videoElement.currentTime);
  };

  return (
    <div>
      <h2>Video Streaming</h2>
      <video
        width="100%"
        controls
        onPlay={handlePlay}
        onPause={handlePause}
        onVolumeChange={handleMute}
        onEnded={handleEnded}
      >
        <source src={videoUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      {!isPlaying && <p>Video is paused.</p>}
    </div>
  );
};

export default VideoPlayer;
