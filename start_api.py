#!/usr/bin/env python3
"""
Startup script for AI Agent API Server
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the AI Agent API server"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    print("🚀 Starting AI Agent API Server...")
    print(f"📁 Working directory: {script_dir}")
    
    # Change to the AI Agent directory
    os.chdir(script_dir)
    
    # Check if virtual environment exists
    venv_path = script_dir / "venv"
    if venv_path.exists():
        print("✅ Virtual environment found")
        
        # Determine the Python executable based on OS
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        if python_exe.exists():
            print(f"🐍 Using Python: {python_exe}")
            
            # Start the API server
            try:
                subprocess.run([str(python_exe), "api_server.py"], check=True)
            except KeyboardInterrupt:
                print("\n👋 Server stopped by user")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error starting server: {e}")
        else:
            print("❌ Python executable not found in virtual environment")
            print("💡 Please activate the virtual environment manually and run: python api_server.py")
    else:
        print("❌ Virtual environment not found")
        print("💡 Please create a virtual environment first:")
        print("   python -m venv venv")
        print("   # Then activate it and install requirements:")
        print("   pip install -r requirements.txt")
        print("   python api_server.py")

if __name__ == "__main__":
    main() 