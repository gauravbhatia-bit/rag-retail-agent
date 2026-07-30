
# 🛍️ RAG Retail Agent

![CI](https://github.com/gauravbhatia-bit/rag-retail-agent/actions/workflows/ci.yml/badge.svg)

**An end-to-end Generative AI Agent for product Q&A in a retail context.**

Built to demonstrate: LangChain RAG pipeline · FastAPI microservice · FAISS vector search · HuggingFace LLMs · full CI/CD pipeline (GitHub Actions → Docker Hub → Kubernetes)

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

## 🔄 CI/CD Pipeline

This repo has a fully automated CI/CD pipeline via GitHub Actions (`.github/workflows/ci.yml`):

**Continuous Integration** (runs on every push/PR to `main`):
- `test` — runs the `pytest` suite
- `lint` — runs `ruff` against `backend/` and `frontend/`
- `docker-build` — validates that both Dockerfiles build cleanly

**Continuous Delivery** (runs on every push to `main`, after CI passes):
- `docker-push` — builds and pushes both images to Docker Hub, tagged with both `:latest` and the commit SHA (`:<git-sha>`), so any previous build can be pinned/rolled back to by tag

**Kubernetes manifests** (`k8s/`):
- Separate `Deployment` + `Service` for backend and frontend, pointing at the Docker Hub images
- Includes `readinessProbe`/`livenessProbe` health checks and CPU/memory `requests`/`limits`
- Deployed and tested manually via `kubectl apply` against local (Minikube) and sandboxed (Killercoda) clusters

---

## ⚠️ Deployment & Resource Notes

- **Render**: platform-driven CD (auto-deploy on push to `main`). The RAG stack (HuggingFace `flan-t5-base` + Torch) exceeds Render's free-tier RAM, so the live instance may crash or stay offline on the free plan.
- **Kubernetes**: the same memory footprint (confirmed locally, and again on free K8s sandboxes with ~3.7GB allocatable nodes) causes the backend pod to be evicted or fail to pull/extract cleanly on small/free-tier nodes. The manifests are correct and would run cleanly on a node with adequate resources (~3-4GB allocatable for the backend pod alone).
- This is documented intentionally, not hidden: the CI pipeline, CD to Docker Hub, and K8s deployment configuration are all fully functional and demonstrate the complete DevOps workflow end-to-end. The one constraint — running a multi-GB ML model on free-tier infrastructure — is a real, common MLOps problem (usually solved with dedicated/paid nodes or a smaller distilled model), not a gap in the pipeline itself.

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
| Container Registry | Docker Hub (auto-published via CI/CD) |
| Orchestration | Kubernetes (Deployments, Services, health probes) |
| CI/CD | GitHub Actions (pytest + ruff + Docker build/push pipeline) |

---

## 📈 CV Talking Points

- Built end-to-end RAG pipeline: data ingestion → embedding → FAISS indexing → LLM generation
- Developed Python microservice with FastAPI serving the agent as a REST API
- Designed and implemented a full CI/CD pipeline in GitHub Actions: automated testing, linting, Docker image build validation, and automatic image publishing to Docker Hub (SHA + latest tagging strategy) on every merge to `main`
- Wrote production-style Kubernetes manifests (Deployments, Services, readiness/liveness probes, resource requests/limits) for a multi-service application
- Diagnosed and documented real infrastructure constraints (RAM limits on Render's free tier, disk/memory limits on Kubernetes free-tier sandboxes) rather than concealing them — a realistic MLOps trade-off