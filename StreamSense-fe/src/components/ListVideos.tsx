import React, { useEffect, useState } from "react";
import mediaJSON from "./mediaJSON.json";

interface Video {
  title: string;
  description: string;
  sources: string[];
  subtitle: string;
  thumb: string;
}

interface ListVideosProps {
  onSelectVideo: (title : string,filename: string) => void;
}

const ListVideos: React.FC<ListVideosProps> = ({ onSelectVideo }) => {
  const [videos, setVideos] = useState<Video[]>([]);

  useEffect(() => {
    // Load videos from mediaJSON
    const loadVideos = () => {
      const videoData = mediaJSON.categories.flatMap((category) => category.videos);
      setVideos(videoData);
    };

    loadVideos();
  }, []);

  return (
    <div>
      <h2>All Videos</h2>
      <ul>
        {videos.map((video, index) => (
          <li key={index}>
            <button onClick={() => onSelectVideo(video.title,video.sources[0])}>
              {video.title}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ListVideos;
