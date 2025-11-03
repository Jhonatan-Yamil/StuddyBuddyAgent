from openai import OpenAI
import tempfile
import os
from modules import rag

client = OpenAI()

def audio_to_text(audio_bytes: bytes, source_name="audio_upload") -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="es"
            )
        os.unlink(tmp_path) 
        text = transcript.text
        if text.strip():
            rag.add_text_document(text, source=source_name)
        return text
    except Exception as e:
        print(f"Error in transcription: {e}")
        return ""