# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
import logfire
from bs4 import BeautifulSoup


def parse_html(file_path: str) -> str:
    """
    Parses HTML files and extracts clean, readable text content.
    Strips script, style, and other non-content tags before extraction.
    """
    with logfire.span("HTML Parsing", filename=file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_html = f.read()

            soup = BeautifulSoup(raw_html, "html.parser")

            # Remove elements that don't contribute readable content
            for tag in soup(["script", "style", "noscript", "iframe", "svg","header","footer","nav","aside"]):
                tag.decompose()

            # Extract text with sensible spacing between block elements
            text = soup.get_text(separator="\n")

            # Collapse excessive blank lines left behind after stripping tags
            lines = [line.strip() for line in text.splitlines()]
            cleaned_text = "\n".join(line for line in lines if line)

            return cleaned_text

        except Exception as e:
            logfire.error(f"HTML Parse failed: {e}")
            raise e