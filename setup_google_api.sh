#!/usr/bin/env bash
set -euo pipefail

# Helper script to configure Google Gemini API key for JARVIS

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   J.A.R.V.I.S. - Google Gemini API Key Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.template .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
fi

# Check current API key
current_key=$(grep "^GOOGLE_API_KEY=" .env 2>/dev/null | cut -d= -f2 || echo "")

if [ -z "$current_key" ] || [ "$current_key" = "PASTE_YOUR_GOOGLE_GEMINI_API_KEY_HERE" ] || [ "$current_key" = "your_google_gemini_api_key_here" ]; then
    echo -e "${YELLOW}⚠ No valid Google Gemini API key found${NC}"
    echo ""
    echo "To get your FREE Google Gemini API key:"
    echo "  1. Visit: ${GREEN}https://aistudio.google.com/app/apikey${NC}"
    echo "  2. Click 'Create API Key'"
    echo "  3. Copy the key"
    echo ""
    echo -n "Paste your Google Gemini API key here: "
    read -r api_key
    
    if [ -n "$api_key" ]; then
        # Update .env file
        if grep -q "^GOOGLE_API_KEY=" .env; then
            # Replace existing line
            sed -i "s|^GOOGLE_API_KEY=.*|GOOGLE_API_KEY=$api_key|" .env
        else
            # Add new line
            echo "GOOGLE_API_KEY=$api_key" >> .env
        fi
        echo ""
        echo -e "${GREEN}✓ API key saved to .env file${NC}"
    else
        echo -e "${RED}✗ No API key provided${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Google Gemini API key found in .env${NC}"
    echo "  Key: ${current_key:0:20}...${current_key: -10}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Configuration complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify your setup: ${YELLOW}./test_google_api.sh${NC}"
echo "  2. Run JARVIS: ${YELLOW}./run.sh${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
