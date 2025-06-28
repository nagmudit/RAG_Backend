import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/upload"
ASK_ENDPOINT = f"{BASE_URL}/ask"

def test_document_upload(file_path: str):
    """Test document upload functionality."""
    print(f"\n=== Testing Document Upload: {file_path} ===")
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Upload document
        with open(file_path, 'rb') as file:
            files = {'file': (Path(file_path).name, file)}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   - Filename: {result['filename']}")
            print(f"   - File type: {result['file_type']}")
            print(f"   - Documents added: {result['documents_added']}")
            print(f"   - Message: {result['message']}")
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_question_with_documents(question: str):
    """Test asking a question after uploading documents."""
    print(f"\n=== Testing Question: {question} ===")
    
    try:
        data = {"query": question}
        response = requests.post(ASK_ENDPOINT, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Question answered!")
            print(f"   - Answer: {result['answer'][:200]}...")
            print(f"   - Citations: {len(result['citations'])}")
            
            for i, citation in enumerate(result['citations'], 1):
                print(f"     {i}. {citation['title']} ({citation['source_type']})")
                if citation['source_type'] == 'url':
                    print(f"        URL: {citation['url']}")
                else:
                    print(f"        File: {citation['url']}")
                print(f"        Relevance: {citation['relevance_score']:.3f}")
            return True
        else:
            print(f"❌ Question failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Question error: {e}")
        return False

def create_sample_files():
    """Create sample files for testing."""
    print("\n=== Creating Sample Test Files ===")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create a sample markdown file
    md_content = """# Sample Document

This is a sample markdown document for testing the RAG backend.

## Features

The RAG backend now supports:
- PDF documents
- Microsoft Word documents (.docx)
- Excel spreadsheets (.xlsx)
- Markdown files (.md)

## How it works

1. Upload your document using the `/upload` endpoint
2. The document is processed and chunked
3. Text chunks are converted to embeddings
4. Embeddings are stored in the FAISS vector database
5. Ask questions using the `/ask` endpoint

## Example Questions

You can ask questions like:
- "What file formats are supported?"
- "How does the upload process work?"
- "What are the main features?"
"""
    
    md_path = data_dir / "sample_document.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Created sample markdown file: {md_path}")
    return str(md_path)

def main():
    """Main test function."""
    print("🚀 RAG Backend Document Upload Test")
    print("=====================================")
    
    # Create sample files
    sample_md = create_sample_files()
    
    # Test document upload
    upload_success = test_document_upload(sample_md)
    
    if upload_success:
        # Test questions
        questions = [
            "What file formats are supported by the RAG backend?",
            "How does the document upload process work?",
            "What are the main features mentioned in the document?"
        ]
        
        for question in questions:
            test_question_with_documents(question)
    
    print("\n=== Test Complete ===")
    print("\nTo test with your own files:")
    print("1. Make sure the server is running: python main.py")
    print("2. Use the upload endpoint: POST /upload")
    print("3. Supported formats: .pdf, .docx, .xlsx, .md")
    print("4. Max file size: 50MB")

if __name__ == "__main__":
    main()
