# app/main.py
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Import services
from .summarizer import summarize_text
from .qa_service import answer_question_over_text_or_file
from .learning_path import generate_learning_path

# ------------------- App Setup -------------------
app = FastAPI(
    title="AI Microservices (LangChain + Ollama)",
    version="1.0.0",
    description="Summarization, Document Q&A, and Dynamic Learning Path APIs powered by Ollama (Mistral)."
)

# Allow frontend calls
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5500",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Raw text to summarize")
    length: Optional[str] = Field(default="short", description="Summary length: short|medium|long")

class SummarizeResponse(BaseModel):
    summary: str

class LearningPathRequest(BaseModel):
    goal: str = Field(..., description="Learning goal, e.g., 'data science'")
    background: Optional[str] = Field(default=None, description="Prior knowledge, e.g., 'Python basics'")
    duration_weeks: Optional[int] = Field(default=8, description="Study duration in weeks")
    hours_per_week: Optional[int] = Field(default=6, description="Hours per week")

class QAResponse(BaseModel):
    answer: str
    reasoning: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest):
    try:
        summary = summarize_text(payload.text, payload.length)
        return SummarizeResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qa", response_model=QAResponse)
async def qa_over_document(
    query: str = Form(...),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    try:
        answer, reasoning = await answer_question_over_text_or_file(query, text, file)
        return QAResponse(answer=answer, reasoning=reasoning)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning-path")
async def learning_path(payload: LearningPathRequest):
    try:
        plan = generate_learning_path(
            goal=payload.goal,
            background=payload.background,
            duration_weeks=payload.duration_weeks or 8,
            hours_per_week=payload.hours_per_week or 6,
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
