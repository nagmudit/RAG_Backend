"""
Knowledge Base Management Demo

This script demonstrates how to use the clear knowledge base API.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def get_vectorstore_info():
    """Get current vectorstore information."""
    response = requests.get(f"{BASE_URL}/vectorstore-info")
    info = response.json()
    
    print(f"📊 Vectorstore Status:")
    print(f"   • Documents: {info['document_count']}")
    print(f"   • Loaded: {info['vectorstore_loaded']}")
    print(f"   • Index on disk: {info['index_exists_on_disk']}")
    print(f"   • Path: {info['index_path']}")
    
    return info

def add_sample_documents():
    """Add some sample documents to the knowledge base."""
    print("📥 Adding sample documents...")
    
    urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://en.wikipedia.org/wiki/Machine_learning"
    ]
    
    response = requests.post(f"{BASE_URL}/scrape", json={"urls": urls})
    result = response.json()
    
    if result.get("success"):
        print(f"✅ Successfully added {result.get('documents_added', 0)} documents")
        print(f"   • Processed URLs: {len(result.get('processed_urls', []))}")
    else:
        print(f"❌ Failed to add documents: {result.get('message', 'Unknown error')}")
    
    return result.get("success", False)

def clear_knowledge_base(confirm=True):
    """Clear the knowledge base."""
    print(f"🗑️  Clearing knowledge base (confirm={confirm})...")
    
    response = requests.post(f"{BASE_URL}/clear", json={"confirm": confirm})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   • Documents cleared: {result['documents_cleared']}")
    else:
        error = response.json().get("detail", "Unknown error")
        print(f"❌ Clear failed: {error}")
    
    return response.status_code == 200

def main():
    """Main demo function."""
    print_section("KNOWLEDGE BASE MANAGEMENT DEMO")
    
    try:
        # Check initial state
        print_section("1. INITIAL STATE")
        get_vectorstore_info()
        
        # Add documents
        print_section("2. ADDING DOCUMENTS")
        add_success = add_sample_documents()
        
        if add_success:
            time.sleep(2)  # Wait for processing
            get_vectorstore_info()
            
            # Try to clear without confirmation
            print_section("3. CLEAR WITHOUT CONFIRMATION")
            clear_knowledge_base(confirm=False)
            
            # Clear with confirmation
            print_section("4. CLEAR WITH CONFIRMATION")
            clear_knowledge_base(confirm=True)
            
            # Check final state
            print_section("5. FINAL STATE")
            get_vectorstore_info()
            
            print_section("DEMO COMPLETED")
            print("✅ Knowledge base management demo completed successfully!")
            print("\n💡 Key Features:")
            print("   • Safe clearing with confirmation requirement")
            print("   • Real-time vectorstore information")
            print("   • Complete document and index file removal")
            print("   • RESTful API design")
        
        else:
            print("\n❌ Demo failed: Could not add sample documents")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the server.")
        print("   Make sure the RAG Backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
