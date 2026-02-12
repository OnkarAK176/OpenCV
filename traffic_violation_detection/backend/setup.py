#!/usr/bin/env python
"""
Quick setup script for Traffic Violation Detection System
Handles model downloads and directory creation
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 60)
    print("  Traffic Violation Detection System - Setup")
    print("=" * 60 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required")
        logger.error(f"   Current version: {sys.version}")
        sys.exit(1)
    logger.info(f"✓ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'results',
        'models',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_cors', 'cv2', 'numpy', 
        'ultralytics', 'easyocr', 'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} not found")
    
    if missing_packages:
        logger.error("\n❌ Missing dependencies. Install them with:")
        logger.error(f"   pip install -r requirements.txt")
        return False
    
    logger.info("\n✓ All dependencies are installed!")
    return True

def download_models():
    """Initialize and download pre-trained models"""
    logger.info("\n" + "=" * 60)
    logger.info("Downloading Pre-trained Models")
    logger.info("=" * 60)
    
    try:
        logger.info("\n📥 Downloading YOLOv8 Model...")
        logger.info("   (This may take 2-5 minutes on first run)")
        
        from ultralytics import YOLO
        
        # Download YOLOv8 Nano model
        model = YOLO('yolov8n.pt')
        logger.info("✓ YOLOv8 model downloaded and cached")
        
        logger.info("\n📥 Initializing EasyOCR Reader...")
        logger.info("   (This may take 1-3 minutes)")
        
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        logger.info("✓ EasyOCR model initialized")
        
        logger.info("\n✓ All models ready!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Error downloading models: {e}")
        logger.error("   Please ensure you have internet connection")
        logger.error("   Models will be downloaded on first use")
        return False

def print_next_steps():
    """Print instructions for running the system"""
    print("\n" + "=" * 60)
    print("  Setup Complete! 🎉")
    print("=" * 60)
    print("\n📍 Next Steps:\n")
    print("1. Start the Backend Server:")
    print("   cd backend")
    print("   python app.py\n")
    print("2. In another terminal, start the Frontend:")
    print("   cd frontend")
    print("   python -m http.server 3000\n")
    print("3. Open your browser and go to:")
    print("   http://localhost:3000\n")
    print("=" * 60 + "\n")

def main():
    """Main setup function"""
    print_banner()
    
    logger.info("Starting setup...\n")
    
    # Check Python version
    check_python_version()
    
    # Create directories
    logger.info("\nCreating directories...")
    create_directories()
    
    # Check dependencies
    logger.info("\nChecking dependencies...")
    if not check_dependencies():
        logger.error("Please install missing dependencies first:")
        logger.error("pip install -r requirements.txt")
        return False
    
    # Download models (optional, can be skipped)
    logger.info("\nModel download is optional. It will happen on first use.")
    response = input("\nDownload models now? (y/n): ").lower().strip()
    
    if response == 'y':
        if not download_models():
            logger.warning("Models will be downloaded on first use")
    
    print_next_steps()
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {e}")
        sys.exit(1)
