import logging
import time
import random
from typing import Optional
from langchain_mistralai import ChatMistralAI
from app.config import settings

logger = logging.getLogger(__name__)

class MistralLLMSetup:
    """Handles Mistral LLM setup and configuration."""
    
    def __init__(self):
        self._llm: Optional[ChatMistralAI] = None
        self._last_request_time = 0
        self._min_request_interval = settings.llm_min_request_interval
        self._base_delay = settings.llm_base_delay
        
    def get_llm(self) -> ChatMistralAI:
        """Get or create Mistral LLM instance."""
        if self._llm is None:
            try:
                self._llm = ChatMistralAI(
                    model=settings.mistral_llm_model,
                    mistral_api_key=settings.mistral_api_key,
                    temperature=0.1,  # Low temperature for more deterministic responses
                    max_tokens=1000,
                    top_p=0.9
                )
                logger.info(f"Initialized Mistral LLM with model: {settings.mistral_llm_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral LLM: {e}")
                raise
                
        return self._llm
    
    def generate_rag_answer(self, query: str, context_docs: list) -> str:
        """Generate an answer using RAG with retrieved documents."""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                f"Title: {doc.metadata.get('title', 'No title')}\n"
                f"Content: {doc.page_content}"
                for doc in context_docs
            ])
            
            # Create the prompt for RAG
            prompt = f"""You are a helpful assistant that answers questions based on the provided context. 
            Use the following pieces of context to answer the question at the end. 
            If you don't know the answer based on the context, just say that you don't know.
            Always cite the sources when possible.

            Context:
            {context}

            Question: {query}

            Answer:"""
            
            # Use retry logic for API calls
            def make_api_call():
                llm = self.get_llm()
                response = llm.invoke(prompt)
                return response.content
            
            result = self._exponential_backoff_retry(make_api_call)
            logger.info("Successfully generated RAG answer")
            return result
            
        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            # Return fallback response instead of raising
            return self._get_fallback_response()

    def _wait_for_rate_limit(self):
        """Ensure minimum time between API requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds before next request")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _exponential_backoff_retry(self, func, max_retries=None):
        """Execute function with exponential backoff retry logic."""
        if max_retries is None:
            max_retries = settings.llm_max_retries
            
        for attempt in range(max_retries + 1):
            try:
                self._wait_for_rate_limit()
                return func()
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if it's a rate limiting error
                if "429" in error_str or "rate limit" in error_str or "capacity exceeded" in error_str:
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff and jitter
                        delay = self._base_delay * (2 ** attempt) + random.uniform(0, 2)
                        logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}). "
                                     f"Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Max retries ({max_retries}) exceeded for rate limiting")
                        # Return a fallback response instead of crashing
                        return self._get_fallback_response()
                else:
                    # Non-rate-limit error, don't retry
                    logger.error(f"Non-rate-limit error: {e}")
                    raise
        
        return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Return a fallback response when API calls fail."""
        return ("I apologize, but I'm currently experiencing high demand and cannot process your request. "
                "Please try again in a few moments. The system has successfully retrieved relevant documents "
                "from your knowledge base, but the AI response generation is temporarily unavailable.")

# Global LLM setup instance
mistral_llm_setup = MistralLLMSetup()
