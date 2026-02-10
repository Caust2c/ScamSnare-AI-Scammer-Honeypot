from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import json

from scam_detector import ScamDetector
from agent_engine import AgentEngine
from intelligence_extractor import IntelligenceExtractor
from intelligence_db import IntelligenceDB
from config import API_KEY

app = FastAPI(title="Agentic Honey-Pot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scam_detector = ScamDetector()
agent_engine = AgentEngine()
intelligence_extractor = IntelligenceExtractor()
intelligence_db = IntelligenceDB()  
conversation_store: Dict[str, List[Dict]] = {}


class Message(BaseModel):
    conversation_id: str
    sender: str 
    message: str
    timestamp: Optional[str] = None


class IncomingRequest(BaseModel):
    conversation_id: str
    message: str
    history: Optional[List[Dict]] = []


class ResponseOutput(BaseModel):
    conversation_id: str
    scam_detected: bool
    agent_activated: bool
    response_message: str
    extracted_intelligence: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    confidence_score: float


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Agentic Honey-Pot API",
        "version": "1.0.0"
    }


@app.post("/detect", response_model=ResponseOutput)
async def detect_and_engage(
    request: IncomingRequest,
    x_api_key: str = Header(..., alias="X-API-Key")
):
  
    verify_api_key(x_api_key)
    
    conversation_id = request.conversation_id
    incoming_message = request.message
    history = request.history or []
    
    if conversation_id not in conversation_store:
        conversation_store[conversation_id] = []
    
    conversation_store[conversation_id].append({
        "role": "scammer",
        "content": incoming_message,
        "timestamp": datetime.now().isoformat()
    })
    
    full_history = conversation_store[conversation_id]
    
    scam_result = await scam_detector.analyze(incoming_message, full_history)
    
    scam_detected = scam_result["is_scam"]
    confidence = scam_result["confidence"]
    scam_type = scam_result.get("scam_type", "unknown")
    
    if scam_detected and confidence > 0.6:

        agent_response = await agent_engine.generate_response(
            message=incoming_message,
            history=full_history,
            scam_type=scam_type,
            conversation_id=conversation_id
        )
        
        response_message = agent_response["message"]
        agent_activated = True
        
        conversation_store[conversation_id].append({
            "role": "agent",
            "content": response_message,
            "timestamp": datetime.now().isoformat()
        })
        
    else:
        response_message = agent_engine.generate_neutral_probe(incoming_message)
        agent_activated = False
        
        conversation_store[conversation_id].append({
            "role": "agent",
            "content": response_message,
            "timestamp": datetime.now().isoformat()
        })
    
    extracted_intel = intelligence_extractor.extract(
        full_history,
        incoming_message
    )
    
    engagement_metrics = {
        "total_turns": len(full_history),
        "agent_turns": len([m for m in full_history if m.get("role") == "agent"]),
        "conversation_duration_seconds": calculate_duration(full_history),
        "intelligence_items_found": len([v for v in extracted_intel.values() if v])
    }
    
    intelligence_db.save_conversation(
        conversation_id=conversation_id,
        scam_detected=scam_detected,
        confidence=confidence,
        intelligence=extracted_intel,
        messages=full_history,
        metrics=engagement_metrics
    )
    
    return ResponseOutput(
        conversation_id=conversation_id,
        scam_detected=scam_detected,
        agent_activated=agent_activated,
        response_message=response_message,
        extracted_intelligence=extracted_intel,
        engagement_metrics=engagement_metrics,
        confidence_score=confidence
    )


def calculate_duration(history: List[Dict]) -> int:
    if len(history) < 2:
        return 0
    
    try:
        first = datetime.fromisoformat(history[0]["timestamp"])
        last = datetime.fromisoformat(history[-1]["timestamp"])
        return int((last - first).total_seconds())
    except:
        return 0


@app.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    
    if conversation_id not in conversation_store:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "history": conversation_store[conversation_id]
    }


@app.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    
    if conversation_id in conversation_store:
        del conversation_store[conversation_id]
        return {"status": "deleted", "conversation_id": conversation_id}
    
    raise HTTPException(status_code=404, detail="Conversation not found")


@app.get("/intelligence/all")
async def get_all_intelligence(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    return intelligence_db.get_all_intelligence()


@app.get("/intelligence/stats")
async def get_intelligence_stats(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    return intelligence_db.get_statistics()


@app.get("/intelligence/high-value")
async def get_high_value_intelligence(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    return intelligence_db.get_high_value_intelligence()


@app.get("/intelligence/conversations")
async def get_all_conversations(
    limit: int = 50,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    return intelligence_db.get_conversations(limit=limit)


@app.get("/intelligence/export")
async def export_intelligence(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(x_api_key)
    filename = intelligence_db.export_intelligence()
    return {"status": "exported", "filename": filename}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
