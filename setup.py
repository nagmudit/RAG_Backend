#!/usr/bin/env python3
"""
Startup script for the RAG Backend
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print("Warning: .env file not found. Creating from template...")
        import shutil
        shutil.copy(".env.example", ".env")
        print("✓ Created .env file from template")
        print("⚠️  Please edit .env file and add your Mistral API key")
        return False
    else:
        print("✓ .env file found")
        return True

def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)

def check_gpu_support():
    """Check if GPU support is available for FAISS."""
    try:
        import faiss
        if faiss.get_num_gpus() > 0:
            print(f"✓ GPU support available - {faiss.get_num_gpus()} GPU(s) detected")
        else:
            print("ℹ️  No GPU detected, will use CPU for FAISS")
    except ImportError:
        print("ℹ️  FAISS not installed yet")

def main():
    """Main startup function."""
    print("🚀 RAG Backend Startup Script")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check .env file
    env_exists = check_env_file()
    
    # Install dependencies
    install_dependencies()
    
    # Check GPU support
    check_gpu_support()
    
    print("\n" + "=" * 40)
    if env_exists:
        print("✅ Setup complete! You can now start the server:")
        print("   python main.py")
        print("   OR")
        print("   uvicorn main:app --reload")
    else:
        print("⚠️  Setup almost complete!")
        print("   1. Edit .env file and add your Mistral API key")
        print("   2. Then start the server with: python main.py")
    
    print("\n📖 API Documentation will be available at:")
    print("   http://localhost:8000/docs")

if __name__ == "__main__":
    main()
