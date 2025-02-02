import fitz  # PyMuPDF
from markdownify import markdownify
import os
from typing import List
import tiktoken
from config.config import Config
import docx2txt
import logging
import mimetypes
from tqdm import tqdm  # For progress tracking

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def get_file_type(self, file_path: str) -> str:
        """Get MIME type from file path."""
        return mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    def pdf_to_markdown(self, pdf_path: str) -> str:
        """Convert PDF to markdown format."""
        doc = fitz.open(pdf_path)
        text = ""
        
        # Add progress bar for large documents
        for page in tqdm(doc, desc="Processing PDF pages"):
            text += page.get_text()
        
        # Convert to markdown
        markdown_text = markdownify(text, heading_style="ATX")
        return markdown_text
    
    def doc_to_markdown(self, doc_path: str) -> str:
        """Convert DOC/DOCX to markdown format."""
        try:
            # Extract text from the document
            text = docx2txt.process(doc_path)
            
            # Convert to markdown
            markdown_text = markdownify(text, heading_style="ATX")
            return markdown_text
        except Exception as e:
            logger.error(f"Error converting doc to markdown: {str(e)}")
            raise
    
    def file_to_markdown(self, file_path: str) -> str:
        """Convert any supported file to markdown format."""
        mime_type = self.get_file_type(file_path)
        
        if mime_type == 'application/pdf':
            return self.pdf_to_markdown(file_path)
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return self.doc_to_markdown(file_path)
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of specified token size with overlap."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            # Get chunk of tokens
            chunk_end = min(i + Config.CHUNK_SIZE, len(tokens))
            chunk = tokens[i:chunk_end]
            
            # Convert chunk back to text
            chunk_text = self.tokenizer.decode(chunk)
            chunks.append(chunk_text)
            
            # Move to next chunk, considering overlap
            i += (Config.CHUNK_SIZE - Config.CHUNK_OVERLAP)
        
        return chunks
    
    def process_document(self, file_path: str) -> List[str]:
        """Process document: convert to markdown and chunk."""
        try:
            logger.info(f"Processing document: {file_path}")
            markdown_text = self.file_to_markdown(file_path)
            chunks = self.chunk_text(markdown_text)
            logger.info(f"Successfully processed document into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise 