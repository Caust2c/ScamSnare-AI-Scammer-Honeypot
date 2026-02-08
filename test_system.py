"""
Test script for Honeypot System
Run this to test the system locally
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-secure-api-key-change-this"  # Match your config.py

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}


def test_health_check():
    """Test if server is running"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_scam_detection_simple():
    """Test simple scam detection"""
    print("\n=== Testing Simple Scam Detection ===")
    
    payload = {
        "conversation_id": "test_simple_001",
        "message": "Congratulations! You won 1 lakh rupees. Send your bank account number to claim.",
        "history": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/detect",
            headers=HEADERS,
            json=payload
        )
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response:\n{json.dumps(result, indent=2)}")
        
        print(f"\n✓ Scam Detected: {result['scam_detected']}")
        print(f"✓ Agent Activated: {result['agent_activated']}")
        print(f"✓ Confidence: {result['confidence_score']}")
        print(f"✓ Agent Response: {result['response_message']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_multi_turn_conversation():
    """Test multi-turn conversation engagement"""
    print("\n=== Testing Multi-Turn Conversation ===")
    
    conversation_id = "test_multiturn_001"
    
    # Turn 1
    print("\n--- Turn 1 ---")
    payload1 = {
        "conversation_id": conversation_id,
        "message": "Sir, this is from State Bank of India. Your account will be blocked in 24 hours due to KYC not updated.",
        "history": []
    }
    
    response1 = requests.post(f"{BASE_URL}/detect", headers=HEADERS, json=payload1)
    result1 = response1.json()
    print(f"Scammer: {payload1['message']}")
    print(f"Agent: {result1['response_message']}")
    print(f"Scam Detected: {result1['scam_detected']} (Confidence: {result1['confidence_score']})")
    
    time.sleep(1)
    
    # Turn 2
    print("\n--- Turn 2 ---")
    payload2 = {
        "conversation_id": conversation_id,
        "message": "You need to verify your account immediately. Please share your account number and UPI ID.",
        "history": [
            {
                "role": "scammer",
                "content": payload1["message"],
                "timestamp": "2024-01-01T10:00:00"
            },
            {
                "role": "agent",
                "content": result1["response_message"],
                "timestamp": "2024-01-01T10:00:05"
            }
        ]
    }
    
    response2 = requests.post(f"{BASE_URL}/detect", headers=HEADERS, json=payload2)
    result2 = response2.json()
    print(f"Scammer: {payload2['message']}")
    print(f"Agent: {result2['response_message']}")
    
    time.sleep(1)
    
    # Turn 3
    print("\n--- Turn 3 ---")
    payload3 = {
        "conversation_id": conversation_id,
        "message": "Sir, please send to this UPI ID: scammer123@paytm. Account number is 1234567890123. Send Rs 1 for verification.",
        "history": payload2["history"] + [
            {
                "role": "scammer",
                "content": payload2["message"],
                "timestamp": "2024-01-01T10:00:10"
            },
            {
                "role": "agent",
                "content": result2["response_message"],
                "timestamp": "2024-01-01T10:00:15"
            }
        ]
    }
    
    response3 = requests.post(f"{BASE_URL}/detect", headers=HEADERS, json=payload3)
    result3 = response3.json()
    print(f"Scammer: {payload3['message']}")
    print(f"Agent: {result3['response_message']}")
    
    # Show extracted intelligence
    print("\n--- Extracted Intelligence ---")
    intel = result3["extracted_intelligence"]
    print(f"Bank Accounts: {intel['bank_accounts']}")
    print(f"UPI IDs: {intel['upi_ids']}")
    print(f"Phone Numbers: {intel['phone_numbers']}")
    print(f"URLs: {intel['urls']}")
    print(f"Total Items Extracted: {intel['extracted_count']}")
    
    print("\n--- Engagement Metrics ---")
    metrics = result3["engagement_metrics"]
    print(f"Total Turns: {metrics['total_turns']}")
    print(f"Agent Turns: {metrics['agent_turns']}")
    print(f"Duration: {metrics['conversation_duration_seconds']} seconds")
    print(f"Intelligence Found: {metrics['intelligence_items_found']}")
    
    return True


def test_phishing_url_detection():
    """Test phishing URL detection"""
    print("\n=== Testing Phishing URL Detection ===")
    
    payload = {
        "conversation_id": "test_phishing_001",
        "message": "Your account security has been compromised. Click here to verify: https://bit.ly/fake-bank-login",
        "history": []
    }
    
    response = requests.post(f"{BASE_URL}/detect", headers=HEADERS, json=payload)
    result = response.json()
    
    print(f"Message: {payload['message']}")
    print(f"Scam Detected: {result['scam_detected']}")
    print(f"URLs Extracted: {result['extracted_intelligence']['urls']}")
    print(f"Agent Response: {result['response_message']}")
    
    return len(result['extracted_intelligence']['urls']) > 0


def test_upi_scam():
    """Test UPI scam detection"""
    print("\n=== Testing UPI Scam ===")
    
    payload = {
        "conversation_id": "test_upi_001",
        "message": "Hello, you have won cashback of Rs 5000. Please send Rs 1 to winner@paytm to claim your prize.",
        "history": []
    }
    
    response = requests.post(f"{BASE_URL}/detect", headers=HEADERS, json=payload)
    result = response.json()
    
    print(f"Message: {payload['message']}")
    print(f"Scam Detected: {result['scam_detected']}")
    print(f"UPI IDs: {result['extracted_intelligence']['upi_ids']}")
    print(f"Agent Response: {result['response_message']}")
    
    return True


def test_get_conversation():
    """Test retrieving conversation history"""
    print("\n=== Testing Get Conversation ===")
    
    conversation_id = "test_multiturn_001"
    
    try:
        response = requests.get(
            f"{BASE_URL}/conversation/{conversation_id}",
            headers={"X-API-Key": API_KEY}
        )
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Conversation ID: {result['conversation_id']}")
        print(f"Total Messages: {len(result['history'])}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("AGENTIC HONEY-POT SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Simple Scam Detection", test_scam_detection_simple),
        ("Multi-Turn Conversation", test_multi_turn_conversation),
        ("Phishing URL Detection", test_phishing_url_detection),
        ("UPI Scam Detection", test_upi_scam),
        ("Get Conversation", test_get_conversation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
            time.sleep(2)  # Wait between tests
        except Exception as e:
            print(f"Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure:")
    print("1. Ollama is running (ollama serve)")
    print("2. Model is pulled (ollama pull llama3.2:3b)")
    print("3. API server is running (python main.py)")
    print("4. API_KEY in this script matches config.py")
    
    input("\nPress Enter to start tests...")
    
    run_all_tests()
