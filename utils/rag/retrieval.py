from utils.supabase_client import supabase
from utils.rag.embeddings import generate_embedding


def search_knowledge(query, match_count=5):
    """
    Find the most relevant knowledge chunks
    using vector similarity.
    """

    if not query.strip():
        return []

    # Create embedding for the user's question
    query_embedding = generate_embedding(query)

    # Call Supabase PostgreSQL RPC function
    response = supabase.rpc(
        "match_knowledge_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count
        }
    ).execute()

    return response.data or []