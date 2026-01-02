from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Teacher Quiz Tool API", "status": "OK"}

@app.get("/health")
def health():
    return {"status": "healthy"}