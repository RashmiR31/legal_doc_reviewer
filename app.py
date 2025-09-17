import os
import streamlit as st

from config import *
from ingestion.file_handlers import save_uploaded_files, load_file_to_docs
from ingestion.index_builder import ingest_files, load_index
from chains.qa_chain import build_llm, build_retriever, build_simple_qa
from chains.audit_chain import run_audit
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="⚖️ Legal Document Reviewer", layout="wide")
st.title("⚖️ Legal Document Reviewer Assistant")

# -------------------------
# OpenAI Key
# -------------------------
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Please set the OPENAI_API_KEY environment variable before running the app.")
    st.stop()

# -------------------------
# Sidebar - Upload + Ingest
# -------------------------
with st.sidebar.form("upload_form"):
    uploaded_files = st.file_uploader(
        "📂 Upload documents",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt"],
    )
    ingest_btn = st.form_submit_button("Process Documents")

if ingest_btn and uploaded_files:
    file_paths = save_uploaded_files(uploaded_files, UPLOAD_DIR)
    st.session_state.index = ingest_files(file_paths, PERSIST_DIR)
    st.success("✅ Documents processed and indexed successfully!")

# -------------------------
# Load Index
# -------------------------
if "index" not in st.session_state:
    st.session_state.index = load_index(PERSIST_DIR)

if not st.session_state.index:
    st.warning("⚠️ No documents found. Upload and process documents from the sidebar.")
    st.stop()

# -------------------------
# Retriever + LLM
# -------------------------
retriever = build_retriever(st.session_state.index)
llm = build_llm(LLM_MODEL)
qa_chain = build_simple_qa(llm, retriever)

# -------------------------
# Tabs: Q&A | Audit
# -------------------------
tab1, tab2 = st.tabs(["💬 Ask Questions", "🧐 Audit Documents"])

# -------------------------
# Tab 1 - Retrieval QA
# -------------------------
with tab1:
    st.subheader("💬 Ask legal questions about your documents")
    user_query = st.text_input("Type your question here:")

    if st.button("Ask"):
        if not user_query.strip():
            st.warning("⚠️ Please enter a question.")
        else:
            with st.spinner("🔎 Searching and generating answer..."):
                response = qa_chain({"query": user_query})
            st.markdown("### 📌 Answer")
            st.write(response["result"])

            with st.expander("📂 Source Documents"):
                for doc in response["source_documents"]:
                    st.write(f"- **{doc.metadata.get('source','Unknown')}**")
                    preview = doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else "")
                    st.caption(preview)

# -------------------------
# Tab 2 - Audit
# -------------------------
with tab2:
    st.subheader("🧐 Quick Audit of Uploaded Documents")

    if st.button("Run Audit"):
        with st.spinner("🔍 Running keyword scan and LLM-based audit..."):
            audit_report = run_audit(st.session_state.index, llm)

        st.markdown("### 📑 Audit Report")
        st.write(audit_report)
