#!/usr/bin/env bash
set -euo pipefail

# Test Google Gemini API key

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Testing Google Gemini API connection...${NC}"
echo ""

# Activate virtualenv
if [ ! -d .venv ]; then
    echo -e "${RED}✗ Virtual environment not found. Run ./setup_env.sh first${NC}"
    exit 1
fi

source .venv/bin/activate

# Run Python test
python3 << 'PYTHON_EOF'
import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key or api_key.startswith(("your_", "PASTE_")):
    print("\033[0;31m✗ No valid Google API key found in .env file\033[0m")
    print("\nRun: ./setup_google_api.sh")
    sys.exit(1)

print(f"API Key found: {api_key[:20]}...{api_key[-10:]}")
print("\nTesting Google Gemini API...")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Create client
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.3,
        convert_system_message_to_human=True
    )
    
    # Test with a simple query
    response = llm.invoke("Say 'JARVIS online' if you can hear me.")
    
    print("\n\033[0;32m✓ Google Gemini API is working!\033[0m")
    print(f"\nResponse: {response.content}")
    print("\n\033[0;34m═══════════════════════════════════════════════════════════\033[0m")
    print("\033[0;32mYour Google Gemini API is configured correctly!\033[0m")
    print("\033[0;34m═══════════════════════════════════════════════════════════\033[0m")
    print("\nYou can now run JARVIS with: ./run.sh")
    
except Exception as e:
    print(f"\n\033[0;31m✗ API test failed: {e}\033[0m")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. API key not activated")
    print("  3. Network connection issue")
    print("  4. API quota exceeded")
    print("\nGet a new key at: https://aistudio.google.com/app/apikey")
    sys.exit(1)

PYTHON_EOF
