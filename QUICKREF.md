# Quick Reference Guide

## File Structure
```
honeypot_system/
├── main.py                      # FastAPI server (entry point)
├── scam_detector.py             # Scam detection logic
├── agent_engine.py              # Persona & response generation
├── intelligence_extractor.py    # Extract scam data
├── config.py                    # Configuration
├── requirements.txt             # Python dependencies
├── start.sh                     # Startup script
├── test_system.py              # Test suite
├── README.md                    # Full documentation
└── SETUP.md                     # Setup instructions
```

## Commands Cheat Sheet

### Initial Setup
```bash
# 1. Start Ollama
ollama serve

# 2. Pull model (in another terminal)
ollama pull llama3.2:3b

# 3. Install dependencies
cd honeypot_system
pip install -r requirements.txt

# 4. Edit config
nano config.py  # Change API_KEY

# 5. Start server
python main.py
# OR
./start.sh
```

### Testing
```bash
# Health check
curl http://localhost:8000/

# Run full test suite
python test_system.py

# Manual test
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"conversation_id":"test","message":"Won lottery!","history":[]}'
```

### Model Management
```bash
# List models
ollama list

# Pull different model (if needed)
ollama pull phi3:mini      # Faster
ollama pull gemma2:2b      # Smallest
ollama pull llama3.2:7b    # More accurate (needs >4GB)

# Remove model
ollama rm llama3.2:3b
```

## Key Configuration Points

### config.py
```python
API_KEY = "change-this-to-something-secure"
OLLAMA_MODEL = "llama3.2:3b"
SCAM_CONFIDENCE_THRESHOLD = 0.6  # 0.0-1.0
```

### For Faster Responses
```python
# In agent_engine.py and scam_detector.py
"num_predict": 80  # Lower = faster (default is 150)
```

### For More Natural Responses
```python
# In agent_engine.py, line ~140
temperature=0.9  # Higher = more creative (default is 0.7)
```

## API Response Format

```json
{
  "conversation_id": "string",
  "scam_detected": true/false,
  "agent_activated": true/false,
  "response_message": "Agent's response",
  "extracted_intelligence": {
    "bank_accounts": ["..."],
    "upi_ids": ["..."],
    "phone_numbers": ["..."],
    "urls": ["..."],
    "extracted_count": 0
  },
  "engagement_metrics": {
    "total_turns": 0,
    "agent_turns": 0,
    "conversation_duration_seconds": 0,
    "intelligence_items_found": 0
  },
  "confidence_score": 0.0-1.0
}
```

## Persona Behavior

| Persona | Tone | Example Response |
|---------|------|------------------|
| Curious Victim | Friendly, questioning | "That sounds interesting! Can you tell me more about how this works?" |
| Eager Victim | Enthusiastic, ready | "Yes, I want to proceed! What should I do next?" |
| Concerned Victim | Worried, compliant | "Oh no! Is my account really in danger? What do I need to do to fix it?" |
| Elderly Victim | Confused, polite | "I'm not very good with these things. Can you explain it step by step?" |

## Conversation Stages

1. **Initial Contact** (Turns 1-2): Establish who they are
2. **Building Trust** (Turns 3-4): Show interest/concern
3. **Information Gathering** (Turns 5-7): Ask detailed questions
4. **Extraction Phase** (Turns 8+): Get specific data

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Connection refused" | Start Ollama: `ollama serve` |
| "Model not found" | Pull model: `ollama pull llama3.2:3b` |
| "401 Unauthorized" | Check API_KEY matches in config.py and request |
| Slow responses | Reduce num_predict or use faster model |
| Out of memory | Use smaller model: `ollama pull gemma2:2b` |
| Responses too robotic | Increase temperature to 0.8-0.9 |
| Too many false positives | Increase SCAM_CONFIDENCE_THRESHOLD to 0.7 |

## Performance Benchmarks (4GB GPU)

### llama3.2:3b
- Response time: 3-8 seconds
- Memory: ~3.5GB
- Quality: ⭐⭐⭐⭐ (Recommended)

### phi3:mini
- Response time: 2-5 seconds
- Memory: ~2GB
- Quality: ⭐⭐⭐

### gemma2:2b
- Response time: 1-3 seconds
- Memory: ~1.5GB
- Quality: ⭐⭐

## Intelligence Extraction Patterns

The system automatically detects:
- Bank accounts: 9-18 digit numbers
- UPI IDs: username@paytm, @ybl, @oksbi, etc.
- Phone: +91-XXXXXXXXXX or 10-digit Indian numbers
- URLs: Any http/https links
- IFSC: ABCD0123456 format
- Email: standard email format

## Production Checklist

- [ ] Change default API_KEY in config.py
- [ ] Use environment variables instead of hardcoded config
- [ ] Add Redis for conversation storage
- [ ] Implement rate limiting
- [ ] Add HTTPS/SSL certificate
- [ ] Set up logging and monitoring
- [ ] Create backup strategy
- [ ] Test with Mock Scammer API
- [ ] Deploy to server with GPU
- [ ] Configure firewall rules

## Next Steps

1. **Test locally**: Run `python test_system.py`
2. **Integrate with Mock Scammer API**: Provide your endpoint URL
3. **Monitor performance**: Check logs for response times
4. **Tune parameters**: Adjust confidence threshold and personas
5. **Optimize**: Based on evaluation metrics

## Support

- Check README.md for full documentation
- Check SETUP.md for detailed setup guide
- Run test_system.py to verify everything works
- Check Ollama logs: `journalctl -u ollama -f` (Linux)
