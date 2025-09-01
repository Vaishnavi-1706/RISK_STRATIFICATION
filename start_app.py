#!/usr/bin/env python3
"""
Quick start script for Risk Stratification Web Application
This script will check dependencies and start the application
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 
        'reportlab', 'matplotlib', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            return False
    
    return True

def check_model():
    """Check if model exists, if not train one"""
    model_path = "models/risk_model.pkl"
    if not os.path.exists(model_path):
        print("🤖 No trained model found. Training a new model...")
        try:
            subprocess.check_call([sys.executable, 'train_model.py'])
            print("✅ Model trained successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to train model. Please run: python train_model.py")
            return False
    else:
        print("✅ Trained model found")
    
    return True

def start_app():
    """Start the Flask application"""
    print("\n🚀 Starting Risk Stratification Web Application...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main function"""
    print("🏥 Risk Stratification Web Application - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return
    
    # Check model
    print("\n🤖 Checking ML model...")
    if not check_model():
        return
    
    # Start application
    start_app()

if __name__ == "__main__":
    main()
