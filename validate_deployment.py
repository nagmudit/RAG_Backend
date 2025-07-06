#!/usr/bin/env python3
"""
Deployment validation script for RAG Backend
Tests if all dependencies can be imported and basic configuration works
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("langchain", "LangChain"),
        ("langchain_mistralai", "LangChain Mistral"),
        ("faiss", "FAISS"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
        ("bs4", "BeautifulSoup4"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "Pydantic"),
    ]
    
    failed_imports = []
    
    for package, name in imports_to_test:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            failed_imports.append(name)
    
    return failed_imports

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing environment...")
    
    # Test if we can import our app modules
    try:
        from app.config import settings
        print("✅ App configuration loaded")
        
        # Test basic settings
        print(f"✅ Log level: {settings.LOG_LEVEL}")
        print(f"✅ FAISS index path: {settings.FAISS_INDEX_PATH}")
        
        # Check if API key is set (without revealing it)
        if settings.MISTRAL_API_KEY:
            print("✅ Mistral API key is set")
        else:
            print("⚠️  Mistral API key not set (required for production)")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories can be created"""
    print("\n📁 Testing directories...")
    
    try:
        # Test data directory creation
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        print("✅ Data directory created")
        
        # Test if we can write to it
        test_file = data_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Data directory is writable")
        
    except Exception as e:
        print(f"❌ Directory error: {e}")
        return False
    
    return True

def main():
    """Run all validation tests"""
    print("🚀 RAG Backend Deployment Validation")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test environment
    env_ok = test_environment()
    
    # Test directories
    dirs_ok = test_directories()
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 30)
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
    else:
        print("✅ All imports successful")
    
    if env_ok:
        print("✅ Environment configuration OK")
    else:
        print("❌ Environment configuration issues")
    
    if dirs_ok:
        print("✅ Directory setup OK")
    else:
        print("❌ Directory setup issues")
    
    # Overall result
    if not failed_imports and env_ok and dirs_ok:
        print("\n🎉 Deployment validation PASSED!")
        print("Your RAG Backend is ready to deploy!")
        return 0
    else:
        print("\n⚠️  Deployment validation FAILED!")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
