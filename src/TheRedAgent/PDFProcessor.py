import pdfplumber
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles reading and chunking of PDF files."""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_text(self):
        """Extract text from the PDF."""
        full_text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    full_text += page.extract_text()
            logger.info("Successfully extracted text from PDF.")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        return full_text

    def chunk_text(self, text, chunk_size=500):
        """Split text into smaller chunks."""
        chunks = []
        while len(text) > chunk_size:
            last_period_index = text[:chunk_size].rfind(".")
            if last_period_index == -1:
                last_period_index = chunk_size
            chunks.append(text[: last_period_index + 1])
            text = text[last_period_index + 1 :]
        chunks.append(text)
        logger.info(f"Text split into {len(chunks)} chunks.")
        return chunks
