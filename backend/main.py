from dotenv import load_dotenv
import os

load_dotenv() 

from fastapi import FastAPI, Request, UploadFile, Form, File
from fastapi.responses import JSONResponse
from typing import List
from modules import ocr, speech, rag, db
from schemas.request_models import GenerateRequest
import uvicorn  

app = FastAPI(title="StudyBuddy AI ")

db.init_db()

@app.get("/")
def root():
    return {"message": "StudyBuddy AI is running"}

@app.post("/ocr")
async def process_image(file: UploadFile):
    text = ocr.extract_text(await file.read())
    return {"extracted_text": text}

@app.post("/speech-to-text")
async def transcribe_audio(file: UploadFile):
    transcript = speech.audio_to_text(await file.read())
    return {"transcription": transcript}

@app.post("/generate")
async def generate_response(body: GenerateRequest):
    answer = rag.query_knowledge_base(body.query)
    return {"response": answer}

@app.post("/upload-pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        data = await file.read()
        if file.filename.endswith(".pdf"):
            res = rag.add_pdf_document(data, source=file.filename)
        else:
            res = False
        results.append({"filename": file.filename, "success": res})
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",        
        host="0.0.0.0",
        port=8000,
        reload=True
    )
