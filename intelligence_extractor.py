import re
from typing import List, Dict, Set


class IntelligenceExtractor:
    def __init__(self):
        self.patterns = {
            "bank_account": r'\b\d{9,18}\b',  # 9-18 digit account numbers
            "ifsc_code": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',  # Indian IFSC codes
            "phone": r'\b(?:\+91[-.\s]?)?[6-9]\d{9}\b',  # Indian phone numbers
            "upi_id": r'\b[\w.-]+@(?:paytm|oksbi|okhdfcbank|okaxis|okicici|ybl|ibl|axl)\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "pan_card": r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            "aadhaar": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        self.upi_handles = [
            "@paytm", "@oksbi", "@ybl", "@okicici", "@okaxis",
            "@okhdfcbank", "@ibl", "@axl", "@fbl", "@upi"
        ]
        
        self.bank_names = [
            "sbi", "hdfc", "icici", "axis", "kotak", "pnb",
            "canara", "bank of baroda", "union bank", "idbi"
        ]
    
    def extract(self, history: List[Dict], current_message: str) -> Dict:
        all_text = current_message + " "
        for msg in history:
            all_text += msg.get("content", "") + " "
        
        all_text = all_text.lower()
        
        intelligence = {
            "bank_accounts": self._extract_unique(all_text, "bank_account"),
            "ifsc_codes": self._extract_unique(all_text, "ifsc_code"),
            "phone_numbers": self._extract_unique(all_text, "phone"),
            "upi_ids": self._extract_unique(all_text, "upi_id"),
            "emails": self._extract_unique(all_text, "email"),
            "urls": self._extract_unique(all_text, "url"),
            "pan_cards": self._extract_unique(all_text, "pan_card"),
            "aadhaar_numbers": self._extract_unique(all_text, "aadhaar"),
            "bank_names": self._extract_bank_names(all_text),
            "company_names": self._extract_company_names(all_text),
            "scammer_claims": self._extract_claims(history),
            "extracted_count": 0
        }
        intelligence["extracted_count"] = sum(
            len(v) if isinstance(v, list) else 0
            for k, v in intelligence.items()
            if k != "extracted_count"
        )
        
        return intelligence
    
    def _extract_unique(self, text: str, pattern_type: str) -> List[str]:
    
        pattern = self.patterns.get(pattern_type)
        if not pattern:
            return []
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        unique_matches = list(set(matches))
        
        if pattern_type == "bank_account":
            unique_matches = [m for m in unique_matches if self._validate_bank_account(m)]
        elif pattern_type == "upi_id":
            unique_matches = [m for m in unique_matches if self._validate_upi(m)]
        elif pattern_type == "url":
            unique_matches = [m for m in unique_matches if self._is_suspicious_url(m)]
        
        return unique_matches
    
    def _validate_bank_account(self, account: str) -> bool:
        if len(account) < 9 or len(account) > 18:
            return False
        
        if len(set(account)) == 1:
            return False
        
        if account in "0123456789" * 2:
            return False
        
        return True
    
    def _validate_upi(self, upi_id: str) -> bool:
        """Validate UPI ID format"""
        return any(handle in upi_id.lower() for handle in self.upi_handles)
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL looks suspicious/phishing"""
        suspicious_indicators = [
            "bit.ly", "tinyurl", "goo.gl",  # URL shorteners
            "tk", "ml", "ga", "cf", "gq",  # Free domains
            ".zip", ".rar", ".exe",  # Suspicious extensions
            "verify", "confirm", "login", "secure", "account"  # Phishing keywords
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in suspicious_indicators)
    
    def _extract_bank_names(self, text: str) -> List[str]:
        found_banks = []
        for bank in self.bank_names:
            if bank in text:
                found_banks.append(bank.upper())
        
        return list(set(found_banks))
    
    def _extract_company_names(self, text: str) -> List[str]:
        companies = []
        
        # Common impersonation targets
        common_targets = [
            "amazon", "flipkart", "paytm", "google pay", "phonepe",
            "income tax", "tax department", "police", "cyber cell",
            "rbi", "reserve bank", "government", "ministry"
        ]
        
        for company in common_targets:
            if company in text:
                companies.append(company.title())
        
        return list(set(companies))
    
    def _extract_claims(self, history: List[Dict]) -> List[str]:
        claims = []
        
        for msg in history:
            if msg.get("role") == "scammer":
                content = msg.get("content", "").lower()
                
                # Extract claim patterns
                if "refund" in content or "cashback" in content:
                    claims.append("Promises refund/cashback")
                
                if "prize" in content or "lottery" in content or "winner" in content:
                    claims.append("Claims lottery/prize win")
                
                if "account" in content and ("blocked" in content or "suspended" in content):
                    claims.append("Claims account issue")
                
                if "verify" in content or "confirm" in content:
                    claims.append("Requests verification")
                
                if "urgent" in content or "immediately" in content:
                    claims.append("Creates urgency")
                
                if any(bank in content for bank in self.bank_names):
                    claims.append("Claims to be from bank")
                
                if "government" in content or "police" in content or "tax" in content:
                    claims.append("Impersonates authority")
        
        return list(set(claims))


class IntelligenceValidator:
    
    @staticmethod
    def validate_extraction(intelligence: Dict) -> Dict:
        
        score = 0
        quality_indicators = {}
        
        if intelligence["bank_accounts"]:
            score += 30
            quality_indicators["has_bank_account"] = True
        
        if intelligence["upi_ids"]:
            score += 25
            quality_indicators["has_upi_id"] = True
        
        if intelligence["urls"]:
            score += 20
            quality_indicators["has_phishing_url"] = True
        
        if intelligence["phone_numbers"]:
            score += 15
            quality_indicators["has_phone"] = True
        
        if intelligence["ifsc_codes"]:
            score += 15
            quality_indicators["has_ifsc"] = True
        
        if intelligence["bank_names"]:
            score += 5
        
        if intelligence["company_names"]:
            score += 5
        
        if intelligence["scammer_claims"]:
            score += 5
        
        return {
            "quality_score": min(score, 100),
            "indicators": quality_indicators,
            "completeness": score / 100.0
        }
