import re
from typing import List, Dict
import requests
import json


class ScamDetector:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"  #Change to whatever model you are using
        self.scam_patterns = {
            "financial": [
                "bank account", "account number", "routing number",
                "credit card", "debit card", "cvv", "pin",
                "transfer money", "send money", "payment",
                "refund", "cashback", "prize", "lottery"
            ],
            "urgent": [
                "urgent", "immediately", "right now", "asap",
                "account blocked", "account suspended", "verify now",
                "expires today", "limited time"
            ],
            "upi": [
                "upi", "upi id", "paytm", "phonepe", "gpay",
                "google pay", "bhim", "@paytm", "@oksbi", "@ybl"
            ],
            "phishing": [
                "click here", "verify your account", "confirm your identity",
                "update your information", "security alert",
                "suspicious activity", "click link", "reset password"
            ],
            "impersonation": [
                "government official", "tax department", "police",
                "bank manager", "customer service", "tech support",
                "amazon", "flipkart", "irs", "income tax"
            ]
        }
    
    async def analyze(self, message: str, history: List[Dict]) -> Dict:
        message_lower = message.lower()
        
        pattern_score = self._pattern_match(message_lower)
        
        llm_analysis = await self._llm_analyze(message, history)
        
        is_scam = pattern_score > 0.3 or llm_analysis["is_scam"]
        confidence = max(pattern_score, llm_analysis["confidence"])
        
        return {
            "is_scam": is_scam,
            "confidence": confidence,
            "scam_type": self._determine_scam_type(message_lower),
            "pattern_score": pattern_score,
            "llm_score": llm_analysis["confidence"],
            "reasoning": llm_analysis.get("reasoning", "")
        }
    
    def _pattern_match(self, message: str) -> float:
        score = 0.0
        matches = 0
        
        for category, patterns in self.scam_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    matches += 1
                    if category == "financial":
                        score += 0.3
                    elif category == "urgent":
                        score += 0.2
                    elif category == "upi":
                        score += 0.3
                    elif category == "phishing":
                        score += 0.25
                    elif category == "impersonation":
                        score += 0.2
        
        if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message):
            score += 0.3
        
        if re.search(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', message):
            score += 0.15
        
        return min(score, 1.0)  
    
    async def _llm_analyze(self, message: str, history: List[Dict]) -> Dict:
        context = self._build_context(history)
        
        prompt = f"""You are a scam detection expert. Analyze the following message and conversation context to determine if it's a scam attempt. REMEMBER NOT ALL ARE SCAMMERS AND COULD BE YOUR FRIEND OR RELATIVES, ALSO TALK LIKE A HUMAN WITH BELIEVABLE PERSONA DITCH THE PROPER PUNCTUATIONS.

Conversation Context:
{context}

Current Message:
"{message}"

Common scam indicators:
- Requests for financial information (bank account, UPI ID, card details)
- Creates urgency or fear (inspect or talk more to determine its genuineness)
- Impersonates authority (bank, government, company)
- Offers unrealistic rewards
- Contains phishing links
- Asks to bypass normal procedures

Respond in JSON format:
{{
    "is_scam": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

JSON Response:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "options": {
                        "num_predict": 150
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "{}")
                
                analysis = self._extract_json(response_text)
                
                return {
                    "is_scam": analysis.get("is_scam", False),
                    "confidence": analysis.get("confidence", 0.5),
                    "reasoning": analysis.get("reasoning", "")
                }
            
        except Exception as e:
            print(f"LLM analysis error: {e}")
        return {
            "is_scam": False,
            "confidence": 0.5,
            "reasoning": "LLM analysis unavailable"
        }
    
    def _build_context(self, history: List[Dict]) -> str:
        if not history:
            return "No previous context"
        
        recent = history[-3:]
        context_lines = []
        
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def _extract_json(self, text: str) -> Dict:
        try:
            json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        is_scam = "true" in text.lower() and "is_scam" in text.lower()
        
        confidence_match = re.search(r'"confidence":\s*(0\.\d+|1\.0)', text)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5
        
        return {
            "is_scam": is_scam,
            "confidence": confidence,
            "reasoning": "Parsed from text"
        }
    
    def _determine_scam_type(self, message: str) -> str:
        if any(p in message for p in self.scam_patterns["upi"]):
            return "upi_scam"
        elif any(p in message for p in self.scam_patterns["phishing"]):
            return "phishing"
        elif any(p in message for p in self.scam_patterns["impersonation"]):
            return "impersonation"
        elif any(p in message for p in self.scam_patterns["financial"]):
            return "financial_fraud"
        else:
            return "unknown"
