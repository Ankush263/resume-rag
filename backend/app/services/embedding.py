import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def prepare_document_text(text: str, title: str | None = None) -> str:
    """
    Format document chunks for retrieval.
    Useful for resume/JD chunks.
    """
    safe_title = title or "none"
    return f"title: {safe_title} | text: {text}"


def prepare_query_text(query: str) -> str:
    """
    Format search query for retrieval.
    """
    return f"task: question answering | query: {query}"


def generate_embadding(text: str) -> list[float]:
    """
    Use this for search queries.
    """
    formatted_text = prepare_query_text(text)

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=formatted_text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS
        ),
    )

    return result.embeddings[0].values


def generate_document_embedding(
    text: str,
    title: str | None = None
) -> list[float]:
    """
    Use this for document chunks
    """
    formatted_text = prepare_document_text(text=text, title=title)

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=formatted_text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS
        ),
    )

    return result.embeddings[0].values


def generate_document_embeddings(
    texts: list[str],
    title: str | None = None
) -> list[list[float]]:
    """
    Simple safe version: one API call per chunk.
    """
    embeddings = []

    for text in texts:
        embedding = generate_document_embedding(
            text=text,
            title=title
        )
        embeddings.append(embedding)
    
    return embeddings
