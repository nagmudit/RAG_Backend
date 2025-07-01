import asyncio
import logging
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from app.models import (
    ScrapeRequest, ScrapeResponse,
    DocumentUploadResponse,
    AskRequest, AskResponse, Citation,
    HealthResponse
)
from app.scraper import web_scraper
from app.vectorstore import faiss_vectorstore
from app.llm_setup import mistral_llm_setup
from app.document_processor import document_processor
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        index_exists = faiss_vectorstore.index_exists()
        
        return HealthResponse(
            status="healthy",
            message="RAG Backend is running",
            faiss_index_exists=index_exists
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_urls(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Scrape URLs and add content to vectorstore."""
    try:
        # Convert URLs to strings
        url_strings = [str(url) for url in request.urls]
        
        logger.info(f"Starting to scrape {len(url_strings)} URLs")
        
        # Scrape URLs asynchronously
        scraped_data = await web_scraper.scrape_urls_async(url_strings)
        
        # Separate successful and failed URLs
        successful_data = [data for data in scraped_data if data['success']]
        failed_urls = [data['url'] for data in scraped_data if not data['success']]
        processed_urls = [data['url'] for data in successful_data]
        
        if not successful_data:
            return ScrapeResponse(
                success=False,
                message="No URLs were successfully scraped",
                processed_urls=[],
                failed_urls=failed_urls,
                documents_added=0
            )
        
        # Create documents from scraped data
        documents = web_scraper.create_documents(successful_data)
        
        if not documents:
            return ScrapeResponse(
                success=False,
                message="No documents could be created from scraped content",
                processed_urls=processed_urls,
                failed_urls=failed_urls,
                documents_added=0
            )
        
        # Add documents to vectorstore in background
        def add_to_vectorstore():
            try:
                docs_added = faiss_vectorstore.add_documents(documents)
                logger.info(f"Added {docs_added} documents to vectorstore")
            except Exception as e:
                logger.error(f"Error adding documents to vectorstore: {e}")
        
        background_tasks.add_task(add_to_vectorstore)
        
        return ScrapeResponse(
            success=True,
            message=f"Successfully processed {len(processed_urls)} URLs",
            processed_urls=processed_urls,
            failed_urls=failed_urls,
            documents_added=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process a document for RAG."""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.md'}
        file_extension = None
        if file.filename:
            file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if not file_extension or file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (limit to 50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 50MB."
            )
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty."
            )
        
        logger.info(f"Processing uploaded file: {file.filename} ({len(file_content)} bytes)")
        
        # Process the document
        documents = await document_processor.process_uploaded_file(
            file_content, file.filename
        )
        
        if not documents:
            return DocumentUploadResponse(
                success=False,
                message="No content could be extracted from the document",
                filename=file.filename,
                documents_added=0,
                file_type=file_extension
            )
        
        # Add documents to vectorstore in background
        def add_to_vectorstore():
            try:
                docs_added = faiss_vectorstore.add_documents(documents)
                logger.info(f"Added {docs_added} documents from {file.filename} to vectorstore")
            except Exception as e:
                logger.error(f"Error adding documents to vectorstore: {e}")
        
        background_tasks.add_task(add_to_vectorstore)
        
        return DocumentUploadResponse(
            success=True,
            message=f"Successfully processed {file.filename}",
            filename=file.filename,
            documents_added=len(documents),
            file_type=file_extension
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Ask a question and get RAG-powered answer."""
    try:
        query = request.query.strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Processing query: {query}")
        
        # Check if vectorstore has documents
        if faiss_vectorstore.get_document_count() == 0:
            raise HTTPException(
                status_code=400, 
                detail="No documents in vectorstore. Please scrape some URLs first."
            )
        
        # Retrieve relevant documents
        search_results = faiss_vectorstore.similarity_search(
            query, k=settings.top_k_documents
        )
        
        if not search_results:
            return AskResponse(
                answer="I couldn't find any relevant documents to answer your question.",
                citations=[],
                query=query
            )
        
        # Extract documents and scores
        documents = [result[0] for result in search_results]
        scores = [result[1] for result in search_results]
        
        # Generate answer using LLM
        answer = mistral_llm_setup.generate_rag_answer(query, documents)
        
        # Create citations
        citations = []
        seen_sources = set()
        
        for doc, score in zip(documents, scores):
            source = doc.metadata.get('source', '')
            title = doc.metadata.get('title', 'No title')
            file_type = doc.metadata.get('file_type', '')
            
            # Determine source type and create appropriate citation
            if source and source not in seen_sources:
                # Check if it's a URL or filename
                if source.startswith('http://') or source.startswith('https://'):
                    source_type = "url"
                    url = source
                else:
                    source_type = "document"
                    url = f"Uploaded file: {source}"
                
                citations.append(Citation(
                    url=url,
                    title=title,
                    relevance_score=float(1.0 - score),  # Convert distance to similarity
                    source_type=source_type
                ))
                seen_sources.add(source)
        
        # Limit to top 5 citations
        citations = citations[:5]
        
        logger.info(f"Generated answer with {len(citations)} citations")
        
        return AskResponse(
            answer=answer,
            citations=citations,
            query=query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get vectorstore statistics."""
    try:
        return {
            "document_count": faiss_vectorstore.get_document_count(),
            "index_exists": faiss_vectorstore.index_exists(),
            "index_path": settings.faiss_index_path
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@router.get("/rate-limit-stats")
async def get_rate_limit_stats():
    """Get rate limiting statistics."""
    try:
        from app.llm_setup import mistral_llm_setup
        from app.embedding import mistral_embedding
        
        return {
            "llm_stats": {
                "last_request_time": mistral_llm_setup._last_request_time,
                "min_request_interval": mistral_llm_setup._min_request_interval,
                "base_delay": mistral_llm_setup._base_delay
            },
            "embedding_stats": {
                "last_request_time": mistral_embedding._last_request_time,
                "min_request_interval": mistral_embedding._min_request_interval
            },
            "config": {
                "llm_max_retries": settings.llm_max_retries,
                "embedding_max_retries": settings.embedding_max_retries,
                "embedding_batch_size": settings.embedding_batch_size
            }
        }
    except Exception as e:
        logger.error(f"Error getting rate limit stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rate limit stats")
