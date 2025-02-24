import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bar, Line, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

interface Analytics {
  video_id: string;
  session_id: string;
  user_id: string;
  total_pause_duration: number;
  total_play_duration: number;
  total_muted_duration: number;
  paused_and_never_resumed: boolean;
  play_positions: number[];
  pause_positions: number[];
  mute_positions: number[];
}

interface VideoAnalyticsProps {
  selectedVideoId: string | null;
}

const VideoAnalytics: React.FC<VideoAnalyticsProps> = ({ selectedVideoId }) => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const backendUrl = "/api";

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!selectedVideoId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(`${backendUrl}/analytics/video/${selectedVideoId}/summary`);
        setAnalytics(response.data.summary || null);
      } catch {
        setError("Failed to fetch analytics. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [selectedVideoId]);

  if (!selectedVideoId) return null;

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2 style={{ textAlign: "center", color: "#333" }}>Video Analytics Dashboard</h2>

      {loading && <p style={{ textAlign: "center", color: "#555" }}>Loading analytics...</p>}

      {!loading && error && <p style={{ textAlign: "center", color: "red" }}>{error}</p>}

      {!loading && !error && analytics && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Session Summary */}
          <div style={{ background: "#f9f9f9", padding: "20px", borderRadius: "8px" }}>
            <h3>Session Summary</h3>
            <p>
              <strong>Session ID:</strong> {analytics.session_id}
            </p>
            <p>
              <strong>User ID:</strong> {analytics.user_id}
            </p>
            <p>
              <strong>Video ID:</strong> {analytics.video_id}
            </p>
            <p>
              <strong>Total Play Duration:</strong> {analytics.total_play_duration} seconds
            </p>
            <p>
              <strong>Total Pause Duration:</strong> {analytics.total_pause_duration} seconds
            </p>
            <p>
              <strong>Total Muted Duration:</strong> {analytics.total_muted_duration} seconds
            </p>
            <p>
              <strong>Paused and Never Resumed:</strong>{" "}
              {analytics.paused_and_never_resumed ? "Yes" : "No"}
            </p>
          </div>

          {/* Visualizations */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            {/* Event Timeline */}
            <div style={{ background: "#fff", padding: "20px", borderRadius: "8px" }}>
              <h4>Event Timeline</h4>
              <Line
                data={{
                  labels: Array.from({ length: analytics.play_positions.length }, (_, i) => i + 1),
                  datasets: [
                    {
                      label: "Play Positions",
                      data: analytics.play_positions,
                      borderColor: "#36A2EB",
                      borderWidth: 2,
                      fill: false,
                    },
                    {
                      label: "Pause Positions",
                      data: analytics.pause_positions,
                      borderColor: "#FF6384",
                      borderWidth: 2,
                      fill: false,
                    },
                    {
                      label: "Mute Positions",
                      data: analytics.mute_positions,
                      borderColor: "#FFCE56",
                      borderWidth: 2,
                      fill: false,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                }}
              />
            </div>

            {/* Session Duration */}
            <div style={{ background: "#fff", padding: "20px", borderRadius: "8px" }}>
              <h4>Session Duration</h4>
              <Bar
                data={{
                  labels: ["Pause", "Play", "Mute"],
                  datasets: [
                    {
                      label: "Duration (seconds)",
                      data: [
                        analytics.total_pause_duration,
                        analytics.total_play_duration,
                        analytics.total_muted_duration,
                      ],
                      backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                }}
              />
            </div>

            {/* Paused and Never Resumed */}
            <div style={{ background: "#fff", padding: "20px", borderRadius: "8px" }}>
              <h4>Paused and Never Resumed</h4>
              <Pie
                data={{
                  labels: ["Resumed", "Paused Forever"],
                  datasets: [
                    {
                      data: [analytics.paused_and_never_resumed ? 0 : 1, analytics.paused_and_never_resumed ? 1 : 0],
                      backgroundColor: ["#36A2EB", "#FF6384"],
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoAnalytics;
