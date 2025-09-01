# app/summarizer.py
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from typing import Literal

_llm = Ollama(model="mistral", temperature=0.2)

_SUMMARY_PROMPT = PromptTemplate.from_template(
    """You are a concise, accurate summarizer.
Write a {length} summary of the following text. Preserve key facts, entities, and numbers.
If the text is already short, paraphrase for clarity.

TEXT:
{input_text}
"""
)

def _length_to_words(length: str) -> str:
    normalized = (length or "short").strip().lower()
    mapping = {
        "short": "in ~3-4 sentences",
        "medium": "in ~8-10 sentences",
        "long": "in a detailed paragraph with bullets if needed"
    }
    return mapping.get(normalized, mapping["short"])

def summarize_text(text: str, length: Literal["short", "medium", "long"] = "short") -> str:
    if not text or not text.strip():
        raise ValueError("Input text is empty.")
    length_words = _length_to_words(length)
    prompt = _SUMMARY_PROMPT.format(length=length_words, input_text=text.strip())
    return _llm.invoke(prompt).strip()
