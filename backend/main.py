import os
import re
import glob
from unittest import result
from langchain_core.runnables import chain
import webvtt
import yt_dlp
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_ROOT = "./youtube_db"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
model = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)


class VideoContext(BaseModel):
    answer: str = Field(..., description="The answer provided by the model based on the video context")


class LoadRequest(BaseModel):
    video_url: str


class AskRequest(BaseModel):
    video_url: str
    question: str


def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise ValueError("Could not extract a valid YouTube video ID from the URL")
    return match.group(1)


def build_db(video_url: str, video_id: str):
    persist_dir = os.path.join(DB_ROOT, video_id)
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        return Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "vtt",
        "outtmpl": f"{video_id}.%(ext)s",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch video captions: {e}")

    vtt_files = glob.glob(f"{video_id}*.vtt")
    if not vtt_files:
        raise RuntimeError("No captions available for this video")

    vtt_path = vtt_files[0]

    try:
        captions = webvtt.read(vtt_path)
    except Exception as e:
        os.remove(vtt_path)
        raise RuntimeError(f"Failed to parse captions: {e}")

    seen = set()
    lines = []
    for caption in captions:
        text = caption.text.strip().replace("\n", " ")
        if text and text not in seen:
            seen.add(text)
            lines.append(text)

    os.remove(vtt_path)

    full_text = " ".join(lines)
    if not full_text:
        raise RuntimeError("Captions were empty for this video")

    docs = [Document(page_content=full_text, metadata={"source": video_url})]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splitter = text_splitter.split_documents(docs)

    os.makedirs(persist_dir, exist_ok=True)
    return Chroma.from_documents(documents=splitter, embedding=embeddings, persist_directory=persist_dir)


@app.post("/api/load")
def load_video(req: LoadRequest):
    try:
        video_id = extract_video_id(req.video_url)
        build_db(req.video_url, video_id)
        return {"status": "ready", "video_id": video_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/ask")
def ask_question(req: AskRequest):
    try:
        video_id = extract_video_id(req.video_url)
        persist_dir = os.path.join(DB_ROOT, video_id)
        if not (os.path.exists(persist_dir) and os.listdir(persist_dir)):
            return {"status": "error", "message": "Video not loaded yet"}

        db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        context_docs = retriever.invoke(req.question)
        combined_context = "\n\n".join(doc.page_content for doc in context_docs)

        prompt = ChatPromptTemplate([
            ("system", "You are a helpful assistant that answers questions about YouTube video content based on the provided context."),
            ("user", "Given the following context from a YouTube video:\n\n{context}\n\nPlease answer the following question:\n\n{question}")
        ])

        chain = prompt | model
        result = chain.invoke({"context": combined_context, "question": req.question})
        return {"status": "ok", "answer": result.content}
    except Exception as e:
        return {"status": "error", "message": str(e)}