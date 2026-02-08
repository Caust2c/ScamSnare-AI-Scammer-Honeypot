# AI-Powered Agentic Honey-Pot System 🕵️

An autonomous AI system that detects scam messages and engages scammers to extract actionable intelligence through believable multi-turn conversations.

## 🎯 Features

- **Hybrid Scam Detection**: Pattern matching + LLM analysis
- **Autonomous Agent**: Maintains believable human personas
- **Multi-Turn Engagement**: Natural conversation flow
- **Intelligence Extraction**: Bank accounts, UPI IDs, phishing URLs, phone numbers
- **Engagement Metrics**: Tracks conversation quality and intelligence gathered
- **Local LLM**: Runs on your hardware (4GB GPU compatible)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Mock Scammer API (External)             │
│            Sends scam message events                 │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│           FastAPI Endpoint (main.py)                 │
│  • Validates API key                                 │
│  • Manages conversation state                        │
│  • Orchestrates components                           │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│         Scam Detector (scam_detector.py)             │
│  • Pattern-based detection (keywords, regex)         │
│  • LLM-based contextual analysis (Ollama)            │
│  • Confidence scoring                                │
│  • Scam type classification                          │
└───────────────────────┬─────────────────────────────┘
                        │
                   Scam Detected?
                        │
                ┌───────┴───────┐
                │  YES (>60%)   │
                └───────┬───────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│          Agent Engine (agent_engine.py)              │
│  • Persona selection (4 types)                       │
│    - Curious victim                                  │
│    - Eager victim                                    │
│    - Concerned victim                                │
│    - Elderly victim                                  │
│  • Stage-aware responses (4 stages)                  │
│    1. Initial contact                                │
│    2. Building trust                                 │
│    3. Information gathering                          │
│    4. Extraction phase                               │
│  • LLM response generation                           │
│  • Fallback mechanisms                               │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│   Intelligence Extractor (intelligence_extractor.py) │
│  • Regex pattern extraction                          │
│  • Validation and filtering                          │
│  • Claims analysis                                   │
│  • Quality scoring                                   │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Structured JSON Response                │
│  • Scam detection status                             │
│  • Agent response message                            │
│  • Extracted intelligence                            │
│  • Engagement metrics                                │
└─────────────────────────────────────────────────────┘
```

## 📋 Component Details

### 1. Main API (main.py)
- FastAPI server handling incoming requests
- API key authentication
- Conversation state management
- Response orchestration

### 2. Scam Detector (scam_detector.py)
**Dual Detection Approach:**

**A. Pattern Matching (Fast)**
- Keywords: "bank account", "upi id", "urgent", "verify"
- Regex: URLs, phone numbers, account numbers
- Weighted scoring by category

**B. LLM Analysis (Accurate)**
- Contextual understanding
- Intent detection
- Confidence scoring
- Uses local Ollama model

**Output:** Scam probability + confidence score

### 3. Agent Engine (agent_engine.py)
**Persona Management:**

| Persona | When Used | Strategy |
|---------|-----------|----------|
| Curious Victim | Early stages, financial scams | Show interest, ask questions |
| Eager Victim | Mid-stage, ready to comply | Express enthusiasm, seek next steps |
| Concerned Victim | Phishing, urgent claims | Show worry, request clarification |
| Elderly Victim | Impersonation scams | Express confusion, need guidance |

**Conversation Stages:**
1. **Initial Contact** (1-2 turns): Establish communication
2. **Building Trust** (3-4 turns): Show interest/concern
3. **Information Gathering** (5-7 turns): Extract details
4. **Extraction Phase** (8+ turns): Maximum intelligence gathering

### 4. Intelligence Extractor (intelligence_extractor.py)
**Extracts:**
- Bank account numbers (9-18 digits, validated)
- IFSC codes (Indian bank codes)
- UPI IDs (@paytm, @ybl, etc.)
- Phone numbers (Indian format)
- Email addresses
- URLs (especially suspicious/phishing)
- PAN cards
- Aadhaar numbers
- Bank names
- Company impersonations
- Scammer claims

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Ollama must be installed and running
ollama serve

# 2. Pull the model (for 4GB GPU)
ollama pull llama3.2:3b
```

### Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
# Edit config.py and set a secure API_KEY

# 3. Start server
python main.py
```

Server starts at `http://localhost:8000`

### Testing
```bash
# Run test suite
python test_system.py
```

## 📡 API Usage

### Endpoint: POST /detect

**Request:**
```json
{
  "conversation_id": "unique_conversation_id",
  "message": "Scammer's message here",
  "history": [
    {
      "role": "scammer",
      "content": "Previous message",
      "timestamp": "2024-01-01T10:00:00"
    }
  ]
}
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key
```

**Response:**
```json
{
  "conversation_id": "unique_conversation_id",
  "scam_detected": true,
  "agent_activated": true,
  "response_message": "Oh really? How do I claim this prize?",
  "extracted_intelligence": {
    "bank_accounts": ["1234567890123"],
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": ["9876543210"],
    "urls": ["https://bit.ly/scam"],
    "bank_names": ["SBI"],
    "company_names": ["Amazon"],
    "scammer_claims": ["Claims lottery win", "Creates urgency"],
    "extracted_count": 5
  },
  "engagement_metrics": {
    "total_turns": 4,
    "agent_turns": 2,
    "conversation_duration_seconds": 120,
    "intelligence_items_found": 5
  },
  "confidence_score": 0.89
}
```

## 🎭 How Personas Work

**Example: Eager Victim Persona**

**Scammer:** "You won Rs 50,000! Send your account number."

**Agent (Eager):** "Wow, that's amazing! Yes, I'd love to claim it! What's the process? Which account details do you need exactly?"

**Strategy:** Shows enthusiasm while extracting specifics about what information they want and how they'll process it.

## 📊 Evaluation Metrics

The system tracks:
- **Scam Detection Accuracy**: Pattern + LLM confidence
- **Engagement Duration**: Conversation length
- **Turn Count**: Number of back-and-forth exchanges
- **Intelligence Quality**: Number and type of extracted items
- **Response Time**: API latency

## ⚙️ Configuration Options

### Model Selection (config.py)
```python
# For 4GB GPU:
OLLAMA_MODEL = "llama3.2:3b"  # Balanced (Recommended)
OLLAMA_MODEL = "phi3:mini"    # Faster
OLLAMA_MODEL = "gemma2:2b"    # Smallest

# If you have more VRAM:
OLLAMA_MODEL = "llama3.2:7b"  # More accurate
```

### Tuning Detection
```python
# config.py
SCAM_CONFIDENCE_THRESHOLD = 0.6  # Lower = more sensitive
```

### Response Tuning
```python
# agent_engine.py line ~140
temperature=0.7  # Higher = more creative (0.7-0.9)
```

## 🐛 Troubleshooting

### Slow Responses
**Problem:** API takes >15 seconds
**Solution:** 
1. Reduce context window: `history[-2:]` instead of `history[-4:]`
2. Reduce num_predict: `80` instead of `150`
3. Use faster model: `phi3:mini`

### GPU Out of Memory
**Problem:** Ollama crashes
**Solution:**
```bash
ollama pull gemma2:2b  # Smallest model
```

### Robotic Responses
**Problem:** Agent sounds like AI
**Solution:** Increase temperature in agent_engine.py to 0.8-0.9

### False Positives
**Problem:** Detecting non-scams as scams
**Solution:** Increase `SCAM_CONFIDENCE_THRESHOLD` to 0.7 or 0.8

## 🔒 Security Notes

- Change default API_KEY in config.py
- Use HTTPS in production
- Implement rate limiting
- Don't log sensitive extracted data
- Use environment variables for production config

## 📈 Performance on 4GB GPU

**With llama3.2:3b:**
- Response time: 3-8 seconds
- Memory usage: ~3.5GB
- Quality: Good balance
- Simultaneous conversations: 2-3

**Optimization tips:**
- Reduce num_predict for faster responses
- Use smaller models for higher throughput
- Implement response caching for common patterns

## 🎯 Key Design Decisions

1. **Hybrid Detection**: Pattern matching catches obvious scams fast, LLM provides context
2. **Staged Conversations**: Different strategies for different conversation phases
3. **Multiple Personas**: Adapt to scam type for believability
4. **Fallback Responses**: System works even if LLM fails
5. **Local LLM**: Privacy + no API costs + works offline

## 🔄 Future Enhancements

- [ ] Redis for persistent conversation storage
- [ ] Multiple language support
- [ ] Voice call integration
- [ ] Advanced intelligence correlation
- [ ] Real-time monitoring dashboard
- [ ] Automated reporting to authorities

## 📝 License

Educational/Research use

## 🤝 Contributing

This is a hackathon/competition project. Contributions welcome!

---

**Built for AI-Powered Agentic Honey-Pot System Challenge**
