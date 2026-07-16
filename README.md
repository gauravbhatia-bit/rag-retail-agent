
# 🛍️ RAG Retail Agent

![CI](https://github.com/gauravbhatia-bit/rag-retail-agent/actions/workflows/ci.yml/badge.svg)

**An end-to-end Generative AI Agent for product Q&A in a retail context.**

Built to demonstrate: LangChain RAG pipeline · FastAPI microservice · FAISS vector search · HuggingFace LLMs · MLOps-ready structure (Docker Compose + GitHub Actions CI)

---

## 🏗️ Architecture
User Question
│
▼
┌─────────────────────────────────┐
│ Streamlit Frontend (UI) │ ← frontend/app.py
│ http://localhost:8501 │
└──────────────┬──────────────────┘
│ HTTP POST /ask
▼
┌─────────────────────────────────┐
│ FastAPI Microservice │ ← backend/main.py
│ http://localhost:8000 │
│ │
│ ┌──────────────────────────┐ │
│ │ LangChain RAG Chain │ │
│ │ ┌────────────────────┐ │ │
│ │ │ FAISS Vector Store │ │ │ ← HuggingFace MiniLM embeddings
│ │ └────────┬───────────┘ │ │
│ │ │ top-k chunks │ │
│ │ ┌────────▼───────────┐ │ │
│ │ │ flan-t5-base LLM │ │ │ ← Free, runs locally (no API key)
│ │ └────────────────────┘ │ │
│ └──────────────────────────┘ │
└─────────────────────────────────┘
│
▼
JSON Response
{ answer, sources, latency_ms }

text

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

## 🐳 Docker (Compose)

This project runs as two containers — a FastAPI backend and a Streamlit frontend — orchestrated via Docker Compose.

```bash
docker-compose up --build
```

- Backend available at `http://localhost:8000`
- Frontend available at `http://localhost:8501`

> **Note:** `docker-compose.yml` lives at the project root and defines both services with shared networking.

---

## ⚠️ Deployment Notes

- Deployed to **Render** using platform-driven CD (auto-deploy on push to `main`).
- The current RAG stack (HuggingFace `flan-t5-base` + Torch) exceeds Render's free-tier RAM limit, so the live backend may crash or stay offline on the free plan.
- This limitation is documented intentionally — the CI/CD pipeline, Docker containerization, and deployment config are fully functional and demonstrate the end-to-end DevOps workflow, even though the live free-tier instance is memory-constrained.

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
| Containerization | Docker Compose (backend + frontend) |
| CI/CD | GitHub Actions (pytest + ruff) |

---

## 📈 CV Talking Points

- Built end-to-end RAG pipeline: data ingestion → embedding → FAISS indexing → LLM generation
- Developed Python microservice with FastAPI serving the agent as a REST API
- Containerized with Docker Compose (multi-service: backend + frontend) and set up platform-driven CD to Render
- Diagnosed and documented a real production constraint (free-tier RAM limits) rather than concealing it
- MLOps-ready: GitHub Actions CI running automated pytest + ruff checks on every push
