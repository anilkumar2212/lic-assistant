from dotenv import load_dotenv
load_dotenv()  # <-- MUST be first

from langchain_openai import OpenAIEmbeddings
from src.utils.config_loader import load_config

config = load_config()

embeddings = OpenAIEmbeddings(
    model=config["embedding"]["model"]
)
