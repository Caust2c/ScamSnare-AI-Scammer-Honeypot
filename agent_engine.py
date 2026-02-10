import requests
import random
import re
from typing import List, Dict


class AgentEngine:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
        #Enter your own type of personality here
        self.victim_profile = {
            "name": "Rajesh Kumar",
            "age": "45",
            "occupation": "small business owner",
            "tech_savvy": "moderate - uses phone but not expert",
            "personality": "friendly, trusting, curious, helpful",
            "language_style": "natural Indian English, casual but polite"
        }
    
    async def generate_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str,
        conversation_id: str
    ) -> Dict:
        response = await self._generate_ai_response(message, history, scam_type)
        
        return {
            "message": response,
            "conversation_id": conversation_id
        }
    
    def generate_neutral_probe(self, message: str) -> str:
        """
        DEPRECATED
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(
                self._generate_simple_response(message)
            )
            return response
        except:
            return self._contextual_fallback(message, 1)
    
    async def _generate_simple_response(self, message: str) -> str:
        prompt = f"""You are Rajesh Kumar, a friendly 45-year-old small business owner in India.

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
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                text = self._minimal_clean(text)
                
                if text and len(text) < 250:
                    return text
        except Exception as e:
            print(f"AI error in simple response: {e}")
        
        return self._contextual_fallback(message, 1)
    
    async def _generate_ai_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str
    ) -> str:
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
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                cleaned = self._minimal_clean(generated_text)
                
                if cleaned and len(cleaned) < 350:
                    return cleaned
        
        except Exception as e:
            print(f"LLM generation error: {e}")
        
        # Fallback
        return self._contextual_fallback(message, turn_count)
    
    def _create_normal_prompt(self, message: str, context: str, turn_count: int) -> str:
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

Respond as Rajesh:"""

    def _create_scam_prompt(self, message: str, context: str, turn_count: int, scam_type: str) -> str:
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
- Early (1-3): Ask who they are, why they contacted you
- Mid (4-7): Show interest, ask for details about the process
- Late (8+): Ask for specific details (their accounts, UPIs, links)

Respond naturally as Rajesh:"""
    
    def _build_full_context(self, history: List[Dict]) -> str:
        if not history:
            return "(Start of conversation)"
        
        lines = []
        for msg in history[-8:]: 
            role = "You" if msg.get("role") == "agent" else "Them"
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def _minimal_clean(self, text: str) -> str:
        text = re.sub(r'^(Response:|Victim:|Rajesh:|You:)\s*', '', text, flags=re.IGNORECASE)
        text = text.strip('"\'')
        text = text.strip()
        
        if '\n\n' in text:
            text = text.split('\n\n')[0]
        
        return text
    
    def _contextual_fallback(self, message: str, turn_count: int) -> str:
        
        msg = message.lower()
        
        if any(w in msg for w in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return random.choice([
                "Hello! How can I help you?",
                "Hi there! What's this about?",
                "Hey! Who is this?"
            ])
        
        if '?' in message and not any(w in msg for w in ['bank', 'account', 'money', 'upi']):
            return random.choice([
                "That's an interesting question. What made you think of that?",
                "Hmm, let me think about that. Why do you ask?",
                "Good question! What's your take on it?"
            ])
        
        if any(w in msg for w in ['bank', 'account', 'upi', 'payment', 'money']):
            return "I have multiple accounts. Which one? And what's your account number so I can verify?"
        
        if any(w in msg for w in ['won', 'prize', 'winner', 'congratulations', 'offer']):
            return "Really? That sounds great! How does this work exactly?"
        
        if any(w in msg for w in ['urgent', 'immediately', 'blocked', 'problem']):
            return "Oh! What happened? Can you explain what's going on?"
        
        if any(w in msg for w in ['link', 'click', 'website', 'url']):
            return "What link? Can you send it again? What website is it?"
        
        if turn_count <= 2:
            return random.choice([
                "I'm not sure I follow. Can you explain a bit more?",
                "Interesting! Tell me more about this.",
                "Okay, I'm listening. What's this about?"
            ])
        elif turn_count <= 5:
            return random.choice([
                "Alright, so what do I need to do exactly?",
                "Got it. What's the next step?",
                "Okay, can you walk me through the process?"
            ])
        else:
            return random.choice([
                "Can you give me your details so I can verify this?",
                "What's your contact information?",
                "Send me your account details first."
            ])
    
    def _get_conversation_stage(self, history: List[Dict]) -> int:
        agent_turns = len([m for m in history if m.get("role") == "agent"])
        
        if agent_turns <= 1:
            return 1
        elif agent_turns <= 3:
            return 2
        elif agent_turns <= 6:
            return 3
        else:
            return 4