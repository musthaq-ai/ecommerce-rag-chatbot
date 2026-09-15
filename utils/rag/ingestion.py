import json

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document

from utils.supabase_client import supabase
from utils.rag.embeddings import generate_embedding


def extract_text_from_file(uploaded_file):
    """
    Extract text from PDF, TXT, or DOCX files.
    """

    file_name = uploaded_file.name.lower()

    # ---------------------------------------
    # PDF
    # ---------------------------------------

    if file_name.endswith(".pdf"):

        reader = PdfReader(uploaded_file)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)

    # ---------------------------------------
    # TXT
    # ---------------------------------------

    elif file_name.endswith(".txt"):

        return uploaded_file.getvalue().decode(
            "utf-8",
            errors="ignore"
        )

    # ---------------------------------------
    # DOCX
    # ---------------------------------------

    elif file_name.endswith(".docx"):

        document = Document(uploaded_file)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n\n".join(paragraphs)

    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload PDF, TXT, or DOCX."
        )


def ingest_document(
    title,
    content,
    source_type="manual",
    source_url=None
):
    """
    Store a document and its vectorized chunks in Supabase.
    """

    if not title.strip():
        raise ValueError("Document title is required.")

    if not content.strip():
        raise ValueError("Document content is empty.")

    # ---------------------------------------
    # 1. Store original document
    # ---------------------------------------

    document_data = {
        "title": title.strip(),
        "content": content.strip(),
        "source_type": source_type,
        "source_url": source_url
    }

    document_response = (
        supabase
        .table("knowledge_documents")
        .insert(document_data)
        .select()
        .execute()
    )

    if not document_response.data:
        raise Exception(
            "Failed to create knowledge document."
        )

    document_id = document_response.data[0]["id"]

    # ---------------------------------------
    # 2. Chunk document
    # ---------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(
        content.strip()
    )

    if not chunks:
        raise Exception(
            "No chunks were created."
        )

    # ---------------------------------------
    # 3. Generate embeddings
    # ---------------------------------------

    chunk_records = []

    for index, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        chunk_records.append({
            "document_id": document_id,
            "chunk_index": index,
            "content": chunk,
            "embedding": embedding
        })

    # ---------------------------------------
    # 4. Store chunks
    # ---------------------------------------

    (
        supabase
        .table("knowledge_chunks")
        .insert(chunk_records)
        .execute()
    )

    return {
        "document_id": document_id,
        "chunks_created": len(chunk_records)
    }