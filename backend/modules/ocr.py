from PIL import Image
import pytesseract
import io

def extract_text(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image, lang="spa")
    return text.strip()
