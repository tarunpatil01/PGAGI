# TalentScout Hiring Assistant

An intelligent AI-powered chatbot for initial candidate screening in technology recruitment. Built with Streamlit and OpenAI's GPT models.

## 🚀 Features

### Core Functionality
- **Interactive Candidate Screening**: Streamlined conversation flow for gathering candidate information
- **Tech Stack Assessment**: Dynamic technical question generation based on candidate's technology stack
- **Intelligent Conversation Management**: Context-aware responses with fallback mechanisms
- **Data Privacy Compliance**: Secure handling of candidate information
- **Professional UI/UX**: Clean, intuitive interface built with Streamlit

### AI/LLM Integration
- **Primary**: Ollama with Phi-3 Mini model for local, private AI responses
- **Fallback**: Hugging Face Transformers for offline capability
- **Backup**: Rule-based responses ensure the app always works
- **No API Keys Required**: Completely self-contained solution

### Technical Capabilities
- **Local LLM Support**: Runs entirely on your machine without external API calls
- **Dynamic Question Generation**: Tailored technical questions for 9+ technology domains
- **Input Validation**: Email, phone number, and data format validation
- **Session Management**: Persistent conversation state and progress tracking
- **Responsive Design**: Mobile-friendly interface with custom styling

## 🏗️ Architecture

### Project Structure
```
hiring-assistant/
├── app.py                 # Main Streamlit application
├── utils.py              # Utility functions and data classes
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── data/                # Directory for candidate data storage
├── README.md            # This file
└── assets/              # Static assets (if needed)
```

### Key Components

1. **TalentScoutChatbot Class**: Main chatbot logic with state management
2. **CandidateInfo DataClass**: Structured candidate data storage
3. **TechnicalQuestionBank**: Repository of technology-specific questions
4. **DataHandler**: Secure data storage and retrieval
5. **PromptTemplates**: Optimized prompts for different scenarios

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- **Option 1**: Ollama installed with Phi-3 model (recommended)
- **Option 2**: Internet connection for Hugging Face models
- **Option 3**: None required (uses fallback responses)
- Git (for version control)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tarunpatil01/PGAGI.git
   cd PGAGI/hiring-assistant
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up AI Model (Choose one option)**

   **Option A: Ollama (Recommended)**
   ```bash
   # Install Ollama from https://ollama.com/download
   # Then run:
   ollama pull phi3:mini
   ollama serve
   ```

   **Option B: Run setup script**
   ```bash
   python setup_ollama.py
   ```

   **Option C: Use without local AI**
   ```bash
   # The app will use fallback responses
   # No additional setup needed
   ```

5. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default settings work for most cases)
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:8501`
   - The chatbot interface will be ready for candidate interactions

## 🎯 Usage Guide

### For Candidates
1. **Start Conversation**: The chatbot greets you and asks for your name
2. **Provide Information**: Share your contact details, experience, and desired position
3. **Declare Tech Stack**: List your programming languages, frameworks, and tools
4. **Answer Technical Questions**: Respond to 3-5 tailored technical questions
5. **Complete Screening**: Review your information and receive next steps

### For Recruiters/Administrators
1. **Monitor Sessions**: Use the sidebar to track candidate progress
2. **Review Data**: Candidate information is stored securely in the `data/` directory
3. **Reset Sessions**: Use the "Start New Session" button to clear the conversation
4. **Customize Questions**: Modify the `TechnicalQuestionBank` in `utils.py`

## 🔧 Configuration

### Supported Technologies
The chatbot can generate questions for:
- **Programming Languages**: Python, JavaScript, Java
- **Frontend**: React, HTML/CSS
- **Backend**: Node.js, Django, Flask
- **Databases**: SQL, PostgreSQL, MongoDB
- **Cloud**: AWS, Azure, GCP
- **DevOps**: Docker, Kubernetes, Git
- **And more...

### Customization Options
1. **Question Bank**: Add/modify questions in `utils.py`
2. **Conversation Flow**: Adjust states in `app.py`
3. **UI Styling**: Modify CSS in the `main()` function
4. **Validation Rules**: Update validation functions in `utils.py`

## 🔐 Security & Privacy

### Data Protection
- **Local Storage**: All candidate data stored locally by default
- **No External Sharing**: Information not shared with third parties
- **Session Isolation**: Each session is independent and secure
- **Input Validation**: All inputs validated and sanitized

### Privacy Compliance
- **GDPR Ready**: Designed with privacy regulations in mind
- **Data Minimization**: Only collects necessary information
- **Secure Processing**: Uses encrypted API communication
- **Audit Trail**: Conversation logs for quality assurance

## 📊 Technical Specifications

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **AI/ML**: 
  - Primary: Ollama with Phi-3 Mini (local)
  - Fallback: Hugging Face Transformers
  - Backup: Rule-based responses
- **Data Storage**: JSON files (local), extensible to databases
- **Deployment**: Local development, cloud-ready

### Dependencies
```
streamlit               # Web framework
requests               # HTTP client
pandas                 # Data manipulation
python-dotenv         # Environment management
ollama                # Local LLM interface
transformers          # Hugging Face models
torch                 # Deep learning framework
accelerate           # Model optimization
sentence-transformers # Text embeddings
```

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment

#### Option 1: Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add environment variables
4. Deploy automatically

#### Option 2: AWS EC2
```bash
# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip -y

# Clone and setup
git clone <repository-url>
cd hiring-assistant
pip3 install -r requirements.txt

# Run with nohup for background execution
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

#### Option 3: Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Greeting and name collection
- [ ] Information gathering (email, phone, experience)
- [ ] Tech stack input and validation
- [ ] Technical question generation
- [ ] Conversation flow and state management
- [ ] Error handling and fallback responses
- [ ] Session reset functionality

### Common Test Scenarios
1. **Happy Path**: Complete full screening process
2. **Invalid Inputs**: Test email/phone validation
3. **Edge Cases**: Empty tech stack, long responses
4. **Conversation Endings**: "goodbye", "exit" keywords
5. **Error Recovery**: API failures, network issues

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is valid and has credits
   - Check the `.env` file configuration

2. **Streamlit Import Error**
   - Verify virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Use different port: `streamlit run app.py --server.port 8502`

4. **Tech Stack Questions Not Generated**
   - Check if technology is supported in `TechnicalQuestionBank`
   - Verify API response format

## 🎨 Customization Examples

### Adding New Technologies
```python
# In utils.py, add to TechnicalQuestionBank
"flutter": [
    TechnicalQuestion("Flutter", "What is the difference between StatefulWidget and StatelessWidget?", "basic"),
    TechnicalQuestion("Flutter", "How do you manage state in Flutter applications?", "intermediate"),
]
```

### Modifying Question Difficulty
```python
# Adjust difficulty distribution in get_questions_for_tech_stack
def get_questions_for_tech_stack(self, tech_stack: List[str], total_questions: int = 5):
    # 60% basic, 30% intermediate, 10% advanced
    basic_count = int(total_questions * 0.6)
    intermediate_count = int(total_questions * 0.3)
    advanced_count = total_questions - basic_count - intermediate_count
```

### Custom Styling
```python
# In app.py, modify the CSS
st.markdown("""
<style>
.custom-header {
    background: linear-gradient(90deg, #your-color1, #your-color2);
    /* Add your custom styles */
}
</style>
""", unsafe_allow_html=True)
```

## 📈 Performance Optimization

### Response Time Optimization
- **Caching**: Implement Streamlit caching for question generation
- **API Calls**: Batch API requests when possible
- **Question Bank**: Use local question bank as fallback

### Scalability Considerations
- **Database Integration**: Replace JSON files with SQL/NoSQL database
- **Load Balancing**: Use multiple OpenAI API keys for high traffic
- **Async Processing**: Implement async operations for better performance

## 🤝 Contributing

### Development Guidelines
1. Follow PEP 8 style guide
2. Add docstrings to all functions
3. Include type hints
4. Write comprehensive tests
5. Update documentation

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Code review and merge

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial release with core functionality
- Support for 9+ technology domains
- Streamlit-based user interface
- OpenAI GPT integration
- Data privacy compliance

### Planned Features
- Multi-language support
- Advanced analytics dashboard
- Integration with ATS systems
- Video/voice interview capabilities
- Machine learning-based candidate ranking

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 📞 Support

For questions, issues, or contributions:
- **Email**: careers@talentscout.com
- **GitHub Issues**: [Create an issue](https://github.com/tarunpatil01/PGAGI/issues)
- **Documentation**: This README file

## 🙏 Acknowledgments

- OpenAI for GPT API
- Streamlit team for the web framework
- Python community for excellent libraries
- Contributors and beta testers

---

**TalentScout Hiring Assistant** - Making technical recruitment more efficient and candidate-friendly through AI-powered conversations.
