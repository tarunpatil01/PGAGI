#!/usr/bin/env python3
"""
Ollama Setup Script for TalentScout Hiring Assistant
This script helps install and configure Ollama with the Phi-3 model
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False, None

def check_ollama_installation():
    """Check if Ollama is installed"""
    print("🔍 Checking Ollama installation...")
    success, output = run_command("ollama --version", "Checking Ollama version", check=False)
    if success:
        print("✅ Ollama is already installed")
        return True
    else:
        print("❌ Ollama is not installed")
        return False

def install_ollama_windows():
    """Install Ollama on Windows"""
    print("📥 Installing Ollama for Windows...")
    print("Please visit https://ollama.com/download and download the Windows installer")
    print("After installation, restart your terminal and run this script again.")
    return False

def install_ollama_unix():
    """Install Ollama on Unix/Linux systems"""
    print("📥 Installing Ollama...")
    success, _ = run_command("curl -fsSL https://ollama.com/install.sh | sh", "Installing Ollama")
    return success

def check_ollama_service():
    """Check if Ollama service is running"""
    print("🔍 Checking if Ollama service is running...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print("❌ Ollama service is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama service is not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Ollama service connection timeout")
        return False

def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    if os.name == 'nt':  # Windows
        # On Windows, Ollama usually runs as a service
        print("Please start Ollama from the Start menu or run 'ollama serve' in a separate terminal")
        return False
    else:
        # On Unix/Linux
        success, _ = run_command("ollama serve &", "Starting Ollama service")
        time.sleep(3)  # Give it time to start
        return success

def pull_phi3_model():
    """Pull the Phi-3 model"""
    print("📥 Pulling Phi-3 model (this may take a while)...")
    success, _ = run_command("ollama pull phi3:mini", "Pulling Phi-3 model")
    return success

def list_available_models():
    """List available models"""
    print("📋 Available models:")
    success, output = run_command("ollama list", "Listing available models")
    if success and output:
        print(output)
    return success

def test_model():
    """Test the model"""
    print("🧪 Testing the model...")
    test_prompt = "Hello, can you help me with technical interviews?"
    success, _ = run_command(f'ollama run phi3:mini "{test_prompt}"', "Testing model")
    return success

def create_env_file():
    """Create or update .env file"""
    env_content = """# Ollama Configuration
OLLAMA_URL=http://localhost:11434
MODEL_NAME=phi3:mini

# Application Settings
APP_NAME=TalentScout Hiring Assistant
APP_VERSION=1.0.0
DEBUG=False

# Contact Information
CONTACT_EMAIL=careers@talentscout.com
COMPANY_NAME=TalentScout
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Ollama configuration")

def main():
    """Main setup function"""
    print("🚀 Setting up Ollama for TalentScout Hiring Assistant")
    print("=" * 60)
    
    # Check if Ollama is installed
    if not check_ollama_installation():
        print("\n📦 Ollama Installation Required")
        print("=" * 40)
        
        if os.name == 'nt':  # Windows
            install_ollama_windows()
            print("\nPlease install Ollama and run this script again.")
            return False
        else:
            if not install_ollama_unix():
                print("Failed to install Ollama. Please install manually from https://ollama.com/")
                return False
    
    # Check if service is running
    if not check_ollama_service():
        print("\n🔧 Starting Ollama Service")
        print("=" * 30)
        
        if not start_ollama_service():
            print("Please start Ollama service manually:")
            print("  Windows: Start Ollama from Start menu or run 'ollama serve'")
            print("  Unix/Linux: Run 'ollama serve' in a separate terminal")
            print("\nThen run this script again.")
            return False
        
        # Wait and check again
        time.sleep(5)
        if not check_ollama_service():
            print("❌ Failed to start Ollama service")
            return False
    
    # Pull the model
    print("\n📥 Setting up Phi-3 Model")
    print("=" * 30)
    
    if not pull_phi3_model():
        print("❌ Failed to pull Phi-3 model")
        return False
    
    # List available models
    print("\n📋 Available Models")
    print("=" * 20)
    list_available_models()
    
    # Test the model
    print("\n🧪 Testing Model")
    print("=" * 15)
    if not test_model():
        print("❌ Model test failed")
        return False
    
    # Create environment file
    print("\n⚙️ Configuration")
    print("=" * 15)
    create_env_file()
    
    print("\n" + "=" * 60)
    print("🎉 Ollama setup completed successfully!")
    print("\nYour setup:")
    print("- Model: Phi-3 Mini")
    print("- Ollama URL: http://localhost:11434")
    print("- Configuration: .env file created")
    
    print("\nNext steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Run the application: streamlit run app.py")
    print("3. Open your browser and go to: http://localhost:8501")
    
    print("\nNote: Keep Ollama service running while using the application")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
