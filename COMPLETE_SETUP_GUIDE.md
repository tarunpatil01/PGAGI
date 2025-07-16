# TalentScout Hiring Assistant - Complete Setup Guide

## 🚀 Overview
TalentScout is an AI-powered hiring assistant that uses **Phi-3 Mini** with **Ollama** for natural language processing. This guide covers complete setup for both local development and cloud deployment.

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (3.10+ recommended)
- **8GB+ RAM** (16GB recommended for optimal performance)
- **5GB+ free disk space** (for models and dependencies)
- **Internet connection** (for initial setup and model downloads)

### Operating System Support
- ✅ **Windows 10/11**
- ✅ **macOS 10.15+**
- ✅ **Linux (Ubuntu 20.04+, CentOS 8+)**

## 🛠️ Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/tarunpatil01/PGAGI.git
cd PGAGI/hiring-assistant
```

### 2. Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# DEPLOYMENT_MODE=local  # or "cloud" for cloud deployment
# OLLAMA_URL=http://localhost:11434
# MODEL_NAME=phi3:mini
```

### 5. Install and Configure Ollama

#### Option A: Automatic Setup (Recommended)
```bash
python setup_ollama.py
```

#### Option B: Manual Setup

**Windows:**
1. Download Ollama from https://ollama.com/download/windows
2. Install the executable
3. Open Command Prompt and run:
```cmd
ollama serve
```

**macOS:**
1. Download from https://ollama.com/download/mac
2. Or install via Homebrew:
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

### 6. Pull Phi-3 Model
```bash
ollama pull phi3:mini
```

### 7. Test the Setup
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Test Phi-3 model
ollama run phi3:mini "Hello, how are you?"
```

### 8. Run the Application
```bash
streamlit run app.py
```

## 🌐 Cloud Deployment

### Docker Deployment

#### Build Docker Image
```bash
docker build -t talentscout-hiring-assistant .
```

#### Run with Docker Compose
```bash
docker-compose up -d
```

### Platform-Specific Deployment

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway deploy
```

#### Render
1. Connect your GitHub repository
2. Select "Docker" as build environment
3. Set environment variables
4. Deploy

#### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly deploy
```

## 🔧 Configuration Options

### LLM Configuration
```python
from local_llm import LLMConfig

config = LLMConfig(
    ollama_url="http://localhost:11434",
    model_name="phi3:mini",
    temperature=0.7,
    max_tokens=500,
    timeout=30,
    is_cloud=False
)
```

### Environment Variables
```bash
# Core Settings
DEPLOYMENT_MODE=local          # local or cloud
OLLAMA_URL=http://localhost:11434
MODEL_NAME=phi3:mini

# Performance Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
LLM_TIMEOUT=30

# Cloud Settings (for cloud deployment)
CLOUD_OLLAMA_URL=http://ollama:11434
CLOUD_MODEL_PULL_TIMEOUT=600
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Performance Tests
```bash
python -m pytest tests/performance/
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Ollama Connection Error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

#### 2. Phi-3 Model Not Found
```bash
# Pull the model
ollama pull phi3:mini

# Verify installation
ollama list
```

#### 3. Memory Issues
```bash
# Check system memory
free -h  # Linux/macOS
wmic computersystem get TotalPhysicalMemory  # Windows

# Reduce model load if needed
export OLLAMA_NUM_PARALLEL=1
```

#### 4. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :11434  # Linux/macOS
netstat -an | findstr :11434  # Windows

# Kill conflicting processes
sudo kill -9 <PID>
```

### Performance Optimization

#### 1. Hardware Acceleration
```bash
# Check GPU availability
nvidia-smi  # NVIDIA GPU
rocm-smi   # AMD GPU

# Enable GPU support
export OLLAMA_GPU=1
```

#### 2. Memory Management
```bash
# Optimize memory usage
export OLLAMA_MODELS_PATH=/path/to/models
export OLLAMA_KEEP_ALIVE=5m
```

#### 3. Concurrent Requests
```bash
# Configure concurrent processing
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=4
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8501/health

# Ollama health
curl http://localhost:11434/api/tags
```

### Logging
```bash
# View application logs
tail -f logs/app.log

# View Ollama logs
ollama logs
```

### Metrics
- Response time monitoring
- Model inference speed
- Memory usage tracking
- Error rate analysis

## 🚀 Advanced Features

### Custom Models
```python
# Use different Phi-3 variants
config = LLMConfig(model_name="phi3:medium")  # More capable
config = LLMConfig(model_name="phi3:mini")    # Faster
```

### Multi-Model Support
```python
# Configure multiple models
models = {
    "screening": "phi3:mini",
    "technical": "phi3:medium",
    "summary": "phi3:mini"
}
```

### API Integration
```python
# REST API endpoint
@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    # Handle API requests
    pass
```

## 📋 Maintenance

### Regular Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Phi-3 model
ollama pull phi3:mini
```

### Backup Configuration
```bash
# Backup models
cp -r ~/.ollama/models /backup/location

# Backup application data
cp -r data/ /backup/location
```

### Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade  # Ubuntu
brew update && brew upgrade          # macOS
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 .
pylint src/

# Type checking
mypy src/
```

## 📞 Support

### Community Support
- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share ideas
- **Documentation**: Comprehensive guides and examples

### Enterprise Support
- **Priority Support**: Dedicated support channel
- **Custom Deployment**: Tailored deployment solutions
- **Training**: Team training and best practices

## 🔄 Updates and Changelog

### Version 2.0.0 (Current)
- ✅ **Phi-3 Mini Integration**: Complete Phi-3 with Ollama support
- ✅ **Cloud Deployment**: Docker and multi-platform support
- ✅ **Intelligent Fallbacks**: Context-aware fallback responses
- ✅ **Performance Optimization**: Improved response times
- ✅ **Enhanced UI**: Better user experience

### Upcoming Features
- 🔄 **Multi-language Support**: Support for multiple languages
- 🔄 **Advanced Analytics**: Detailed hiring insights
- 🔄 **Integration APIs**: Third-party system integration
- 🔄 **Custom Workflows**: Configurable hiring processes

---

**Need Help?** Check our [FAQ](FAQ.md) or [create an issue](https://github.com/tarunpatil01/PGAGI/issues) for support.
