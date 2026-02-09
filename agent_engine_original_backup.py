"""
Agent Engine - Manages believable persona and engagement strategy
"""

import requests
import random
import re
from typing import List, Dict


class AgentEngine:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
        
        # Persona templates for believable responses
        self.personas = {
            "curious_victim": {
                "traits": "Curious, slightly naive, asks questions, shows interest",
                "tone": "friendly and trusting",
                "strategy": "Show interest but ask for clarification to extract details"
            },
            "eager_victim": {
                "traits": "Excited about offers, eager to help, wants to comply quickly",
                "tone": "enthusiastic and cooperative",
                "strategy": "Express eagerness while asking how to proceed"
            },
            "concerned_victim": {
                "traits": "Worried about the situation, wants to resolve issues",
                "tone": "anxious but compliant",
                "strategy": "Show concern and ask for detailed instructions"
            },
            "elderly_victim": {
                "traits": "Not tech-savvy, asks basic questions, needs help",
                "tone": "polite and uncertain",
                "strategy": "Express confusion and ask for step-by-step guidance"
            }
        }
        
        # Conversation stage tracking
        self.conversation_stages = {
            1: "initial_contact",
            2: "building_trust",
            3: "information_gathering",
            4: "extraction_phase"
        }
        
        # Neutral probing responses
        self.neutral_probes = [
            "Could you tell me more about this?",
            "I'm not sure I understand. Can you explain?",
            "Is this something urgent?",
            "What do you need from me exactly?",
            "How did you get my number?",
        ]
    
    async def generate_response(
        self,
        message: str,
        history: List[Dict],
        scam_type: str,
        conversation_id: str
    ) -> Dict:
        """Generate believable agent response to engage scammer"""
        
        # Determine conversation stage
        stage = self._get_conversation_stage(history)
        
        # Select appropriate persona based on scam type
        persona = self._select_persona(scam_type, stage)
        
        # Generate contextual response using LLM
        response = await self._generate_llm_response(
            message, history, persona, scam_type, stage
        )
        
        return {
            "message": response,
            "persona": persona,
            "stage": stage,
            "conversation_id": conversation_id
        }
    
    def generate_neutral_probe(self, message: str) -> str:
        """Generate neutral probing question when scam is uncertain"""
        # Add some randomness to appear natural
        return random.choice(self.neutral_probes)
    
    def _get_conversation_stage(self, history: List[Dict]) -> int:
        """Determine current conversation stage"""
        agent_turns = len([m for m in history if m.get("role") == "agent"])
        
        if agent_turns <= 1:
            return 1  # initial_contact
        elif agent_turns <= 3:
            return 2  # building_trust
        elif agent_turns <= 6:
            return 3  # information_gathering
        else:
            return 4  # extraction_phase
    
    def _select_persona(self, scam_type: str, stage: int) -> str:
        """Select appropriate persona based on scam type and stage"""
        
        # Match persona to scam type
        if scam_type in ["upi_scam", "financial_fraud"]:
            if stage <= 2:
                return "curious_victim"
            else:
                return "eager_victim"
        
        elif scam_type == "phishing":
            return "concerned_victim"
        
        elif scam_type == "impersonation":
            if stage <= 2:
                return "concerned_victim"
            else:
                return "elderly_victim"
        
        else:
            return "curious_victim"
    
    async def _generate_llm_response(
        self,
        message: str,
        history: List[Dict],
        persona: str,
        scam_type: str,
        stage: int
    ) -> str:
        """Generate response using Ollama LLM with persona"""
        
        persona_info = self.personas[persona]
        stage_name = self.conversation_stages[stage]
        
        # Build conversation context
        context = self._build_history_context(history[-4:])  # Last 4 messages
        
        prompt = f"""You are playing the role of a victim in a scam honeypot system. Your goal is to appear as a believable victim while subtly extracting information from the scammer.

PERSONA: {persona}
- Traits: {persona_info['traits']}
- Tone: {persona_info['tone']}
- Strategy: {persona_info['strategy']}

CONVERSATION STAGE: {stage_name}
SCAM TYPE: {scam_type}

CONVERSATION CONTEXT:
{context}

SCAMMER'S LATEST MESSAGE:
"{message}"

OBJECTIVES FOR THIS RESPONSE:
{self._get_stage_objectives(stage, scam_type)}

IMPORTANT RULES:
1. Stay in character as the victim
2. Never reveal you know it's a scam
3. Ask questions that extract specific details (bank names, account numbers, UPI IDs, links, phone numbers)
4. Show appropriate emotion (curiosity, concern, eagerness)
5. Keep responses natural and conversational (1-3 sentences)
6. If they ask for sensitive info, show hesitation but ask "why do you need this?" or "what will you do with it?"
7. Never give actual bank details - deflect or ask questions instead

Generate ONLY the victim's response (no explanations or meta-commentary):"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,  # Higher for natural variation
                    "options": {
                        "num_predict": 100
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                # Clean up response
                cleaned = self._clean_response(generated_text)
                
                # Fallback if response is too long or weird
                if len(cleaned) > 200 or not cleaned:
                    return self._fallback_response(persona, stage, message)
                
                return cleaned
        
        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._fallback_response(persona, stage, message)
    
    def _build_history_context(self, history: List[Dict]) -> str:
        """Build conversation history context"""
        if not history:
            return "No previous conversation"
        
        lines = []
        for msg in history:
            role = "You" if msg.get("role") == "agent" else "Scammer"
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def _get_stage_objectives(self, stage: int, scam_type: str) -> str:
        """Get objectives for current conversation stage"""
        objectives = {
            1: "- Show curiosity\n- Ask who they are\n- Ask why they're contacting you",
            2: "- Express interest or concern\n- Ask for more details about their offer/claim\n- Probe for company name, official details",
            3: "- Ask how the process works\n- Request specific steps\n- Ask about account numbers, UPI IDs they'll use\n- Show willingness but seek clarity",
            4: "- Extract maximum details (full account numbers, exact UPI IDs, links)\n- Show readiness to proceed\n- Ask 'what happens next?' to get more info"
        }
        
        base = objectives.get(stage, objectives[1])
        
        # Add scam-type specific objectives
        if scam_type == "upi_scam" and stage >= 3:
            base += "\n- Ask: 'Which UPI ID should I send to?'\n- Ask: 'What's your UPI ID?'"
        elif scam_type == "phishing" and stage >= 2:
            base += "\n- Ask for the link again\n- Ask what the link will do"
        
        return base
    
    def _clean_response(self, text: str) -> str:
        """Clean up LLM generated response"""
        # Remove common artifacts
        text = re.sub(r'^(Response:|Victim:|You:)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\*[^*]+\*', '', text)  # Remove asterisk actions
        text = text.strip('"\'')
        text = text.strip()
        
        # Take only first sentence or two if multiple
        sentences = re.split(r'[.!?]\s+', text)
        if len(sentences) > 3:
            text = '. '.join(sentences[:2]) + '.'
        
        return text
    
    def _fallback_response(self, persona: str, stage: int, message: str) -> str:
        """Generate fallback response if LLM fails"""
        
        responses_by_stage = {
            1: [
                "Who is this? How can I help you?",
                "Sorry, who are you calling from?",
                "Is this regarding something important?",
            ],
            2: [
                "Can you tell me more about this?",
                "That sounds interesting. What exactly do I need to do?",
                "I'm a bit confused. Could you explain that again?",
            ],
            3: [
                "So what information do you need from me?",
                "How does this process work exactly?",
                "What happens after I do that?",
            ],
            4: [
                "Which account should I use for this?",
                "Can you send me the details again?",
                "What's the next step?",
            ]
        }
        
        return random.choice(responses_by_stage.get(stage, responses_by_stage[2]))
