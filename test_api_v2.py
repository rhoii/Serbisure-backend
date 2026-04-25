import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_endpoint(name, method, endpoint, data=None):
    print(f"\n--- Testing {name} ({method} {endpoint}) ---")
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

# 1. Test Services (Public)
test_endpoint("Services List", "GET", "/services/")

# 2. Test Login
login_data = {
    "email": "homeowner@test.com",
    "password": "pass1234"
}
test_endpoint("Login", "POST", "/auth/login/", login_data)
