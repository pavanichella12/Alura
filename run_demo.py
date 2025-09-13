#!/usr/bin/env python3
"""
AI Content Moderation System - One-Command Demo Runner
This script starts everything needed to run the demo with proper error handling.
"""

import os
import sys
import subprocess
import time
import signal
import platform
from pathlib import Path

class DemoRunner:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path.cwd()
        self.ollama_process = None
        
    def print_header(self):
        print("=" * 60)
        print("🛡️  AI CONTENT MODERATION SYSTEM - DEMO")
        print("=" * 60)
        print("Starting all services...")
        print("=" * 60)
    
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check if virtual environment exists
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            print("❌ Virtual environment not found!")
            print("Please run: python setup.py")
            return False
        
        # Check if requirements are installed
        if self.system == "windows":
            pip_path = venv_path / "Scripts" / "pip"
        else:
            pip_path = venv_path / "bin" / "pip"
        
        try:
            result = subprocess.run([str(pip_path), 'list'], capture_output=True, text=True)
            if 'streamlit' not in result.stdout:
                print("❌ Dependencies not installed!")
                print("Please run: python setup.py")
                return False
        except Exception as e:
            print(f"❌ Error checking dependencies: {e}")
            return False
        
        print("✅ Requirements check passed")
        return True
    
    def start_ollama(self):
        """Start Ollama service"""
        print("🤖 Starting Ollama service...")
        
        try:
            # Check if Ollama is already running
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama is already running")
                return True
        except FileNotFoundError:
            print("❌ Ollama not found! Please install Ollama first.")
            print("Run: python setup.py")
            return False
        
        try:
            # Start Ollama in background
            self.ollama_process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for Ollama to start
            print("⏳ Waiting for Ollama to start...")
            for i in range(10):
                try:
                    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        print("✅ Ollama started successfully")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"   Attempt {i+1}/10...")
            
            print("❌ Ollama failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Ollama: {e}")
            return False
    
    def check_llama_model(self):
        """Check if Llama 3 model is available"""
        print("🔍 Checking Llama 3 model...")
        
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if 'llama3' in result.stdout:
                print("✅ Llama 3 model found")
                return True
            else:
                print("⚠️ Llama 3 model not found")
                print("The system will use fallback mode (keyword matching)")
                return True  # This is okay, system has fallbacks
        except Exception as e:
            print(f"⚠️ Could not check model: {e}")
            return True  # Continue anyway
    
    def start_streamlit(self):
        """Start Streamlit application"""
        print("🌐 Starting Streamlit application...")
        
        # Determine the correct python path
        if self.system == "windows":
            python_path = self.project_root / "venv" / "Scripts" / "python"
        else:
            python_path = self.project_root / "venv" / "bin" / "python"
        
        try:
            print("=" * 60)
            print("🚀 APPLICATION STARTING...")
            print("=" * 60)
            print("🌐 The app will open in your browser at: http://localhost:8501")
            print("=" * 60)
            print("📝 Demo Instructions:")
            print("   1. Try typing: 'Hello, how are you?' → Should be approved")
            print("   2. Try typing: 'You are a bitch' → Should be blocked with alternatives")
            print("   3. Use the sidebar to switch users and test different scenarios")
            print("=" * 60)
            print("Press Ctrl+C to stop the application")
            print("=" * 60)
            
            # Start Streamlit
            subprocess.run([
                str(python_path), '-m', 'streamlit', 'run', 'app.py',
                '--server.port', '8501',
                '--server.headless', 'false',
                '--browser.gatherUsageStats', 'false'
            ])
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping application...")
            return True
        except Exception as e:
            print(f"❌ Error starting Streamlit: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.ollama_process:
            print("🛑 Stopping Ollama...")
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=5)
            except:
                self.ollama_process.kill()
    
    def run_demo(self):
        """Run the complete demo"""
        self.print_header()
        
        # Set up signal handler for cleanup
        def signal_handler(signum, frame):
            print("\n🛑 Received interrupt signal...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Check requirements
            if not self.check_requirements():
                return False
            
            # Start Ollama
            if not self.start_ollama():
                return False
            
            # Check model
            self.check_llama_model()
            
            # Start Streamlit
            self.start_streamlit()
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

if __name__ == "__main__":
    runner = DemoRunner()
    success = runner.run_demo()
    sys.exit(0 if success else 1)