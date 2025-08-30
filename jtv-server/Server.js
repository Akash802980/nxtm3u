
import express from "express";
import fetch from "node-fetch";

const app = express();

const M3U_URL = process.env.M3U_URL; // yaha apna m3u link env me rakho

// Root route (check ke liye)
app.get("/", (req, res) => {
  res.send("Server is running ✅. Use /api/:tvgid to fetch stream.");
});

// API route
app.get("/api/:tvgid", async (req, res) => {
  try {
    const tvgid = req.params.tvgid;
    const response = await fetch(M3U_URL);
    const text = await response.text();

    // Regex to match tvg-id and extract link
    const regex = new RegExp(`#EXTINF.*tvg-id="${tvgid}".*\\n(.*)`, "i");
    const match = text.match(regex);

    if (match) {
      res.json({ link: match[1] });
    } else {
      res.status(404).json({ error: "Channel not found" });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default app;
