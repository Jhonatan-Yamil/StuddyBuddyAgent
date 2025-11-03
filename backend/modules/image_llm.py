import base64
from openai import OpenAI
from PIL import Image
import io
from modules import db, rag

client = OpenAI()

def process_image(image_bytes: bytes, prompt_extra: str = "", include_history: bool = False) -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        mime_type = img.format.lower()
    except Exception as e:  
        raise ValueError(f"Invalid image data: {str(e)}")
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    history_text = ""
    if include_history:
        history = db.get_last_messages(5)
        history_text = "\n".join(f"{role}: {msg}" for role, msg in history)
    prompt_text = (
        f"{prompt_extra}\n{history_text}\n\n"
        f"Analiza la siguiente imagen y genera un resumen que pueda ser usado para responder preguntas posteriormente."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un tutor educativo experto capaz de analizar imágenes y explicarlas."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{mime_type};base64,{image_base64}"
                        }
                    }
                ]}
            ]
        )
        answer = response.choices[0].message.content
        rag.add_text_document(answer, source="image_upload")
        return answer
    except Exception as api_e:
        print(f"Error in OpenAI vision: {api_e}")
        raise ValueError("Failed to analyze image with AI.")