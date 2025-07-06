from langchain_qdrant import QdrantVectorStore, RetrievalMode
from src.vectordb.client import client
from src.config import (
    QDRANT_COLLECTION_NAME,
    embedding_model,
    sparse_embedding_model,
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
)

def get_qdrant_store() -> QdrantVectorStore:
    """Initializes and returns the configured QdrantVectorStore object."""
    return QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME,
        embedding=embedding_model,
        sparse_embedding=sparse_embedding_model,
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name=DENSE_VECTOR_NAME,
        sparse_vector_name=SPARSE_VECTOR_NAME,
    )