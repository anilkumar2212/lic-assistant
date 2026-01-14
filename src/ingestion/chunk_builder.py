import re
import tiktoken
from collections import defaultdict
from typing import List
from datetime import datetime
from uuid import uuid4

from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pydantic import BaseModel
from typing import Literal

# ===============================
# TOKENIZER
# ===============================
enc = tiktoken.encoding_for_model("text-embedding-3-small")

def token_length(text: str) -> int:
    return len(enc.encode(text))

def get_last_n_tokens(text: str, n=100) -> str:
    tokens = enc.encode(text)
    return enc.decode(tokens[-n:]) if len(tokens) > n else text


# ===============================
# METADATA MODEL
# ===============================
class ChunkMetadata(BaseModel):
    plan_name: str
    product_name: str
    file_name: str
    page_number: int
    type: Literal["text", "table"]
    source: str


# ===============================
# NORMALIZATION
# ===============================
def normalize_text(text: str) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ===============================
# TABLE HELPERS
# ===============================
def html_table_to_string(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)


# ===============================
# CORE FUNCTION
# ===============================
def blocks_to_documents(blocks) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=token_length
    )

    documents: List[Document] = []
    pages = defaultdict(list)

    for b in blocks:
        pages[b.page_number].append(b)

    prev_page_tail = None

    for page_no in sorted(pages.keys()):
        page_blocks = pages[page_no]
        page_text = "\n\n".join(b.content for b in page_blocks)
        clean_text = page_text

        # TABLE CHUNKS
        for b in page_blocks:
            if b.type == "table":
                table_text = html_table_to_string(b.content)
                documents.append(Document(
                    page_content=normalize_text(table_text),
                    metadata=ChunkMetadata(
                        plan_name=b.plan_name,
                        product_name=b.product_name,
                        file_name=b.file_name,
                        page_number=b.page_number,
                        type="table",
                        source=b.source
                    ).model_dump()
                ))
                clean_text = clean_text.replace(b.content, "")

        # TEXT CHUNKS
        clean_text = normalize_text(clean_text)
        chunks = splitter.split_text(clean_text)

        for i, chunk in enumerate(chunks):
            if i == 0 and prev_page_tail:
                chunk = prev_page_tail + "\n\n" + chunk

            meta = page_blocks[0]
            documents.append(Document(
                page_content=chunk,
                metadata=ChunkMetadata(
                    plan_name=meta.plan_name,
                    product_name=meta.product_name,
                    file_name=meta.file_name,
                    page_number=page_no,
                    type="text",
                    source=meta.source
                ).model_dump()
            ))

        if chunks:
            prev_page_tail = get_last_n_tokens(chunks[-1], 100)
        else:
            prev_page_tail = None

    return documents
