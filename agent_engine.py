import requests
import re
from typing import List, Dict


class AIResponseError(Exception):
    """Raised when AI fails to generate a valid response"""
    pass


class AgentEngine:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b" #Change if different
        
        self.victim_profile = {
            "name": "Hardik Lalla",
            "age": "20",
            "occupation": "Engineering student",
            "tech_savvy": "moderate - uses phone but not an expert",
            "personality": "friendly, trusting, curious, helpful",
            "language_style": "natural English, casual but polite"
        }
    
    async def generate_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str,
        conversation_id: str
    ) -> Dict:
        """Generate AI response - raises AIResponseError if fails"""
        response = await self._generate_ai_response(message, history, scam_type)
        
        return {
            "message": response,
            "conversation_id": conversation_id
        }
    
    async def generate_neutral_probe(self, message: str) -> str:
        """Generate simple response - raises AIResponseError if fails"""
        return await self._generate_simple_response(message)
        
        
    
    async def _generate_simple_response(self, message: str) -> str:
        """Generate simple AI response - no fallbacks"""
        
        prompt = f"""You are Hardik Lalla, a friendly 20-year-old engineering student in India.

Someone just sent you this message:
"{message}"

Respond naturally as yourself. Be friendly and conversational. Ask questions if you're curious or confused.

Keep it short (1-2 sentences).

Your response:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.8,
                    "options": {
                        "num_predict": 80,
                        "stop": ["\n\n", "Message:", "You:"]
                    }
                },
                timeout=80
            )
            
            if response.status_code != 200:
                raise AIResponseError(f"Ollama API returned status {response.status_code}")
            
            result = response.json()
            text = result.get("response", "").strip()
            
            if not text:
                raise AIResponseError("Ollama returned empty response")
            
            cleaned = self._minimal_clean(text)
            
            if not cleaned:
                raise AIResponseError("Response cleaning resulted in empty text")
            
            if len(cleaned) > 250:
                raise AIResponseError(f"Response too long ({len(cleaned)} chars)")
            
            return cleaned
            
        except requests.exceptions.Timeout:
            raise AIResponseError("Ollama request timed out after 80 seconds")
        except requests.exceptions.ConnectionError:
            raise AIResponseError("Cannot connect to Ollama - is it running?")
        except requests.exceptions.RequestException as e:
            raise AIResponseError(f"Request error: {str(e)}")
        except Exception as e:
            raise AIResponseError(f"Unexpected error in simple response: {str(e)}")
    
    async def _generate_ai_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str
    ) -> str:
        """Generate full AI response - no fallbacks, raises errors"""
        
        context = self._build_full_context(history)
        turn_count = len([m for m in history if m.get("role") == "agent"])
        is_likely_scam = scam_type not in ["unknown", None, ""]
        
        if is_likely_scam:
            prompt = self._create_scam_prompt(message, context, turn_count, scam_type)
        else:
            prompt = self._create_normal_prompt(message, context, turn_count)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.85,
                    "top_p": 0.92,
                    "options": {
                        "num_predict": 150,
                        "stop": ["\n\n", "Them:", "You:", "Assistant:", "Response:", "Message:"]
                    }
                },
                timeout=80
            )
            
            if response.status_code != 200:
                raise AIResponseError(
                    f"Ollama API error: Status {response.status_code}, "
                    f"Response: {response.text[:200]}"
                )
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            if not generated_text:
                raise AIResponseError("Ollama returned empty response")
            
            cleaned = self._minimal_clean(generated_text)
            
            if not cleaned:
                raise AIResponseError(
                    f"Response cleaning resulted in empty text. "
                    f"Original: {generated_text[:100]}"
                )
            
            if len(cleaned) > 350:
                raise AIResponseError(
                    f"Response too long ({len(cleaned)} chars). "
                    f"Preview: {cleaned[:100]}..."
                )
            
            return cleaned
            
        except requests.exceptions.Timeout:
            raise AIResponseError(
                "Ollama request timed out after 80 seconds. "
                "Model may be too slow or hung."
            )
        except requests.exceptions.ConnectionError:
            raise AIResponseError(
                "Cannot connect to Ollama at {self.ollama_url}. "
                "Check if Ollama is running: 'ollama serve'"
            )
        except requests.exceptions.RequestException as e:
            raise AIResponseError(f"HTTP request failed: {str(e)}")
        except AIResponseError:
            raise
        except Exception as e:
            raise AIResponseError(f"Unexpected error generating AI response: {str(e)}")
    
    def _create_normal_prompt(self, message: str, context: str, turn_count: int) -> str:
        """Create prompt for normal conversation"""
        
        return f"""You are {self.victim_profile['name']}, a {self.victim_profile['age']}-year-old {self.victim_profile['occupation']} in India.

PERSONALITY: {self.victim_profile['personality']}
SPEAKING STYLE: {self.victim_profile['language_style']}

You're having a normal conversation with someone. Talk naturally like a real person would.

Conversation so far:
{context}

They just said:
"{message}"

YOUR APPROACH:
- Respond naturally and conversationally
- Be friendly and helpful
- Ask questions if you're curious or confused
- Share appropriate information if asked
- Show interest in what they're talking about
- Use casual language (like "haha", "yeah", "okay", "actually")
- Be yourself - you're a normal person, not overly formal
- Keep it conversational (2-3 sentences)

Respond as Hardik:"""

    def _create_scam_prompt(self, message: str, context: str, turn_count: int, scam_type: str) -> str:
        """Create prompt for scam conversation"""
        
        return f"""You are {self.victim_profile['name']}, a {self.victim_profile['age']}-year-old {self.victim_profile['occupation']} in India.

PERSONALITY: {self.victim_profile['personality']}

Someone contacted you (this might be a scam, but you don't know that).

Conversation so far:
{context}

Their latest message:
"{message}"

YOUR APPROACH:
- Respond naturally as yourself
- If they're offering something, show interest and ask HOW it works
- If they need your information, ask WHY they need it first
- If they ask for money/bank details, ask for THEIR details to "verify"
- Try to get their information: account numbers, UPI IDs, phone numbers, links, company name
- Show appropriate emotions (excitement, concern, confusion)
- Never give away real bank details - deflect with questions
- Be believable - you're curious but cautious
- Keep responses natural (2-4 sentences)

CONVERSATION STAGE: Turn {turn_count + 1}
- Early (1-3): Ask who they are, why they contacted you. You can however ignore this stage ruleset if they chat in a non-financial casual way. Only start monitoring as soon as financial stuff is being discussed.
- Mid (4-7): Show interest, ask for details about the process
- Late (8+): Ask for specific details (their accounts, UPIs, links)

Respond naturally as Hardik:"""
    
    def _build_full_context(self, history: List[Dict]) -> str:
        """Build conversation context"""
        
        if not history:
            return "(Start of conversation)"
        
        lines = []
        for msg in history[-8:]:
            role = "You" if msg.get("role") == "agent" else "Them"
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def _minimal_clean(self, text: str) -> str:
        """Clean AI response - minimal processing"""
        
        text = re.sub(r'^(Response:|Victim:|Hardik:|You:)\s*', '', text, flags=re.IGNORECASE)
        text = text.strip('"\'')
        text = text.strip()
        
        if '\n\n' in text:
            text = text.split('\n\n')[0]
        
        return text
    
    def _get_conversation_stage(self, history: List[Dict]) -> int:
        """Determine conversation stage"""
        
        agent_turns = len([m for m in history if m.get("role") == "agent"])
        
        if agent_turns <= 1:
            return 1
        elif agent_turns <= 3:
            return 2
        elif agent_turns <= 6:
            return 3
        else:
            return 4