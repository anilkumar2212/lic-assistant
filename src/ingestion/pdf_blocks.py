import fitz  # PyMuPDF
import camelot
from pathlib import Path
from collections import defaultdict
from typing import List
from pydantic import BaseModel
from typing import Literal


class Block(BaseModel):
    type: Literal["paragraph", "table"]
    content: str
    page_number: int
    y: float
    plan_name: str
    product_name: str
    file_name: str
    source: str


def extract_pdf_blocks(pdf_path: Path) -> List[Block]:
    plan_name = pdf_path.parent.parent.name
    product_name = pdf_path.parent.name
    file_name = pdf_path.name
    source = str(pdf_path)

    tables = camelot.read_pdf(str(pdf_path), pages="all", flavor="lattice")

    tables_by_page = defaultdict(list)
    table_text_by_page = defaultdict(set)

    for t in tables:
        tables_by_page[t.page].append(t)
        for row in t.df.values:
            for cell in row:
                if isinstance(cell, str):
                    table_text_by_page[t.page].add(
                        " ".join(cell.split()).lower()
                    )

    doc = fitz.open(str(pdf_path))
    blocks: List[Block] = []

    for page_index, page in enumerate(doc):
        page_no = page_index + 1
        table_texts = table_text_by_page.get(page_no, set())

        # Paragraph blocks
        for block in page.get_text("blocks"):
            x0, y0, x1, y1, text, *_ = block
            if not text.strip():
                continue

            cleaned = " ".join(text.split()).lower()
            if any(t in cleaned for t in table_texts):
                continue

            blocks.append(Block(
                type="paragraph",
                content=text.strip(),
                page_number=page_no,
                y=y0,
                plan_name=plan_name,
                product_name=product_name,
                file_name=file_name,
                source=source
            ))

        # Table blocks
        for t in tables_by_page.get(page_no, []):
            blocks.append(Block(
                type="table",
                content=t.df.to_html(index=False),
                page_number=page_no,
                y=9999.0,
                plan_name=plan_name,
                product_name=product_name,
                file_name=file_name,
                source=source
            ))

    doc.close()
    return sorted(blocks, key=lambda b: (b.page_number, b.y))
