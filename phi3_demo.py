#!/usr/bin/env python3
"""
Demo script for TalentScout Hiring Assistant with Phi-3
Tests the complete implementation including Ollama setup
"""

import os
import sys
import time
from local_llm import Phi3OllamaManager, LLMConfig
from utils import TechnicalQuestionBank, validate_email, validate_phone, get_random_question

def test_phi3_connection():
    """Test Phi-3 connection and basic functionality"""
    print("🔄 Testing Phi-3 connection...")
    
    # Initialize with local config
    config = LLMConfig(
        ollama_url="http://localhost:11434",
        model_name="phi3:mini",
        temperature=0.7,
        max_tokens=200,
        timeout=30,
        is_cloud=False
    )
    
    try:
        # Initialize manager
        manager = Phi3OllamaManager(config)
        
        # Check status
        print(f"✅ Connection Status: {'Connected' if manager.is_connected else 'Disconnected'}")
        print(f"✅ Model Available: {'Yes' if manager.model_available else 'No'}")
        print(f"✅ Fallback Mode: {'Yes' if manager.fallback_mode else 'No'}")
        
        # Test basic response
        print("\n🧪 Testing basic response...")
        response = manager.generate_response(
            "Hello, how are you?",
            "You are a friendly hiring assistant."
        )
        print(f"Response: {response}")
        
        return manager
        
    except Exception as e:
        print(f"❌ Error testing Phi-3: {str(e)}")
        return None

def test_hiring_conversation():
    """Test hiring conversation flow"""
    print("\n🎯 Testing hiring conversation flow...")
    
    config = LLMConfig()
    manager = Phi3OllamaManager(config)
    
    # Simulate a hiring conversation
    conversation_flow = [
        {
            "stage": "welcome",
            "prompt": "Hello",
            "system_message": "You are a professional hiring assistant. Welcome the candidate warmly."
        },
        {
            "stage": "basic_info",
            "prompt": "My name is John Smith",
            "system_message": "You are collecting basic information from the candidate."
        },
        {
            "stage": "basic_info", 
            "prompt": "john.smith@email.com",
            "system_message": "The candidate has provided their email. Ask for their phone number."
        },
        {
            "stage": "technical_questions",
            "prompt": "I have 5 years of experience in Python and React",
            "system_message": "Generate a relevant technical question based on their skills.",
            "candidate_info": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "skills": "Python, React",
                "experience": "5 years"
            }
        }
    ]
    
    for step in conversation_flow:
        print(f"\n--- {step['stage'].upper()} ---")
        print(f"User: {step['prompt']}")
        
        context = {
            "stage": step["stage"],
            "candidate_info": step.get("candidate_info", {})
        }
        
        response = manager.generate_response(
            step["prompt"],
            step["system_message"],
            context
        )
        
        print(f"Assistant: {response}")
        time.sleep(1)  # Simulate natural conversation timing

def test_technical_questions():
    """Test technical question generation"""
    print("\n📝 Testing technical question generation...")
    
    bank = TechnicalQuestionBank()
    
    # Test different tech stacks
    tech_stacks = [
        "python",
        "javascript", 
        "react",
        "java",
        "data_science",
        "devops",
        "general"
    ]
    
    for stack in tech_stacks:
        question = get_random_question(stack)
        print(f"✅ {stack.upper()}: {question}")

def test_validation_functions():
    """Test validation functions"""
    print("\n🔍 Testing validation functions...")
    
    # Test email validation
    emails = [
        "john.smith@email.com",
        "invalid-email",
        "user@domain.co.uk",
        "test@.com"
    ]
    
    for email in emails:
        is_valid = validate_email(email)
        print(f"Email '{email}': {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test phone validation
    phones = [
        "+1-555-123-4567",
        "555-123-4567",
        "15551234567",
        "invalid-phone"
    ]
    
    for phone in phones:
        is_valid = validate_phone(phone)
        print(f"Phone '{phone}': {'✅ Valid' if is_valid else '❌ Invalid'}")

def test_fallback_responses():
    """Test fallback response system"""
    print("\n🔄 Testing fallback response system...")
    
    # Force fallback mode
    config = LLMConfig(ollama_url="http://invalid:11434")  # Force connection failure
    manager = Phi3OllamaManager(config)
    
    test_prompts = [
        "Hello",
        "My name is John Smith",
        "john.smith@email.com",
        "I have 5 years of Python experience",
        "Thank you"
    ]
    
    for prompt in test_prompts:
        response = manager.generate_response(prompt)
        print(f"User: {prompt}")
        print(f"Assistant (Fallback): {response}")
        print()

def main():
    """Main demo function"""
    print("🎉 TalentScout Hiring Assistant - Phi-3 Demo")
    print("=" * 50)
    
    # Test 1: Phi-3 Connection
    manager = test_phi3_connection()
    
    # Test 2: Technical Questions
    test_technical_questions()
    
    # Test 3: Validation Functions
    test_validation_functions()
    
    # Test 4: Fallback Responses
    test_fallback_responses()
    
    # Test 5: Hiring Conversation (if Phi-3 is available)
    if manager and manager.is_connected:
        test_hiring_conversation()
    else:
        print("\n⚠️ Skipping hiring conversation test - Phi-3 not available")
    
    print("\n🎊 Demo completed!")
    print("\nTo run the full application:")
    print("streamlit run app.py")

if __name__ == "__main__":
    main()
