# StudyBuddy AI

StudyBuddy AI es un tutor virtual inteligente que combina un LLM (OpenAI) con una base de conocimiento vectorial (RAG) para ofrecer ayuda educativa personalizada. Permite almacenar documentos (PDFs), transcripciones de audio, imágenes analizadas y el historial de chat para construir contexto y generar respuestas más precisas, resúmenes, explicaciones y quizzes.


## Integrantes

- Jhonatan Cabezas 70416
- Rebeca Navarro 68919
- Valeria Zerain 68019

## Funcionalidades principales

- Respuestas contextuales usando RAG (vector store con Chroma + SentenceTransformers).
- Ingesta de PDFs: se extrae texto de PDFs y se indexa en la RAG.
- Procesamiento de imágenes: análisis de imágenes con el LLM y almacenamiento del resumen en la RAG.
- Transcripción de audio (Whisper/OpenAI audio) y almacenamiento del texto en la RAG.
- Historial de chat (SQLite) usado como contexto en las consultas.
- Generación de quizzes en JSON a partir de un tema o del contexto disponible.
- Endpoints REST simples con FastAPI y frontend estático incluido.

## Arquitectura y componentes

- Backend: FastAPI.
- RAG: ChromaDB + embeddings con `sentence-transformers` (modelo `all-MiniLM-L6-v2`).
- LLM y multimodal: OpenAI (chat completions para generación y visión; audio transcription / Whisper para audio).
- Base de datos local: SQLite (`chat_history.db`) para historial de conversaciones.
- Frontend: archivos estáticos en (chat, formulario de quiz simple).

## Endpoints principales

- POST `/generate` — Genera respuesta a una consulta (usa RAG + LLM).
- POST `/upload-pdf` — Sube uno o más PDFs y los indexa en la RAG.
- POST `/upload-image` — Sube una imagen para análisis, el resumen generado se almacena en la RAG.
- POST `/speech-to-text` — Sube audio (wav/mp3) y obtiene transcripción (se agrega a la RAG).
- POST `/generate-quiz` — Genera un quiz en JSON sobre un tema dado.
- GET `/debug-rag` — Devuelve contenido indexado en la RAG (para depuración).

## Requisitos

- Python 3.12 o Uvicorn.
- Recomendado: entorno virtual (venv).
- Se necesita una clave de OpenAI: exportada en el archivo `.env` como `OPENAI_API_KEY`.

Dependencias principales (en `requirements.txt`): FastAPI, Uvicorn, OpenAI, sentence-transformers, chromadb, pypdf, pillow, python-multipart, python-dotenv, torch, entre otras.

## Cómo levantar la aplicación con uvicorn (Windows / PowerShell)

1. Crear y activar un entorno virtual:

```powershell
.\.venv\Scripts\activate
```

2. Instalar dependencias:

```powershell
uv sync
```

3. Archivo `.env` en `backend/` con clave de OpenAI :

```
OPENAI_API_KEY=clave_aqui
```

4. Ejecutar la aplicación (Uvicorn):

```powershell
fastapi dev .\backend\main.py
```

5. Abrir el navegador en `http://127.0.0.1:8000` para acceder al frontend estático y `http://127.0.0.1:8000/docs` para la documentación de la API y probar directamente los endpoints.


## Cómo levantar la aplicación con python (Windows / PowerShell)

1. Ingresar a la carpeta de backend:

```powershell 
cd backend
```

2. Instalar dependencias usando el documento:
```powershell
pip install -r requirements.txt
```

3. Archivo `.env` en `backend/` con clave de OpenAI :

```
OPENAI_API_KEY=clave_aqui
```

4. Ejecutar la aplicación (python):

```powershell
python main.py
```

5. Abrir el navegador en `http://127.0.0.1:8000` para acceder al frontend estático y `http://127.0.0.1:8000/docs` para la documentación de la API y probar directamente los endpoints.

### Notas operativas:
- Al arrancar, la app inicializa la base SQLite (`chat_history.db`) automáticamente.
- La carpeta `vector_store/` se crea/usa por Chroma para persistencia de embeddings.