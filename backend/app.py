from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Teacher Quiz Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Teacher Quiz Tool API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "quiz-tool"}
