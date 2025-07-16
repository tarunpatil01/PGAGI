"""
Test script for TalentScout Hiring Assistant
Run this script to test the core functionality
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    CandidateInfo, 
    TechnicalQuestionBank, 
    DataHandler, 
    validate_tech_stack,
    CandidateResponse
)

class TestCandidateInfo(unittest.TestCase):
    """Test CandidateInfo data class"""
    
    def test_candidate_info_initialization(self):
        """Test CandidateInfo initialization"""
        candidate = CandidateInfo()
        self.assertEqual(candidate.full_name, "")
        self.assertEqual(candidate.email, "")
        self.assertEqual(candidate.tech_stack, [])
    
    def test_candidate_info_with_data(self):
        """Test CandidateInfo with actual data"""
        candidate = CandidateInfo(
            full_name="John Doe",
            email="john@example.com",
            tech_stack=["Python", "React"]
        )
        self.assertEqual(candidate.full_name, "John Doe")
        self.assertEqual(candidate.email, "john@example.com")
        self.assertEqual(candidate.tech_stack, ["Python", "React"])

class TestTechnicalQuestionBank(unittest.TestCase):
    """Test TechnicalQuestionBank functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.question_bank = TechnicalQuestionBank()
    
    def test_get_python_questions(self):
        """Test getting Python questions"""
        questions = self.question_bank.get_questions_for_technology("python", 3)
        self.assertEqual(len(questions), 3)
        self.assertTrue(all(q.technology == "Python" for q in questions))
    
    def test_get_questions_for_unknown_technology(self):
        """Test getting questions for unknown technology"""
        questions = self.question_bank.get_questions_for_technology("unknown", 3)
        self.assertEqual(len(questions), 0)
    
    def test_get_questions_for_tech_stack(self):
        """Test getting questions for multiple technologies"""
        tech_stack = ["python", "javascript", "react"]
        questions = self.question_bank.get_questions_for_tech_stack(tech_stack, 6)
        self.assertLessEqual(len(questions), 6)
        self.assertGreater(len(questions), 0)

class TestDataHandler(unittest.TestCase):
    """Test DataHandler functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_handler = DataHandler("test_data")
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
    
    def test_data_directory_creation(self):
        """Test data directory creation"""
        self.assertTrue(os.path.exists("test_data"))
    
    def test_save_and_load_candidate_data(self):
        """Test saving and loading candidate data"""
        from datetime import datetime
        
        candidate_info = {
            "full_name": "Test User",
            "email": "test@example.com",
            "tech_stack": ["Python", "React"]
        }
        
        responses = [
            CandidateResponse(
                question="What is Python?",
                answer="A programming language",
                technology="Python",
                timestamp=datetime.now()
            )
        ]
        
        # Save data
        filepath = self.data_handler.save_candidate_data(candidate_info, responses)
        self.assertTrue(os.path.exists(filepath))
        
        # Load data
        loaded_data = self.data_handler.load_candidate_data(filepath)
        self.assertEqual(loaded_data["candidate_info"]["full_name"], "Test User")
        self.assertEqual(len(loaded_data["responses"]), 1)

class TestValidation(unittest.TestCase):
    """Test validation functions"""
    
    def test_validate_tech_stack_single(self):
        """Test tech stack validation with single technology"""
        result = validate_tech_stack("Python")
        self.assertEqual(result, ["Python"])
    
    def test_validate_tech_stack_multiple(self):
        """Test tech stack validation with multiple technologies"""
        result = validate_tech_stack("Python, JavaScript, React")
        self.assertEqual(len(result), 3)
        self.assertIn("Python", result)
        self.assertIn("JavaScript", result)
        self.assertIn("React", result)
    
    def test_validate_tech_stack_normalization(self):
        """Test tech stack normalization"""
        result = validate_tech_stack("js, py, react.js")
        self.assertIn("JavaScript", result)
        self.assertIn("Python", result)
        self.assertIn("React", result)
    
    def test_validate_tech_stack_empty(self):
        """Test tech stack validation with empty input"""
        result = validate_tech_stack("")
        self.assertEqual(result, [])

class TestChatbotCore(unittest.TestCase):
    """Test core chatbot functionality"""
    
    @patch('openai.ChatCompletion.create')
    def test_openai_response_mock(self, mock_openai):
        """Test OpenAI API response handling"""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello, welcome to TalentScout!"
        mock_openai.return_value = mock_response
        
        # Import and test the chatbot
        from app import TalentScoutChatbot
        
        chatbot = TalentScoutChatbot()
        response = chatbot.get_openai_response("Generate a greeting")
        
        self.assertEqual(response, "Hello, welcome to TalentScout!")
        mock_openai.assert_called_once()

class TestEmailValidation(unittest.TestCase):
    """Test email validation"""
    
    def test_valid_emails(self):
        """Test valid email addresses"""
        from app import TalentScoutChatbot
        
        chatbot = TalentScoutChatbot()
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "user.name123@example-site.com"
        ]
        
        for email in valid_emails:
            self.assertTrue(chatbot.validate_email(email), f"Email {email} should be valid")
    
    def test_invalid_emails(self):
        """Test invalid email addresses"""
        from app import TalentScoutChatbot
        
        chatbot = TalentScoutChatbot()
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user.example.com",
            "user@.com",
            ""
        ]
        
        for email in invalid_emails:
            self.assertFalse(chatbot.validate_email(email), f"Email {email} should be invalid")

class TestPhoneValidation(unittest.TestCase):
    """Test phone validation"""
    
    def test_valid_phones(self):
        """Test valid phone numbers"""
        from app import TalentScoutChatbot
        
        chatbot = TalentScoutChatbot()
        valid_phones = [
            "+1234567890",
            "123-456-7890",
            "(123) 456-7890",
            "1234567890",
            "+44 20 7946 0958"
        ]
        
        for phone in valid_phones:
            self.assertTrue(chatbot.validate_phone(phone), f"Phone {phone} should be valid")
    
    def test_invalid_phones(self):
        """Test invalid phone numbers"""
        from app import TalentScoutChatbot
        
        chatbot = TalentScoutChatbot()
        invalid_phones = [
            "123",
            "abcdefghij",
            "123-abc-7890",
            "",
            "12345",
            "123 456"
        ]
        
        for phone in invalid_phones:
            self.assertFalse(chatbot.validate_phone(phone), f"Phone {phone} should be invalid")

def run_tests():
    """Run all tests"""
    print("🧪 Running TalentScout Hiring Assistant Tests")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    
    # Add current test classes
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCandidateInfo))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTechnicalQuestionBank))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDataHandler))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestValidation))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEmailValidation))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPhoneValidation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
