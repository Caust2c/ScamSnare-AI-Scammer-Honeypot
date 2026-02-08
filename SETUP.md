# Agentic Honey-Pot System - Setup Guide

## Prerequisites

1. **Ollama installed and running**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/version
   ```

2. **Python 3.8+**

3. **GPU with 4GB VRAM** (RTX 2050)

## Installation Steps

### 1. Install Python Dependencies

```bash
cd honeypot_system
pip install -r requirements.txt
```

### 2. Pull Ollama Model

For 4GB GPU, use the 3B parameter model:

```bash
ollama pull llama3.2:3b
```

**Alternative models for 4GB GPU:**
- `llama3.2:3b` (Recommended - best balance)
- `phi3:mini` (Faster, less accurate)
- `gemma2:2b` (Smallest, fastest)

### 3. Configure API Key

Edit `config.py` and change:
```python
API_KEY = "your-secure-api-key-change-this"
```

To something secure like:
```python
API_KEY = "honeypot_secure_key_12345"
```

### 4. Start the Server

```bash
python main.py
```

Server will start on `http://localhost:8000`

## Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "online",
  "service": "Agentic Honey-Pot API",
  "version": "1.0.0"
}
```

### Test 2: Scam Detection (Manual Test)

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secure-api-key-change-this" \
  -d '{
    "conversation_id": "test_001",
    "message": "Congratulations! You have won Rs 50,000. Please share your bank account number to claim the prize.",
    "history": []
  }'
```

### Test 3: Multi-turn Conversation

```bash
# First message
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "conversation_id": "test_002",
    "message": "Hello sir, this is from SBI bank. Your account has been blocked due to suspicious activity.",
    "history": []
  }'

# Second message (use response from agent)
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "conversation_id": "test_002",
    "message": "To unblock, please verify your account by sharing your account number and UPI ID.",
    "history": [
      {
        "role": "scammer",
        "content": "Hello sir, this is from SBI bank. Your account has been blocked.",
        "timestamp": "2024-01-01T10:00:00"
      },
      {
        "role": "agent",
        "content": "Oh no! What happened? How can I fix this?",
        "timestamp": "2024-01-01T10:00:05"
      }
    ]
  }'
```

## Expected Output Format

```json
{
  "conversation_id": "test_001",
  "scam_detected": true,
  "agent_activated": true,
  "response_message": "Oh really? That's amazing! What do I need to do to get the money?",
  "extracted_intelligence": {
    "bank_accounts": [],
    "ifsc_codes": [],
    "phone_numbers": [],
    "upi_ids": [],
    "emails": [],
    "urls": [],
    "pan_cards": [],
    "aadhaar_numbers": [],
    "bank_names": ["SBI"],
    "company_names": [],
    "scammer_claims": ["Claims lottery/prize win"],
    "extracted_count": 1
  },
  "engagement_metrics": {
    "total_turns": 2,
    "agent_turns": 1,
    "conversation_duration_seconds": 5,
    "intelligence_items_found": 1
  },
  "confidence_score": 0.85
}
```

## Connecting to Mock Scammer API

When you have the Mock Scammer API endpoint:

1. Provide your endpoint: `http://your-server:8000/detect`
2. Provide your API key (X-API-Key header)
3. The Mock Scammer will send requests in this format:

```json
{
  "conversation_id": "unique_id",
  "message": "scammer message here",
  "history": [...]
}
```

## Performance Optimization

### For 4GB GPU:

1. **Reduce context window:**
   - Edit `agent_engine.py`, line with `history[-4:]` → change to `history[-2:]`

2. **Use faster model:**
   ```bash
   ollama pull phi3:mini
   ```
   Then edit `config.py`:
   ```python
   OLLAMA_MODEL = "phi3:mini"
   ```

3. **Reduce num_predict:**
   - In `scam_detector.py` and `agent_engine.py`
   - Change `"num_predict": 150` → `"num_predict": 80`

## Troubleshooting

### Issue: Ollama timeout
**Solution:** Increase timeout in requests
```python
timeout=30  # Instead of timeout=15
```

### Issue: GPU out of memory
**Solution:** Use smaller model
```bash
ollama pull gemma2:2b
```

### Issue: Slow responses
**Solution:** Reduce context size and num_predict parameters

### Issue: Agent responses seem robotic
**Solution:** Increase temperature (0.7 → 0.9) in agent_engine.py

## Monitoring

Check conversation history:
```bash
curl -X GET http://localhost:8000/conversation/test_001 \
  -H "X-API-Key: your-api-key"
```

Delete conversation:
```bash
curl -X DELETE http://localhost:8000/conversation/test_001 \
  -H "X-API-Key: your-api-key"
```

## Production Deployment (Later)

You mentioned Docker deployment later, but here are quick tips:

1. Use environment variables for sensitive config
2. Add Redis for conversation storage
3. Add logging and monitoring
4. Use HTTPS with proper certificates
5. Rate limiting for API endpoints

## Key Features

✅ **Pattern-based + LLM detection** (hybrid approach)
✅ **Believable personas** (curious, eager, concerned, elderly)
✅ **Multi-turn conversations** with context
✅ **Intelligence extraction** (bank accounts, UPI, URLs, phone)
✅ **Engagement metrics** tracking
✅ **Configurable confidence thresholds**
✅ **Fallback responses** if LLM fails

## Next Steps

1. Test with your Mock Scammer API
2. Tune confidence thresholds based on results
3. Adjust personas and responses
4. Monitor extraction quality
5. Optimize for your specific use cases
