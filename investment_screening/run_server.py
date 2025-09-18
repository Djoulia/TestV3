#!/usr/bin/env python3
"""
Startup script for the Investment Screening System
Runs the FastAPI server with proper configuration
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

def main():
    """Main function to start the server"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Change working directory to script directory
    os.chdir(script_dir)
    
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        env_path = script_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded environment variables from {env_path}")
        else:
            print(f"⚠️ No .env file found at {env_path}")
    except ImportError:
        print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Check environment variables
    api_key = os.getenv("LIGHTON_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        logger.warning("⚠️  LIGHTON_API_KEY not set or using default value")
        logger.warning("   Please set your API key in .env file: LIGHTON_API_KEY=your_actual_key")
        logger.warning(f"   Looking for .env file in: {script_dir}")
    else:
        logger.info("✅ LIGHTON_API_KEY loaded successfully")
    
    # Check if frontend file exists
    frontend_path = script_dir / "frontend.html"
    if not frontend_path.exists():
        logger.error("❌ frontend.html not found!")
        logger.error(f"   Looking in: {frontend_path}")
        logger.error("   Please ensure frontend.html is in the same directory as this script")
        logger.error(f"   Current files in directory: {list(script_dir.glob('*'))}")
        sys.exit(1)
    else:
        logger.info(f"✅ Found frontend.html at: {frontend_path}")
    
    logger.info("🚀 Starting Investment Screening System...")
    logger.info(f"📁 Working directory: {script_dir}")
    logger.info("📁 Frontend will be available at: http://localhost:8000")
    logger.info("📊 API documentation at: http://localhost:8000/docs")
    logger.info("🛑 Press Ctrl+C to stop the server")
    
    # Start the server
    try:
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload on code changes
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()