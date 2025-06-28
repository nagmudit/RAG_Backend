import logging
from typing import List, Optional
from langchain_mistralai import MistralAIEmbeddings
from langchain.schema import Document
from app.config import settings

logger = logging.getLogger(__name__)

class MistralEmbedding:
    """Handles Mistral embeddings for document vectorization."""
    
    def __init__(self):
        self._embeddings: Optional[MistralAIEmbeddings] = None
        
    def get_embeddings(self) -> MistralAIEmbeddings:
        """Get or create Mistral embeddings instance."""
        if self._embeddings is None:
            try:
                self._embeddings = MistralAIEmbeddings(
                    model=settings.mistral_embed_model,
                    mistral_api_key=settings.mistral_api_key
                )
                logger.info(f"Initialized Mistral embeddings with model: {settings.mistral_embed_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral embeddings: {e}")
                raise
                
        return self._embeddings
    
    def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """Create embeddings for a list of documents."""
        try:
            embeddings = self.get_embeddings()
            texts = [doc.page_content for doc in documents]
            
            logger.info(f"Creating embeddings for {len(texts)} documents")
            embedded_docs = embeddings.embed_documents(texts)
            
            logger.info(f"Successfully created {len(embedded_docs)} document embeddings")
            return embedded_docs
            
        except Exception as e:
            logger.error(f"Error creating document embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """Create embedding for a single query."""
        try:
            embeddings = self.get_embeddings()
            embedded_query = embeddings.embed_query(query)
            
            logger.info(f"Successfully created query embedding")
            return embedded_query
            
        except Exception as e:
            logger.error(f"Error creating query embedding: {e}")
            raise

# Global embedding instance
mistral_embedding = MistralEmbedding()
