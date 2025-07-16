# 🤖 Local LLM Setup Instructions for TalentScout Hiring Assistant

This guide provides multiple options for setting up local Large Language Models (LLMs) for the TalentScout Hiring Assistant, eliminating the need for external API keys.

## 📋 Overview

The application supports three LLM options in order of preference:
1. **Ollama with Phi-3 Mini** (Recommended - Best performance)
2. **Hugging Face Transformers** (Fallback - Good offline capability)
3. **Rule-based responses** (Backup - Always works)

---

## 🥇 Option 1: Ollama with Phi-3 Mini (Recommended)

### Why Ollama + Phi-3?
- **Fast**: Optimized for local inference
- **Lightweight**: Phi-3 Mini is only 2.4GB
- **High Quality**: Microsoft's latest small language model
- **Private**: No data leaves your machine
- **Easy**: Simple installation and management

### Installation Steps

#### Windows
1. **Download Ollama**
   ```bash
   # Visit https://ollama.com/download
   # Download and run the Windows installer
   ```

2. **Install Phi-3 Mini Model**
   ```bash
   ollama pull phi3:mini
   ```

3. **Start Ollama Service**
   ```bash
   # Ollama usually starts automatically on Windows
   # If not, run:
   ollama serve
   ```

4. **Test the Installation**
   ```bash
   ollama run phi3:mini "Hello, can you help with technical interviews?"
   ```

#### Linux/macOS
1. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull Phi-3 Mini Model**
   ```bash
   ollama pull phi3:mini
   ```

3. **Start Ollama Service**
   ```bash
   ollama serve
   ```

4. **Test the Installation**
   ```bash
   ollama run phi3:mini "Hello, can you help with technical interviews?"
   ```

### Configuration

1. **Update .env file**
   ```bash
   OLLAMA_URL=http://localhost:11434
   MODEL_NAME=phi3:mini
   ```

2. **Verify Setup**
   ```bash
   python setup_ollama.py
   ```

### Alternative Models

If you want to try other models:

```bash
# Smaller and faster (1.1GB)
ollama pull phi3:3.8b

# Larger and more capable (7GB)
ollama pull llama3:8b

# Code-focused model (4GB)
ollama pull codellama:7b
```

Update your `.env` file with the chosen model:
```bash
MODEL_NAME=llama3:8b
```

---

## 🥈 Option 2: Hugging Face Transformers (Fallback)

### Why Hugging Face?
- **Offline**: Works without internet after initial download
- **Variety**: Access to thousands of models
- **Automatic**: Falls back automatically if Ollama isn't available
- **Flexible**: Can use different model sizes based on your hardware

### Installation Steps

1. **Install Required Packages**
   ```bash
   pip install torch transformers accelerate
   ```

2. **GPU Support (Optional)**
   ```bash
   # For NVIDIA GPUs
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **The application will automatically download and cache models on first use**

### Supported Models

The application includes several model options:

- **DialoGPT-small** (117MB) - Fast, good for basic conversations
- **DialoGPT-medium** (345MB) - Better quality, still fast
- **DistilGPT-2** (319MB) - Lightweight, general purpose

### Configuration

No additional configuration needed - the app automatically selects the best available model.

---

## 🥉 Option 3: Rule-based Responses (Backup)

### Why Rule-based?
- **Always Works**: No dependencies or downloads
- **Fast**: Instant responses
- **Reliable**: Consistent behavior
- **Lightweight**: No additional resources needed

### How it Works

The application includes pre-written responses for common scenarios:
- Greeting messages
- Technical questions from the built-in question bank
- Information collection guidance
- Fallback responses for unexpected inputs

This option is automatically active when neither Ollama nor Hugging Face models are available.

---

## 🚀 Quick Start Guide

### Method 1: Automated Setup (Recommended)

1. **Run the Ollama Setup Script**
   ```bash
   python setup_ollama.py
   ```

2. **Start the Application**
   ```bash
   streamlit run app.py
   ```

### Method 2: Manual Setup

1. **Install Ollama** (follow Option 1 above)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Services**
   ```bash
   # Terminal 1: Start Ollama
   ollama serve
   
   # Terminal 2: Start Application
   streamlit run app.py
   ```

### Method 3: Docker Setup

1. **Build and Run with Docker**
   ```bash
   docker-compose up --build
   ```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

#### 2. "Model not found"
```bash
# List available models
ollama list

# Pull the required model
ollama pull phi3:mini
```

#### 3. "Out of memory" errors
```bash
# Try a smaller model
ollama pull phi3:mini

# Or use Hugging Face fallback
# The app will automatically use smaller models
```

#### 4. Slow responses
```bash
# Check if you have GPU support
python -c "import torch; print(torch.cuda.is_available())"

# Consider using a smaller model
ollama pull phi3:mini
```

### Performance Tips

1. **For Better Performance**
   - Use an SSD for model storage
   - Ensure adequate RAM (8GB minimum, 16GB recommended)
   - Close unnecessary applications
   - Use GPU acceleration if available

2. **For Lower Resource Usage**
   - Use `phi3:mini` instead of larger models
   - Enable the Hugging Face fallback
   - Use rule-based responses for basic functionality

---

## 🎛️ Configuration Options

### Environment Variables

```bash
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
MODEL_NAME=phi3:mini

# Application Settings
APP_NAME=TalentScout Hiring Assistant
DEBUG=False

# Model Preferences
PREFER_OLLAMA=true
ENABLE_HF_FALLBACK=true
ENABLE_RULE_BASED=true
```

### Model Selection Priority

1. **Ollama** (if available and configured)
2. **Hugging Face** (if models can be loaded)
3. **Rule-based** (always available)

---

## 📊 Model Comparison

| Model | Size | Speed | Quality | Memory | Best For |
|-------|------|-------|---------|---------|----------|
| Phi-3 Mini | 2.4GB | Fast | High | 4GB RAM | Recommended |
| Phi-3 3.8B | 2.3GB | Fast | Higher | 6GB RAM | Better responses |
| Llama-3 8B | 7GB | Medium | Highest | 12GB RAM | Best quality |
| DialoGPT-small | 117MB | Very Fast | Medium | 2GB RAM | Low resources |
| Rule-based | 0MB | Instant | Basic | Minimal | Always works |

---

## 🏃‍♂️ Getting Started

1. **Choose your preferred option** based on your system resources
2. **Follow the installation steps** for your chosen option
3. **Test the setup** using the demo script: `python demo.py`
4. **Run the application**: `streamlit run app.py`
5. **Open your browser** to `http://localhost:8501`

---

## 📞 Support

If you encounter issues:

1. **Check the application logs** in the terminal
2. **Run the demo script** to test individual components
3. **Try the fallback options** if one method doesn't work
4. **Check the troubleshooting section** above

The application is designed to be robust and will work with at least rule-based responses even if all LLM options fail.

---

## 🔄 Updates

To update your models:

```bash
# Update Ollama models
ollama pull phi3:mini

# Update Hugging Face cache
# Models are automatically updated when available
```

---

**🎉 You're ready to go! The TalentScout Hiring Assistant will now use your local LLM for intelligent, private candidate screening.**
