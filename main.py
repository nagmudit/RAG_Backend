import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, validate_settings
from app.routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting RAG Backend...")
    
    try:
        # Validate settings
        validate_settings()
        logger.info("Configuration validated successfully")
        
        # Initialize components (lazy loading will handle actual initialization)
        logger.info("RAG Backend started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Backend...")

# Create FastAPI application
app = FastAPI(
    title="RAG Backend",
    description="A FastAPI-based Retrieval-Augmented Generation backend using Mistral LLM, LangChain, and FAISS. Supports web scraping and document upload (PDF, DOCX, XLSX, MD).",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "RAG Backend API",
        "version": "1.0.0",
        "features": [
            "Web scraping and content extraction",
            "Document upload (PDF, DOCX, XLSX, MD)",
            "Vector search with FAISS",
            "RAG-powered question answering"
        ],
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "scrape": "/api/v1/scrape",
            "upload": "/api/v1/upload",
            "ask": "/api/v1/ask",
            "clear": "/api/v1/clear",
            "stats": "/api/v1/stats",
            "vectorstore_info": "/api/v1/vectorstore-info",
            "rate_limit_stats": "/api/v1/rate-limit-stats"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
