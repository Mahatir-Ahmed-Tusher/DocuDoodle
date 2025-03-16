import os
import re
import fitz  # PyMuPDF
from typing import List, Optional
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
import logging
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace and invalid characters."""
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = ''.join(char for char in text if char.isprintable() or char == '\n')  # Remove non-printable characters
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove multiple newlines
    return text.strip()

def extract_text_from_pdf(file_path: str) -> Optional[str]:
    """
    Extract text from PDF using PyMuPDF (faster than pdfplumber).
    """
    try:
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text("text") for page in doc)
        return clean_text(text) if text else None
    except Exception as e:
        logger.error(f"Error extracting text from {file_path} using PyMuPDF: {e}")
        return None

def extract_text_from_docx(file_path: str) -> Optional[str]:
    """
    Extract text from DOCX with enhanced error handling.
    """
    try:
        doc = Document(file_path)
        text = '\n'.join(para.text for para in doc.paragraphs if para.text.strip())
        return clean_text(text) if text else None
    except Exception as e:
        logger.error(f"Failed to process DOCX {file_path}: {e}")
        return None

def extract_text_from_txt(file_path: str) -> Optional[str]:
    """
    Extract text from plain text files with encoding fallback.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = clean_text(file.read())
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="latin-1") as file:
                text = clean_text(file.read())
        except Exception as e:
            logger.error(f"Failed to read text file {file_path}: {e}")
            return None
    return text

def extract_text_from_file(uploaded_file) -> Optional[str]:
    """
    Extract text from various file types.
    """
    if isinstance(uploaded_file, str):  # Handle direct file paths
        file_path = uploaded_file
    else:  # Handle file-like objects (e.g., uploaded files)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())  # Save file contents temporarily
            file_path = temp_file.name  # Temporary file path

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    try:
        if file_extension == ".pdf":
            text = extract_text_from_pdf(file_path)  # Use PyMuPDF
        elif file_extension == ".docx":
            text = extract_text_from_docx(file_path)
        elif file_extension == ".txt":
            text = extract_text_from_txt(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return None

        if not text:
            logger.warning(f"No text content extracted from {file_path}")
            return None

        return text

    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into chunks with improved handling and validation.
    """
    if not text:
        logger.warning("Empty text provided for splitting")
        return []

    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        
        splits = text_splitter.split_text(text)
        
        logger.info(f"Split text into {len(splits)} chunks")
        
        return splits

    except Exception as e:
        logger.error(f"Error splitting text: {e}")
        return []