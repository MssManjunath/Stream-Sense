import React, { useState } from "react";
import ListVideos from "./components/ListVideos";
import VideoPlayer from "./components/VideoPlayer";
import VideoAnalytics from "./components/VideoAnalytics";

const App: React.FC = () => {
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [selectedTitle,setSelectedTitle] = useState<string | null>(null);

  const handleVideoSelect = (title: string,filename: string): void => {
    setSelectedVideo(filename);
    setSelectedTitle(title)
  };

  return (
    <div className="App" style={{ padding: "20px" }}>
      <h1>Video Upload, Streaming, and Analytics</h1>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {/* Video List */}
        <div style={{ flex: 1, marginRight: "20px" }}>
          <h2>Available Videos</h2>
          <ListVideos onSelectVideo={handleVideoSelect} />
        </div>

        {/* Video Player */}
        <div style={{ flex: 2, marginRight: "20px" }}>
          {selectedVideo ? (
            <>
              <h2>Video Player</h2>
              <VideoPlayer title = {selectedTitle} videoUrl={selectedVideo} />
            </>
          ) : (
            <p>Select a video to play.</p>
          )}
        </div>

        {/* Video Analytics */}
        <div style={{ flex: 2 }}>
          {selectedVideo ? (
            <>
              <h2>Analytics for Selected Video</h2>
              <VideoAnalytics selectedVideoId={selectedTitle} />
            </>
          ) : (
            <p>Select a video to view analytics.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
