"""
CVAlign Lens — File Handler Utility
Handles file upload validation and text extraction from supported formats.
"""

import io
from werkzeug.datastructures import FileStorage


ALLOWED_EXTENSIONS = {"pdf", "txt", "doc", "docx"}
MAX_TEXT_LENGTH = 15000  # ~3000 words, sufficient for any resume

# Note: For PDF and DOCX processing, ensure the required libraries (pdfplumber, python-docx) are installed in your environment.

class FileHandler:
    """Handles uploaded resume file validation and text extraction."""

    def extract_text(self, file: FileStorage) -> dict:
        """ Extract text content from an uploaded file.
        Args:
            file: Werkzeug FileStorage object.
        Returns:
            dict with 'text' key on success, 'error' key on failure.
        """
        if not file or not file.filename:
            return {"error": "No file provided."}

        extension = self._get_extension(file.filename)
        if extension not in ALLOWED_EXTENSIONS:
            return {
                "error": f"Unsupported file type '.{extension}'. "
                         f"Supported formats: PDF, TXT, DOC, DOCX."
            }

        file_bytes = file.read()
        if len(file_bytes) == 0:
            return {"error": "Uploaded file is empty."}

        if extension == "pdf":
            return self._extract_from_pdf(file_bytes)
        elif extension == "txt":
            return self._extract_from_txt(file_bytes)
        elif extension in {"doc", "docx"}:
            return self._extract_from_docx(file_bytes)

        return {"error": "Could not process file."}

    def _extract_from_pdf(self, file_bytes: bytes) -> dict:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages).strip()
            if not text:
                return {"error": "PDF appears to be image-based or empty. Please paste your resume text instead."}
            return {"text": text[:MAX_TEXT_LENGTH]}
        except ImportError:
            return {"error": "PDF processing library not available. Please paste your resume text instead."}
        except Exception as e:
            return {"error": f"Could not read PDF: {str(e)}"}

    def _extract_from_txt(self, file_bytes: bytes) -> dict:
        try:
            text = file_bytes.decode("utf-8", errors="ignore").strip()
            if not text:
                return {"error": "Text file is empty."}
            return {"text": text[:MAX_TEXT_LENGTH]}
        except Exception as e:
            return {"error": f"Could not read text file: {str(e)}"}

    def _extract_from_docx(self, file_bytes: bytes) -> dict:
        try:
            import docx
            document = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in document.paragraphs]).strip()
            if not text:
                return {"error": "DOCX file appears to be empty."}
            return {"text": text[:MAX_TEXT_LENGTH]}
        except ImportError:
            return {"error": "DOCX processing library not available. Please paste your resume text instead."}
        except Exception as e:
            return {"error": f"Could not read DOCX file: {str(e)}"}

    def _get_extension(self, filename: str) -> str:
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
