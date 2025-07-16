import streamlit as st
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local LLM manager
try:
    from local_llm import Phi3OllamaManager, LLMConfig
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ Local LLM not available. Using fallback responses.")

@dataclass
class CandidateInfo:
    """Data class to store candidate information"""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    years_experience: str = ""
    desired_position: str = ""
    current_location: str = ""
    tech_stack: List[str] = None
    
    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []

class TalentScoutChatbot:
    def __init__(self):
        self.conversation_state = "greeting"
        self.candidate_info = CandidateInfo()
        self.current_field = None
        self.technical_questions = []
        self.current_question_index = 0
        self.conversation_history = []
        
    def get_llm_response(self, prompt: str, system_message: str = None) -> str:
        """Get response from local LLM or fallback"""
        if LLM_AVAILABLE:
            try:
                # Initialize Phi3OllamaManager with cloud config if needed
                is_cloud = os.getenv("DEPLOYMENT_MODE") == "cloud"
                config = LLMConfig(is_cloud=is_cloud)
                llm_manager = Phi3OllamaManager(config)
                
                context = {
                    "stage": self.conversation_state,
                    "candidate_info": self.candidate_info.__dict__
                }
                
                return llm_manager.generate_response(prompt, system_message, context)
            except Exception as e:
                st.error(f"Error with LLM: {str(e)}")
                return self.get_fallback_response(prompt, system_message)
        else:
            return self.get_fallback_response(prompt, system_message)
    
    def get_fallback_response(self, prompt: str, system_message: str = None) -> str:
        """Fallback responses when LLM is not available"""
        
        if system_message and "greeting" in system_message.lower():
            return """Hello! Welcome to TalentScout, your AI-powered hiring assistant. 
            
I'm here to help you through our initial candidate screening process for technology positions. This will take about 10-15 minutes and will help our team understand your background and skills better.

To get started, could you please tell me your full name?"""
        
        elif system_message and "technical" in system_message.lower():
            return [
                "Can you describe your experience with the technologies you mentioned?",
                "What's your most challenging project involving these technologies?",
                "How do you stay updated with the latest developments in your field?"
            ]
        
        elif system_message and "fallback" in system_message.lower():
            return """I understand you'd like to share that information, but let's focus on the screening process for now. 
            
Could you please provide the information I'm currently asking for? This will help me assist you better with your application."""
        
        else:
            return """Thank you for your response. Let's continue with the screening process. 
            
Please provide the information I'm asking for, and I'll guide you through the next steps."""

    def generate_greeting(self) -> str:
        """Generate personalized greeting"""
        system_message = """You are a friendly and professional hiring assistant chatbot for TalentScout, 
        a recruitment agency specializing in technology placements. Your role is to conduct initial 
        candidate screening by gathering essential information and asking relevant technical questions.
        
        Generate a warm, professional greeting that:
        1. Welcomes the candidate
        2. Briefly explains your purpose
        3. Asks for their name to begin the process
        
        Keep it concise, friendly, and professional."""
        
        prompt = "Generate a greeting message for the hiring assistant chatbot."
        
        return self.get_llm_response(prompt, system_message)

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators and spaces
        cleaned = re.sub(r'[-\s\(\)]+', '', phone)
        # Check if it's a valid phone number (10-15 digits)
        pattern = r'^\+?[1-9]\d{9,14}$'
        return re.match(pattern, cleaned) is not None

    def generate_technical_questions(self, tech_stack: List[str]) -> List[str]:
        """Generate technical questions based on tech stack"""
        system_message = """You are an expert technical interviewer. Generate 3-5 relevant technical 
        questions for each technology in the candidate's tech stack. The questions should:
        
        1. Be appropriate for initial screening
        2. Test both theoretical knowledge and practical application
        3. Vary in difficulty from basic to intermediate
        4. Be specific to the technology mentioned
        5. Be answerable in a conversational format
        
        Return only the questions as a simple list, one per line."""
        
        tech_list = ", ".join(tech_stack)
        prompt = f"""Generate technical questions for a candidate with the following tech stack: {tech_list}
        
        Please provide 3-5 questions total, distributed across the technologies mentioned."""
        
        response = self.get_llm_response(prompt, system_message)
        
        # Handle case where response might be a list or None
        if isinstance(response, list):
            response = " ".join(response)
        elif response is None:
            response = ""
        
        # Parse the response to extract questions
        questions = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Remove numbering and clean up
            if line and ('?' in line or line.strip().endswith('?')):
                # Remove common prefixes like "1.", "Q1:", etc.
                line = re.sub(r'^[0-9]+\.?\s*', '', line)
                line = re.sub(r'^[Qq][0-9]*[:.]?\s*', '', line)
                line = re.sub(r'^[-•*]\s*', '', line)
                questions.append(line.strip())
        
        return questions[:5]  # Limit to 5 questions

    def process_user_input(self, user_input: str) -> str:
        """Process user input based on current conversation state"""
        user_input = user_input.strip()
        
        # Check for conversation ending keywords
        ending_keywords = ["goodbye", "bye", "exit", "quit", "end", "stop", "finish"]
        if any(keyword in user_input.lower() for keyword in ending_keywords):
            return self.end_conversation()
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        if self.conversation_state == "greeting":
            return self.handle_greeting(user_input)
        elif self.conversation_state == "collecting_info":
            return self.handle_info_collection(user_input)
        elif self.conversation_state == "tech_stack":
            return self.handle_tech_stack(user_input)
        elif self.conversation_state == "technical_questions":
            return self.handle_technical_questions(user_input)
        else:
            return self.handle_fallback(user_input)

    def handle_greeting(self, user_input: str) -> str:
        """Handle greeting and name collection"""
        # Extract name from user input
        self.candidate_info.full_name = user_input
        self.conversation_state = "collecting_info"
        self.current_field = "email"
        
        return f"Nice to meet you, {self.candidate_info.full_name}! Now I'll need to collect some basic information from you. Let's start with your email address."

    def handle_info_collection(self, user_input: str) -> str:
        """Handle information collection process"""
        if self.current_field == "email":
            if self.validate_email(user_input):
                self.candidate_info.email = user_input
                self.current_field = "phone"
                return "Thank you! Now, could you please provide your phone number?"
            else:
                return "Please provide a valid email address (e.g., john.doe@email.com)."
        
        elif self.current_field == "phone":
            if self.validate_phone(user_input):
                self.candidate_info.phone = user_input
                self.current_field = "years_experience"
                return "Great! How many years of professional experience do you have?"
            else:
                return "Please provide a valid phone number (e.g., +1234567890 or 123-456-7890)."
        
        elif self.current_field == "years_experience":
            self.candidate_info.years_experience = user_input
            self.current_field = "desired_position"
            return "What position(s) are you interested in applying for?"
        
        elif self.current_field == "desired_position":
            self.candidate_info.desired_position = user_input
            self.current_field = "current_location"
            return "Where are you currently located?"
        
        elif self.current_field == "current_location":
            self.candidate_info.current_location = user_input
            self.conversation_state = "tech_stack"
            return """Perfect! Now let's talk about your technical skills. Please list your tech stack - this includes programming languages, frameworks, databases, and tools you're proficient in. 

For example: "Python, Django, PostgreSQL, React, AWS, Docker"

Please provide your tech stack:"""

    def handle_tech_stack(self, user_input: str) -> str:
        """Handle tech stack collection and question generation"""
        # Parse tech stack from user input
        tech_items = [item.strip() for item in re.split(r'[,;]', user_input) if item.strip()]
        self.candidate_info.tech_stack = tech_items
        
        # Generate technical questions
        self.technical_questions = self.generate_technical_questions(tech_items)
        
        if self.technical_questions:
            self.conversation_state = "technical_questions"
            self.current_question_index = 0
            
            tech_summary = ", ".join(tech_items)
            return f"""Excellent! I can see you have experience with: {tech_summary}

Now I'll ask you a few technical questions to better understand your proficiency. Don't worry - these are just for initial screening purposes.

**Question 1 of {len(self.technical_questions)}:**
{self.technical_questions[0]}"""
        else:
            return "I'm having trouble generating questions for your tech stack. Could you please rephrase your technologies?"

    def handle_technical_questions(self, user_input: str) -> str:
        """Handle technical question responses"""
        # Store the answer (in a real application, you might want to save this)
        self.conversation_history.append({
            "question": self.technical_questions[self.current_question_index],
            "answer": user_input
        })
        
        self.current_question_index += 1
        
        if self.current_question_index < len(self.technical_questions):
            return f"""Thank you for your response!

**Question {self.current_question_index + 1} of {len(self.technical_questions)}:**
{self.technical_questions[self.current_question_index]}"""
        else:
            return self.complete_screening()

    def complete_screening(self) -> str:
        """Complete the screening process"""
        self.conversation_state = "completed"
        
        return f"""Thank you for completing the initial screening, {self.candidate_info.full_name}!

I've gathered all the necessary information about your background and technical skills. Here's a summary:

**Personal Information:**
- Name: {self.candidate_info.full_name}
- Email: {self.candidate_info.email}
- Phone: {self.candidate_info.phone}
- Experience: {self.candidate_info.years_experience}
- Desired Position: {self.candidate_info.desired_position}
- Location: {self.candidate_info.current_location}

**Technical Skills:**
{', '.join(self.candidate_info.tech_stack)}

**Next Steps:**
1. Your profile will be reviewed by our recruitment team
2. We'll match you with suitable opportunities
3. You'll hear back from us within 2-3 business days

Thank you for your time today! Is there anything else you'd like to add or any questions you have about the process?"""

    def generate_summary(self) -> str:
        """Generate a comprehensive summary of the screening"""
        return f"""
## 📋 Screening Summary for {self.candidate_info.full_name}

### 👤 Personal Information
- **Name:** {self.candidate_info.full_name}
- **Email:** {self.candidate_info.email}
- **Phone:** {self.candidate_info.phone}
- **Experience:** {self.candidate_info.years_experience}
- **Desired Position:** {self.candidate_info.desired_position}
- **Location:** {self.candidate_info.current_location}

### 💻 Technical Skills
{', '.join(self.candidate_info.tech_stack)}

### 💬 Technical Q&A
{self.current_question_index} questions completed

### 📈 Assessment Status
- **Screening Stage:** {self.conversation_state.title()}
- **Completion:** {len(self.conversation_history)} interactions
- **Status:** {'Complete' if self.conversation_state == 'completed' else 'In Progress'}

### 🎯 Next Steps
1. Profile review by recruitment team
2. Matching with suitable opportunities
3. Follow-up within 2-3 business days
"""

    def handle_fallback(self, user_input: str) -> str:
        """Handle fallback responses for unknown states"""
        return "I'm not sure how to help with that. Could you please clarify what you'd like to do?"

    def end_conversation(self) -> str:
        """End the conversation gracefully"""
        return f"""Thank you for your time, {self.candidate_info.full_name or 'candidate'}! 

If you'd like to continue the screening process later, please feel free to restart the session. 

Have a great day! 🌟"""

def main():
    """Enhanced main application with modern UI/UX"""
    st.set_page_config(
        page_title="TalentScout AI Hiring Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS styling with proper colors and animations
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Loading animation */
    @keyframes pageLoad {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        0% { opacity: 0; transform: translateX(-50px); }
        100% { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        0% { opacity: 0; transform: translateX(50px); }
        100% { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Main container with loading animation */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        animation: pageLoad 0.8s ease-out;
    }
    
    .main {
        font-family: 'Inter', sans-serif;
        background: transparent;
        min-height: 100vh;
        animation: pageLoad 0.8s ease-out;
    }
    
    /* Enhanced header with animation */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.2);
        animation: fadeInUp 1s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmer 2s infinite;
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        animation: pulse 2s infinite;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.4rem;
        font-weight: 300;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* Enhanced chat container with animation */
    .chat-container {
        background: #ffffff;
        border-radius: 25px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        margin-bottom: 2rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        animation: slideInLeft 0.8s ease-out 0.3s both;
        position: relative;
    }
    
    .chat-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        background-size: 200% 100%;
        animation: shimmer 3s infinite;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.8rem;
        text-align: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .chat-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    .chat-header h3 {
        color: #ffffff;
        margin: 0;
        font-weight: 600;
        font-size: 1.6rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* Enhanced chat messages area */
    .chat-messages {
        max-height: 650px;
        overflow-y: auto;
        padding: 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        position: relative;
    }
    
    .chat-messages::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
        pointer-events: none;
    }
    
    /* Enhanced message styling */
    .message {
        margin-bottom: 1.8rem;
        padding: 1.5rem;
        border-radius: 20px;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.5s ease-out;
        position: relative;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .message:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        margin-left: auto;
        border-bottom-right-radius: 8px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .user-message strong {
        color: #ffffff;
        font-weight: 600;
    }
    
    .bot-message {
        background: #ffffff;
        color: #2d3748;
        margin-right: auto;
        border: 2px solid #e2e8f0;
        border-bottom-left-radius: 8px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .bot-message strong {
        color: #4a5568;
        font-weight: 600;
    }
    
    /* Enhanced sidebar with animations */
    .sidebar-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.8rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.3);
        animation: slideInRight 0.8s ease-out 0.5s both;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .sidebar-card:hover::before {
        transform: scaleX(1);
    }
    
    .sidebar-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .sidebar-card h3 {
        color: #2d3748;
        margin-bottom: 1.2rem;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    .sidebar-card p {
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    /* Enhanced progress indicator */
    .progress-indicator {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2.5rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 2rem;
        color: #2d3748;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.8s ease-out 0.7s both;
        position: relative;
        overflow: hidden;
    }
    
    .progress-indicator::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 3s infinite;
    }
    
    .progress-indicator h3 {
        margin-bottom: 1.5rem;
        font-weight: 600;
        color: #2d3748;
    }
    
    .progress-percentage {
        font-size: 3rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.8rem;
        animation: pulse 2s infinite;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced status badge */
    .status-badge {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #ffffff;
        padding: 1rem 2rem;
        border-radius: 30px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        animation: slideInRight 0.8s ease-out 0.9s both;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .status-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Enhanced info cards */
    .info-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.2rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.5s ease-out;
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
    }
    
    .info-card strong {
        color: #2d3748;
        font-weight: 600;
    }
    
    /* Enhanced candidate profile */
    .candidate-profile {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        color: #2d3748;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.8s ease-out 1.1s both;
        position: relative;
        overflow: hidden;
    }
    
    .candidate-profile::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 3s infinite;
    }
    
    .candidate-profile h3 {
        color: #2d3748;
        margin-bottom: 1.5rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced input section */
    .input-section {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 0 0 25px 25px;
        border-top: 2px solid rgba(102, 126, 234, 0.1);
        animation: fadeInUp 0.8s ease-out 1.3s both;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border: none;
        border-radius: 30px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced text inputs */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 1.2rem 2rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        background: #ffffff;
        color: #2d3748;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
        background: #ffffff;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0;
    }
    
    /* Enhanced feature cards */
    .feature-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .feature-card h4 {
        color: #667eea;
        margin-bottom: 1rem;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .feature-card p {
        color: #4a5568;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Enhanced help section */
    .help-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 25px;
        margin-top: 2rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.8s ease-out 1.5s both;
        position: relative;
        overflow: hidden;
    }
    
    .help-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 4s infinite;
    }
    
    .help-section h4 {
        color: #2d3748;
        margin-bottom: 1.5rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .help-section ul {
        list-style: none;
        padding: 0;
    }
    
    .help-section li {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem 1.5rem;
        margin-bottom: 0.8rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        color: #2d3748;
    }
    
    .help-section li:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .help-section li strong {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Enhanced footer */
    .footer {
        text-align: center;
        padding: 2.5rem;
        color: #4a5568;
        font-size: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        margin-top: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.8s ease-out 1.7s both;
        backdrop-filter: blur(10px);
    }
    
    .footer p {
        margin: 0.5rem 0;
    }
    
    .footer strong {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Loading skeleton */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
        border-radius: 10px;
        height: 20px;
        margin-bottom: 10px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.2rem;
        }
        
        .message {
            max-width: 95%;
            padding: 1rem;
        }
        
        .chat-messages {
            max-height: 400px;
            padding: 1rem;
        }
        
        .sidebar-card {
            padding: 1.5rem;
        }
        
        .progress-indicator {
            padding: 1.5rem;
        }
        
        .input-section {
            padding: 1.5rem;
        }
        
        .stButton > button {
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
        }
    }
    
    /* Custom scrollbar */
    .chat-messages::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Accessibility improvements */
    .stButton > button:focus,
    .stTextInput > div > div > input:focus {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .bot-message {
            background: #2d3748;
            color: #e2e8f0;
            border-color: #4a5568;
        }
        
        .bot-message strong {
            color: #cbd5e0;
        }
        
        .sidebar-card {
            background: #2d3748;
            border-color: #4a5568;
        }
        
        .sidebar-card h3 {
            color: #e2e8f0;
        }
        
        .sidebar-card p {
            color: #cbd5e0;
        }
        
        .feature-card {
            background: #2d3748;
            border-color: #4a5568;
        }
        
        .feature-card h4 {
            color: #81c784;
        }
        
        .feature-card p {
            color: #cbd5e0;
        }
        
        .info-card {
            background: #2d3748;
            color: #e2e8f0;
        }
        
        .info-card strong {
            color: #cbd5e0;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add lazy loading with progress bar
    if 'app_loaded' not in st.session_state:
        st.session_state.app_loaded = False
    
    if not st.session_state.app_loaded:
        # Loading screen
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
            <div style="text-align: center; animation: fadeInUp 1s ease-out;">
                <h1 style="color: #667eea; font-size: 3rem; margin-bottom: 1rem; animation: pulse 2s infinite;">
                    🤖 TalentScout AI
                </h1>
                <p style="color: #4a5568; font-size: 1.2rem; margin-bottom: 2rem;">
                    Loading your intelligent hiring assistant...
                </p>
                <div style="width: 300px; height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); width: 100%; animation: shimmer 2s ease-in-out;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate loading time
        import time
        time.sleep(1)
        st.session_state.app_loaded = True
        st.rerun()
    
    # Enhanced Header with staggered animation
    st.markdown("""
    <div class="main-header">
        <h1>🤖 TalentScout AI Hiring Assistant</h1>
        <p>Your intelligent recruitment partner powered by advanced AI technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = TalentScoutChatbot()
        st.session_state.messages = []
        # Add initial greeting
        initial_greeting = st.session_state.chatbot.generate_greeting()
        st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-card">
            <h3>🎯 About This Session</h3>
            <p>Our AI assistant will guide you through a comprehensive screening process designed to understand your skills and career goals.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Progress Indicator
        state_map = {
            "greeting": 0,
            "collecting_info": 25,
            "tech_stack": 50,
            "technical_questions": 75,
            "completed": 100
        }
        
        progress = state_map.get(st.session_state.chatbot.conversation_state, 0)
        
        st.markdown(f"""
        <div class="progress-indicator">
            <h3>📊 Session Progress</h3>
            <div class="progress-percentage">{progress}%</div>
            <div style="margin-top: 0.5rem;">Complete</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(progress / 100)
        
        # Enhanced Current State Display
        state_labels = {
            "greeting": "👋 Initial Greeting",
            "collecting_info": "📝 Information Collection",
            "tech_stack": "⚡ Technical Skills Assessment",
            "technical_questions": "🤔 Technical Interview",
            "completed": "✅ Screening Complete"
        }
        
        current_state = state_labels.get(st.session_state.chatbot.conversation_state, "Unknown")
        st.markdown(f"""
        <div class="status-badge">
            {current_state}
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Candidate Profile Display
        if st.session_state.chatbot.candidate_info.full_name:
            st.markdown("""
            <div class="candidate-profile">
                <h3>👤 Candidate Profile</h3>
            </div>
            """, unsafe_allow_html=True)
            
            info = st.session_state.chatbot.candidate_info
            
            profile_items = [
                ("Name", info.full_name),
                ("Email", info.email),
                ("Phone", info.phone),
                ("Experience", info.years_experience),
                ("Position", info.desired_position),
                ("Location", info.current_location),
                ("Tech Stack", ', '.join(info.tech_stack) if info.tech_stack else "")
            ]
            
            for label, value in profile_items:
                if value:
                    st.markdown(f"""
                    <div class="info-card">
                        <strong>{label}:</strong> {value}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Enhanced AI Model Status
        st.markdown("""
        <div class="sidebar-card">
            <h3>🤖 AI Model Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if LLM_AVAILABLE:
            try:
                # Initialize Phi3OllamaManager to check status
                is_cloud = os.getenv("DEPLOYMENT_MODE") == "cloud"
                config = LLMConfig(is_cloud=is_cloud)
                llm_manager = Phi3OllamaManager(config)
                
                if llm_manager.is_connected and llm_manager.model_available:
                    st.success("✅ Phi-3 with Ollama Connected")
                    st.info("🚀 Using advanced AI responses")
                elif llm_manager.is_connected and not llm_manager.model_available:
                    st.info("🔄 Phi-3 Model Loading...")
                    st.warning("⏳ Please wait for model to initialize")
                else:
                    st.warning("⚠️ Ollama service not available")
                    st.info("🔧 Check setup instructions below")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")
                st.info("🔧 Check setup instructions below")
        else:
            st.error("❌ LLM Module Not Available")
            st.info("🔧 Check setup instructions below")
        
        # Enhanced Help Section
        st.markdown("""
        <div class="help-section">
            <h4>❓ Need Help?</h4>
            <ul>
                <li><strong>Stuck?</strong> Try rephrasing your response</li>
                <li><strong>Error?</strong> Use the restart button below</li>
                <li><strong>Questions?</strong> Type 'goodbye' to end session</li>
                <li><strong>Technical Issues?</strong> Check model status above</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Setup Instructions
        with st.expander("🔧 Setup Instructions", expanded=False):
            st.markdown("""
            <div class="feature-card">
                <h4>🚀 For Optimal Performance:</h4>
                <p><strong>1. Install Ollama:</strong><br>
                Download from <a href="https://ollama.com/download" target="_blank">ollama.com</a></p>
                
                <p><strong>2. Install Phi-3 Model:</strong><br>
                Run: <code>ollama pull phi3:mini</code></p>
                
                <p><strong>3. Start Ollama Service:</strong><br>
                Run: <code>ollama serve</code></p>
                
                <p><strong>4. Restart Application:</strong><br>
                Refresh this page to reconnect</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Reset Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Start New Session", type="primary"):
            st.session_state.chatbot = TalentScoutChatbot()
            st.session_state.messages = []
            initial_greeting = st.session_state.chatbot.generate_greeting()
            st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
            st.rerun()
    
    # Enhanced Main Chat Interface
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            <h3>💬 AI Conversation</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Enhanced Chat Messages Container
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        # Display chat messages with enhanced styling
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message user-message">
                    <strong>You:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message bot-message">
                    <strong>🤖 TalentScout Assistant:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Input Section
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # User input with better styling
        user_input = st.text_input(
            "Your response:",
            key="user_input",
            placeholder="Type your message here... (or 'goodbye' to end)",
            help="Press Enter or click Send to submit your response"
        )
        
        # Enhanced Button Layout
        col_send, col_clear, col_help = st.columns([1, 1, 1])
        
        with col_send:
            if st.button("📤 Send Response", type="primary") and user_input:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Get bot response
                bot_response = st.session_state.chatbot.process_user_input(user_input)
                
                # Add bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Clear input and rerun
                st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.session_state.chatbot = TalentScoutChatbot()
                initial_greeting = st.session_state.chatbot.generate_greeting()
                st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
                st.rerun()
        
        with col_help:
            if st.button("❓ Get Help"):
                help_message = """
                **Available Commands:**
                - Type your responses naturally
                - Use 'goodbye' or 'exit' to end the session
                - Click 'Clear Chat' to start over
                - Check the sidebar for session progress
                
                **Tips:**
                - Be specific with your technical skills
                - Provide complete answers to questions
                - Ask for clarification if needed
                """
                st.session_state.messages.append({"role": "assistant", "content": help_message})
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Enhanced Status Panel
        st.markdown(f"""
        <div class="feature-card">
            <h4>📈 Session Analytics</h4>
            <p><strong>Messages:</strong> {len(st.session_state.messages)}</p>
            <p><strong>Stage:</strong> {current_state}</p>
            <p><strong>Completion:</strong> {progress}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Quick Actions
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📋 View Summary", key="summary"):
            if st.session_state.chatbot.candidate_info.full_name:
                summary = st.session_state.chatbot.generate_summary()
                st.session_state.messages.append({"role": "assistant", "content": summary})
                st.rerun()
            else:
                st.warning("Complete the screening first!")
        
        if st.button("💾 Save Session", key="save"):
            st.success("Session saved! (Feature coming soon)")
        
        if st.button("📧 Email Summary", key="email"):
            st.info("Email feature coming soon!")
    
    # Enhanced Footer
    st.markdown("""
    <div class="footer">
        <p>Powered by <strong>Phi-3 AI</strong> and <strong>Ollama</strong> • Built with ❤️ by TalentScout</p>
        <p>🔒 Your data is handled securely and in compliance with privacy standards</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
