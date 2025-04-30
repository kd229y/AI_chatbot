import os
import fitz
import requests
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction

# 全域對話歷史紀錄
chat_history: List[str] = []

app = FastAPI()

# 允許跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Utilities =====

def download_pdf(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def extract_text_from_pdf_file_path(file_path: str) -> str:
    try:
        with fitz.open(file_path) as doc:
            return "".join([page.get_text() for page in doc])
    except Exception as e:
        return f"Error while reading PDF: {str(e)}"

def split_text(text: str, max_chunk_size=500, overlap=50) -> List[str]:
    chunks, start = [], 0
    while start < len(text):
        end = min(start + max_chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start += max_chunk_size - overlap
    return chunks

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model: str = "models/embedding-001", title: str = "Restaurant Menu"):
        self.api_key = api_key
        self.model = model
        self.title = title
        genai.configure(api_key=self.api_key)

    def __call__(self, input: List[str]) -> List[List[float]]:
        return [
            genai.embed_content(
                model=self.model,
                content=doc,
                task_type="retrieval_document",
                title=self.title)["embedding"] for doc in input
        ]

def update_chroma_db(client, collection_name: str, new_documents: List[str]):
    collection = client.get_or_create_collection(collection_name)
    for i, document in enumerate(new_documents):
        collection.add(
            ids=[f"new_doc_{i}"],
            documents=[document],
        )

def get_relevant_passage(query: str, db, name: str, n_results: int = 3) -> List[str]:
    collection = db.get_collection(name)
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]

def make_rag_prompt(query: str, relevant_passages: List[str]) -> str:
    context = "\n\n".join(relevant_passages)
    history = "\n".join(chat_history[-3:])
    return f"""
    Previous Conversation:
    {history}

    Customer's Question:
    {query}

    IMPORTANT:
    - Try to be nice**.
    - Always answer based on the context.
    Provide a concise but friendly response.
    """

def generate_answer(prompt: str) -> str:
    load_dotenv()
    api_key = os.getenv('Geminiapikey')
    if not api_key:
        raise ValueError("Missing Gemini API key")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    return model.generate_content(prompt).text

def initialize_database(db_folder: str, db_name: str) -> chromadb.PersistentClient:
    db_path = os.path.join(os.getcwd(), db_folder)
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    client.get_or_create_collection(db_name)
    return client

# ===== FastAPI 路由 =====

class QueryRequest(BaseModel):
    query: str
    db_name: str

@app.post("/upload_pdf/")
async def upload_pdf(db_name: str = Form(...), file: UploadFile = File(...)):
    filepath = f"./uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf_file_path(filepath)
    chunks = split_text(text)

    client = initialize_database("chroma_db", db_name)
    update_chroma_db(client, db_name, chunks)

    return {"message": f"{db_name} updated with PDF"}


@app.post("/chat/")
async def ask_question(req: QueryRequest):
    client = initialize_database("chroma_db", req.db_name)
    relevant_texts = get_relevant_passage(req.query, client, req.db_name)

    if relevant_texts:
        prompt = make_rag_prompt(req.query, relevant_texts)
        answer = generate_answer(prompt)

        if "recommend" in answer.lower():
            chat_history.append(f"Waiter (previous recommendation): {answer}")

        chat_history.append(f"User: {req.query}")
        chat_history.append(f"Your Waiter: {answer}")
        chat_history[:] = chat_history[-6:]

        return {"response": answer}
    else:
        return {"response": "No relevant information found."}

@app.post("/session")
async def create_session(request: Request):
    global chat_history
    chat_history = []
    return {"message": "Session reset."}

@app.get("/session")
async def list_session(request: Request):

@app.get("/")
def read_root():
    return {"message": "Welcome to the Food Recommendation Chatbot API!"}

@app.get("/session/{id}")
def 