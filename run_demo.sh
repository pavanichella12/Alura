#!/bin/bash
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
