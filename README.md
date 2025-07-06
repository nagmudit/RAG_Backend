# RAG Backend

A production-ready FastAPI-based Retrieval-Augmented Generation backend using Mistral LLM, LangChain, and FAISS vectorstore.

## 🎉 **LIVE DEPLOYMENT**

✅ **Successfully deployed on Render!**
- **Live URL**: https://rag-backend-bqd7.onrender.com
- **Health Check**: https://rag-backend-bqd7.onrender.com/api/v1/health
- **API Documentation**: https://rag-backend-bqd7.onrender.com/docs
- **Interactive API**: https://rag-backend-bqd7.onrender.com/redoc

## 🚀 Features

### Core RAG Pipeline
- **Web Scraping**: Intelligent content extraction from URLs
- **Document Processing**: Support for PDF, DOCX, TXT, and Markdown files
- **Vector Storage**: FAISS-based vectorstore with persistent storage
- **Embeddings**: Mistral embeddings for semantic search
- **Question Answering**: RAG-powered responses using Mistral LLM

### Production Features
- **Rate Limiting**: Intelligent API rate limiting with exponential backoff
- **Batch Processing**: Optimized embedding generation in batches
- **Error Handling**: Comprehensive error handling and logging
- **Health Monitoring**: Health checks and usage statistics
- **Persistent Storage**: Durable FAISS index storage
- **Auto-scaling**: Handles concurrent requests efficiently

### Technical Stack
- **FastAPI**: Modern Python web framework
- **Mistral AI**: LLM and embedding models
- **LangChain**: RAG pipeline orchestration
- **FAISS**: High-performance vector similarity search
- **Gunicorn + Uvicorn**: Production ASGI server
- **Render**: Cloud deployment platform

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11+ (tested with 3.13.4)
- Mistral API key

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/nagmudit/RAG_Backend.git
cd RAG_Backend
```

2. **Install dependencies:**
```bash
# Option 1: Full requirements
pip install -r requirements.txt

# Option 2: Minimal requirements (faster)
pip install -r requirements-minimal.txt
```

3. **Set up environment variables:**
```bash
# On Windows
copy .env.example .env

# On Linux/Mac
cp .env.example .env
```

4. **Configure your API key in `.env`:**
```env
MISTRAL_API_KEY=your_actual_mistral_api_key_here
FAISS_INDEX_PATH=./data/faiss_index
LOG_LEVEL=INFO
```

5. **Run the server:**
```bash
# Development server
python main.py

# Or with uvicorn (recommended for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server (local testing)
./start.sh
```

6. **Access the API:**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- Interactive API: http://localhost:8000/redoc

## 🌐 API Endpoints

### Core RAG Endpoints
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v1/scrape` | POST | Scrape web content and add to knowledge base |
| `/api/v1/ask` | POST | Ask questions using RAG pipeline |
| `/api/v1/clear` | POST | Clear entire knowledge base (requires confirmation) |

### Information & Monitoring
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v1/health` | GET | Health check and system status |
| `/api/v1/stats` | GET | Usage statistics and metrics |
| `/api/v1/vectorstore-info` | GET | Detailed vectorstore information |
| `/api/v1/rate-limit-stats` | GET | Rate limiting statistics |

### Documentation
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |

## 📋 Usage Examples

### 1. Scrape Web Content
```bash
curl -X POST "https://rag-backend-bqd7.onrender.com/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_depth": 2
  }'
```

### 2. Ask Questions
```bash
curl -X POST "https://rag-backend-bqd7.onrender.com/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the website?",
    "max_tokens": 150
  }'
```

### 3. Check System Health
```bash
curl "https://rag-backend-bqd7.onrender.com/api/v1/health"
```

### 4. Get Usage Statistics
```bash
curl "https://rag-backend-bqd7.onrender.com/api/v1/stats"
```

## 📁 Project Structure

```
RAG_Backend/
├── main.py                     # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration and environment variables
│   ├── models.py              # Pydantic models for API requests/responses
│   ├── llm_setup.py           # Mistral LLM configuration and setup
│   ├── embedding.py           # Mistral embedding functionality
│   ├── vectorstore.py         # FAISS vectorstore management
│   ├── scraper.py             # Web scraping functionality
│   └── routes.py              # API route handlers
├── data/                      # FAISS index storage (persistent)
├── requirements.txt           # Full Python dependencies
├── requirements-minimal.txt   # Minimal dependencies for quick setup
├── .env.example              # Environment variables template
├── .env                      # Environment variables (not in git)
├── .gitignore                # Git ignore rules
├── start.sh                  # Production startup script
├── Dockerfile                # Docker configuration
├── runtime.txt               # Python version specification
├── pyproject.toml            # Modern Python project configuration
├── render.yaml               # Render deployment (Docker)
├── render-python.yaml        # Render deployment (Python)
├── DEPLOYMENT.md             # Detailed deployment guide
├── DEPLOYMENT_SUCCESS.md     # Deployment success documentation
├── setup.py                  # Development setup script
├── test_api.py               # API testing script
├── workflow_example.py       # Complete workflow example
├── clear_demo.py             # Clear functionality demo
├── validate_deployment.py    # Deployment validation script
└── README.md                 # This file
```

## 🚀 Production Deployment

### Deploy on Render (Recommended)

✅ **Already deployed successfully!**

For new deployments or updates, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick deployment steps:**
1. Fork this repository
2. Connect to Render
3. Set `MISTRAL_API_KEY` environment variable
4. Deploy using Docker or Python runtime

### Deploy with Docker

```bash
# Build image
docker build -t rag-backend .

# Run container
docker run -p 8000:8000 \
  -e MISTRAL_API_KEY=your_api_key_here \
  rag-backend
```

### Deploy Manually

```bash
# Clone repository
git clone https://github.com/nagmudit/RAG_Backend.git
cd RAG_Backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MISTRAL_API_KEY=your_api_key_here
export FAISS_INDEX_PATH=./data/faiss_index

# Run production server
./start.sh
```

## 🧪 Testing & Development

### Run Tests
```bash
# Test API endpoints
python test_api.py

# Validate configuration
python validate_deployment.py

# Complete workflow example
python workflow_example.py

# Test clear functionality
python clear_demo.py
```

### Development Scripts
```bash
# Setup development environment
python setup.py

# Start development server
python main.py
```

## 🔧 Configuration

### Environment Variables
```env
# Required
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional (with defaults)
FAISS_INDEX_PATH=./data/faiss_index
LOG_LEVEL=INFO
LLM_MIN_REQUEST_INTERVAL=2.0
LLM_BASE_DELAY=5.0
LLM_MAX_RETRIES=3
EMBEDDING_MIN_REQUEST_INTERVAL=1.0
EMBEDDING_MAX_RETRIES=2
EMBEDDING_BATCH_SIZE=20
```

### Models Configuration
- **LLM Model**: `mistral-large-latest`
- **Embedding Model**: `mistral-embed`
- **Vector Dimensions**: 1024
- **Similarity Search**: Cosine similarity

## 📊 Performance & Monitoring

### Production Metrics
- **Response Time**: <1s for warm requests
- **Cold Start**: ~10-15s (free tier)
- **Concurrent Requests**: Supported with auto-scaling
- **Rate Limiting**: Configured for Mistral API limits
- **Memory Usage**: ~200MB baseline
- **Storage**: Persistent FAISS index

### Monitoring Endpoints
- **Health**: `/api/v1/health`
- **Statistics**: `/api/v1/stats`
- **Rate Limits**: `/api/v1/rate-limit-stats`
- **Vectorstore Info**: `/api/v1/vectorstore-info`

## 🔐 Security

- **API Key Protection**: Environment variables only
- **Input Validation**: Pydantic models
- **Rate Limiting**: Prevents API abuse
- **Error Handling**: No sensitive data in responses
- **CORS**: Configured for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/nagmudit/RAG_Backend/issues)
- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **API Docs**: https://rag-backend-bqd7.onrender.com/docs

## 🎯 Roadmap

- [ ] Add support for more document types
- [ ] Implement user authentication
- [ ] Add conversation history
- [ ] Implement semantic caching
- [ ] Add batch processing endpoints
- [ ] Implement webhook notifications

---

**🚀 RAG Backend is production-ready and successfully deployed!**
