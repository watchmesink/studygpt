import chromadb
import openai
from typing import List, Dict
from config.config import Config
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        logger.info("Initializing VectorStore")
        try:
            # Updated ChromaDB client initialization
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}  # Using cosine similarity
            )
            openai.api_key = Config.OPENAI_API_KEY
            logger.info("VectorStore initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing VectorStore: {str(e)}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text."""
        try:
            logger.debug(f"Getting embedding for text of length {len(text)}")
            response = openai.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text
            )
            logger.debug("Successfully got embedding")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
    
    def add_chunks(self, chunks: List[str], user_id: str, document_id: str):
        """Add document chunks to vector store."""
        try:
            logger.info(f"Adding {len(chunks)} chunks for user {user_id}, document {document_id}")
            embeddings = [self.get_embedding(chunk) for chunk in chunks]
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                ids=[f"{document_id}_{i}" for i in range(len(chunks))],
                metadatas=[{"user_id": user_id} for _ in chunks]
            )
            logger.info("Successfully added chunks to vector store")
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {str(e)}")
            raise
    
    def query(self, query: str, user_id: str, n_results: int = 3) -> List[str]:
        """Query vector store for relevant chunks."""
        try:
            logger.info(f"Querying vector store for user {user_id}")
            query_embedding = self.get_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"user_id": user_id}
            )
            
            logger.info(f"Found {len(results['documents'][0])} relevant chunks")
            return results["documents"][0]
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise 