from dotenv import load_dotenv
import os

load_dotenv() 

from fastapi import FastAPI, Request, UploadFile, Form, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from modules import speech, rag, db, image_llm
from schemas.request_models import GenerateRequest
import uvicorn  

app = FastAPI(title="StudyBuddy AI ")

db.init_db()

@app.get("/")
def root():
    return {"message": "StudyBuddy AI is running"}

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Images only.")
    try:
        image_bytes = await file.read()
        llm_context = image_llm.process_image(
            image_bytes,
            prompt_extra="Analiza esta imagen y genera un resumen que pueda ser usado para responder preguntas posteriormente."
        )
        return {
            "message": "Image processed successfully and added to RAG.",
            "llm_context": llm_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/speech-to-text")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Audio files only (WAV/MP3).")
    try:
        audio_bytes = await file.read()
        transcript = speech.audio_to_text(audio_bytes)
        return {"transcription": transcript}
    except Exception as e:
        print(f"Error in transcription: {e}")
        raise HTTPException(status_code=500, detail="Error transcribing audio.")

@app.post("/generate")
async def generate_response(body: GenerateRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        answer = rag.query_knowledge_base(body.query)
        return {"response": answer}
    except Exception as e:
        print(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail="Error generating response.")

@app.post("/upload-pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF required.")
    try:
        results = []
        for file in files:
            if not file.filename.endswith(".pdf"):
                results.append({"filename": file.filename, "success": False, "error": "Not a PDF."})
                continue
            data = await file.read()
            res = rag.add_pdf_document(data, source=file.filename)
            results.append({"filename": file.filename, "success": res})
        return {"results": results}
    except Exception as e:
        print(f"Error uploading PDFs: {e}")
        raise HTTPException(status_code=500, detail="Error uploading PDFs.")
    
@app.post("/generate-quiz")
async def generate_quiz_endpoint(body: GenerateRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        quiz_json = rag.generate_quiz(body.query)
        return {"quiz": quiz_json}
    except Exception as e:
        print(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail="Error generating quiz.")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",        
        host="0.0.0.0",
        port=8000,
        reload=True
    )
