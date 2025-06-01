# document_processor.py
import os
import numpy as np
import PyPDF2
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_CHUNKS
from logger import logger

class DocumentProcessor:
    """Processes documents into searchable chunks using embeddings."""
    
    def __init__(self):
        """Initialize with sentence transformer model for embeddings."""
        self.chunks: List[str] = []
        self.embeddings: np.ndarray = None
        # use model all-MiniLM-L6-v2
        logger.info("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")

    def process_document(self, file_path: str) -> None:
        """Process document into chunks and generate embeddings."""
        logger.info(f"Processing document: {file_path}")

        # Extract text from PDF or TXT
        if file_path.lower().endswith('.pdf'):
            logger.info("Extracting text from PDF...")
            text = self._extract_pdf_text(file_path)
        elif file_path.lower().endswith('.txt'):
            logger.info("Reading text file...")
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")

        # Clean and chunk text
        text = text.replace('\n', ' ').strip()
        # from config 
        logger.info(f"Extracted {len(text)} characters")
        logger.info("Creating text chunks...")
        self.chunks = self._create_chunks(text)
        logger.info(f"Created {len(self.chunks)} chunks")

        # Generate embeddings in batches
        logger.info("Generating embeddings...")
        self.embeddings = []
        # batch to speed up embedding generation
        batch_size = 32
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i + batch_size]
            embeddings = self.model.encode(batch, normalize_embeddings=True, show_progress_bar=False)
            self.embeddings.extend(embeddings)
            logger.info(f"Processed chunk batch {i+1} to {i + len(batch)}")

        self.embeddings = np.array(self.embeddings)
        logger.info("Embeddings generated successfully")

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF pages."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            logger.info(f"PDF has {len(pdf_reader.pages)} pages")
            # extract text from each page
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or ""
                text += page_text + "\n"
                logger.debug(f"Extracted {len(page_text)} characters from page {i + 1}")
        return text

    def _create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks of fixed size."""
        chunks = []
        start = 0
        while start < len(text):
            # chunk size from config
            end = min(start + CHUNK_SIZE, len(text))
            chunks.append(text[start:end])
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def search(self, query: str, top_k: int = TOP_K_CHUNKS) -> List[Tuple[str, float]]:
        """Search for most similar chunks using cosine similarity."""
        if not self.chunks or self.embeddings is None:
            logger.warning("No document chunks available for search")
            return []

        logger.info(f"Searching for: {query}")
        query_embedding = self.model.encode(query, normalize_embeddings=True, show_progress_bar=False)

        # Find most similar chunks using cosine similarity
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = [(self.chunks[i], float(similarities[i])) for i in top_indices]
        logger.info(f"Found {len(results)} relevant chunks")
        return results
