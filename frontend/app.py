"""
RAG Retail Agent - Streamlit Frontend
Connects to FastAPI backend to demonstrate the RAG pipeline
"""

import streamlit as st
import requests
import json
import os

# ── Config ─────────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL","http://localhost:8000")

st.set_page_config(
    page_title="🛍️ RetailBot — AI Product Assistant",
    page_icon="🛍️",
    layout="wide"
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛍️ RetailBot")
    st.caption("Powered by RAG + LangChain + FastAPI")
    st.divider()

    st.subheader("⚙️ Settings")
    backend_url = st.text_input("Backend URL", value=BACKEND_URL)
    top_k = st.slider("Results to retrieve (top_k)", 1, 5, 3)

    st.divider()
    st.subheader("📊 System Status")
    if st.button("Check Status"):
        try:
            r = requests.get(f"{backend_url}/status", timeout=5)
            data = r.json()
            st.success(f"✅ Status: {data['status']}")
            st.info(f"📦 Products indexed: {data['num_products']}")
            st.info(f"🔍 Vectorstore: {'Ready' if data['vectorstore_ready'] else 'Not ready'}")
        except Exception as e:
            st.error(f"❌ Cannot connect to backend: {e}")

# ── Main Area ──────────────────────────────────────────────────────────────────
st.title("🛍️ RetailBot — AI Product Assistant")
st.caption("Ask anything about our products — availability, prices, features, comparisons.")

# Example questions
st.subheader("💡 Try asking:")
example_cols = st.columns(3)
examples = [
    "Do you have running shoes under €200?",
    "What's the best product for post-workout recovery?",
    "Which electronics are in stock?",
    "I need something for cold-weather hiking",
    "What yoga gear do you have?",
    "Tell me about the Samsung Galaxy"
]
for i, ex in enumerate(examples):
    with example_cols[i % 3]:
        if st.button(ex, key=f"ex_{i}"):
            st.session_state["question"] = ex

st.divider()

# ── Chat Interface ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

question = st.text_input(
    "Ask your question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What running shoes do you have under €200?",
    key="main_input"
)

if st.button("🔍 Ask RetailBot", type="primary") and question:
    with st.spinner("Searching product knowledge base..."):
        try:
            response = requests.post(
                f"{backend_url}/ask",
                json={"question": question, "top_k": top_k},
                timeout=60
            )
            data = response.json()

            # Store in chat history
            st.session_state["chat_history"].append({
                "question": question,
                "answer": data["answer"],
                "sources": data["source_products"],
                "latency": data["latency_ms"]
            })
            st.session_state["question"] = ""

        except Exception as e:
            st.error(f"❌ Error: {e}. Make sure the FastAPI backend is running.")

# Display chat history
if st.session_state["chat_history"]:
    st.subheader("💬 Conversation")
    for i, entry in enumerate(reversed(st.session_state["chat_history"])):
        with st.container():
            st.markdown(f"**🧑 You:** {entry['question']}")
            st.markdown(f"**🤖 RetailBot:** {entry['answer']}")
            col1, col2 = st.columns([3, 1])
            with col1:
                if entry["sources"]:
                    st.caption(f"📦 Sources: {', '.join(entry['sources'])}")
            with col2:
                st.caption(f"⚡ {entry['latency']}ms")
            st.divider()

# ── Product Explorer Tab ───────────────────────────────────────────────────────
st.subheader("🗂️ Browse Product Catalog")
col1, col2 = st.columns(2)
with col1:
    category_filter = st.selectbox("Filter by category:", ["All", "Shoes", "Electronics", "Clothing", "Home", "Sports"])
with col2:
    max_price = st.number_input("Max price (€):", min_value=0.0, value=1000.0, step=10.0)

if st.button("🔎 Browse Products"):
    try:
        params = {}
        if category_filter != "All":
            params["category"] = category_filter
        if max_price < 1000.0:
            params["max_price"] = max_price

        r = requests.get(f"{backend_url}/products/search", params=params, timeout=10)
        products = r.json()["products"]

        if products:
            for p in products:
                with st.expander(f"**{p['name']}** — €{p['price']} | {p['category']} | Stock: {p['stock']}"):
                    st.write(p["description"])
        else:
            st.info("No products found with those filters.")
    except Exception as e:
        st.error(f"❌ Cannot connect: {e}")
