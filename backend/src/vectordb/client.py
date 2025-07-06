from qdrant_client import QdrantClient
from src.config import QDRANT_URL

client = QdrantClient(url=QDRANT_URL)