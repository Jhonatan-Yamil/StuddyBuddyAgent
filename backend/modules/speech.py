from openai import OpenAI
import tempfile
from modules import rag

client = OpenAI()

from openai import OpenAI
import tempfile
from modules import rag

client = OpenAI()

def audio_to_text(audio_bytes, source_name="audio_upload"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="es"
            )
    text = transcript.text
    if text.strip():  
        rag.add_text_document(text, source=source_name)
    return text