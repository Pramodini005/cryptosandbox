#!/usr/bin/env python3
"""
Crypto Price Alert Assistant - Application Runner
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

def run_fastapi():
    """Run FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error running FastAPI server: {e}")

def run_streamlit():
    """Run Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for FastAPI to start
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit server: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def main():
    """Main application runner"""
    print("=" * 60)
    print("🚀 CRYPTO PRICE ALERT ASSISTANT")
    print("=" * 60)
    print("🔧 AI-Powered Real-time Cryptocurrency Monitoring")
    print("📊 Smart Alerts • Pattern Recognition • Sentiment Analysis")
    print("=" * 60)
    
    # Check if required files exist
    required_files = ["main.py", "streamlit_app.py", "requirements.txt"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all files are in the current directory.")
        return
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Some dependencies might not have installed correctly")
        print("You may need to install them manually:")
        print("pip install fastapi uvicorn streamlit plotly pandas requests websocket-client")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start servers in separate threads
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    
    print("\n🌟 Starting application servers...")
    print("📡 FastAPI Backend: http://localhost:8000")
    print("🎨 Streamlit Frontend: http://localhost:8501")
    print("\n⚡ Features Available:")
    print("  • Real-time price monitoring")
    print("  • Smart AI-powered alerts")
    print("  • Market sentiment analysis")
    print("  • Technical pattern recognition")
    print("  • Volume spike detection")
    print("  • Whale movement tracking")
    print("  • Arbitrage opportunities")
    print("  • Advanced analytics & predictions")
    print("\n🔥 Ready for hackathon demo!")
    print("=" * 60)
    
    # Start threads
    fastapi_thread.start()
    streamlit_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    
    print("👋 Thank you for using Crypto Price Alert Assistant!")

if __name__ == "__main__":
    main()
