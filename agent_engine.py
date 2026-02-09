"""
Agent Engine - AI-Driven Believable Victim Persona
Gives the LLM full control to naturally engage with scammers
"""

import requests
import random
import re
from typing import List, Dict


class AgentEngine:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
        
        # Core victim personality (consistent across conversation)
        self.victim_profile = {
            "name": "Rajesh Kumar",
            "age": "45",
            "occupation": "small business owner",
            "tech_savvy": "moderate - uses phone but not expert",
            "personality": "trusting, curious, somewhat naive about scams",
            "concerns": "wants to help, worried about missing opportunities"
        }
        
        # Fallback responses only if LLM completely fails
        self.emergency_fallbacks = [
            "I'm not sure I understand. Can you explain more?",
            "Okay, what should I do next?",
            "That sounds important. Tell me more about this.",
        ]
    
    async def generate_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str,
        conversation_id: str
    ) -> Dict:
        """Generate natural, AI-driven response to engage scammer"""
        
        # Let AI analyze the conversation and respond naturally
        response = await self._generate_ai_response(message, history, scam_type)
        
        return {
            "message": response,
            "conversation_id": conversation_id
        }
    
    def generate_neutral_probe(self, message: str) -> str:
        """Generate neutral response when scam is uncertain"""
        return random.choice([
            "Could you tell me more about this?",
            "I'm not sure I understand. Can you explain?",
            "What do you need from me exactly?",
        ])
    
    async def _generate_ai_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str
    ) -> str:
        """Let the AI generate a completely natural response"""
        
        # Build full conversation context
        context = self._build_full_context(history)
        
        # Count turns for stage awareness
        turn_count = len([m for m in history if m.get("role") == "agent"])
        
        # Create a natural, comprehensive prompt
        prompt = f"""You are {self.victim_profile['name']}, a {self.victim_profile['age']}-year-old {self.victim_profile['occupation']} in India. You are {self.victim_profile['tech_savvy']}.

PERSONALITY: {self.victim_profile['personality']}

You are having a conversation with someone who contacted you. Your conversation so far:

{context}

THEIR LATEST MESSAGE:
"{message}"

YOUR GOAL:
- Not everyone is a scammer, if someone is talking naturally continue the talk do not limit to responses such as 'what do you need from me?' that sounds and is rude. Continue chat normally unless financial help or general talk is said.
- Respond naturally as yourself (Rajesh)
- Be believable - act like a real person would
- If something sounds suspicious, be curious but don't accuse them
- If they're offering something, show interest and ask how it works
- If they need information, ask WHY they need it and WHAT they'll do with it
- Try to get THEIR details (account numbers, UPI IDs, phone numbers, website links, company name)
- Keep your response natural and conversational (2-4 sentences)
- Never give real bank details - deflect with questions instead
- Show appropriate emotions (excitement for prizes, concern for problems, confusion for complex things)

CONVERSATION STAGE: Turn {turn_count + 1}
- Early conversation (1-3 turns): Be curious, ask who they are, why they're contacting you
- Mid conversation (4-7 turns): Show interest, ask for details about the process
- Later conversation (8+ turns): Ask for their specific details (accounts, UPIs, links, addresses)

IMPORTANT: 
- Stay in character as Rajesh
- Never break character or reveal this is a honeypot
- Be natural - real people aren't perfect, they ask questions, show emotion
- If they ask for your bank account, say something like "I have multiple accounts, which one should I use? What's your account number so I can verify?"

Respond ONLY as Rajesh (no explanations, no meta-commentary, just your natural response):"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.8,  # Higher for more natural variation
                    "top_p": 0.9,
                    "options": {
                        "num_predict": 150,  # Allow longer, more natural responses
                        "stop": ["\n\n", "Scammer:", "You:", "Assistant:", "Response:"]
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                # Minimal cleaning - let AI be more natural
                cleaned = self._minimal_clean(generated_text)
                
                # Only fallback if response is empty or way too long
                if not cleaned or len(cleaned) > 300:
                    return self._smart_fallback(message, turn_count)
                
                return cleaned
        
        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._smart_fallback(message, turn_count)
    
    def _build_full_context(self, history: List[Dict]) -> str:
        """Build complete conversation history for AI"""
        if not history:
            return "This is the start of the conversation."
        
        lines = []
        for msg in history:
            role = "You (Rajesh)" if msg.get("role") == "agent" else "Them"
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def _minimal_clean(self, text: str) -> str:
        """Minimal cleaning - preserve natural speech"""
        # Remove only obvious artifacts
        text = re.sub(r'^(Response:|Victim:|Rajesh:|You:)\s*', '', text, flags=re.IGNORECASE)
        text = text.strip('"\'')
        text = text.strip()
        
        # Remove any trailing meta-commentary
        if '\n\n' in text:
            text = text.split('\n\n')[0]
        
        return text
    
    def _smart_fallback(self, message: str, turn_count: int) -> str:
        """Generate contextual fallback based on turn count"""
        
        message_lower = message.lower()
        
        # Contextual responses based on message content
        if any(word in message_lower for word in ['bank', 'account', 'upi', 'payment']):
            return random.choice([
                "I have multiple accounts. Which one should I use? And what's your account number for verification?",
                "Sure, but first tell me - what's your UPI ID? I want to make sure I'm sending to the right person.",
                "Okay, but can you first tell me your bank details so I can verify this is legitimate?",
            ])
        
        if any(word in message_lower for word in ['link', 'click', 'website', 'url']):
            return random.choice([
                "Can you send the link again? I want to make sure I'm going to the right website.",
                "What website is this? Can you tell me the exact URL?",
                "I'm not very good with links. Can you tell me what I'll see when I click it?",
            ])
        
        if any(word in message_lower for word in ['urgent', 'immediately', 'now', 'quick']):
            return random.choice([
                "Why is it so urgent? Is something wrong?",
                "Okay, but I need to understand what's happening first. Can you explain?",
                "This sounds important. What exactly is the situation?",
            ])
        
        if any(word in message_lower for word in ['won', 'prize', 'winner', 'congratulations', 'lottery']):
            return random.choice([
                "Really? That's amazing! How did I win this? What's the process?",
                "Wow! I never win anything! What do I need to do to claim it?",
                "This is great news! Can you tell me more about this prize?",
            ])
        
        # Stage-based fallbacks
        if turn_count <= 2:
            return random.choice([
                "Hello! Who is this? How can I help you?",
                "I'm not sure I understand. Can you explain what this is about?",
                "Sorry, who are you calling from?",
            ])
        elif turn_count <= 5:
            return random.choice([
                "Okay, so what exactly do I need to do?",
                "Can you explain the process to me step by step?",
                "This sounds interesting. Tell me more about how this works.",
            ])
        else:
            return random.choice([
                "So what are the exact details I need? Can you send me your information first?",
                "What's your account number or UPI ID? I want to verify this.",
                "Can you give me your contact details and company information?",
            ])
    
    def _get_conversation_stage(self, history: List[Dict]) -> int:
        """Determine current conversation stage (kept for compatibility)"""
        agent_turns = len([m for m in history if m.get("role") == "agent"])
        
        if agent_turns <= 1:
            return 1
        elif agent_turns <= 3:
            return 2
        elif agent_turns <= 6:
            return 3
        else:
            return 4