from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Teacher Quiz Tool API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Question(BaseModel):
    question: str
    options: List[str]
    correct: int

class Quiz(BaseModel):
    title: str
    description: Optional[str] = ""
    questions: List[Question]

class QuizResponse(Quiz):
    id: str
    created: str

# In-memory storage (for demo)
quizzes_db = []

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Teacher Quiz Tool API", "status": "OK", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/quizzes", response_model=List[QuizResponse])
def get_all_quizzes():
    """Get all saved quizzes"""
    return quizzes_db

@app.get("/api/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: str):
    """Get a specific quiz by ID"""
    for quiz in quizzes_db:
        if quiz["id"] == quiz_id:
            return quiz
    raise HTTPException(status_code=404, detail="Quiz not found")

@app.post("/api/quizzes", response_model=dict)
def create_quiz(quiz: Quiz):
    """Save a new quiz"""
    quiz_data = quiz.dict()
    quiz_data["id"] = str(uuid.uuid4())
    quiz_data["created"] = datetime.now().isoformat()
    quizzes_db.append(quiz_data)
    return {"message": "Quiz saved successfully!", "id": quiz_data["id"], "quiz_count": len(quizzes_db)}

@app.delete("/api/quizzes/{quiz_id}")
def delete_quiz(quiz_id: str):
    """Delete a quiz by ID"""
    global quizzes_db
    initial_length = len(quizzes_db)
    quizzes_db = [quiz for quiz in quizzes_db if quiz["id"] != quiz_id]
    
    if len(quizzes_db) < initial_length:
        return {"message": "Quiz deleted successfully", "quizzes_remaining": len(quizzes_db)}
    else:
        raise HTTPException(status_code=404, detail="Quiz not found")
