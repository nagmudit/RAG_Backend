import os
import pickle
import logging
from typing import List, Optional, Tuple
import faiss
import numpy as np
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from app.config import settings
from app.embedding import mistral_embedding

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """Manages FAISS vectorstore with GPU support and persistence."""
    
    def __init__(self):
        self._vectorstore: Optional[FAISS] = None
        self._documents: List[Document] = []
        self.index_path = settings.faiss_index_path
        
    def _create_new_vectorstore(self) -> FAISS:
        """Create a new FAISS vectorstore."""
        try:
            # Create a dummy document to initialize the vectorstore
            dummy_doc = Document(
                page_content="Initialization document",
                metadata={"source": "init", "title": "Init"}
            )
            
            embeddings = mistral_embedding.get_embeddings()
            vectorstore = FAISS.from_documents([dummy_doc], embeddings)
            
            # Remove the dummy document
            vectorstore.delete([0])
            
            logger.info("Created new FAISS vectorstore")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating new vectorstore: {e}")
            raise
    
    def _setup_gpu_index(self, vectorstore: FAISS):
        """Setup GPU acceleration for FAISS if available."""
        try:
            # Check if GPU is available
            if faiss.get_num_gpus() > 0:
                logger.info(f"Found {faiss.get_num_gpus()} GPU(s), setting up GPU index")
                
                # Convert to GPU index
                gpu_resource = faiss.StandardGpuResources()
                index_cpu = vectorstore.index
                
                # Create GPU index
                index_gpu = faiss.index_cpu_to_gpu(gpu_resource, 0, index_cpu)
                vectorstore.index = index_gpu
                
                logger.info("Successfully setup GPU acceleration for FAISS")
            else:
                logger.info("No GPU available, using CPU index")
                
        except Exception as e:
            logger.warning(f"Failed to setup GPU acceleration: {e}, falling back to CPU")
    
    def get_vectorstore(self) -> FAISS:
        """Get or create FAISS vectorstore."""
        if self._vectorstore is None:
            if self.load_index():
                logger.info("Loaded existing FAISS index")
            else:
                self._vectorstore = self._create_new_vectorstore()
                self._setup_gpu_index(self._vectorstore)
                
        return self._vectorstore
    
    def add_documents(self, documents: List[Document]) -> int:
        """Add documents to the vectorstore."""
        try:
            if not documents:
                return 0
                
            vectorstore = self.get_vectorstore()
            
            # Add documents to vectorstore
            vectorstore.add_documents(documents)
            
            # Keep track of documents for persistence
            self._documents.extend(documents)
            
            logger.info(f"Added {len(documents)} documents to vectorstore")
            
            # Save the updated index
            self.save_index()
            
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error adding documents to vectorstore: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents with scores."""
        try:
            vectorstore = self.get_vectorstore()
            
            # Perform similarity search with scores
            results = vectorstore.similarity_search_with_score(query, k=k)
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise
    
    def get_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """Get a retriever for the vectorstore."""
        try:
            vectorstore = self.get_vectorstore()
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            
            logger.info(f"Created retriever with k={k}")
            return retriever
            
        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            raise
    
    def save_index(self):
        """Save FAISS index and documents to disk."""
        try:
            if self._vectorstore is None:
                logger.warning("No vectorstore to save")
                return
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            index_file = f"{self.index_path}.faiss"
            pkl_file = f"{self.index_path}.pkl"
            
            # Convert GPU index to CPU for saving
            if hasattr(self._vectorstore.index, 'device') and self._vectorstore.index.device >= 0:
                cpu_index = faiss.index_gpu_to_cpu(self._vectorstore.index)
                faiss.write_index(cpu_index, index_file)
            else:
                faiss.write_index(self._vectorstore.index, index_file)
            
            # Save documents and metadata
            with open(pkl_file, 'wb') as f:
                pickle.dump({
                    'documents': self._documents,
                    'docstore': self._vectorstore.docstore,
                    'index_to_docstore_id': self._vectorstore.index_to_docstore_id
                }, f)
            
            logger.info(f"Saved FAISS index to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def load_index(self) -> bool:
        """Load FAISS index and documents from disk."""
        try:
            index_file = f"{self.index_path}.faiss"
            pkl_file = f"{self.index_path}.pkl"
            
            if not (os.path.exists(index_file) and os.path.exists(pkl_file)):
                logger.info("No existing FAISS index found")
                return False
            
            # Load FAISS index
            index = faiss.read_index(index_file)
            
            # Load documents and metadata
            with open(pkl_file, 'rb') as f:
                data = pickle.load(f)
            
            # Reconstruct FAISS vectorstore
            embeddings = mistral_embedding.get_embeddings()
            self._vectorstore = FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=data['docstore'],
                index_to_docstore_id=data['index_to_docstore_id']
            )
            
            self._documents = data['documents']
            
            # Setup GPU acceleration
            self._setup_gpu_index(self._vectorstore)
            
            logger.info(f"Loaded FAISS index with {len(self._documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vectorstore."""
        return len(self._documents)
    
    def index_exists(self) -> bool:
        """Check if FAISS index exists on disk."""
        index_file = f"{self.index_path}.faiss"
        pkl_file = f"{self.index_path}.pkl"
        return os.path.exists(index_file) and os.path.exists(pkl_file)

# Global vectorstore instance
faiss_vectorstore = FAISSVectorStore()
