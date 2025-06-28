"""
Configuration example for the RAG Backend

To get your Mistral API key:
1. Go to https://console.mistral.ai/
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your .env file

Example .env file contents:
MISTRAL_API_KEY=your_actual_mistral_api_key_here
FAISS_INDEX_PATH=./data/faiss_index
LOG_LEVEL=INFO
"""

# Test configuration loading
if __name__ == "__main__":
    from app.config import settings, validate_settings
    
    try:
        validate_settings()
        print("✅ Configuration is valid!")
        print(f"FAISS index path: {settings.faiss_index_path}")
        print(f"LLM model: {settings.mistral_llm_model}")
        print(f"Embedding model: {settings.mistral_embed_model}")
        print(f"Log level: {settings.log_level}")
        
        if settings.mistral_api_key and settings.mistral_api_key != "your_mistral_api_key_here":
            print("✅ Mistral API key is configured")
        else:
            print("⚠️  Please set your Mistral API key in the .env file")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
