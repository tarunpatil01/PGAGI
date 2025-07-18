"""
Enhanced LLM Manager with Phi-3 + Ollama support
Provides intelligent hiring assistant responses with fallback mechanisms
"""

import os
import json
import requests
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM settings"""
    ollama_url: str = "http://localhost:11434"
    model_name: str = "phi3:mini"
    temperature: float = 0.7
    max_tokens: int = 200
    timeout: int = 15
    is_cloud: bool = False

class Phi3OllamaManager:
    """Enhanced manager for Phi-3 with Ollama integration"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.is_connected = False
        self.model_available = False
        self.fallback_mode = False
        self.last_check_time = 0
        self.check_interval = 60  # Check every 60 seconds
        self.response_cache = {}  # Simple response cache
        self.cache_max_size = 10
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection to Ollama service"""
        current_time = time.time()
        
        # Skip if recently checked
        if current_time - self.last_check_time < self.check_interval and self.is_connected:
            return
            
        try:
            logger.info("🔄 Checking Ollama connection...")
            
            # Check if Ollama service is running
            if self._check_ollama_service():
                logger.info("✅ Ollama service is running")
                self.is_connected = True
                
                # Check if model is available
                if self._check_model_availability():
                    logger.info(f"✅ Model {self.config.model_name} is available")
                    self.model_available = True
                else:
                    logger.warning(f"⚠️ Model {self.config.model_name} not found")
                    self.fallback_mode = True
            else:
                logger.warning("⚠️ Ollama service not running")
                self.fallback_mode = True
                
            self.last_check_time = current_time
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection: {str(e)}")
            self.fallback_mode = True
            self.last_check_time = current_time
    
    def _check_ollama_service(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.config.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_model_availability(self) -> bool:
        """Check if the required model is available"""
        try:
            response = requests.get(f"{self.config.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                return any(self.config.model_name in name for name in model_names)
            return False
        except Exception:
            return False
    
    def generate_response(self, prompt: str, system_message: str = None, context: Dict = None) -> str:
        """Generate response using Phi-3"""
        
        # Create cache key
        cache_key = f"{prompt[:50]}_{system_message[:30] if system_message else ''}"
        
        # Check cache first
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        # Only check connection if not recently checked
        self._initialize_connection()
        
        # Generate response with Phi-3
        if self.is_connected and self.model_available:
            try:
                response = self._generate_phi3_response(prompt, system_message, context)
                if response:
                    # Cache the response
                    self._cache_response(cache_key, response)
                    return response
                else:
                    return "I'm having trouble generating a response. Could you please try again?"
            except Exception as e:
                logger.error(f"❌ Phi-3 generation failed: {str(e)}")
                return "I'm experiencing technical difficulties. Please try again in a moment."
        
        return "I'm unable to connect to the AI model. Please check if Ollama is running and try again."
    
    def _cache_response(self, key: str, response: str):
        """Cache response with size limit"""
        if len(self.response_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        self.response_cache[key] = response
    
    def _generate_phi3_response(self, prompt: str, system_message: str = None, context: Dict = None) -> str:
        """Generate response using Phi-3"""
        try:
            # Build the complete prompt
            full_prompt = self._build_prompt(prompt, system_message, context)
            
            # Make request to Ollama with optimized settings
            response = requests.post(
                f"{self.config.ollama_url}/api/generate",
                json={
                    "model": self.config.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                        "stop": ["\n\n", "User:", "Assistant:"]
                    }
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                return self._clean_response(ai_response)
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout - model taking too long to respond")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error - cannot reach Ollama service")
            return None
        except Exception as e:
            logger.error(f"❌ Error generating Phi-3 response: {str(e)}")
            return None
    
    def _build_prompt(self, prompt: str, system_message: str = None, context: Dict = None) -> str:
        """Build context-aware prompt for Phi-3"""
        
        # Default system message for hiring assistant
        if not system_message:
            system_message = """You are TalentScout's hiring assistant. Be professional, friendly, and concise. 
            Ask clear questions. Keep responses to 1-2 sentences. Focus on the hiring process."""
        
        # Add context if available
        context_str = ""
        if context:
            stage = context.get("stage", "")
            candidate_info = context.get("candidate_info", {})
            
            if stage:
                context_str += f"\nCurrent Stage: {stage}"
            
            if candidate_info:
                info_summary = []
                for key, value in candidate_info.items():
                    if value:
                        info_summary.append(f"{key}: {value}")
                if info_summary:
                    context_str += f"\nCandidate Information: {'; '.join(info_summary)}"
        
        # Build the complete prompt
        full_prompt = f"System: {system_message}{context_str}\n\nUser: {prompt}\n\nAssistant:"
        
        return full_prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean up AI response"""
        # Remove common AI response artifacts
        response = response.replace("System:", "")
        response = response.replace("User:", "")
        response = response.replace("Assistant:", "")
        
        # Clean up extra whitespace
        response = " ".join(response.split())
        
        return response.strip()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the LLM manager"""
        return {
            "ollama_connected": self.is_connected,
            "model_available": self.model_available,
            "fallback_mode": self.fallback_mode,
            "model_name": self.config.model_name,
            "ollama_url": self.config.ollama_url
        }
