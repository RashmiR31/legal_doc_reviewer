# chains/audit_chain.py
import re
from typing import Dict, List, Any
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

DEFAULT_KEYWORDS = {
    "Termination": ["termination", "end of agreement", "terminate"],
    "Governing Law": ["governing law", "jurisdiction"],
    "Confidentiality": ["confidential", "nondisclosure", "non-disclosure", "NDA"],
    "Indemnity": ["indemnify", "hold harmless", "indemnity"],
    "Limitation of Liability": ["limitation of liability", "liability cap", "cap on liability", "cap on damages"],
    "Definitions": ["definitions", "meaning of", "defined terms"],
    "Force Majeure": ["force majeure", "act of god", "unforeseeable"],
    "Payment Terms": ["payment", "invoice", "due date", "fees", "remit"],
    "Assignment": ["assignment", "assign", "successors", "transfer"],
}

def _extract_snippet(text: str, kws: List[str], max_len: int = 300) -> str:
    txt = text.lower()
    for kw in kws:
        m = re.search(rf".{{0,120}}{re.escape(kw.lower())}.{{0,120}}", txt)
        if m:
            return m.group(0).strip()
    return txt[:max_len].strip()

def quick_keyword_scan(retriever, keywords: Dict[str, List[str]] = None, k: int = 6) -> Dict[str, Any]:
    """
    Do an inexpensive, non-LLM keyword-based scan using the retriever.
    Returns {'present': [...], 'missing': [...], 'snippets': {clause: {...}}}
    Each snippet contains 'present' (bool), 'snippet' (str) and optionally 'source' (path).
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS

    present = []
    missing = []
    snippets = {}

    for name, kws in keywords.items():
        try:
            docs: List[Document] = retriever.get_relevant_documents(name)
        except Exception:
            docs = retriever.get_relevant_documents(name) if hasattr(retriever, "get_relevant_documents") else []

        found = False
        snippet_info = {"present": False}
        for d in docs[:k]:
            content = (d.page_content or "").lower()
            if any(kw.lower() in content for kw in kws):
                found = True
                snippet = _extract_snippet(content, kws)
                snippet_info = {
                    "present": True,
                    "snippet": snippet,
                    "source": d.metadata.get("source"),
                    "page": d.metadata.get("page"),
                    "chunk_id": d.metadata.get("chunk_id"),
                }
                break

        if found:
            present.append(name)
        else:
            missing.append(name)

        snippets[name] = snippet_info

    return {"present": present, "missing": missing, "snippets": snippets}


def run_llm_audit(conversational_chain, instructions: str = None) -> str:
    """
    Run a robust LLM-based audit. conversational_chain should be a ConversationalRetrievalChain
    created with your retriever + ChatOpenAI LLM. Returns raw text (LLM answer).
    """
    if instructions is None:
        instructions = (
            "You are an expert commercial contracts reviewer. Audit the provided uploaded documents and:\n"
            "1) Produce a checklist of common commercial contract clauses and mark whether each is present or missing.\n"
            "2) For any missing items, provide a short rationale (1-2 sentences) and a suggested clause draft (3-6 sentences).\n"
            "3) When possible, reference the document names / pages where relevant clauses were found.\n"
            "Keep the output structured, human-readable, and suitable for pasting into a report."
        )

    response = conversational_chain({"question": instructions, "chat_history": []})
    return response.get("answer") or response.get("result") or str(response)


def draft_missing_clauses(conversational_chain, missing: List[str]) -> Dict[str, str]:
    """
    For each missing clause name, ask the chain to produce a short rationale + suggested clause draft.
    Returns a dict mapping clause name -> draft text.
    """
    drafts = {}
    for name in missing:
        q = (
            f"You are a contracts lawyer. For the clause titled '{name}':\n"
            "- Give a 1-2 sentence rationale why this clause matters in a commercial contract.\n"
            "- Provide a concise suggested clause draft (3-6 sentences), ready to paste into a contract.\n"
            "Keep language neutral and modular (suitable for both parties to negotiate)."
        )
        resp = conversational_chain({"question": q, "chat_history": []})
        txt = resp.get("answer") or resp.get("result") or str(resp)
        drafts[name] = txt
    return drafts


# -------------------------
# Simple keyword check
# -------------------------
CRITICAL_KEYWORDS = [
    "termination", "liability", "confidentiality", "dispute",
    "indemnity", "jurisdiction", "intellectual property", "payment",
]

def keyword_scan(docs):
    """Scan for presence of critical keywords in docs."""
    text = " ".join([d.page_content for d in docs])
    found = []
    missing = []
    for kw in CRITICAL_KEYWORDS:
        if kw.lower() in text.lower():
            found.append(kw)
        else:
            missing.append(kw)
    return found, missing


# -------------------------
# LLM-based Audit
# -------------------------
AUDIT_PROMPT = """
You are a legal expert reviewing a contract/document.
Given the following document text, provide an audit report with:

1. Potential risks or red flags
2. Missing or ambiguous clauses
3. Suggestions for improvements
4. Any unusual terms to highlight

Document Text:
{context}

Audit Report:
"""

def run_audit(index, llm):
    """Perform keyword scan + LLM-based audit on documents in FAISS index."""

    docs = index.similarity_search(" ", k=50) 

    if not docs:
        return "No documents found in the index."

    # Keyword scan
    found, missing = keyword_scan(docs)
    keyword_summary = (
        "### 🔑 Keyword Scan\n"
        f"- Found: {', '.join(found) if found else 'None'}\n"
        f"- Missing: {', '.join(missing) if missing else 'None'}\n\n"
    )

    # Run LLM audit
    combined_text = "\n\n".join([d.page_content for d in docs])
    prompt = PromptTemplate.from_template(AUDIT_PROMPT)
    audit_chain = LLMChain(llm=llm, prompt=prompt)

    audit_result = audit_chain.run({"context": combined_text})

    return keyword_summary + "### 🧾 LLM Audit Report\n" + audit_result
