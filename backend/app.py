from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Teacher Quiz Tool", version="2.0")

# Get environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Teacher Quiz Tool API is running!",
        "version": "2.0",
        "status": "active"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "quiz-tool"
    }

@app.post("/api/upload-word")
async def upload_word_document(file: UploadFile = File(...)):
    """Receive and validate Word document upload"""
    
    # Check file type
    if not file.filename.lower().endswith(('.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Only .doc and .docx files are allowed")
    
    try:
        # Check file size (max 10MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
        
        # Create uploads directory
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{file.filename}"
        
        # Save the file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "size": file_size,
            "message": "File uploaded successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/test")
def test_endpoint():
    return {"test": "API is working correctly"}
