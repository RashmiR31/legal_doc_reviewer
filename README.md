# ⚖️ Legal Document Reviewer Assistant

A modular **Streamlit application** for reviewing legal documents (contracts, agreements, policies, etc.).  
It supports **PDF / DOCX / TXT ingestion**, **OCR for scanned PDFs**, and provides:

- **Retrieval QA** → Ask questions about your documents and get answers with source references.  
- **Contract Audit** → Automatically check for missing clauses, summarize structure, and draft suggested clauses.  

---

## ✨ Features

- 📂 **Upload & Ingest Documents**
  - PDF, DOCX, TXT (with OCR fallback for scanned PDFs).
  - Files are chunked and indexed using **OpenAI embeddings + FAISS**.

- 🔍 **Retrieval QA**
  - Ask natural-language questions (e.g., *“Is there a termination clause?”*).
  - Answers include **source snippets** for traceability.

- 🧐 **Audit Contracts**
  - Quick keyword scan for essential clauses (Termination, Governing Law, Confidentiality, etc.).
  - LLM-powered detailed audit:
    - Checklist of present/missing clauses.
    - Draft sample clauses (3–6 sentences) for missing items.

- 💾 **Persistence**
  - Saves uploaded files to disk.
  - Persists FAISS index locally for reuse.
  - Session-state management so queries and answers survive Streamlit reruns.

- 🛠 **Debug & Safety**
  - Clear logging and error messages.
  - Index reset and export options.
  - Uses `allow_dangerous_deserialization=True` only for **trusted local FAISS indexes**.

---

## 🏗 Project Structure

```bash
legal_doc_reviewer/
│
├── app.py    
├── config.py            
│
├── ingestion/
│   ├── __init__.py
│   ├── file_loader.py     
│   ├── splitter.py       
│   ├── index_builder.py  
│
├── chains/
│   ├── __init__.py
│   ├── qa_chain.py       
│   ├── audit_chain.py    
│
├── uploads/               
├── faiss_index/          
│
└── README.md              

```
## Architecture
<img width="430" height="787" alt="image" src="https://github.com/user-attachments/assets/c86d687e-b9bb-49a5-826f-06565f315314" />

## ⚙️ Installation
1. Clone Repo
```
git clone https://github.com/<your-username>/legal_doc_reviewer.git
cd legal_doc_reviewer
```

2. Create Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python Dependencies
```
pip install -r requirements.txt
```

## 🔑 Environment Setup
Set your OpenAI API key:
```
export OPENAI_API_KEY="sk-..."
```

On Windows (PowerShell):
```
$env:OPENAI_API_KEY="sk-..."
```

## Usage
Run the app:
```
streamlit run app.py
```
Open http://localhost:8501 in your browser.

## 🖥 How It Works

1. Upload Documents → Drag and drop PDF/DOCX/TXT.

2. Process Documents: Ingest / Rebuild Index → Extracts text, splits into chunks, builds FAISS vector index.

3. Ask Questions → Query documents with Retrieval QA.

4. Returns direct answers + expandable source snippets.

5. Run Audit →
    - Quick Scan: Checks for key clauses using keyword matching.
    - LLM Audit: Generates a full checklist and suggests drafts for missing clauses.

## Future Enhancements

- Integrate LangGraph Agentic AI for multi-step audits.

- Multi-user access with role-based document management.

- Export audit report as PDF/Word with structured formatting.

- Fine-tuned legal clause detection with custom models.

## Author
Rashmi R
