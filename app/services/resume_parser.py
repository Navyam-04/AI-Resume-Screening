from abc import ABC, abstractmethod
import fitz  # PyMuPDF
from docx import Document


class ResumeParser(ABC):
    """Contract: give me a file path, I give you back plain text."""

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        ...


class PDFParser(ResumeParser):
    def extract_text(self, file_path: str) -> str:
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()


class DOCXParser(ResumeParser):
    def extract_text(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()


def get_parser(filename: str) -> ResumeParser:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return PDFParser()
    elif lower.endswith(".docx"):
        return DOCXParser()
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")