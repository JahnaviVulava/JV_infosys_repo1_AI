import os
import re
from pathlib import Path
import traceback
from datetime import datetime

import pdfplumber
from docx import Document


class ResumeParser:
    def __init__(self, upload_dir: str) -> None:
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def parse_file(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._parse_pdf(path)
        if suffix == ".docx":
            return self._parse_docx(path)
        raise ValueError("Unsupported file type")

    def _parse_pdf(self, path: Path) -> str:
        text_chunks: list[str] = []
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    try:
                        text = page.extract_text() or ""
                    except Exception:
                        text = ""
                    text_chunks.append(text)
            return "\n".join(text_chunks)
        except Exception as first_exc:  # try a PyPDF2 fallback for corrupted PDFs
            # log the original exception
            try:
                log_file = self.upload_dir / "parse_errors.log"
                with log_file.open("a", encoding="utf-8") as fh:
                    fh.write(f"[{datetime.utcnow().isoformat()}] pdfplumber failed for {path}: {first_exc}\n")
                    traceback.print_exc(file=fh)
            except Exception:
                pass

            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(str(path))
                for page in reader.pages:
                    try:
                        page_text = page.extract_text() or ""
                    except Exception:
                        page_text = ""
                    text_chunks.append(page_text)
                return "\n".join(text_chunks)
            except Exception:
                # re-raise the original exception to preserve context
                raise first_exc

    def _parse_docx(self, path: Path) -> str:
        document = Document(path)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def save_uploaded_file(self, uploaded_file, filename: str) -> str:
        # IMPORTANT: uploaded_file is the underlying SpooledTemporaryFile
        # from FastAPI's UploadFile. By the time it reaches here, Starlette
        # has already written the incoming multipart data into it, which
        # leaves its cursor sitting at EOF. Reading from it without
        # rewinding first returns b"" and silently writes a 0-byte file to
        # disk, which then fails to parse as a PDF/DOCX downstream (this
        # was the bug: "Failed to process resume" on every upload).
        try:
            uploaded_file.seek(0)
        except Exception:
            pass  # some file-like objects may not support seek; ignore if so

        destination = self.upload_dir / filename
        with destination.open("wb") as buffer:
            buffer.write(uploaded_file.read())
        return str(destination)

    def validate_resume(self, filename: str) -> bool:
        suffix = Path(filename).suffix.lower()
        return suffix in {".pdf", ".docx"}