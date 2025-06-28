"""
Example usage script for the RAG Backend API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_scrape(urls):
    """Test the scrape endpoint."""
    print(f"Testing scrape endpoint with {len(urls)} URLs...")
    
    data = {"urls": urls}
    response = requests.post(f"{BASE_URL}/scrape", json=data)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    print(f"Processed URLs: {len(result.get('processed_urls', []))}")
    print(f"Failed URLs: {len(result.get('failed_urls', []))}")
    print(f"Documents added: {result.get('documents_added')}")
    print()
    
    return result.get('success', False)

def test_ask(query):
    """Test the ask endpoint."""
    print(f"Testing ask endpoint with query: '{query}'")
    
    data = {"query": query}
    response = requests.post(f"{BASE_URL}/ask", json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result.get('answer')}")
        print(f"Citations ({len(result.get('citations', []))}):")
        for i, citation in enumerate(result.get('citations', []), 1):
            source_type = citation.get('source_type', 'url')
            print(f"  {i}. {citation.get('title')} ({source_type})")
            print(f"     Source: {citation.get('url')}")
            print(f"     Relevance: {citation.get('relevance_score', 0):.3f}")
    else:
        print(f"Error: {response.text}")
    print()

def test_document_upload(file_path):
    """Test the document upload endpoint."""
    print(f"Testing document upload with file: {file_path}")
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path.split('/')[-1], file)}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Filename: {result.get('filename')}")
            print(f"File type: {result.get('file_type')}")
            print(f"Documents added: {result.get('documents_added')}")
            return result.get('success', False)
        else:
            print(f"Error: {response.text}")
            return False
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    print()

def get_stats():
    """Get vectorstore statistics."""
    print("Getting vectorstore statistics...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Main example function."""
    print("🤖 RAG Backend API Test Script")
    print("=" * 40)
    
    # Test health
    test_health()
    
    # Get initial stats
    get_stats()
    
    # Example URLs to scrape
    example_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://python.langchain.com/docs/get_started/introduction"
    ]
    
    # Test scraping
    scrape_success = test_scrape(example_urls)
    
    if scrape_success:
        # Get updated stats
        get_stats()
        
        # Test asking questions
        example_queries = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "What is LangChain used for?"
        ]
        
        for query in example_queries:
            test_ask(query)
    else:
        print("❌ Scraping failed, skipping question tests")
    
    # Test document upload
    test_document_upload("example.pdf")
    
    print("✅ Test script completed!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the server.")
        print("   Make sure the RAG Backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
