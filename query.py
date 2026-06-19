import os
from dotenv import load_dotenv
from groq import Groq

from retrieval import retrieve


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.3-70b-versatile"


def format_context(results: list[dict]) -> str:
    context_blocks = []

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]

        block = f"""
[{i}]
Title: {metadata.get("title", "Unknown title")}
Section: {metadata.get("section", "Unknown section")}
Source: {metadata.get("source", "Unknown source")}
Text:
{result["text"]}
""".strip()

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def format_sources(results: list[dict]) -> list[str]:
    sources = []

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]
        distance = result["distance"]

        source_text = (
            f"[{i}] {metadata.get('title', 'Unknown title')} — "
            f"{metadata.get('section', 'Unknown section')} "
            f"({metadata.get('source', 'Unknown source')}) "
            f"distance={distance:.4f}"
        )

        sources.append(source_text)

    return sources


def ask(question: str) -> dict:
    results = retrieve(question, k=8)

    context = format_context(results)

    system_prompt = """
You are answering questions for a RAG system called The Unofficial Guide.

Rules:
- Answer using ONLY the provided context.
- Do not use outside knowledge.
- Do not guess.
- If the context is not enough, say exactly: "I don't have enough information on that."
- Cite context blocks using bracket citations like [1], [2], or [3].
- Keep the answer clear and direct.
""".strip()

    user_prompt = f"""
Question:
{question}

Retrieved context:
{context}

Answer the question using only the retrieved context.
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": format_sources(results),
    }