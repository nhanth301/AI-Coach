from qdrant_client.http import models
from src.vectordb.client import client
from src.config import (
    QDRANT_COLLECTION_NAME, 
    DENSE_VECTOR_DIM, 
    DENSE_VECTOR_NAME, 
    SPARSE_VECTOR_NAME
)

def create_qdrant_collection():
    """Create a collection in Qdrant with configuration for both dense and sparse vectors."""
    try:
        print(f"Attempting to create collection '{QDRANT_COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config={
                DENSE_VECTOR_NAME: models.VectorParams(
                    size=DENSE_VECTOR_DIM,
                    distance=models.Distance.COSINE
                )
            },
            sparse_vectors_config={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
        )
        print(f"✅ Collection '{QDRANT_COLLECTION_NAME}' created successfully!")
    except Exception as e:
        print(f"⚠️ Could not create collection: {e}")

if __name__ == "__main__":
    create_qdrant_collection()