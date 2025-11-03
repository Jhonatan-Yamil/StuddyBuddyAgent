import base64
from openai import OpenAI
from modules import db, rag

client = OpenAI()

def process_image(image_bytes: bytes, prompt_extra: str = "") -> str:
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    history = db.get_last_messages(5)
    history_text = "\n".join(f"{role}: {msg}" for role, msg in history)
    prompt_text = (
        f"{prompt_extra}\nChat history:\n{history_text}\n\n"
        f"Analiza la siguiente imagen y genera un resumen que pueda ser usado para responder preguntas posteriormente."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un tutor educativo experto capaz de analizar imágenes y explicarlas."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url", 
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}" 
                    }
                }
            ]}
        ]
    )
    answer = response.choices[0].message.content
    rag.add_text_document(answer, source="image_upload")
    
    return answer