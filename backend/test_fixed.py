import requests
import json

def test_endpoint(name, url, method='GET', data=None):
    """Test a single endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print('='*50)
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ SUCCESS - JSON Response:")
                print(json.dumps(result, indent=2))
            except:
                print("📄 SUCCESS - Text Response:")
                print(response.text)
        else:
            print("❌ ERROR:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")

def main():
    base_url = "http://localhost:5000"
    
    # Test endpoints
    test_endpoint("Main Health", f"{base_url}/")
    test_endpoint("Debug Routes", f"{base_url}/debug/routes")
    test_endpoint("Mobile Health", f"{base_url}/api/mobile/health")
    test_endpoint("Mobile Demo", f"{base_url}/api/mobile/demo")
    
    # Test SMS analysis
    test_data = {
        "user_id": "test_user",
        "device_id": "test_device",
        "sms_text": "Rs.1500 unauthorized debit from HBL Bank"
    }
    test_endpoint("Mobile Analyze", f"{base_url}/api/mobile/analyze", "POST", test_data)
    
    # Test user summary
    test_endpoint("User Summary", f"{base_url}/api/mobile/user/test_user/summary")
    
    # Test agent orchestration
    test_endpoint("Agent Orchestrate", f"{base_url}/api/agent_orchestrate", "POST", {
        "user_id": "test_user",
        "sms_text": "Rs.500 credited from Easypaisa"
    })

if __name__ == "__main__":
    main()