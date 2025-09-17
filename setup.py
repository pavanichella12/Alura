#!/usr/bin/env python3
"""
AI Content Moderation System - Automated Setup Script
This script automatically installs and configures everything needed to run the system.
"""

import os
import sys
import subprocess
import platform
import json
import shutil
from pathlib import Path

class SystemSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.project_root = Path.cwd()
        
    def print_header(self):
        print("=" * 60)
        print("🛡️  AI CONTENT MODERATION SYSTEM - SETUP")
        print("=" * 60)
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print("=" * 60)
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🔍 Checking Python version...")
        if self.python_version < (3, 9):
            print("❌ Python 3.9+ required. Current version:", f"{self.python_version.major}.{self.python_version.minor}")
            print("Please upgrade Python and try again.")
            return False
        print("✅ Python version compatible")
        return True
    
    def check_ollama_installed(self):
        """Check if Ollama is installed"""
        print("🔍 Checking Ollama installation...")
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama is already installed")
                return True
        except FileNotFoundError:
            pass
        
        print("⚠️ Ollama not found. Installing...")
        return self.install_ollama()
    
    def install_ollama(self):
        """Install Ollama based on the operating system"""
        print("📦 Installing Ollama...")
        
        if self.system == "darwin":  # macOS
            print("🍎 Detected macOS - Ollama requires manual installation")
            print("📥 Please download and install Ollama from: https://ollama.ai/")
            print("   1. Go to https://ollama.ai/")
            print("   2. Click 'Download for macOS'")
            print("   3. Install the .dmg file")
            print("   4. Run this setup script again")
            print()
            print("⚠️  The system will work without Ollama (using fallback mode)")
            print("   But for full AI functionality, please install Ollama manually.")
            return False
                
        elif self.system == "linux":
            try:
                print("🐧 Detected Linux - Installing Ollama automatically...")
                subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                             shell=True, check=True)
                print("✅ Ollama installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Ollama: {e}")
                print("Please install Ollama manually from: https://ollama.ai/")
                return False
                
        elif self.system == "windows":
            print("🪟 Detected Windows - Ollama requires manual installation")
            print("📥 Please download and install Ollama from: https://ollama.ai/")
            print("   1. Go to https://ollama.ai/")
            print("   2. Click 'Download for Windows'")
            print("   3. Install the .exe file")
            print("   4. Run this setup script again")
            print()
            print("⚠️  The system will work without Ollama (using fallback mode)")
            print("   But for full AI functionality, please install Ollama manually.")
            return False
        
        return False
    
    def download_llama_model(self):
        """Download Llama 3 model"""
        print("🤖 Downloading Llama 3 model (this may take a few minutes)...")
        try:
            # Start Ollama service
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a moment for service to start
            import time
            time.sleep(3)
            
            # Pull the model
            result = subprocess.run(['ollama', 'pull', 'llama3:8b'], 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("✅ Llama 3 model downloaded successfully")
                return True
            else:
                print(f"❌ Failed to download model: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Model download timed out. Please try again.")
            return False
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("🐍 Creating virtual environment...")
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        # Determine the correct pip path
        if self.system == "windows":
            pip_path = self.project_root / "venv" / "Scripts" / "pip"
        else:
            pip_path = self.project_root / "venv" / "bin" / "pip"
        
        try:
            subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], check=True)
            print("✅ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def create_env_template(self):
        """Create .env template file"""
        print("📝 Creating environment configuration...")
        
        env_template = """# AI Content Moderation System - Environment Configuration
# Copy this file to .env and fill in your actual values

# Twilio WhatsApp Configuration (Optional - for notifications)
# Get these from: https://console.twilio.com/
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE=+14155238886
REVIEWER_PHONE=+15714733917

# System Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
"""
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write(env_template)
            print("✅ Environment template created (.env)")
        else:
            print("✅ Environment file already exists")
        
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating project directories...")
        
        directories = [
            "data/database",
            "data/knowledge_base", 
            "data/rag",
            "data/processed",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directories created")
        return True
    
    def test_system(self):
        """Test if the system is working"""
        print("🧪 Testing system components...")
        
        # Test Python imports
        try:
            sys.path.insert(0, str(self.project_root))
            from src.core.hybrid_moderator import HybridModerator
            print("✅ Python imports working")
        except ImportError as e:
            print(f"❌ Python import failed: {e}")
            return False
        
        # Test Ollama connection
        try:
            import ollama
            models = ollama.list()
            if any('llama3' in model['name'] for model in models['models']):
                print("✅ Ollama and Llama 3 model working")
            else:
                print("⚠️ Llama 3 model not found, but Ollama is working")
        except Exception as e:
            print(f"⚠️ Ollama test failed: {e}")
            print("This is okay - the system will use fallback mode")
        
        return True
    
    def create_run_script(self):
        """Create easy-to-use run script"""
        print("🚀 Creating run script...")
        
        if self.system == "windows":
            run_script = """@echo off
echo Starting AI Content Moderation System...
echo.

REM Activate virtual environment
call venv\\Scripts\\activate

REM Start Ollama in background
echo Starting Ollama service...
start /B ollama serve

REM Wait for Ollama to start
timeout /t 5 /nobreak > nul

REM Start the application
echo Starting Streamlit application...
echo.
echo 🌐 The app will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.port 8501
"""
            with open("run_demo.bat", "w") as f:
                f.write(run_script)
        else:
            run_script = """#!/bin/bash
echo "Starting AI Content Moderation System..."
echo

# Activate virtual environment
source venv/bin/activate

# Start Ollama in background
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 5

# Start the application
echo "Starting Streamlit application..."
echo
echo "🌐 The app will open in your browser at: http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application"
echo

# Function to cleanup on exit
cleanup() {
    echo "Stopping Ollama..."
    kill $OLLAMA_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

streamlit run app.py --server.port 8501
"""
            with open("run_demo.sh", "w") as f:
                f.write(run_script)
            
            # Make it executable
            os.chmod("run_demo.sh", 0o755)
        
        print("✅ Run script created")
        return True
    
    def run_setup(self):
        """Run the complete setup process"""
        self.print_header()
        
        # Core setup steps (must succeed)
        core_steps = [
            ("Python Version Check", self.check_python_version),
            ("Create Directories", self.create_directories),
            ("Create Virtual Environment", self.create_virtual_environment),
            ("Install Python Dependencies", self.install_python_dependencies),
            ("Create Environment Template", self.create_env_template),
            ("Create Run Script", self.create_run_script),
        ]
        
        # Optional steps (can fail gracefully)
        optional_steps = [
            ("Check Ollama Installation", self.check_ollama_installed),
            ("Download Llama Model", self.download_llama_model),
        ]
        
        # Run core steps first
        for step_name, step_func in core_steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                print("\n🔧 Manual setup required. Please check the README.md for instructions.")
                return False
        
        # Run optional steps (don't fail if they don't work)
        ollama_working = True
        for step_name, step_func in optional_steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"⚠️  {step_name} failed - system will use fallback mode")
                ollama_working = False
                break
        
        # Test the system
        print(f"\n📋 Testing System...")
        if not self.test_system():
            print("⚠️  System test failed - but basic functionality should work")
        
        # Show final status
        if ollama_working:
            print("\n" + "=" * 60)
            print("🎉 SETUP COMPLETE!")
            print("=" * 60)
            print("✅ Your AI Content Moderation System is ready!")
            print("✅ Full AI functionality available (Ollama + Llama 3)")
        else:
            print("\n" + "=" * 60)
            print("🎉 SETUP COMPLETE!")
            print("=" * 60)
            print("✅ Your AI Content Moderation System is ready!")
            print("⚠️  Running in fallback mode (keyword matching)")
            print("📥 To enable full AI: Install Ollama from https://ollama.ai/")
        
        print()
        print("🚀 To start the system:")
        if self.system == "windows":
            print("   Double-click: run_demo.bat")
        else:
            print("   Run: ./run_demo.sh")
        print()
        print("📖 For detailed instructions, see: README.md")
        print("🌐 The app will open at: http://localhost:8501")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    setup = SystemSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)