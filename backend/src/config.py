import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse


load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv('GG_API_KEY')

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0,
    max_retries=2,
)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = "ai_coach_collection"
DENSE_VECTOR_DIM = 1024 
DENSE_VECTOR_NAME = "dense_vector"
SPARSE_VECTOR_NAME = "sparse_vector"

embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
sparse_embedding_model = FastEmbedSparse(model_name="Qdrant/bm25")

