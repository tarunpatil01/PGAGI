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
            # Use the technical question bank from utils
            try:
                from utils import TechnicalQuestionBank
                question_bank = TechnicalQuestionBank()
                
                # Extract tech stack from prompt
                tech_stack = []
                if "tech stack:" in prompt.lower():
                    tech_part = prompt.lower().split("tech stack:")[1].strip()
                    tech_stack = [tech.strip() for tech in tech_part.split(",")]
                
                if tech_stack:
                    questions = question_bank.get_questions_for_tech_stack(tech_stack, 3)
                    return [q.question for q in questions]
                else:
                    return [
                        "Can you describe your experience with the technologies you mentioned?",
                        "What's your most challenging project involving these technologies?",
                        "How do you stay updated with the latest developments in your field?"
                    ]
            except ImportError:
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

**Summary of your information:**
- **Name:** {self.candidate_info.full_name}
- **Email:** {self.candidate_info.email}
- **Phone:** {self.candidate_info.phone}
- **Experience:** {self.candidate_info.years_experience}
- **Desired Position:** {self.candidate_info.desired_position}
- **Location:** {self.candidate_info.current_location}
- **Tech Stack:** {', '.join(self.candidate_info.tech_stack)}

Your responses have been recorded and will be reviewed by our hiring team. You can expect to hear back from us within 2-3 business days.

If you have any questions or need to update your information, please contact us at careers@talentscout.com.

Thank you for your interest in opportunities with TalentScout! You can type 'goodbye' to end this conversation."""

    def handle_fallback(self, user_input: str) -> str:
        """Handle unexpected inputs"""
        system_message = """You are a professional hiring assistant chatbot. The user has provided 
        an input that doesn't fit the current conversation flow. Provide a helpful response that:
        
        1. Acknowledges their input politely
        2. Gently redirects them back to the screening process
        3. Maintains a professional and friendly tone
        4. Doesn't deviate from the hiring assistant purpose"""
        
        prompt = f"""The user said: "{user_input}"
        
        Current conversation state: {self.conversation_state}
        
        Provide a helpful response that redirects them back to the screening process."""
        
        return self.get_llm_response(prompt, system_message)

    def end_conversation(self) -> str:
        """End the conversation gracefully"""
        return f"""Thank you for your time, {self.candidate_info.full_name if self.candidate_info.full_name else 'candidate'}! 

If you didn't complete the screening process, you're welcome to start over anytime. 

For any questions or concerns, please contact us at careers@talentscout.com.

Have a great day and good luck with your job search!

*This conversation has ended. Refresh the page to start a new session.*"""

def main():
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        text-align: right;
    }
    
    .bot-message {
        background-color: #ffffff;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 2rem;
        border-left: 4px solid #667eea;
    }
    
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 TalentScout Hiring Assistant</h1>
        <p>Your AI-powered recruitment partner for technology placements</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = TalentScoutChatbot()
        st.session_state.messages = []
        # Add initial greeting
        initial_greeting = st.session_state.chatbot.generate_greeting()
        st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-info">
            <h3>📋 About This Session</h3>
            <p>This AI assistant will help you through our initial screening process.</p>
            
            <h4>📝 What We'll Collect:</h4>
            <ul>
                <li>Personal Information</li>
                <li>Professional Experience</li>
                <li>Technical Skills</li>
                <li>Career Preferences</li>
            </ul>
            
            <h4>⚡ Process:</h4>
            <ol>
                <li>Information Gathering</li>
                <li>Tech Stack Assessment</li>
                <li>Technical Questions</li>
                <li>Screening Complete</li>
            </ol>
            
            <h4>🔒 Privacy Note:</h4>
            <p>Your information is handled securely and in compliance with privacy standards.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current candidate info (if available)
        if st.session_state.chatbot.candidate_info.full_name:
            st.markdown("### 👤 Current Candidate")
            info = st.session_state.chatbot.candidate_info
            if info.full_name:
                st.write(f"**Name:** {info.full_name}")
            if info.email:
                st.write(f"**Email:** {info.email}")
            if info.years_experience:
                st.write(f"**Experience:** {info.years_experience}")
            if info.tech_stack:
                st.write(f"**Tech Stack:** {', '.join(info.tech_stack)}")
        
        # LLM Status
        st.markdown("### 🤖 AI Model Status")
        if LLM_AVAILABLE:
            try:
                # Initialize Phi3OllamaManager to check status
                is_cloud = os.getenv("DEPLOYMENT_MODE") == "cloud"
                config = LLMConfig(is_cloud=is_cloud)
                llm_manager = Phi3OllamaManager(config)
                
                if llm_manager.is_connected and llm_manager.model_available:
                    st.success("✅ Phi-3 with Ollama Connected")
                elif llm_manager.is_connected and not llm_manager.model_available:
                    st.info("🔄 Phi-3 Model Loading...")
                else:
                    st.warning("⚠️ Using Intelligent Fallback Responses")
            except Exception as e:
                st.warning(f"⚠️ Using Intelligent Fallback Responses ({str(e)})")
        else:
            st.warning("⚠️ Using Intelligent Fallback Responses")
        
        # Help section
        st.markdown("### ❓ Need Help?")
        st.markdown("""
        - **Stuck?** Try rephrasing your response
        - **Error?** Refresh the page to restart
        - **Questions?** Type 'goodbye' to end and contact us
        - **Technical Issues?** Check the sidebar for guidance
        """)
        
        # Setup Instructions
        with st.expander("🔧 Setup Instructions"):
            st.markdown("""
            **For better AI responses, install Ollama:**
            
            1. **Windows**: Download from [ollama.com](https://ollama.com/download)
            2. **Install Phi-3**: Run `ollama pull phi3:mini`
            3. **Start service**: Run `ollama serve`
            4. **Restart app**: Refresh this page
            
            **Alternative**: The app works with fallback responses if Ollama isn't available.
            """)
        
        # Reset button
        if st.button("🔄 Start New Session"):
            st.session_state.chatbot = TalentScoutChatbot()
            st.session_state.messages = []
            initial_greeting = st.session_state.chatbot.generate_greeting()
            st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Chat Interface")
        
        # Display chat messages
        chat_placeholder = st.empty()
        
        with chat_placeholder.container():
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="bot-message">
                        <strong>TalentScout Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # User input
        user_input = st.text_input(
            "Your response:",
            key="user_input",
            placeholder="Type your message here...",
            help="Type 'goodbye' or 'exit' to end the conversation"
        )
        
        col_send, col_clear = st.columns([1, 1])
        
        with col_send:
            if st.button("📤 Send", type="primary") and user_input:
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
    
    with col2:
        st.markdown("### 📊 Session Status")
        
        # Progress indicator
        state_map = {
            "greeting": 0,
            "collecting_info": 25,
            "tech_stack": 50,
            "technical_questions": 75,
            "completed": 100
        }
        
        progress = state_map.get(st.session_state.chatbot.conversation_state, 0)
        st.progress(progress / 100)
        st.write(f"Progress: {progress}%")
        
        # Current state
        state_labels = {
            "greeting": "👋 Greeting",
            "collecting_info": "📝 Collecting Info",
            "tech_stack": "⚡ Tech Stack",
            "technical_questions": "🤔 Technical Questions",
            "completed": "✅ Completed"
        }
        
        current_state = state_labels.get(st.session_state.chatbot.conversation_state, "Unknown")
        st.write(f"**Current Stage:** {current_state}")
        
        # Help section
        st.markdown("### ❓ Need Help?")
        st.markdown("""
        - **Stuck?** Try rephrasing your response
        - **Error?** Refresh the page to restart
        - **Questions?** Type 'goodbye' to end and contact us
        - **Technical Issues?** Check the sidebar for guidance
        """)

if __name__ == "__main__":
    main()
