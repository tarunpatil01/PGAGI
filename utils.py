import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class TechnicalQuestion:
    """Data class for technical questions"""
    technology: str
    question: str
    difficulty: str
    category: str = "general"

@dataclass
class CandidateResponse:
    """Data class for candidate responses"""
    question: str
    answer: str
    technology: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "technology": self.technology,
            "timestamp": self.timestamp.isoformat()
        }

class TechnicalQuestionBank:
    """Repository of technical questions by technology"""
    
    def __init__(self):
        self.questions = {
            "python": [
                TechnicalQuestion("Python", "What is the difference between lists and tuples in Python?", "basic"),
                TechnicalQuestion("Python", "Explain the concept of decorators in Python with an example.", "intermediate"),
                TechnicalQuestion("Python", "What is the Global Interpreter Lock (GIL) in Python?", "advanced"),
                TechnicalQuestion("Python", "How do you handle exceptions in Python?", "basic"),
                TechnicalQuestion("Python", "What are Python generators and when would you use them?", "intermediate"),
            ],
            "javascript": [
                TechnicalQuestion("JavaScript", "What is the difference between 'let', 'const', and 'var'?", "basic"),
                TechnicalQuestion("JavaScript", "Explain closures in JavaScript with an example.", "intermediate"),
                TechnicalQuestion("JavaScript", "What is the event loop in JavaScript?", "advanced"),
                TechnicalQuestion("JavaScript", "How do you handle asynchronous operations in JavaScript?", "intermediate"),
                TechnicalQuestion("JavaScript", "What is the difference between '==' and '===' in JavaScript?", "basic"),
            ],
            "react": [
                TechnicalQuestion("React", "What are React hooks and why are they useful?", "intermediate"),
                TechnicalQuestion("React", "Explain the difference between functional and class components.", "basic"),
                TechnicalQuestion("React", "What is the virtual DOM and how does it work?", "intermediate"),
                TechnicalQuestion("React", "How do you manage state in a React application?", "basic"),
                TechnicalQuestion("React", "What are React lifecycle methods?", "intermediate"),
            ],
            "java": [
                TechnicalQuestion("Java", "What is the difference between abstract classes and interfaces?", "intermediate"),
                TechnicalQuestion("Java", "Explain the concept of polymorphism in Java.", "basic"),
                TechnicalQuestion("Java", "What is the Java Memory Model?", "advanced"),
                TechnicalQuestion("Java", "How does garbage collection work in Java?", "intermediate"),
                TechnicalQuestion("Java", "What are the main principles of Object-Oriented Programming?", "basic"),
            ],
            "sql": [
                TechnicalQuestion("SQL", "What is the difference between INNER JOIN and LEFT JOIN?", "basic"),
                TechnicalQuestion("SQL", "How do you optimize a slow-running SQL query?", "intermediate"),
                TechnicalQuestion("SQL", "What are database indexes and when should you use them?", "intermediate"),
                TechnicalQuestion("SQL", "Explain the ACID properties of database transactions.", "advanced"),
                TechnicalQuestion("SQL", "What is normalization in database design?", "intermediate"),
            ],
            "aws": [
                TechnicalQuestion("AWS", "What is the difference between EC2 and Lambda?", "basic"),
                TechnicalQuestion("AWS", "How do you secure data in AWS S3?", "intermediate"),
                TechnicalQuestion("AWS", "What is auto-scaling in AWS and how does it work?", "intermediate"),
                TechnicalQuestion("AWS", "Explain the concept of Infrastructure as Code.", "advanced"),
                TechnicalQuestion("AWS", "What are the main AWS storage services?", "basic"),
            ],
            "docker": [
                TechnicalQuestion("Docker", "What is the difference between Docker images and containers?", "basic"),
                TechnicalQuestion("Docker", "How do you optimize Docker images for production?", "intermediate"),
                TechnicalQuestion("Docker", "What is Docker Compose and when would you use it?", "intermediate"),
                TechnicalQuestion("Docker", "How do you handle persistent data in Docker containers?", "intermediate"),
                TechnicalQuestion("Docker", "What are Docker volumes and bind mounts?", "basic"),
            ],
            "kubernetes": [
                TechnicalQuestion("Kubernetes", "What is the difference between Pods and Services in Kubernetes?", "basic"),
                TechnicalQuestion("Kubernetes", "How do you manage configuration in Kubernetes?", "intermediate"),
                TechnicalQuestion("Kubernetes", "What are Kubernetes operators?", "advanced"),
                TechnicalQuestion("Kubernetes", "How does service discovery work in Kubernetes?", "intermediate"),
                TechnicalQuestion("Kubernetes", "What is a Kubernetes deployment?", "basic"),
            ],
            "git": [
                TechnicalQuestion("Git", "What is the difference between 'git merge' and 'git rebase'?", "intermediate"),
                TechnicalQuestion("Git", "How do you resolve merge conflicts in Git?", "basic"),
                TechnicalQuestion("Git", "What is Git branching strategy?", "intermediate"),
                TechnicalQuestion("Git", "How do you undo changes in Git?", "basic"),
                TechnicalQuestion("Git", "What is the difference between 'git pull' and 'git fetch'?", "basic"),
            ]
        }
    
    def get_questions_for_technology(self, technology: str, count: int = 3) -> List[TechnicalQuestion]:
        """Get random questions for a specific technology"""
        tech_key = technology.lower()
        if tech_key in self.questions:
            import random
            available_questions = self.questions[tech_key]
            return random.sample(available_questions, min(count, len(available_questions)))
        return []
    
    def get_questions_for_tech_stack(self, tech_stack: List[str], total_questions: int = 5) -> List[TechnicalQuestion]:
        """Get distributed questions across the tech stack"""
        questions = []
        questions_per_tech = max(1, total_questions // len(tech_stack))
        
        for tech in tech_stack:
            tech_questions = self.get_questions_for_technology(tech, questions_per_tech)
            questions.extend(tech_questions)
        
        # If we have fewer questions than requested, try to fill from any technology
        if len(questions) < total_questions:
            remaining = total_questions - len(questions)
            for tech in tech_stack:
                if remaining <= 0:
                    break
                additional = self.get_questions_for_technology(tech, remaining)
                for q in additional:
                    if q not in questions:
                        questions.append(q)
                        remaining -= 1
        
        return questions[:total_questions]

class DataHandler:
    """Handle data storage and retrieval"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_candidate_data(self, candidate_info: dict, responses: List[CandidateResponse]):
        """Save candidate data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"candidate_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        data = {
            "candidate_info": candidate_info,
            "responses": [response.to_dict() for response in responses],
            "timestamp": timestamp,
            "session_id": f"session_{timestamp}"
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def load_candidate_data(self, filepath: str) -> dict:
        """Load candidate data from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def get_all_candidate_files(self) -> List[str]:
        """Get all candidate data files"""
        files = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith("candidate_") and filename.endswith(".json"):
                files.append(os.path.join(self.data_dir, filename))
        return sorted(files)

class PromptTemplates:
    """Collection of prompt templates for different scenarios"""
    
    GREETING_PROMPT = """You are a friendly and professional hiring assistant chatbot for TalentScout, 
    a recruitment agency specializing in technology placements. Your role is to conduct initial 
    candidate screening by gathering essential information and asking relevant technical questions.
    
    Generate a warm, professional greeting that:
    1. Welcomes the candidate
    2. Briefly explains your purpose (initial screening for tech positions)
    3. Asks for their name to begin the process
    4. Mentions that the process will take about 10-15 minutes
    
    Keep it concise, friendly, and professional. Use a conversational tone."""
    
    TECH_QUESTION_GENERATION = """You are an expert technical interviewer for a recruitment agency. 
    Generate {count} relevant technical questions for the following technologies: {tech_stack}
    
    Requirements:
    1. Questions should be appropriate for initial screening (not deep technical interviews)
    2. Mix of theoretical knowledge and practical application
    3. Vary difficulty from basic to intermediate
    4. Be specific to each technology
    5. Be answerable in a conversational format (not requiring code implementation)
    
    Format each question clearly and make them engaging. Focus on understanding the candidate's
    practical experience and problem-solving approach."""
    
    FALLBACK_RESPONSE = """You are a professional hiring assistant chatbot. The candidate has provided 
    an input that doesn't fit the current conversation flow. 
    
    Current context: {context}
    User input: {user_input}
    
    Provide a helpful response that:
    1. Acknowledges their input politely
    2. Gently redirects them back to the screening process
    3. Maintains a professional and friendly tone
    4. Doesn't deviate from the hiring assistant purpose
    5. Provides clear guidance on what they should do next
    
    Be helpful but stay focused on the recruitment process."""
    
    QUESTION_EVALUATION = """You are an expert technical interviewer evaluating a candidate's response.
    
    Question: {question}
    Technology: {technology}
    Candidate's Answer: {answer}
    
    Provide a brief, encouraging response that:
    1. Acknowledges their answer
    2. Shows you understood their response
    3. Maintains a positive tone
    4. Doesn't provide the "correct" answer (this is screening, not teaching)
    5. Transitions smoothly to the next question or conclusion
    
    Keep it brief and professional."""

def validate_tech_stack(tech_input: str) -> List[str]:
    """Validate and clean tech stack input"""
    import re
    
    # Common separators
    separators = [',', ';', '&', 'and', '\n', '\t']
    
    # Split by common separators
    technologies = []
    current_tech = tech_input
    
    for sep in separators:
        if sep in current_tech:
            technologies.extend([t.strip() for t in current_tech.split(sep) if t.strip()])
            break
    else:
        # If no separators found, treat as single technology
        technologies = [tech_input.strip()]
    
    # Clean and validate each technology
    cleaned_technologies = []
    for tech in technologies:
        # Remove extra whitespace and normalize
        tech = re.sub(r'\s+', ' ', tech.strip())
        
        # Skip empty or very short entries
        if len(tech) < 2:
            continue
        
        # Common technology name normalization
        tech_lower = tech.lower()
        if tech_lower in ['js', 'javascript']:
            tech = 'JavaScript'
        elif tech_lower in ['py', 'python']:
            tech = 'Python'
        elif tech_lower in ['java script']:
            tech = 'JavaScript'
        elif tech_lower in ['react.js', 'reactjs']:
            tech = 'React'
        elif tech_lower in ['node.js', 'nodejs']:
            tech = 'Node.js'
        elif tech_lower in ['aws', 'amazon web services']:
            tech = 'AWS'
        
        cleaned_technologies.append(tech)
    
    return cleaned_technologies
                
                 c l e a n e d _ t e c h n o l o g i e s . a p p e n d ( t e c h ) 
         
         r e t u r n   c l e a n e d _ t e c h n o l o g i e s 
 
 d e f   v a l i d a t e _ e m a i l ( e m a i l :   s t r )   - >   b o o l : 
         \ 
 
 \ \ V a l i d a t e 
 
 e m a i l 
 
 f o r m a t \ \ \ 
         p a t t e r n   =   r ' ^ [ a - z A - Z 0 - 9 . _ % + - ] + @ [ a - z A - Z 0 - 9 . - ] + \ . [ a - z A - Z ] { 2 , } $ ' 
         r e t u r n   r e . m a t c h ( p a t t e r n ,   e m a i l )   i s   n o t   N o n e 
 
 d e f   v a l i d a t e _ p h o n e ( p h o n e :   s t r )   - >   b o o l : 
         \ \ \ V a l i d a t e 
 
 p h o n e 
 
 n u m b e r 
 
 f o r m a t \ \ \ 
         #   R e m o v e   a l l   n o n - d i g i t   c h a r a c t e r s 
         d i g i t s _ o n l y   =   r e . s u b ( r ' \ D ' ,   ' ' ,   p h o n e ) 
         
         #   C h e c k   i f   i t ' s   a   v a l i d   l e n g t h   ( 1 0 - 1 5   d i g i t s ) 
         i f   l e n ( d i g i t s _ o n l y )   <   1 0   o r   l e n ( d i g i t s _ o n l y )   >   1 5 : 
                 r e t u r n   F a l s e 
         
         #   C h e c k   c o m m o n   p a t t e r n s 
         p a t t e r n s   =   [ 
                 r ' ^ \ + ? 1 ? [ 0 - 9 ] { 1 0 } $ ' ,     #   U S   f o r m a t 
                 r ' ^ \ + ? [ 0 - 9 ] { 1 0 , 1 5 } $ ' ,     #   I n t e r n a t i o n a l   f o r m a t 
                 r ' ^ \ ( [ 0 - 9 ] { 3 } \ ) \ s ? [ 0 - 9 ] { 3 } - [ 0 - 9 ] { 4 } $ ' ,     #   ( 5 5 5 )   1 2 3 - 4 5 6 7 
                 r ' ^ [ 0 - 9 ] { 3 } - [ 0 - 9 ] { 3 } - [ 0 - 9 ] { 4 } $ ' ,     #   5 5 5 - 1 2 3 - 4 5 6 7 
         ] 
         
         f o r   p a t t e r n   i n   p a t t e r n s : 
                 i f   r e . m a t c h ( p a t t e r n ,   p h o n e ) : 
                         r e t u r n   T r u e 
         
         r e t u r n   F a l s e 
 
 d e f   g e t _ r a n d o m _ q u e s t i o n ( t e c h _ s t a c k :   s t r )   - >   s t r : 
         \ \ \ G e t 
 
 a 
 
 r a n d o m 
 
 q u e s t i o n 
 
 f o r 
 
 f a l l b a c k 
 
 r e s p o n s e s \ \ \ 
         b a n k   =   T e c h n i c a l Q u e s t i o n B a n k ( ) 
         q u e s t i o n s   =   b a n k . g e t _ q u e s t i o n s _ f o r _ t e c h n o l o g y ( t e c h _ s t a c k ,   1 ) 
         i f   q u e s t i o n s : 
                 r e t u r n   q u e s t i o n s [ 0 ] . q u e s t i o n 
         r e t u r n   \ C a n 
 
 y o u 
 
 t e l l 
 
 m e 
 
 a b o u t 
 
 y o u r 
 
 e x p e r i e n c e 
 
 w i t h 
 
 t h i s 
 
 t e c h n o l o g y ? \ 
 
 