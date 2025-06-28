"""
Complete workflow example for the RAG Backend

This script demonstrates:
1. Scraping web content
2. Adding it to the vectorstore
3. Asking questions and getting RAG-powered answers

Make sure to start the server first: python main.py
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def scrape_example_content():
    """Scrape some example content."""
    print_header("SCRAPING WEB CONTENT")
    
    # Example URLs with good content for RAG
    urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Natural_language_processing",
        "https://docs.python.org/3/tutorial/introduction.html"
    ]
    
    print(f"📥 Scraping {len(urls)} URLs...")
    for url in urls:
        print(f"   • {url}")
    
    data = {"urls": urls}
    
    try:
        response = requests.post(f"{BASE_URL}/scrape", json=data, timeout=60)
        result = response.json()
        
        print(f"\n✅ Scraping completed!")
        print(f"   • Success: {result.get('success')}")
        print(f"   • Message: {result.get('message')}")
        print(f"   • Processed URLs: {len(result.get('processed_urls', []))}")
        print(f"   • Failed URLs: {len(result.get('failed_urls', []))}")
        print(f"   • Documents added: {result.get('documents_added')}")
        
        if result.get('failed_urls'):
            print(f"\n⚠️  Failed URLs:")
            for url in result.get('failed_urls', []):
                print(f"   • {url}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return False

def ask_questions():
    """Ask example questions."""
    print_header("ASKING QUESTIONS")
    
    questions = [
        "What is artificial intelligence and how does it work?",
        "Explain the difference between machine learning and AI",
        "What are the main applications of natural language processing?",
        "How do I get started with Python programming?",
        "What are neural networks and how are they used in AI?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n🤔 Question {i}: {question}")
        print("-" * 50)
        
        try:
            data = {"query": question}
            response = requests.post(f"{BASE_URL}/ask", json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"🤖 Answer:")
                print(f"   {result.get('answer', 'No answer')}")
                
                citations = result.get('citations', [])
                if citations:
                    print(f"\n📚 Sources ({len(citations)}):")
                    for j, citation in enumerate(citations, 1):
                        print(f"   {j}. {citation.get('title', 'No title')}")
                        print(f"      URL: {citation.get('url', 'No URL')}")
                        print(f"      Relevance: {citation.get('relevance_score', 0):.3f}")
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Question failed: {e}")
        
        # Small delay between questions
        time.sleep(1)

def get_vectorstore_stats():
    """Get and display vectorstore statistics."""
    print_header("VECTORSTORE STATISTICS")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        
        print(f"📊 Vectorstore Statistics:")
        print(f"   • Document count: {stats.get('document_count', 0)}")
        print(f"   • Index exists: {stats.get('index_exists', False)}")
        print(f"   • Index path: {stats.get('index_path', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")

def main():
    """Main workflow function."""
    print_header("RAG BACKEND WORKFLOW EXAMPLE")
    print("This example demonstrates the complete RAG workflow:")
    print("1. Check server health")
    print("2. Scrape web content")
    print("3. Ask questions")
    print("4. View statistics")
    
    # Check if server is running
    if not check_server():
        print("\n❌ Error: Server is not running!")
        print("   Please start the server first:")
        print("   python main.py")
        return
    
    print("\n✅ Server is running!")
    
    # Get initial stats
    get_vectorstore_stats()
    
    # Scrape content
    scrape_success = scrape_example_content()
    
    if scrape_success:
        # Wait a moment for background processing
        print("\n⏳ Waiting for document processing...")
        time.sleep(3)
        
        # Get updated stats
        get_vectorstore_stats()
        
        # Ask questions
        ask_questions()
        
        print_header("WORKFLOW COMPLETED")
        print("✅ Successfully completed the RAG workflow!")
        print("\n💡 Next steps:")
        print("   • Try asking your own questions at http://localhost:8000/docs")
        print("   • Add more URLs using the /scrape endpoint")
        print("   • Explore the API documentation")
        
    else:
        print("\n❌ Scraping failed. Cannot proceed with questions.")
        print("   This might be due to:")
        print("   • Network connectivity issues")
        print("   • Missing Mistral API key")
        print("   • Server configuration problems")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
