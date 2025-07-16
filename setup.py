#!/usr/bin/env python3
"""
Setup script for TalentScout Hiring Assistant
This script helps set up the environment and dependencies
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor} is compatible")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activation command depends on OS
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
    
    print(f"📝 To activate virtual environment, run: {activate_cmd}")
    return True

def install_dependencies():
    """Install required packages"""
    pip_cmd = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    return True

def setup_environment_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            if os.name == 'nt':
                run_command("copy .env.example .env", "Creating .env file")
            else:
                run_command("cp .env.example .env", "Creating .env file")
            
            print("\n🔑 IMPORTANT: Please edit .env file and add your OpenAI API key!")
            print("   Edit the line: OPENAI_API_KEY=your_openai_api_key_here")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_data_directory():
    """Create data directory for storing candidate information"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up TalentScout Hiring Assistant")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        sys.exit(1)
    
    # Create data directory
    if not create_data_directory():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Activate virtual environment:")
    
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("3. Run the application:")
    print("   streamlit run app.py")
    print("\n4. Open your browser and go to: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    main()
