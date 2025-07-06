#!/bin/bash

# Render startup script for RAG Backend
# This script tells Render how to start the FastAPI application

echo "🚀 Starting RAG Backend on Render..."

# Set environment variables for production
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"
export PYTHONUNBUFFERED=1

# Create data directory if it doesn't exist
mkdir -p data

echo "📦 Installing Python dependencies..."
# Show Python version
python --version

# Upgrade pip and install build dependencies first
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel

# Try minimal requirements first (latest compatible versions)
echo "🔄 Attempting minimal requirements installation..."
if pip install -r requirements-minimal.txt --timeout=300; then
    echo "✅ Minimal requirements installed successfully"
else
    echo "⚠️ Minimal requirements failed, trying full requirements..."
    pip install -r requirements.txt --verbose --timeout=300
fi

echo "🔧 Validating configuration..."
python -c "
from app.config import settings, validate_settings
try:
    validate_settings()
    print('✅ Configuration validated successfully')
    print(f'📁 FAISS index path: {settings.faiss_index_path}')
    print(f'🤖 LLM model: {settings.mistral_llm_model}')
    print(f'🔗 Embedding model: {settings.mistral_embed_model}')
    if settings.mistral_api_key and settings.mistral_api_key != 'your_mistral_api_key_here':
        print('✅ Mistral API key is configured')
    else:
        print('⚠️  Warning: Mistral API key not configured properly')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

echo "🌐 Starting FastAPI server..."
# Use Gunicorn with Uvicorn workers for production
# Bind to 0.0.0.0 and use PORT environment variable (required by Render)
exec gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info
