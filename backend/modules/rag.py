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

def query_knowledge_base(query: str):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        docs = results.get("documents", [[]])[0]
        if not docs:
            print("No relevant documents found. Using GPT-4o directly.")
            return generate_with_gpt(query)
        context = "\n".join(docs)
        return generate_with_gpt(query, context=context)
    except Exception as e:
        print("Error in RAG:", e)
        return generate_with_gpt(query)

def generate_with_gpt(prompt: str, context: str = None):
    history = db.get_last_messages(5)
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
    return answer
