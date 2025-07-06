# RAG Backend

A FastAPI-based Retrieval-Augmented Generation backend using Mistral LLM, LangChain, and FAISS.

## Features

- Web scraping endpoint for content ingestion
- FAISS vectorstore with GPU support
- Mistral LLM integration for text generation
- Mistral embeddings for document retrieval
- Persistent FAISS index storage
- Clean modular architecture

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment variables:
```bash
# On Windows
copy .env.example .env

# On Linux/Mac
cp .env.example .env
```

3. Add your Mistral API key to `.env`:
```
MISTRAL_API_KEY=your_actual_api_key_here
```

4. Run the server:
```bash
# Method 1: Direct Python
python main.py

# Method 2: Using uvicorn
uvicorn main:app --reload

# Method 3: Windows batch file
start_server.bat
```

## API Endpoints

- `POST /scrape` - Scrape content from URLs and add to vectorstore
- `POST /ask` - Ask questions and get RAG-powered answers
- `POST /clear` - Clear the entire knowledge base (requires confirmation)
- `GET /health` - Health check endpoint
- `GET /stats` - Get vectorstore statistics
- `GET /vectorstore-info` - Get detailed vectorstore information
- `GET /rate-limit-stats` - Get rate limiting statistics

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration and environment variables
│   ├── models.py          # Pydantic models for API requests/responses
│   ├── llm_setup.py       # Mistral LLM configuration
│   ├── embedding.py       # Mistral embedding functionality
│   ├── vectorstore.py     # FAISS vectorstore management
│   ├── scraper.py         # Web scraping functionality
│   └── routes.py          # API route handlers
├── data/                  # FAISS index storage
├── requirements.txt       # Python dependencies
├── start.sh              # Production startup script for Render
├── render.yaml           # Render deployment configuration
├── DEPLOYMENT.md         # Deployment guide for Render
└── README.md
```

## 🚀 Deployment

For production deployment on Render, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick deployment:
1. Push code to GitHub
2. Connect repository to Render
3. Set `MISTRAL_API_KEY` environment variable
4. Deploy using `start.sh`
