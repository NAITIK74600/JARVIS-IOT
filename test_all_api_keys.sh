#!/usr/bin/env bash
set -euo pipefail

# Test all Google Gemini API keys to ensure they work
echo "═══════════════════════════════════════════════════════════"
echo "  Testing All Google Gemini API Keys"
echo "═══════════════════════════════════════════════════════════"
echo ""

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "❌ Virtual environment not found. Run ./setup_env.sh first."
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Check if .env exists
if [ ! -f .env ]; then
  echo "❌ .env file not found. API keys not configured."
  exit 1
fi

echo "Loading API keys from .env file..."
source .env

# Test each key
KEY_COUNT=0
WORKING_KEYS=0

test_key() {
  local KEY_NAME="$1"
  local KEY_VALUE="$2"
  local KEY_NUM="$3"
  
  if [ -z "$KEY_VALUE" ] || [[ "$KEY_VALUE" == "your_"* ]] || [[ "$KEY_VALUE" == "PASTE_"* ]]; then
    return 1
  fi
  
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Testing Key #$KEY_NUM: ${KEY_NAME}"
  echo "Key: ${KEY_VALUE:0:20}...${KEY_VALUE: -4}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  python3 << EOF
import os
import sys
os.environ['GOOGLE_API_KEY'] = '$KEY_VALUE'

try:
    import google.generativeai as genai
    
    # Configure the API key
    genai.configure(api_key='$KEY_VALUE')
    
    # Test with a simple query using the direct API
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'API key working' in exactly 3 words.")
    
    print(f"✅ SUCCESS - Response: {response.text.strip()}")
    sys.exit(0)
    
except Exception as e:
    error_msg = str(e)
    if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
        print(f"❌ FAILED - Invalid API key")
    elif "quota" in error_msg.lower() or "rate" in error_msg.lower() or "429" in error_msg:
        print(f"⚠️  RATE LIMITED - Key is valid but hit quota limit")
        sys.exit(0)  # Still count as working
    else:
        print(f"❌ FAILED - Error: {error_msg}")
    sys.exit(1)
EOF
  
  return $?
}

# Test primary key
if [ -n "${GOOGLE_API_KEY:-}" ]; then
  KEY_COUNT=$((KEY_COUNT + 1))
  if test_key "GOOGLE_API_KEY" "$GOOGLE_API_KEY" "1"; then
    WORKING_KEYS=$((WORKING_KEYS + 1))
  fi
fi

# Test additional keys (2-10)
for i in {2..10}; do
  VAR_NAME="GOOGLE_API_KEY_${i}"
  KEY_VALUE="${!VAR_NAME:-}"
  
  if [ -n "$KEY_VALUE" ] && [[ ! "$KEY_VALUE" == "your_"* ]]; then
    KEY_COUNT=$((KEY_COUNT + 1))
    if test_key "$VAR_NAME" "$KEY_VALUE" "$i"; then
      WORKING_KEYS=$((WORKING_KEYS + 1))
    fi
  fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Test Results"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Total keys found: $KEY_COUNT"
echo "Working keys: $WORKING_KEYS"
echo ""

if [ $WORKING_KEYS -eq 0 ]; then
  echo "❌ No working API keys found!"
  echo ""
  echo "Please check:"
  echo "1. Keys are correctly pasted in .env file"
  echo "2. Keys are valid (not expired/revoked)"
  echo "3. You have internet connection"
  exit 1
elif [ $WORKING_KEYS -lt $KEY_COUNT ]; then
  echo "⚠️  Some keys failed, but $WORKING_KEYS working key(s) available"
  echo ""
  echo "✅ JARVIS can run with automatic key rotation"
else
  echo "✅ All $KEY_COUNT API keys are working!"
  echo ""
  echo "✨ Excellent! JARVIS has $WORKING_KEYS keys for automatic rotation"
fi

echo ""
echo "Next steps:"
echo "  ./run.sh    # Start JARVIS"
echo ""
