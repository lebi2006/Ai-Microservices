# app/qa_service.py
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

_llm = Ollama(model="mistral", temperature=0.0)

_QA_PROMPT = PromptTemplate.from_template(
    """You are a careful assistant that answers questions ONLY using the provided context.
If the answer cannot be found in the context, say "I cannot find this in the provided document."

CONTEXT:
{context}

QUESTION: {question}

Answer with a short, direct response first, then a brief explanation.
"""
)

_MAX_CONTEXT_CHARS = 12000

async def _read_text_file(upload: UploadFile) -> str:
    if upload.content_type not in {"text/plain", "text/markdown"}:
        raise HTTPException(status_code=415, detail="Only text files (.txt, .md) are supported in this minimal build.")
    raw = await upload.read()
    try:
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to decode file as UTF-8 text.")

def _prepare_context(text: str) -> str:
    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No document content provided.")
    if len(text) > _MAX_CONTEXT_CHARS:
        head = text[:_MAX_CONTEXT_CHARS // 2]
        tail = text[-_MAX_CONTEXT_CHARS // 2 :]
        text = head + "\n...\n" + tail
    return text

async def answer_question_over_text_or_file(query: str, inline_text: Optional[str], file: Optional[UploadFile]) -> Tuple[str, str]:
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query is required.")

    doc_text = None
    if inline_text and inline_text.strip():
        doc_text = inline_text.strip()
    elif file is not None:
        doc_text = await _read_text_file(file)
    else:
        raise HTTPException(status_code=400, detail="Provide either 'text' or a text 'file'.")

    context = _prepare_context(doc_text)
    prompt = _QA_PROMPT.format(context=context, question=query.strip())
    output = _llm.invoke(prompt).strip()

    parts = output.split("\n", 1)
    answer = parts[0].strip()
    reasoning = parts[1].strip() if len(parts) > 1 else None
    return answer, reasoning
