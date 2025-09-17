"""
Streamlit Cloud Deployment Entry Point
This file is required for Streamlit Cloud deployment
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()