from langchain_postgres import PGVector
from src.embeddings.embedder import embeddings
from src.utils.config_loader import load_config
import os

config = load_config()

CONNECTION_STRING = os.getenv("PGVECTOR_URL")

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=config["vectorstore"]["collection_name"],
    connection=CONNECTION_STRING,
    use_jsonb=True,
)
