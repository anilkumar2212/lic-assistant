# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(
#     model="gpt-4o",
#     temperature=0
# )

# from langchain_openai import ChatOpenAI
# from src.utils.config_loader import load_config

# config = load_config()

# llm = ChatOpenAI(
#     model=config["llm"]["model"],
#     temperature=config["llm"]["temperature"]
# )

from dotenv import load_dotenv
import os

load_dotenv()  # 🔥 THIS IS THE FIX

from langchain_openai import ChatOpenAI
from src.utils.config_loader import load_config

config = load_config()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Check your .env or environment variables."
    )

llm = ChatOpenAI(
    model=config["llm"]["model"],
    temperature=config["llm"]["temperature"]
)
