# 🛍️ RAG Retail Agent

**An end-to-end Generative AI Agent for product Q&A in a retail context.**

Built to demonstrate: LangChain RAG pipeline · FastAPI microservice · FAISS vector search · HuggingFace LLMs · MLOps-ready structure (Docker + GitHub Actions CI)

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌─────────────────────────────────┐
│   Streamlit Frontend (UI)       │  ← frontend/app.py
│   http://localhost:8501         │
└──────────────┬──────────────────┘
               │ HTTP POST /ask
               ▼
┌─────────────────────────────────┐
│   FastAPI Microservice          │  ← backend/main.py
│   http://localhost:8000         │
│                                 │
│  ┌──────────────────────────┐  │
│  │  LangChain RAG Chain     │  │
│  │  ┌────────────────────┐  │  │
│  │  │ FAISS Vector Store │  │  │  ← HuggingFace MiniLM embeddings
│  │  └────────┬───────────┘  │  │
│  │           │ top-k chunks  │  │
│  │  ┌────────▼───────────┐  │  │
│  │  │  flan-t5-base LLM  │  │  │  ← Free, runs locally (no API key)
│  │  └────────────────────┘  │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
               │
               ▼
         JSON Response
    { answer, sources, latency_ms }
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the FastAPI backend
```bash
cd backend
uvicorn main:app --reload
# API docs at http://localhost:8000/docs
```

### 3. Start the Streamlit frontend
```bash
cd frontend
streamlit run app.py
# UI at http://localhost:8501
```

### 4. Run in Google Colab
Open `notebooks/RAG_Retail_Agent_Colab.ipynb` in Colab — runs entirely free, no GPU needed.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/status` | Vectorstore status |
| POST | `/ask` | Ask a product question (RAG) |
| GET | `/products` | List all products |
| GET | `/products/search` | Filter by category / price |

### Example: Ask a question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Do you have running shoes under 200 euros?"}'
```

```json
{
  "answer": "Yes, the Nike Air Max 270 is available for €149.99.",
  "source_products": ["Nike Air Max 270", "Adidas Ultraboost 22"],
  "latency_ms": 1243.5
}
```

---

## 🐳 Docker

```bash
docker build -t rag-retail-agent .
docker run -p 8000:8000 rag-retail-agent
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| RAG Framework | LangChain |
| Vector Store | FAISS (CPU) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | google/flan-t5-base (free, local) |
| API Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

## 📈 CV Talking Points

- Built end-to-end RAG pipeline: data ingestion → embedding → FAISS indexing → LLM generation
- Developed Python microservice with FastAPI serving the agent as a REST API
- Deployed free-tier stack: HuggingFace models (no API cost), FAISS (in-memory), Leapcell/Render
- MLOps-ready: Dockerfile for containerization, GitHub Actions CI for automated testing
