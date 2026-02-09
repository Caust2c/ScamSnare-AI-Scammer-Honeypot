"""
Intelligence Database - Stores extracted scam intelligence
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class IntelligenceDB:
    def __init__(self, db_file="intelligence_db.json"):
        self.db_file = db_file
        self.db_path = Path(db_file)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not self.db_path.exists():
            initial_data = {
                "conversations": {},
                "all_intelligence": {
                    "bank_accounts": [],
                    "upi_ids": [],
                    "phone_numbers": [],
                    "urls": [],
                    "ifsc_codes": [],
                    "emails": [],
                    "pan_cards": [],
                    "aadhaar_numbers": []
                },
                "statistics": {
                    "total_conversations": 0,
                    "total_scams_detected": 0,
                    "total_intelligence_items": 0,
                    "last_updated": datetime.now().isoformat()
                }
            }
            self._write_db(initial_data)
    
    def _read_db(self) -> Dict:
        """Read database from file"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading database: {e}")
            return {}
    
    def _write_db(self, data: Dict):
        """Write database to file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing database: {e}")
    
    def save_conversation(
        self,
        conversation_id: str,
        scam_detected: bool,
        confidence: float,
        intelligence: Dict,
        messages: List[Dict],
        metrics: Dict
    ):
        """Save a conversation and its extracted intelligence"""
        db = self._read_db()
        
        # Save conversation details
        db["conversations"][conversation_id] = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "scam_detected": scam_detected,
            "confidence_score": confidence,
            "total_turns": metrics.get("total_turns", 0),
            "intelligence_extracted": intelligence,
            "message_count": len(messages),
            "metrics": metrics
        }
        
        # Aggregate intelligence (remove duplicates)
        for key in ["bank_accounts", "upi_ids", "phone_numbers", "urls", 
                    "ifsc_codes", "emails", "pan_cards", "aadhaar_numbers"]:
            if key in intelligence and intelligence[key]:
                existing = set(db["all_intelligence"][key])
                new_items = set(intelligence[key])
                db["all_intelligence"][key] = list(existing | new_items)
        
        # Update statistics
        db["statistics"]["total_conversations"] = len(db["conversations"])
        db["statistics"]["total_scams_detected"] = sum(
            1 for conv in db["conversations"].values() 
            if conv.get("scam_detected", False)
        )
        db["statistics"]["total_intelligence_items"] = sum(
            len(items) for items in db["all_intelligence"].values()
        )
        db["statistics"]["last_updated"] = datetime.now().isoformat()
        
        self._write_db(db)
    
    def get_all_intelligence(self) -> Dict:
        """Get all extracted intelligence"""
        db = self._read_db()
        return db.get("all_intelligence", {})
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        db = self._read_db()
        return db.get("statistics", {})
    
    def get_conversations(self, limit: int = 50) -> List[Dict]:
        """Get recent conversations"""
        db = self._read_db()
        conversations = list(db.get("conversations", {}).values())
        # Sort by timestamp, most recent first
        conversations.sort(
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        return conversations[:limit]
    
    def get_conversation(self, conversation_id: str) -> Dict:
        """Get a specific conversation"""
        db = self._read_db()
        return db.get("conversations", {}).get(conversation_id, {})
    
    def export_intelligence(self, output_file: str = "intelligence_export.json"):
        """Export all intelligence to a file"""
        db = self._read_db()
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "statistics": db.get("statistics", {}),
            "all_intelligence": db.get("all_intelligence", {}),
            "conversations": list(db.get("conversations", {}).values())
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_file
    
    def clear_database(self):
        """Clear all data (use with caution!)"""
        self._ensure_db_exists()
    
    def get_high_value_intelligence(self) -> Dict:
        """Get only high-value intelligence (bank accounts, UPIs, etc.)"""
        all_intel = self.get_all_intelligence()
        
        return {
            "bank_accounts": all_intel.get("bank_accounts", []),
            "upi_ids": all_intel.get("upi_ids", []),
            "phone_numbers": all_intel.get("phone_numbers", []),
            "urls": all_intel.get("urls", []),
            "ifsc_codes": all_intel.get("ifsc_codes", []),
            "count": (
                len(all_intel.get("bank_accounts", [])) +
                len(all_intel.get("upi_ids", [])) +
                len(all_intel.get("phone_numbers", [])) +
                len(all_intel.get("urls", []))
            )
        }
