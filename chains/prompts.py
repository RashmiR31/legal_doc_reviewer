# chains/prompts.py
from langchain.prompts import PromptTemplate

AUDIT_SUMMARY_PROMPT = PromptTemplate.from_template(
    "You are an expert commercial contracts reviewer. Audit the provided documents and produce:\n"
    "1) A checklist of common contract clauses (present/missing).\n"
    "2) Rationale + suggested clause drafts for missing items.\n\n{context}\n\nRespond in a structured format."
)
