import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000"

# Test 1: Health check
print("Testing health endpoint...")
try:
    response = requests.get(f"{BACKEND_URL}/health")
    print(f"✅ Health check: {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Chat endpoint
print("\nTesting chat endpoint...")
try:
    response = requests.post(
        f"{BACKEND_URL}/chat",
        json={"message": "Hello"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Chat response: {response.json()}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Chat test failed: {e}")

# Test 3: Check environment variables
print("\nChecking environment variables...")
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    print(f"✅ GROQ_API_KEY is set (length: {len(groq_key)})")
else:
    print("❌ GROQ_API_KEY is NOT set")

model = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
print(f"✅ MODEL_NAME: {model}")
