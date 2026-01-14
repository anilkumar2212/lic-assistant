from pydantic import BaseModel
from typing import Literal
from uuid import UUID
from datetime import datetime

class ChunkMetadata(BaseModel):
    document_id: UUID
    chunk_id: UUID
    plan_name: str
    product_name: str
    file_name: str
    page_number: int
    type: Literal["text", "table"]
    source: str
    checksum: str
    ingested_at: datetime
