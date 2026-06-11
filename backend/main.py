"""
RAG Retail Agent - FastAPI Backend (Microservice)
Uses: LangChain + HuggingFace Embeddings + FAISS + local LLM (no OpenAI cost)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os, time
from pathlib import Path

# --- LangChain & Vector DB ---
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from transformers import pipeline as hf_pipeline

# ── App Setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RAG Retail Agent API",
    description="Generative AI agent for product Q&A using RAG pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global State ───────────────────────────────────────────────────────────────
vectorstore = None
qa_chain = None
product_data = []

# ── Pydantic Models ────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    source_products: list
    latency_ms: float

class IndexStatus(BaseModel):
    status: str
    num_products: int
    vectorstore_ready: bool

# ── Helper: Load & Index Products ─────────────────────────────────────────────
def load_and_index_products(data_path: str = "../data/products.json"):
    global vectorstore, product_data

    with open(data_path, "r") as f:
        product_data = json.load(f)

    # Convert each product into a LangChain Document
    docs = []
    for p in product_data:
        text = (
            f"Product: {p['name']}\n"
            f"Category: {p['category']}\n"
            f"Price: €{p['price']}\n"
            f"Stock: {p['stock']} units available\n"
            f"Description: {p['description']}"
        )
        docs.append(Document(
            page_content=text,
            metadata={"id": p["id"], "name": p["name"], "price": p["price"], "category": p["category"]}
        ))

    # Chunk documents (useful for longer product descriptions)
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    # Embed using free HuggingFace model (runs locally, no API key needed)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Build FAISS vector index
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print(f"[RAG] Indexed {len(chunks)} chunks from {len(product_data)} products")
    return vectorstore

# ── Helper: Build QA Chain ─────────────────────────────────────────────────────
def build_qa_chain():
    global qa_chain, vectorstore

    # Free local LLM via HuggingFace (small model, works without GPU)
    generator = hf_pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_new_tokens=256,
        temperature=0.1
    )
    llm = HuggingFacePipeline(pipeline=generator)

    # Custom prompt for retail context
    prompt_template = """You are a helpful retail assistant for an online store.
Use the following product information to answer the customer's question accurately.
If you don't know the answer from the provided context, say "I don't have that information."

Product Context:
{context}

Customer Question: {question}

Helpful Answer:"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    print("[RAG] QA chain ready")
    return qa_chain

# ── Startup Event ──────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    data_path = Path(__file__).parent.parent / "data" / "products.json"
    load_and_index_products(str(data_path))
    build_qa_chain()

# ── API Endpoints ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"message": "RAG Retail Agent API is running", "docs": "/docs"}

@app.get("/status", response_model=IndexStatus, tags=["Health"])
def status():
    return IndexStatus(
        status="ready" if vectorstore else "not_initialized",
        num_products=len(product_data),
        vectorstore_ready=vectorstore is not None
    )

@app.post("/ask", response_model=QueryResponse, tags=["Agent"])
def ask_question(request: QueryRequest):
    if not qa_chain:
        raise HTTPException(status_code=503, detail="QA chain not initialized")

    start = time.time()
    result = qa_chain({"query": request.question})
    latency = (time.time() - start) * 1000

    # Extract source product names from retrieved docs
    sources = list(set([
        doc.metadata.get("name", "Unknown")
        for doc in result.get("source_documents", [])
    ]))

    return QueryResponse(
        answer=result["result"].strip(),
        source_products=sources,
        latency_ms=round(latency, 2)
    )

@app.get("/products", tags=["Data"])
def get_all_products():
    return {"products": product_data, "total": len(product_data)}

@app.get("/products/search", tags=["Data"])
def search_products(category: str = None, max_price: float = None):
    results = product_data
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    return {"products": results, "total": len(results)}
