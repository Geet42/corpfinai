"""
RAG Engine: Chunk, embed, and query SEC 10-K filings using ChromaDB.
Enables the agent to answer qualitative questions about company strategy,
risk factors, management outlook, and competitive positioning.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Optional
import hashlib
import logging
import re

logger = logging.getLogger(__name__)

# Persistent ChromaDB client (file-based, zero-config)
_chroma_client = None


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.Client(ChromaSettings(
            anonymized_telemetry=False,
        ))
    return _chroma_client


def _clean_filing_text(text: str) -> str:
    """Clean raw SEC filing HTML/text for better chunking."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove common SEC boilerplate patterns
    text = re.sub(r"&#\d+;", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    return text.strip()


def _extract_sections(text: str) -> dict:
    """Try to identify key 10-K sections by common headers."""
    sections = {}
    section_patterns = [
        ("business_overview", r"(?i)(item\s*1[.\s]|business\b)"),
        ("risk_factors", r"(?i)(item\s*1a[.\s]|risk\s*factors)"),
        ("financial_discussion", r"(?i)(item\s*7[.\s]|management.s discussion)"),
        ("financial_statements", r"(?i)(item\s*8[.\s]|financial statements)"),
    ]

    for name, pattern in section_patterns:
        match = re.search(pattern, text)
        if match:
            start = match.start()
            # Take up to 15000 chars from this section
            sections[name] = text[start : start + 15000]

    return sections


def ingest_filing(ticker: str, filing_text: str) -> int:
    """Chunk and store a 10-K filing in ChromaDB. Returns number of chunks."""
    if not filing_text or len(filing_text.strip()) < 100:
        logger.warning(f"Filing text too short for {ticker}, skipping RAG ingest")
        return 0

    client = _get_chroma_client()
    collection_name = f"filing_{ticker.upper()}"

    # Delete existing collection if present (re-ingest)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    # Clean text
    cleaned = _clean_filing_text(filing_text)

    # Extract sections for metadata tagging
    sections = _extract_sections(cleaned)

    # Chunk the full text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " "],
    )

    chunks = splitter.split_text(cleaned)

    if not chunks:
        return 0

    # Determine which section each chunk belongs to
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{ticker}_{i}_{chunk[:50]}".encode()).hexdigest()
        ids.append(chunk_id)
        documents.append(chunk)

        # Tag with section if identifiable
        section_tag = "general"
        for sec_name, sec_text in sections.items():
            if chunk[:100] in sec_text:
                section_tag = sec_name
                break

        metadatas.append({
            "ticker": ticker.upper(),
            "chunk_index": i,
            "section": section_tag,
        })

    # Add to ChromaDB (in batches of 100)
    batch_size = 100
    for start in range(0, len(ids), batch_size):
        end = min(start + batch_size, len(ids))
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    logger.info(f"RAG: Ingested {len(chunks)} chunks for {ticker}")
    return len(chunks)


def query_filing(
    ticker: str, query: str, n_results: int = 5
) -> List[dict]:
    """Query the 10-K filing chunks. Returns relevant passages with metadata."""
    client = _get_chroma_client()
    collection_name = f"filing_{ticker.upper()}"

    try:
        collection = client.get_collection(collection_name)
    except Exception:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    passages = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else None
            passages.append({
                "text": doc,
                "section": meta.get("section", "unknown"),
                "relevance_score": round(1 - distance, 4) if distance else None,
            })

    return passages


def get_filing_context(ticker: str, query: str, max_chars: int = 4000) -> str:
    """Get formatted context from filing for LLM consumption."""
    passages = query_filing(ticker, query, n_results=5)
    if not passages:
        return f"No 10-K filing data available for {ticker}."

    context_parts = []
    total_chars = 0
    for p in passages:
        if total_chars + len(p["text"]) > max_chars:
            break
        context_parts.append(
            f"[Section: {p['section']} | Relevance: {p.get('relevance_score', 'N/A')}]\n"
            f"{p['text']}"
        )
        total_chars += len(p["text"])

    return "\n\n---\n\n".join(context_parts)
