"""
The Unofficial Guide — RAG app over MIT student-generated knowledge.

Flow per question:
  1. retrieve() returns the top-k chunks from ChromaDB (text + metadata + distance).
  2. We format those chunks into numbered context blocks ([1], [2], ...).
  3. We ask Groq (llama-3.3-70b-versatile) to answer ONLY from that context,
     citing chunks by their numbers.
  4. We build the Sources list ourselves from the retrieved metadata so the
     attribution is guaranteed correct regardless of what the LLM writes.
"""

import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

from retrieval import retrieve


# Load GROQ_API_KEY from .env (see .env.example for the format).
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# How many chunks to pull per query, and which Groq model to use.
TOP_K = 8
MODEL = "llama-3.3-70b-versatile"


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
# The system prompt locks the model into "grounded answering" mode:
#   - Answer ONLY from the numbered context blocks we provide.
#   - Cite the blocks it uses with bracketed numbers like [1], [2].
#   - If the context doesn't cover the question, refuse with a fixed sentence
#     instead of guessing. This is what keeps the system honest about what the
#     student sources actually say.
SYSTEM_PROMPT = """You are The Unofficial Guide, a question-answering assistant \
about MIT classes, Course 6, workload, and student life. You answer using ONLY \
the numbered context blocks provided by the user.

Rules:
- Use only information found in the context blocks. Do not use outside knowledge.
- Cite the blocks you draw from using bracketed numbers like [1], [2], [3]. \
Place a citation right after the claim it supports.
- If the context does not contain enough information to answer, reply exactly: \
"I don't have enough information on that."
- Keep the answer concise and grounded. Do not invent sources, links, or facts."""


def format_context(results: list[dict]) -> str:
    """
    Turn retrieved chunks into numbered context blocks for the prompt.

    Block numbers are 1-based and line up exactly with the Sources list built
    by format_sources(), so a citation like [2] in the answer points at the
    same chunk listed as 2. in Sources.
    """
    blocks = []
    for i, result in enumerate(results, start=1):
        meta = result["metadata"]
        header = f"[{i}] {meta.get('title', 'Untitled')}"
        section = meta.get("section")
        if section:
            header += f" — {section}"
        blocks.append(f"{header}\n{result['text']}")
    return "\n\n".join(blocks)


def format_sources(results: list[dict]) -> str:
    """
    Build the Sources list directly from retrieved metadata.

    This is the programmatic source-attribution guarantee: the numbered list is
    generated from the chunks we actually retrieved, NOT parsed out of the LLM
    response. So even if the model miscites or omits a number, the displayed
    sources are always accurate to what was retrieved.
    """
    lines = []
    for i, result in enumerate(results, start=1):
        meta = result["metadata"]
        title = meta.get("title", "Untitled")
        section = meta.get("section")
        source = meta.get("source", "")
        source_type = meta.get("type", "")

        label = title
        if section:
            label += f" — {section}"

        # Append type and source/URL when available for traceability.
        suffix_parts = [p for p in (source_type, source) if p]
        suffix = f" ({', '.join(suffix_parts)})" if suffix_parts else ""

        lines.append(f"{i}. {label}{suffix}")
    return "\n".join(lines)


def answer_question(question: str) -> str:
    """
    Retrieve relevant chunks, ask Groq to answer from them, and return the
    answer followed by a programmatically generated Sources list.
    """
    question = (question or "").strip()
    if not question:
        return "Please enter a question."

    # 1. Retrieve top-k chunks for the question.
    results = retrieve(question, k=TOP_K)

    if not results:
        return "I don't have enough information on that.\n\nSources:\n(none)"

    # 2. Format the retrieved chunks as numbered context blocks.
    context = format_context(results)

    # 3. Build the user message: the context blocks plus the question.
    user_message = (
        f"Context blocks:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context blocks above, citing them like [1], [2]."
    )

    # 4. Send to Groq. Low temperature keeps the answer grounded and stable.
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    answer = response.choices[0].message.content.strip()

    # 5. Append our own Sources list (not the model's) for guaranteed attribution.
    sources = format_sources(results)

    return f"{answer}\n\nSources:\n{sources}"


# ---------------------------------------------------------------------------
# Gradio interface
# ---------------------------------------------------------------------------
demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(
        lines=2,
        label="Your question",
        placeholder="e.g. Is 6-3 a hard major? What are the best Course 6 classes?",
    ),
    outputs=gr.Textbox(label="Answer", lines=16),
    title="The Unofficial Guide",
    description=(
        "Ask questions about MIT classes, Course 6, workload, and student "
        "experiences based on collected student sources."
    ),
)


if __name__ == "__main__":
    demo.launch()
