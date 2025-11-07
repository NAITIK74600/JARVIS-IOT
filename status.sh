#!/usr/bin/env bash
# Quick Status Check for JARVIS

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          JARVIS System Status Check                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check virtual environment
if [ -d ".venv" ]; then
    echo "✅ Virtual environment: Installed"
else
    echo "❌ Virtual environment: Missing (run ./setup_env.sh)"
fi

# Check .env file
if [ -f ".env" ]; then
    echo "✅ Configuration file: Found"
    
    # Count API keys
    source .env 2>/dev/null
    KEY_COUNT=0
    [ -n "${GOOGLE_API_KEY:-}" ] && KEY_COUNT=$((KEY_COUNT + 1))
    [ -n "${GOOGLE_API_KEY_2:-}" ] && KEY_COUNT=$((KEY_COUNT + 1))
    [ -n "${GOOGLE_API_KEY_3:-}" ] && KEY_COUNT=$((KEY_COUNT + 1))
    [ -n "${GOOGLE_API_KEY_4:-}" ] && KEY_COUNT=$((KEY_COUNT + 1))
    
    if [ $KEY_COUNT -gt 0 ]; then
        echo "✅ API keys configured: $KEY_COUNT key(s)"
    else
        echo "⚠️  API keys: Not configured"
    fi
else
    echo "❌ Configuration file: Missing"
fi

# Check if pigpiod is running (for servo control)
if systemctl is-active --quiet pigpiod 2>/dev/null; then
    echo "✅ pigpiod service: Running"
else
    echo "⚠️  pigpiod service: Not running (servos won't work)"
    echo "   Fix: sudo systemctl start pigpiod"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ -d ".venv" ] && [ -f ".env" ] && [ $KEY_COUNT -gt 0 ]; then
    echo "🎉 System Ready!"
    echo ""
    echo "Quick Commands:"
    echo "  ./run.sh                  - Start JARVIS"
    echo "  ./test_all_api_keys.sh    - Test API keys"
    echo ""
    echo "Documentation:"
    echo "  MULTI_KEY_SETUP.md        - Multi-key configuration guide"
    echo "  README_RUN.md             - Full setup guide"
    echo ""
else
    echo "⚠️  Setup incomplete. Run these steps:"
    echo ""
    if [ ! -d ".venv" ]; then
        echo "  1. ./setup_env.sh          (Install dependencies)"
    fi
    if [ ! -f ".env" ] || [ $KEY_COUNT -eq 0 ]; then
        echo "  2. Edit .env               (Add your Google API keys)"
    fi
    echo "  3. ./run.sh                (Start JARVIS)"
    echo ""
fi
