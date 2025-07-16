"""
Demo script for TalentScout Hiring Assistant
This script demonstrates the core functionality without requiring Streamlit
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import TechnicalQuestionBank, validate_tech_stack, CandidateResponse
    from app import TalentScoutChatbot, CandidateInfo
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def simulate_conversation():
    """Simulate a complete conversation flow"""
    print("\n🤖 TalentScout Hiring Assistant Demo")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = TalentScoutChatbot()
    
    # Simulate conversation steps
    print("\n1. 👋 Greeting Phase")
    print("Bot: Hello! Welcome to TalentScout. I'm here to help with your initial screening.")
    print("User: Hi, I'm John Smith")
    
    # Process name
    chatbot.candidate_info.full_name = "John Smith"
    chatbot.conversation_state = "collecting_info"
    chatbot.current_field = "email"
    
    print("\n2. 📧 Information Collection")
    print("Bot: Nice to meet you, John! Now I'll need to collect some basic information.")
    
    # Simulate email collection
    test_email = "john.smith@email.com"
    if chatbot.validate_email(test_email):
        chatbot.candidate_info.email = test_email
        print(f"User: {test_email}")
        print("Bot: Great! Now, could you please provide your phone number?")
    
    # Simulate phone collection
    test_phone = "+1234567890"
    if chatbot.validate_phone(test_phone):
        chatbot.candidate_info.phone = test_phone
        print(f"User: {test_phone}")
        print("Bot: Perfect! How many years of professional experience do you have?")
    
    # Simulate other info
    chatbot.candidate_info.years_experience = "5 years"
    chatbot.candidate_info.desired_position = "Full Stack Developer"
    chatbot.candidate_info.current_location = "New York, NY"
    
    print("User: 5 years")
    print("Bot: What position are you interested in?")
    print("User: Full Stack Developer")
    print("Bot: Where are you currently located?")
    print("User: New York, NY")
    
    print("\n3. ⚡ Tech Stack Assessment")
    print("Bot: Now let's talk about your technical skills.")
    
    # Simulate tech stack input
    tech_input = "Python, JavaScript, React, Node.js, PostgreSQL, AWS"
    tech_stack = validate_tech_stack(tech_input)
    chatbot.candidate_info.tech_stack = tech_stack
    
    print(f"User: {tech_input}")
    print(f"Bot: Excellent! I can see you have experience with: {', '.join(tech_stack)}")
    
    print("\n4. 🤔 Technical Questions")
    question_bank = TechnicalQuestionBank()
    questions = question_bank.get_questions_for_tech_stack(tech_stack, 3)
    
    for i, question in enumerate(questions, 1):
        print(f"\nBot: Question {i}: {question.question}")
        print(f"User: [Simulated answer for {question.technology}]")
    
    print("\n5. ✅ Completion")
    print("Bot: Thank you for completing the screening! Here's your information:")
    print(f"   Name: {chatbot.candidate_info.full_name}")
    print(f"   Email: {chatbot.candidate_info.email}")
    print(f"   Phone: {chatbot.candidate_info.phone}")
    print(f"   Experience: {chatbot.candidate_info.years_experience}")
    print(f"   Position: {chatbot.candidate_info.desired_position}")
    print(f"   Location: {chatbot.candidate_info.current_location}")
    print(f"   Tech Stack: {', '.join(chatbot.candidate_info.tech_stack)}")
    
    print("\nBot: You can expect to hear back from us within 2-3 business days.")
    
    return chatbot

def test_technical_questions():
    """Test the technical question generation"""
    print("\n🧪 Testing Technical Question Generation")
    print("=" * 50)
    
    question_bank = TechnicalQuestionBank()
    
    # Test different technologies
    test_technologies = ["python", "javascript", "react", "java", "sql", "aws"]
    
    for tech in test_technologies:
        print(f"\n{tech.upper()} Questions:")
        questions = question_bank.get_questions_for_technology(tech, 2)
        if questions:
            for i, q in enumerate(questions, 1):
                print(f"  {i}. [{q.difficulty}] {q.question}")
        else:
            print(f"  No questions found for {tech}")

def test_validation():
    """Test validation functions"""
    print("\n🔍 Testing Validation Functions")
    print("=" * 50)
    
    chatbot = TalentScoutChatbot()
    
    # Test email validation
    print("\nEmail Validation:")
    test_emails = [
        "valid@example.com",
        "invalid-email",
        "user@domain.co.uk",
        "not-an-email"
    ]
    
    for email in test_emails:
        result = chatbot.validate_email(email)
        status = "✅ Valid" if result else "❌ Invalid"
        print(f"  {email}: {status}")
    
    # Test phone validation
    print("\nPhone Validation:")
    test_phones = [
        "+1234567890",
        "123-456-7890",
        "(123) 456-7890",
        "invalid-phone",
        "123"
    ]
    
    for phone in test_phones:
        result = chatbot.validate_phone(phone)
        status = "✅ Valid" if result else "❌ Invalid"
        print(f"  {phone}: {status}")
    
    # Test tech stack validation
    print("\nTech Stack Validation:")
    test_inputs = [
        "Python, JavaScript, React",
        "python; java; sql",
        "React.js and Node.js",
        "js, py, aws",
        ""
    ]
    
    for input_str in test_inputs:
        result = validate_tech_stack(input_str)
        print(f"  Input: '{input_str}'")
        print(f"  Output: {result}")

def main():
    """Main demo function"""
    print("🚀 TalentScout Hiring Assistant - Demo Mode")
    print("=" * 60)
    
    try:
        # Run demonstration
        print("\n📋 Running Complete Conversation Demo...")
        chatbot = simulate_conversation()
        
        print("\n" + "=" * 60)
        print("🧪 Running Technical Tests...")
        test_technical_questions()
        
        print("\n" + "=" * 60)
        test_validation()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("\nTo run the full application:")
        print("1. Set up your OpenAI API key in .env file")
        print("2. Run: streamlit run app.py")
        print("3. Open http://localhost:8501 in your browser")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
