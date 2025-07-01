import logging
import time
import random
from typing import List, Optional
from langchain_mistralai import MistralAIEmbeddings
from langchain.schema import Document
from app.config import settings

logger = logging.getLogger(__name__)

class MistralEmbedding:
    """Handles Mistral embeddings for document vectorization."""
    
    def __init__(self):
        self._embeddings: Optional[MistralAIEmbeddings] = None
        self._last_request_time = 0
        self._min_request_interval = settings.embedding_min_request_interval
        
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
            def create_embeddings():
                embeddings = self.get_embeddings()
                texts = [doc.page_content for doc in documents]
                
                logger.info(f"Creating embeddings for {len(texts)} documents")
                
                # Process in smaller batches to avoid rate limits
                batch_size = settings.embedding_batch_size  # Configurable batch size
                all_embeddings = []
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    logger.info(f"Processing embedding batch {i//batch_size + 1} ({len(batch)} documents)")
                    
                    # Add delay between batches
                    if i > 0:
                        time.sleep(2)
                    
                    batch_embeddings = embeddings.embed_documents(batch)
                    all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Successfully created {len(all_embeddings)} document embeddings")
                return all_embeddings
            
            return self._retry_with_backoff(create_embeddings)
            
        except Exception as e:
            logger.error(f"Error creating document embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """Create embedding for a single query."""
        try:
            def create_query_embedding():
                embeddings = self.get_embeddings()
                embedded_query = embeddings.embed_query(query)
                logger.info("Successfully created query embedding")
                return embedded_query
            
            return self._retry_with_backoff(create_query_embedding)
            
        except Exception as e:
            logger.error(f"Error creating query embedding: {e}")
            raise

    def _wait_for_rate_limit(self):
        """Ensure minimum time between API requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _retry_with_backoff(self, func, max_retries=None):
        """Execute function with retry logic for embeddings."""
        if max_retries is None:
            max_retries = settings.embedding_max_retries
            
        for attempt in range(max_retries + 1):
            try:
                self._wait_for_rate_limit()
                return func()
                
            except Exception as e:
                error_str = str(e).lower()
                
                if "429" in error_str or "rate limit" in error_str:
                    if attempt < max_retries:
                        delay = 3 * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Embedding rate limit hit (attempt {attempt + 1}/{max_retries + 1}). "
                                     f"Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Max embedding retries ({max_retries}) exceeded")
                        raise
                else:
                    raise
        
        raise Exception("Max retries exceeded for embedding request")

# Global embedding instance
mistral_embedding = MistralEmbedding()
