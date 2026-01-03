### COMPLETE NEW app.py - WITH POSTGRESQL DATABASE ###
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Teacher Quiz Tool API", version="2.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://boukmn-byte.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/quizdb")
pool = None

# Data Models
class Question(BaseModel):
    question: str
    options: List[str]
    correct: int
    question_type: str = "multiple_choice"  # New field: multiple_choice, true_false, image_based
    image_url: Optional[str] = None  # For image-based questions

class Quiz(BaseModel):
    title: str
    description: Optional[str] = ""
    questions: List[Question]

class QuizResponse(Quiz):
    id: str
    created: str

# Database setup
async def get_db_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        await create_tables()
    return pool

async def create_tables():
    """Create necessary database tables"""
    async with (await get_db_pool()).acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                created TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                quiz_id TEXT REFERENCES quizzes(id) ON DELETE CASCADE,
                question_text TEXT NOT NULL,
                options TEXT[],  -- Array of options
                correct_index INTEGER,
                question_type TEXT DEFAULT 'multiple_choice',
                image_url TEXT
            )
        ''')

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await get_db_pool()

@app.get("/")
async def read_root():
    return {
        "message": "Teacher Quiz Tool API", 
        "status": "OK", 
        "version": "2.0.0",
        "features": ["PostgreSQL", "Multiple Question Types", "Image Support"]
    }

@app.get("/health")
async def health():
    pool = await get_db_pool()
    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
            db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    return {
        "status": "healthy", 
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/quizzes", response_model=List[QuizResponse])
async def get_all_quizzes():
    """Get all saved quizzes with their questions"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Get all quizzes
        quizzes = await conn.fetch("SELECT * FROM quizzes ORDER BY created DESC")
        
        result = []
        for quiz in quizzes:
            # Get questions for this quiz
            questions_data = await conn.fetch(
                "SELECT question_text, options, correct_index, question_type, image_url FROM questions WHERE quiz_id = $1",
                quiz['id']
            )
            
            questions = []
            for q in questions_data:
                questions.append({
                    "question": q['question_text'],
                    "options": q['options'],
                    "correct": q['correct_index'],
                    "question_type": q['question_type'],
                    "image_url": q['image_url']
                })
            
            result.append({
                "id": quiz['id'],
                "title": quiz['title'],
                "description": quiz['description'] or "",
                "created": quiz['created'].isoformat(),
                "questions": questions
            })
        
        return result

@app.get("/api/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    """Get a specific quiz by ID"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        quiz = await conn.fetchrow("SELECT * FROM quizzes WHERE id = $1", quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        questions_data = await conn.fetch(
            "SELECT question_text, options, correct_index, question_type, image_url FROM questions WHERE quiz_id = $1",
            quiz_id
        )
        
        questions = []
        for q in questions_data:
            questions.append({
                "question": q['question_text'],
                "options": q['options'],
                "correct": q['correct_index'],
                "question_type": q['question_type'],
                "image_url": q['image_url']
            })
        
        return {
            "id": quiz['id'],
            "title": quiz['title'],
            "description": quiz['description'] or "",
            "created": quiz['created'].isoformat(),
            "questions": questions
        }

@app.post("/api/quizzes", response_model=dict)
async def create_quiz(quiz: Quiz):
    """Save a new quiz to database"""
    pool = await get_db_pool()
    quiz_id = str(uuid.uuid4())
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Insert quiz
            await conn.execute(
                "INSERT INTO quizzes (id, title, description, created) VALUES ($1, $2, $3, NOW())",
                quiz_id, quiz.title, quiz.description
            )
            
            # Insert questions
            for question in quiz.questions:
                await conn.execute(
                    """INSERT INTO questions 
                    (quiz_id, question_text, options, correct_index, question_type, image_url) 
                    VALUES ($1, $2, $3, $4, $5, $6)""",
                    quiz_id,
                    question.question,
                    question.options,
                    question.correct,
                    question.question_type,
                    question.image_url
                )
    
    return {
        "message": "Quiz saved to database!", 
        "id": quiz_id, 
        "question_count": len(quiz.questions)
    }

@app.delete("/api/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str):
    """Delete a quiz and all its questions"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM quizzes WHERE id = $1", quiz_id)
        
        if result == "DELETE 1":
            return {"message": "Quiz deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Quiz not found")
### END OF NEW app.py ###
