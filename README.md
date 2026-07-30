<div align="center">

# 🎬 YouTube Video Q&A — Chrome Extension

### Ask questions about any YouTube video and get instant, context-aware answers powered by AI.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM_Inference-F55036?style=for-the-badge&logo=lightning&logoColor=white)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-6E56CF?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Caption_Extraction-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension_MV3-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/mv3/intro/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Embeddings-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)

</div>

---

## 📖 Overview

**YouTube Video Q&A** is a lightweight Chrome extension paired with a local Python backend that lets you ask natural-language questions about any YouTube video — directly from your browser. It pulls the video's captions, breaks them into searchable chunks, embeds them into a vector store, and uses a fast LLM to answer your questions using only the video's actual content.

No more scrubbing through a 40-minute video looking for the one thing someone said. Just ask.

---

## ✨ Features

- 🎯 **Automatic caption extraction** — pulls subtitles straight from YouTube via `yt-dlp`, no manual transcript needed
- 🧠 **Retrieval-Augmented Generation (RAG)** — answers are grounded in the actual video content, not hallucinated
- ⚡ **Groq-powered inference** — near-instant responses using Groq's LPU-accelerated LLMs
- 💾 **Smart caching** — each video's embeddings are stored once and reused, so re-asking questions is instant
- 🎨 **Minimal, clean UI** — no clutter, no gradients, just a simple red-and-white popup that gets out of your way
- 🛡️ **Robust error handling** — clear feedback for missing captions, unreachable backend, or invalid videos

---

## 🖼️ Screenshots

<div align="center">

**Popup on a non-YouTube page**

<img src="imgs/not_video.PNG" width="500" alt="Extension prompting user to open a YouTube video">

**Asking a question on an active video**

<img src="imgs/yes_video.PNG" width="500" alt="Extension answering a question about video content">

</div>

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Chrome Popup    │  HTTP   │  FastAPI Backend │         │   Groq LLM      │
│  (HTML/CSS/JS)   │ ──────► │  (Python)        │ ──────► │  (gpt-oss-120b) │
└─────────────────┘         └────────┬─────────┘         └─────────────────┘
                                      │
                       ┌──────────────┼───────────────┐
                       ▼              ▼               ▼
                  ┌─────────┐   ┌───────────┐   ┌──────────────┐
                  │ yt-dlp  │   │  Chroma   │   │ HuggingFace  │
                  │ (VTT)   │   │ (Vectors) │   │ (Embeddings) │
                  └─────────┘   └───────────┘   └──────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Extension UI** | HTML, CSS, JavaScript (Chrome Manifest V3) |
| **Backend API** | FastAPI (Python) |
| **Caption Extraction** | yt-dlp + webvtt-py |
| **Text Splitting** | LangChain `RecursiveCharacterTextSplitter` |
| **Embeddings** | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Store** | ChromaDB (persisted per video) |
| **LLM Inference** | Groq API (`openai/gpt-oss-120b`) |
| **Orchestration** | LangChain |

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/MuhammadSarimUmer/Youtube_QA_ChromeExtension.git
cd Youtube_QA_ChromeExtension
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq API key to `.env`:

```
GROQ_API_KEY=your_actual_key_here
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

### 3. Load the extension into Chrome

1. Open `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `extension` folder

### 4. Use it

1. Open any YouTube video with captions
2. Click the extension icon in your toolbar
3. Click **Load Video** and wait for processing
4. Type a question and hit **Ask**

---

## 📂 Project Structure

```
Youtube_QA_ChromeExtension/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
└── imgs/
    ├── not_video.PNG
    └── yes_video.PNG
```

---

## ⚠️ Notes & Limitations

- Videos with captions disabled cannot be processed — the extension will surface a clear error in that case
- The backend must be running locally on port `8000` for the extension to function
- First-time embedding model load may take a moment while HuggingFace weights are cached locally

---

<div align="center">

</div>
