import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    response = requests.get(f"{BASE_URL}/")
    print("Health Check:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_mobile_health():
    response = requests.get(f"{BASE_URL}/api/mobile/health")
    print("Mobile Health Check:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_mobile_analyze():
    test_data = {
        "user_id": "test_user_123",
        "device_id": "android_device_001",
        "sms_text": "Rs.1500 unauthorized debit from HBL Bank"
    }
    response = requests.post(f"{BASE_URL}/api/mobile/analyze", json=test_data)
    print("Mobile Analyze:")
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_agent_orchestrate():
    test_data = {
        "user_id": "test_user_123",
        "sms_text": "Rs.1500 unauthorized debit from HBL Bank"
    }
    response = requests.post(f"{BASE_URL}/api/agent_orchestrate", json=test_data)
    print("Agent Orchestrate:")
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    test_health()
    test_mobile_health()
    test_mobile_analyze()
    test_agent_orchestrate()