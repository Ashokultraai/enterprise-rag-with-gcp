# pyrefly: ignore [missing-import]
import logfire
from pypdf import PdfReader


def parse_pdf(file_path: str) -> str:
    """
    Parses PDF files and extracts text content page by page using pypdf (local, free).

    Note: pypdf extracts embedded text only. Scanned/image-only PDFs have no text
    layer and will return empty — those would need a local OCR step (e.g. tesseract),
    which is intentionally not included here.
    """
    with logfire.span("PDF Parsing", filename=file_path):
        try:
            reader = PdfReader(file_path)

            page_texts = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    page_texts.append(page_text)

            full_text = "\n\n".join(page_texts)

            if not full_text.strip():
                logfire.warn(
                    f"No extractable text found in PDF (likely scanned/image-only): {file_path}"
                )

            return full_text

        except Exception as e:
            logfire.error(f"PDF Parse failed: {e}")
            raise e
