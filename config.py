"""
Configuration file for Honeypot System
"""

# API Configuration
API_KEY = "123456"  # CHANGE THIS!
API_HOST = "0.0.0.0"
API_PORT = 8000

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"  # Good for 4GB GPU

# Conversation Settings
MAX_CONVERSATION_TURNS = 20
SCAM_CONFIDENCE_THRESHOLD = 0.6

# Agent Settings
ENABLE_FALLBACK_RESPONSES = True
RESPONSE_TIMEOUT_SECONDS = 15
MAX_RESPONSE_LENGTH = 200

# Storage (for production)
# Use Redis or Database instead of in-memory storage
USE_REDIS = False
REDIS_URL = "redis://localhost:6379"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "honeypot.log"
