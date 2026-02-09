

API_KEY = "123456"  # API KEY, keep whatever
API_HOST = "0.0.0.0"
API_PORT = 8000
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"  #Use whatever you want, and whatever your hardware can support

MAX_CONVERSATION_TURNS = 20
SCAM_CONFIDENCE_THRESHOLD = 0.65

ENABLE_FALLBACK_RESPONSES = True
RESPONSE_TIMEOUT_SECONDS = 15
MAX_RESPONSE_LENGTH = 200

USE_REDIS = False
REDIS_URL = "redis://localhost:6379"

LOG_LEVEL = "INFO"
LOG_FILE = "honeypot.log"
