from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from pypdf import PdfReader
from modules import db
from openai import OpenAI
import io
import os
import uuid

client = OpenAI()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client(Settings(persist_directory="./vector_store"))
collection = chroma_client.get_or_create_collection(name="educational_docs")

# Funciones para agregar documentos 
def add_text_document(text: str, source: str):
    try:
        if not text.strip():
            raise ValueError("Text is empty.")
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        embeddings = embedding_model.encode(chunks).tolist()
        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings
        )
        print(f"Text '{source}' added successfully with {len(chunks)} chunks.")
        return True
    except Exception as e:
        print("Error adding text:", e)
        return False

def add_pdf_document(file_bytes: bytes, source: str):
    try:
        pdf = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        if not text.strip():
            raise ValueError("PDF does not contain readable text.")
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        embeddings = embedding_model.encode(chunks).tolist()
        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings
        )
        print(f"Document {source} added with {len(chunks)} chunks.")
        return True
    except Exception as e:
        print("Error adding document:", e)
        return False

# Retrieval
def retrieve_context(query: str, n_results: int = 3) -> str:
    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs) if docs else ""
    except Exception as e:
        print("Error en retrieval:", e)
        return ""
    
# RAG + LLM
def query_knowledge_base(query: str):
    try:
        context = retrieve_context(query)
        if not context:
            return generate_with_gpt(query)
        return generate_with_gpt(query, context=context)
    except Exception as e:
        print("Error in RAG:", e)
        return generate_with_gpt(query)

def generate_with_gpt(prompt: str, context: str = None, store_in_rag: bool = True):
    history = db.get_last_messages(10)
    history_text = "\n".join(f"{role}: {msg}" for role, msg in history)
    final_prompt = (
        f"Chat history:\n{history_text}\n\nContext:\n{context}\n\nQuestion: {prompt}\n\n"
        if context else f"Chat history:\n{history_text}\n\nQuestion: {prompt}\n\n"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "Eres un tutor educativo experto que responde con claridad, precisión y ejemplos en español."},
            {"role": "user", "content": final_prompt}
        ]
    )
    answer = response.choices[0].message.content
    db.add_message("user", prompt)
    db.add_message("assistant", answer)
    if store_in_rag and len(answer.split()) > 20:
        add_text_document(answer, source="chat_response")    
    return answer

# Quizz
def generate_quiz(topic: str, n_questions: int = 10):
    context = retrieve_context(topic)  
    prompt = f"""
    Genera {n_questions} preguntas de opción múltiple sobre el siguiente tema:
    {context if context else topic}

    Devuelve un JSON nada más que un JSON con la siguiente estructura:
    [
      {{
        "question": "Texto de la pregunta",
        "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
        "answer": "Opción correcta"
      }},
      ...
    ]
    """
    return generate_with_gpt(prompt, store_in_rag=False)