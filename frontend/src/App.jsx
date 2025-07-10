import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [prompt, setPrompt] = useState("");
  const [frames, setFrames] = useState(30); // default frames
  const [jobs, setJobs] = useState([]);
  const [videoUrls, setVideoUrls] = useState({}); // Map job_id to video URL

  const fetchJobs = async () => {
    try {
      const res = await axios.get(`/jobs`);
      setJobs(res.data);

      res.data.forEach(async (job) => {
        if (job.status === "COMPLETED" && !videoUrls[job.job_id]) {
          try {
            const resultRes = await axios.get(`/jobs/${job.job_id}/result`);
            if (resultRes.data.url) {
              setVideoUrls((prev) => ({
                ...prev,
                [job.job_id]: resultRes.data.url,
              }));
            }
          } catch (e) {
            console.error("Error fetching video URL", e);
          }
        }
      });
    } catch (error) {
      console.error("Failed to fetch jobs", error);
    }
  };

  const submitPrompt = async () => {
    if (!prompt) return;

    const framesInt = parseInt(frames, 10);
    if (isNaN(framesInt) || framesInt <= 0) {
      alert("Please enter a valid positive number for frames.");
      return;
    }

    try {
      await axios.post(`/jobs`, { prompt, frames: framesInt });
      setPrompt("");
      setFrames(30); // reset to default
      fetchJobs();
    } catch (e) {
      console.error("Failed to submit prompt", e);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🎥 Text-to-Video Generator</h1>

      <div style={styles.inputRow}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter a prompt..."
          style={styles.input}
        />
        <input
          type="number"
          value={frames}
          onChange={(e) => setFrames(e.target.value)}
          placeholder="Frames"
          style={{ ...styles.input, maxWidth: 100 }}
          min={1}
        />
        <button onClick={submitPrompt} style={styles.button}>
          Submit
        </button>
      </div>

      <h2 style={styles.subheading}>📋 Jobs</h2>
      <ul style={styles.jobList}>
        {jobs.map((job) => (
          <li key={job.job_id} style={styles.jobItem}>
            <p>
              <strong>{job.prompt}</strong> – <em>{job.status}</em> –{" "}
              <span>Frames: {job.frames || "default"}</span>
            </p>
            {job.status === "COMPLETED" && videoUrls[job.job_id] && (
              <div style={styles.videoBlock}>
                <video
                  controls
                  width="400"
                  preload="metadata"
                  style={styles.video}
                >
                  <source src={videoUrls[job.job_id]} type="video/mp4" />
                </video>
                <a
                  href={videoUrls[job.job_id]}
                  download={`video-${job.job_id}.mp4`}
                  style={styles.downloadLink}
                >
                  ⬇️ Download Video
                </a>
              </div>
            )}
            {job.status === "FAILED" && (
              <p style={styles.errorText}>{job.result}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

const styles = {
  container: {
    padding: 30,
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#f9f9f9",
    minHeight: "100vh",
  },
  title: {
    color: "#333",
  },
  inputRow: {
    display: "flex",
    gap: "10px",
    marginBottom: "20px",
    alignItems: "center",
  },
  input: {
    flex: 1,
    padding: "10px",
    fontSize: "16px",
    border: "1px solid #ccc",
    borderRadius: "4px",
  },
  button: {
    padding: "10px 16px",
    fontSize: "16px",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  subheading: {
    color: "#444",
    marginBottom: "10px",
  },
  jobList: {
    listStyle: "none",
    padding: 0,
  },
  jobItem: {
    marginBottom: "30px",
    padding: "15px",
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "8px",
  },
  videoBlock: {
    marginTop: "10px",
  },
  video: {
    display: "block",
    marginBottom: "10px",
    borderRadius: "6px",
  },
  downloadLink: {
    textDecoration: "none",
    color: "#007bff",
    fontWeight: "bold",
  },
  errorText: {
    color: "red",
  },
};

export default App;
