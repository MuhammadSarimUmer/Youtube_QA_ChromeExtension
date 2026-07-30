const BACKEND_URL = "http://localhost:8000";

const statusEl = document.getElementById("status");
const loadBtn = document.getElementById("loadBtn");
const askSection = document.getElementById("askSection");
const questionEl = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const answerEl = document.getElementById("answer");

let currentVideoUrl = null;

function setStatus(text, isError) {
  statusEl.textContent = text;
  statusEl.className = isError ? "error" : "";
}

async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab ? tab.url : null;
}

function isYoutubeVideo(url) {
  return !!url && (url.includes("youtube.com/watch") || url.includes("youtu.be/"));
}

async function init() {
  try {
    const url = await getCurrentTabUrl();
    if (!isYoutubeVideo(url)) {
      setStatus("Open a YouTube video to use this extension", true);
      loadBtn.disabled = true;
      return;
    }
    currentVideoUrl = url;
    setStatus("Video detected. Click Load Video to begin.");
  } catch (err) {
    setStatus("Could not read the current tab", true);
  }
}

async function loadVideo() {
  if (!currentVideoUrl) return;
  loadBtn.disabled = true;
  setStatus("Processing video, this may take a moment...");
  try {
    const res = await fetch(`${BACKEND_URL}/api/load`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_url: currentVideoUrl }),
    });
    const data = await res.json();
    if (data.status === "ready") {
      setStatus("Video ready. Ask your question below.");
      askSection.classList.remove("hidden");
    } else {
      setStatus(data.message || "Failed to process video", true);
      loadBtn.disabled = false;
    }
  } catch (err) {
    setStatus("Could not reach the backend server", true);
    loadBtn.disabled = false;
  }
}

async function askQuestion() {
  const question = questionEl.value.trim();
  if (!question) return;
  askBtn.disabled = true;
  answerEl.textContent = "Thinking...";
  try {
    const res = await fetch(`${BACKEND_URL}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_url: currentVideoUrl, question }),
    });
    const data = await res.json();
    if (data.status === "ok") {
      answerEl.textContent = data.answer;
    } else {
      answerEl.textContent = data.message || "Something went wrong";
    }
  } catch (err) {
    answerEl.textContent = "Could not reach the backend server";
  } finally {
    askBtn.disabled = false;
  }
}

loadBtn.addEventListener("click", loadVideo);
askBtn.addEventListener("click", askQuestion);

init();
