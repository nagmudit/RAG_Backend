import logging
from typing import Optional
from langchain_mistralai import ChatMistralAI
from app.config import settings

logger = logging.getLogger(__name__)

class MistralLLMSetup:
    """Handles Mistral LLM setup and configuration."""
    
    def __init__(self):
        self._llm: Optional[ChatMistralAI] = None
        
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
            
            llm = self.get_llm()
            response = llm.invoke(prompt)
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            raise

# Global LLM setup instance
mistral_llm_setup = MistralLLMSetup()
