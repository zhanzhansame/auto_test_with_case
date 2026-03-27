from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf_bytes(file_bytes):
    """
    从 PDF 二进制内容提取文本。
    """
    reader = PdfReader(BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    text = "\n".join(parts).strip()
    if not text:
        raise ValueError("PDF 未提取到可读文本，可能是扫描件或空文档")
    return text
