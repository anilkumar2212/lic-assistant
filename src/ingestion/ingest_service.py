from pathlib import Path
from uuid import uuid4
from datetime import datetime

from src.ingestion.pdf_blocks import extract_pdf_blocks
from src.ingestion.chunk_builder import blocks_to_documents
from src.vectorstore.pgvector_store import vector_store
from src.utils.checksum import file_checksum
from src.utils.logger import get_logger

logger = get_logger("ingestion", "ingestion.log")

def ingest_folder(base_path: str):
    pdfs = list(Path(base_path).rglob("*.pdf"))

    logger.info(f"Found {len(pdfs)} PDFs")

    for pdf in pdfs:
        logger.info(f"Processing: {pdf}")

        checksum = file_checksum(pdf)
        document_id = uuid4()
        ingested_at = datetime.utcnow()

        blocks = extract_pdf_blocks(pdf)
        docs = blocks_to_documents(blocks)

        for d in docs:
            d.metadata.update({
                "document_id": str(document_id),
                "chunk_id": str(uuid4()),
                "checksum": checksum,
                "ingested_at": ingested_at.isoformat()
            })

        vector_store.add_documents(docs)

        logger.info(
            f"Uploaded {len(docs)} chunks for {pdf.name}"
        )
