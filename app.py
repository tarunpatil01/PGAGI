# Local question bank for popular skills
LOCAL_QUESTION_BANK = {
    "react": "What is a React component and how does state management work in React?",
    "fastapi": "What is FastAPI and how does it differ from Flask? Give a simple example of a FastAPI endpoint.",
    "cpp": "What is RAII in C++ and how does its implementation affect resource management within an application? Provide a brief code example.",
    "python": "What is a Python decorator and how is it used? Provide a simple example.",
    "javascript": "What is event delegation in JavaScript and why is it useful?",
    "mongodb": "What is a MongoDB document and how does it differ from a relational database row?",
    "sql": "What is a JOIN in SQL and provide an example query.",
    "docker": "What is Docker and how does containerization benefit development workflows?",
    "git": "What is the difference between git merge and git rebase?",
    "html": "What is the purpose of the <head> tag in HTML?",
    "css": "What is the box model in CSS?",
    "node.js": "What is the event loop in Node.js?",
    "java": "What is inheritance in Java and how is it implemented?",
}
def is_valid_position(position):
    val = position.strip()
    # Only letters and spaces, at least two words, minimum 5 characters
    if not re.match(r'^[A-Za-z ]+$', val):
        return False
    if len(val) < 5:
        return False
    if len(val.split()) < 2:
        return False
    return True
import streamlit as st
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pymongo import MongoClient

load_dotenv()

try:
    from local_llm import Phi3OllamaManager, LLMConfig
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ Local LLM not available. Using fallback responses.")

def main():
    # MongoDB connection (minimal, auto-save)
    MONGO_URL = os.getenv("MONGO_URL")
    MONGO_DB = os.getenv("MONGO_DB", "Chatbot")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "sessions")
    if "mongo_client" not in st.session_state:
        try:
            st.session_state.mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
            st.session_state.mongo_client.server_info()
            st.session_state.mongo_ok = True
            # Ensure 'user' collection exists in the database
            db = st.session_state.mongo_client[MONGO_DB]
            if 'user' not in db.list_collection_names():
                db.create_collection('user')
        except Exception:
            st.session_state.mongo_ok = False


    # Sentiment analyzer
    if "sentiment_analyzer" not in st.session_state:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        st.session_state.sentiment_analyzer = SentimentIntensityAnalyzer()

    # Minimal session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "chatbot" not in st.session_state:
        is_cloud = os.getenv("DEPLOYMENT_MODE") == "cloud"
        # Increase timeout and optimize config for Phi3:mini
        config = LLMConfig(is_cloud=is_cloud)
        if hasattr(config, 'timeout'):
            config.timeout = 120  # Increase timeout to 120 seconds
        if hasattr(config, 'model'):
            config.model = "phi3:mini"
        if hasattr(config, 'max_tokens'):
            config.max_tokens = 512  # Limit response length for speed
        st.session_state.chatbot = Phi3OllamaManager(config)

    # Show loading animation at the very start
    if "app_loaded" not in st.session_state:
        st.session_state.app_loaded = False

    if not st.session_state.app_loaded:
        st.markdown("""
        <style>
        .center-spinner {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 60vh;
        }
        .lds-dual-ring {
          display: inline-block;
          width: 80px;
          height: 80px;
        }
        .lds-dual-ring:after {
          content: " ";
          display: block;
          width: 64px;
          height: 64px;
          margin: 8px;
          border-radius: 50%;
          border: 6px solid #00c3ff;
          border-color: #00c3ff transparent #00c3ff transparent;
          animation: lds-dual-ring 1.2s linear infinite;
        # Auto-save to MongoDB
        @keyframes lds-dual-ring {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        </style>
        <div class="center-spinner">
          <div class="lds-dual-ring"></div>
          <div style="margin-top: 2rem; font-size: 1.2rem; color: #00c3ff; animation: fadeIn 1s;">Loading TalentScout... Please wait.</div>
        </div>
        <style>
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        </style>
        """, unsafe_allow_html=True)
        import time as _time
        _time.sleep(1.2)
        st.session_state.app_loaded = True
        st.rerun()

    # Conversation state machine
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = "greeting"
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {
            "name": None,
            "email": None,
            "phone": None,
            "experience": None,
            "position": None,
            "location": None,
            "tech_stack": None,
            "tech_questions": [],
            "answers": {}
        }
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hello! Welcome to TalentScout. I'm your AI hiring assistant. I'll guide you through a quick screening to help match you with the best opportunities. You can type 'exit' or 'quit' anytime to end the chat.\n\nLet's get started! What's your full name?"
        })
        st.session_state.conversation_state = "get_name"

    st.set_page_config(
        page_title="TalentScout AI Hiring Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Minimal sidebar
    with st.sidebar:
        st.markdown("<h3 style='color:#fff;'>TalentScout</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)
        st.markdown("<span style='color:#aaa;'>AI Hiring Assistant</span>", unsafe_allow_html=True)
        st.markdown("<span style='color:#aaa;'>Powered by Phi-3 + Ollama</span>", unsafe_allow_html=True)
        if st.session_state.mongo_ok:
            st.markdown("<span style='color:#0f0;'>Session auto-saved</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#f00;'>Session not saved</span>", unsafe_allow_html=True)

    # Main chat area CSS
    st.markdown("""
    <style>
    .chat-bubble-user {
        background: #fff;
        color: #23272f;
        border-radius: 16px 16px 4px 16px;
        padding: 0.8rem 1.1rem;
        max-width: 70%;
        font-size: 1.08rem;
        margin-left: auto;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        word-break: break-word;
    }
    .chat-bubble-bot {
        background: #23272f;
        color: #fff;
        border-radius: 16px 16px 16px 4px;
        padding: 1rem 1.3rem;
        max-width: 70%;
        font-size: 1.08rem;
        margin-right: auto;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        word-break: break-word;
    }
    .send-btn {
        background: #00c3ff;
        border: none;
        border-radius: 50%;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-left: 8px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .send-btn:hover {
        background: #0099cc;
    }
    .send-icon {
        color: #fff;
        font-size
        font-size: 1.3rem;
    }
    .stTextArea textarea {
        border-radius: 16px;
        min-height: 48px;
        font-size: 1.08rem;
        padding-right: 48px;
    }
    .input-row {
        display: flex;
        align-items: center;
        margin-top: 1.2rem;
    }
    /* Responsive styles for mobile */
    @media (max-width: 600px) {
        .chat-bubble-user, .chat-bubble-bot {
            max-width: 98vw !important;
            font-size: 1rem !important;
            padding: 0.7rem 0.7rem !important;
        }
        .stTextArea textarea {
            font-size: 1rem !important;
            min-height: 38px !important;
            padding-right: 38px !important;
        }
        .input-row {
            flex-direction: column;
            align-items: stretch;
        }
        [data-testid="send-btn"] button {
            width: 100% !important;
            margin: 0.5rem 0 0 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'><span style='font-weight:600;color:#00c3ff;'>🤖 TalentScout:</span><br>{message['content']}</div>", unsafe_allow_html=True)

    # Chat input row with send icon
    # Use Streamlit form for reliable Ctrl+Enter and input handling
    with st.form(key="chat_form", clear_on_submit=True):
        input_col, btn_col = st.columns([10,1])
        with input_col:
            user_input = st.text_area(
                "Your message",
                value="",  # Always start empty
                key="user_input_box",
                height=160,
                label_visibility="collapsed",
                max_chars=1000,
                help=None
            )
        with btn_col:
            st.markdown("""
            <style>
            [data-testid="send-btn"] button {
                background: #00c3ff !important;
                border-radius: 50% !important;
                width: 38px !important;
                height: 38px !important;
                padding: 0 !important;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.3rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
            send_clicked = st.form_submit_button("✈️", help="Send", type="primary")

    # No custom JS, using Streamlit form for Ctrl+Enter

    # Handle send
    # Debug: print state and input
    print(f"[DEBUG] send_clicked: {send_clicked}, user_input: '{user_input}', session user_input: '{st.session_state.get('user_input','')}'")
    print(f"[DEBUG] conversation_state: {st.session_state.get('conversation_state')}, candidate_info: {st.session_state.get('candidate_info')}")
    if send_clicked and user_input.strip():
        # Only use the current text area value, do not rely on st.session_state.user_input
        user_text = user_input.strip()
        # Always clear input after send (handled by clear_on_submit, but ensure session state is also cleared)
        st.session_state.user_input = ""
        # Sentiment analysis
        analyzer = st.session_state.sentiment_analyzer
        sentiment = analyzer.polarity_scores(user_text)
        # Exit keywords
        if user_text.lower() in ["exit", "quit", "goodbye", "bye"]:
            st.session_state.messages.append({"role": "user", "content": user_text, "sentiment": sentiment})
            mongo_status = st.session_state.candidate_info.get("_mongo_save_status")
            candidate_name = st.session_state.candidate_info.get("name")
            candidate_position = st.session_state.candidate_info.get("position")
            if mongo_status is True:
                thank_you_msg = "Thank you, your answers have been saved. "
                if candidate_name:
                    thank_you_msg += f"{candidate_name}, "
                if candidate_position:
                    thank_you_msg += f"we'll be in touch regarding the {candidate_position} position. "
                thank_you_msg += "You can close the window now."
                st.session_state.messages.append({"role": "assistant", "content": thank_you_msg})
            elif mongo_status is False:
                st.session_state.messages.append({"role": "assistant", "content": "Error in storing your answers. Please try again later."})
            else:
                thank_you_msg = "Thank you for your time! "
                if candidate_name:
                    thank_you_msg += f"{candidate_name}, "
                if candidate_position:
                    thank_you_msg += f"we'll be in touch regarding the {candidate_position} position. "
                thank_you_msg += "Have a great day! 👋"
                st.session_state.messages.append({"role": "assistant", "content": thank_you_msg})
            st.session_state.conversation_state = "ended"
            st.session_state.user_input = ""
            st.rerun()
        # State machine for info gathering
        state = st.session_state.conversation_state
        info = st.session_state.candidate_info
        # Only append user message once per send
        if not (len(st.session_state.messages) > 0 and st.session_state.messages[-1].get("role") == "user" and st.session_state.messages[-1].get("content") == user_text):
            st.session_state.messages.append({"role": "user", "content": user_text, "sentiment": sentiment})
        def validate_with_llm(field, value, context=None):
            prompt = f"You are a strict data validator for a job application form. The user entered the following for the field '{field}': '{value}'. "
            if context:
                prompt += f"Context: {context}. "
            prompt += f"Is this a valid {field}? Reply only with 'yes' or 'no'."
            try:
                resp = st.session_state.chatbot.generate_response(prompt, system_message=None)
            except Exception:
                resp = None
            # Debug output for LLM validation
            print(f"[DEBUG] LLM validation prompt: {prompt}")
            print(f"[DEBUG] LLM validation response: {resp}")
            if resp and isinstance(resp, str):
                answer = resp.strip().lower()
                if answer.startswith('yes') or answer == 'yes':
                    return True
            return False

        if state == "get_name":
            # Fallback: Accept if name looks valid (letters, spaces, hyphens, apostrophes, at least 2 words)
            def looks_like_name(val):
                val = val.strip()
                # At least two words, only letters, spaces, hyphens, apostrophes
                return bool(re.match(r"^[A-Za-z][A-Za-z\-' ]+[A-Za-z]$", val)) and len(val.split()) >= 2

            llm_valid = validate_with_llm("name", user_text)
            if not llm_valid:
                # If LLM says no, but regex says yes, accept
                if looks_like_name(user_text):
                    print(f"[DEBUG] LLM rejected name but regex accepted: '{user_text}'")
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid full name (no numbers or special characters)."})
                    st.session_state.user_input = ""
                    st.rerun()
            info["name"] = user_text
            personalized_name = info.get("name")
            if personalized_name:
                st.session_state.messages.append({"role": "assistant", "content": f"Thanks, {personalized_name}! What's your email address?"})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Thanks! What's your email address?"})
            st.session_state.conversation_state = "get_email"
        elif state == "get_email":
            def looks_like_email(val):
                # Simple email regex
                return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", val.strip()))

            llm_valid = validate_with_llm("email", user_text)
            if not llm_valid:
                if looks_like_email(user_text):
                    print(f"[DEBUG] LLM rejected email but regex accepted: '{user_text}'")
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid email address (e.g., user@email.com)."})
                    st.session_state.user_input = ""
                    st.rerun()
            info["email"] = user_text
            personalized_name = info.get("name")
            if personalized_name:
                st.session_state.messages.append({"role": "assistant", "content": f"Great, {personalized_name}. And your phone number?"})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "And your phone number?"})
            st.session_state.conversation_state = "get_phone"
        elif state == "get_phone":
            def looks_like_phone(val):
                val = val.strip().replace(' ', '').replace('-', '')
                # Digits only, length 7-15
                return val.isdigit() and 7 <= len(val) <= 15

            if any(c.isalpha() for c in user_text):
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid phone number (digits only, no letters)."})
                st.session_state.user_input = ""
                st.rerun()
            llm_valid = validate_with_llm("phone number", user_text)
            if not llm_valid:
                if looks_like_phone(user_text):
                    print(f"[DEBUG] LLM rejected phone but regex accepted: '{user_text}'")
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid phone number (digits only, no letters, and a reasonable length)."})
                    st.session_state.user_input = ""
                    st.rerun()
            info["phone"] = user_text
            personalized_name = info.get("name")
            if personalized_name:
                st.session_state.messages.append({"role": "assistant", "content": f"Thank you, {personalized_name}. How many years of professional experience do you have?"})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "How many years of professional experience do you have?"})
            st.session_state.conversation_state = "get_experience"
        elif state == "get_experience":
            def looks_like_experience(val):
                val = val.strip()
                # Accept 0-50 years, integer or float
                try:
                    years = float(val)
                    return 0 <= years <= 50
                except Exception:
                    return False

            llm_valid = validate_with_llm("years of professional experience", user_text)
            if not llm_valid:
                if looks_like_experience(user_text):
                    print(f"[DEBUG] LLM rejected experience but regex accepted: '{user_text}'")
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid number of years of professional experience (e.g., 3, 5, 10)."})
                    st.session_state.user_input = ""
                    st.rerun()
            info["experience"] = user_text
            personalized_name = info.get("name")
            if personalized_name:
                st.session_state.messages.append({"role": "assistant", "content": f"Thanks, {personalized_name}. What position(s) are you interested in?"})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "What position(s) are you interested in?"})
            st.session_state.conversation_state = "get_position"
        elif state == "get_position":
            if not is_valid_position(user_text):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Please enter a valid job position or role (at least two words, only letters and spaces, minimum 5 characters, no symbols or numbers)."
                })
                st.session_state.user_input = ""
                st.rerun()
            else:
                info["position"] = user_text.strip()
                personalized_name = info.get("name")
                if personalized_name:
                    st.session_state.messages.append({"role": "assistant", "content": f"Thank you, {personalized_name}. Where are you currently located? (City, Country)"})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Where are you currently located? (City, Country)"})
                st.session_state.conversation_state = "get_location"
        elif state == "get_location":
            def is_valid_location(val):
                val = val.strip()
                # Only letters, spaces, commas, hyphens; at least two words, minimum 5 characters
                if not re.match(r'^[A-Za-z ,\-]+$', val):
                    return False
                if len(val) < 5:
                    return False
                if len(val.split()) < 2:
                    return False
                return True

            if not is_valid_location(user_text):
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid location (e.g., City, Country). Use only letters, spaces, commas, and hyphens."})
                st.session_state.user_input = ""
                st.rerun()
            info["location"] = user_text
            personalized_name = info.get("name")
            if personalized_name:
                st.session_state.messages.append({"role": "assistant", "content": f"Thanks, {personalized_name}. Please list your tech stack (programming languages, frameworks, databases, tools)."})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Please list your tech stack (programming languages, frameworks, databases, tools)."})
            st.session_state.conversation_state = "get_tech_stack"
        elif state == "get_tech_stack":
            info["tech_stack"] = user_text
            # Split tech stack into skills (comma or semicolon separated)
            skills = [s.strip() for s in re.split(r",|;", user_text) if s.strip()]
            info["tech_questions"] = []
            info["answers"] = {}
            # Validate tech stack
            if not skills or any(len(skill) < 2 for skill in skills):
                st.session_state.messages.append({"role": "assistant", "content": "Please enter at least one valid skill in your tech stack (e.g., python, fastapi, langchain)."})
                st.session_state.user_input = ""
                st.rerun()
            info["_skills"] = skills
            info["_current_skill_idx"] = 0
            # Generate all questions for all skills at once
            all_questions = []
            asked_questions = set()
            for skill in skills:
                max_attempts = 3
                question = None
                for attempt in range(max_attempts):
                    with st.spinner(f"Wait, we are getting a technical question for {skill}... (Attempt {attempt+1})"):
                        system_prompt = (
                            f"You are an AI hiring assistant. Generate a technical interview question for a BEGINNER about the following skill: {skill}. "
                            f"The question must be specific to {skill} and NOT about any other skill. "
                            "Return only the question, do not number it."
                        )
                        print(f"[DEBUG] LLM system_prompt for skill '{skill}': {system_prompt}")
                        try:
                            question = st.session_state.chatbot.generate_response(system_prompt, system_message=None)
                            print(f"[DEBUG] LLM response for skill '{skill}': {question}")
                        except Exception as e:
                            print(f"[ERROR] LLM exception for skill '{skill}': {e}")
                            question = None
                        if question and isinstance(question, str) and len(question.strip()) > 5:
                            qtext = question.strip()
                            if qtext not in asked_questions:
                                all_questions.append(qtext)
                                asked_questions.add(qtext)
                                break
                            else:
                                print(f"[DEBUG] Duplicate question detected for skill '{skill}': {qtext}")
                                question = None
                # Fallback to local question bank if LLM fails
                if not question or not (isinstance(question, str) and len(question.strip()) > 5):
                    local_q = LOCAL_QUESTION_BANK.get(skill.lower())
                    if local_q:
                        all_questions.append(local_q)
                        print(f"[DEBUG] Local question bank used for skill '{skill}': {local_q}")
                    else:
                        all_questions.append(f"[ERROR] Could not generate a unique technical question for {skill}. Please try again, rephrase your tech stack, or answer: What is your experience with {skill}? (Describe briefly.)")
                        print(f"[DEBUG] Fallback error message for skill '{skill}'")
            info["tech_questions"] = all_questions
            info["_asked_questions"] = list(asked_questions)
            info["_current_skill_idx"] = 0
            # Ask the first question
            personalized_name = info.get("name")
            first_question = all_questions[0] if all_questions else None
            if first_question:
                if personalized_name:
                    st.session_state.messages.append({"role": "assistant", "content": f"Great, {personalized_name}! Here is your technical question:\n\n{first_question}"})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"Great! Here is your technical question:\n\n{first_question}"})
                st.session_state.conversation_state = "tech_questions"
            else:
                st.session_state.messages.append({"role": "assistant", "content": "I'm having trouble generating technical questions for your tech stack. Please try again or rephrase your tech stack."})
                st.session_state.user_input = ""
                st.rerun()
        elif state == "tech_questions":
            # Save answer to the last question
            qlist = info["tech_questions"] if isinstance(info["tech_questions"], list) else []
            answered = len(info["answers"])
            # Ask next question in the list
            if answered < len(qlist):
                info["answers"][f"Q{answered+1}"] = user_text
                next_idx = answered + 1
                if next_idx < len(qlist):
                    next_question = qlist[next_idx]
                    personalized_name = info.get("name")
                    if personalized_name:
                        st.session_state.messages.append({"role": "assistant", "content": f"Thank you, {personalized_name}! Here is your next technical question:\n\n{next_question}"})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": f"Thank you! Here is your next technical question:\n\n{next_question}"})
                    st.session_state.conversation_state = "tech_questions"
                else:
                    # All questions answered
                    info["_current_skill_idx"] = len(qlist)
                    personalized_name = info.get("name")
                    personalized_position = info.get("position")
                    thank_you_msg = "Thank you for answering all the questions! "
                    if personalized_name:
                        thank_you_msg += f"{personalized_name}, "
                    if personalized_position:
                        thank_you_msg += f"we'll be in touch regarding the {personalized_position} position. "
                    thank_you_msg += "If you have anything else to add, let me know. Otherwise, type 'exit' to finish."
                    st.session_state.messages.append({"role": "assistant", "content": thank_you_msg})
                    st.session_state.conversation_state = "completed"
                    # Insert candidate_info into 'user' collection in MongoDB
                    if st.session_state.mongo_ok:
                        try:
                            mongo_url = MONGO_URL
                            mongo_db = "Chatbot"
                            mongo_collection = "user"
                            print(f"[DEBUG] MongoDB URL: {mongo_url}")
                            print(f"[DEBUG] MongoDB Database: {mongo_db}")
                            print(f"[DEBUG] MongoDB Collection: {mongo_collection}")
                            db = st.session_state.mongo_client[mongo_db]
                            db[mongo_collection].insert_one(dict(info))
                            print("[DEBUG] Inserted candidate_info into Chatbot.user collection.")
                            info["_mongo_save_status"] = True
                        except Exception as e:
                            print(f"[ERROR] Failed to insert into Chatbot.user collection: {e}")
                            info["_mongo_save_status"] = False
                    # Now clear tech_questions if desired
                    info["tech_questions"] = []
        elif state == "question_retry_choice":
            # Handle user choice after failed question generation
            user_choice = user_text.lower().strip()
            skill = st.session_state.get("failed_skill")
            idx = st.session_state.get("failed_skill_idx")
            info["_current_skill_idx"] = idx
            if user_choice == "retry":
                st.session_state.conversation_state = "tech_questions"
                st.session_state.user_input = ""
                st.rerun()
            elif user_choice == "skip":
                info["_current_skill_idx"] = idx + 1
                st.session_state.conversation_state = "tech_questions"
                st.session_state.user_input = ""
                st.rerun()
            elif user_choice == "rephrase":
                st.session_state.messages.append({"role": "assistant", "content": f"Please enter a new skill name to replace '{skill}':"})
                st.session_state.conversation_state = "rephrase_skill"
                st.session_state.user_input = ""
                st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Invalid choice. Please type 'retry', 'skip', or 'rephrase'."})
                st.session_state.user_input = ""
                st.rerun()

        elif state == "rephrase_skill":
            # Accept new skill name and retry question generation
            new_skill = user_text.strip()
            idx = st.session_state.get("failed_skill_idx")
            skills = info.get("_skills", [])
            if new_skill:
                skills[idx] = new_skill
                info["_skills"] = skills
                st.session_state.messages.append({"role": "assistant", "content": f"Skill updated to '{new_skill}'. Trying to generate a question..."})
                st.session_state.conversation_state = "tech_questions"
                st.session_state.user_input = ""
                st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid skill name."})
                st.session_state.user_input = ""
                st.rerun()
        else:
            # Fallback for unexpected state
            fallback_name = info.get("name")
            fallback_position = info.get("position")
            fallback_msg = "I'm here to help with your screening. "
            if fallback_name:
                fallback_msg += f"{fallback_name}, "
            fallback_msg += "please answer the previous question or type 'exit' to finish."
            if fallback_position:
                fallback_msg += f" (Position: {fallback_position})"
            st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
        st.session_state.user_input = ""
        # Auto-save to MongoDB
        if st.session_state.mongo_ok:
            try:
                from datetime import UTC
                doc = {
                    "messages": st.session_state.messages,
                    "timestamp": datetime.now(UTC),
                    "user": os.getenv("USER", "anonymous"),
                    "candidate_info": st.session_state.candidate_info
                }
                db = st.session_state.mongo_client[MONGO_DB]
                db[MONGO_COLLECTION].insert_one(doc)
            except Exception:
                pass
        st.rerun()
    else:
        # No need to update st.session_state.user_input here; let the text area always start empty
        if st.button("🔄 Start New Session", type="primary"):
            st.session_state.chatbot = Phi3OllamaManager(LLMConfig(is_cloud=os.getenv("DEPLOYMENT_MODE") == "cloud"))
            st.session_state.messages = []
            st.session_state.user_input = ""
            st.session_state.user_name = None
            st.session_state.conversation_state = "greeting"
            st.session_state.candidate_info = {
                "name": None,
                "email": None,
                "phone": None,
                "experience": None,
                "position": None,
                "location": None,
                "tech_stack": None,
                "tech_questions": [],
                "answers": {}
            }
            st.rerun()

    st.markdown("<div style='margin-top:2rem;text-align:center;color:#aaa;'>Powered by Phi-3 AI and Ollama • Built with TalentScout | 🔒 Data handled securely.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
