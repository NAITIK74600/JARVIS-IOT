#!/bin/bash
# Install espeak for 7x faster short phrase responses

echo "════════════════════════════════════════════════════════════"
echo "Installing eSpeak for Ultra-Fast Local TTS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "This will enable instant responses for short phrases:"
echo "• 'yes sir' - 0.5s instead of 7s (14x faster!)"
echo "• 'hello' - 0.5s instead of 7s"
echo "• 'checking now' - 1s instead of 8s"
echo ""
echo "Long responses will still use high-quality Google TTS."
echo ""
read -p "Install espeak? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing espeak..."
    sudo apt-get update
    sudo apt-get install -y espeak
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ eSpeak installed successfully!"
        echo ""
        echo "Testing espeak..."
        espeak "Hello, this is a test" 2>/dev/null
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "✅ SETUP COMPLETE!"
        echo "════════════════════════════════════════════════════════════"
        echo ""
        echo "Short responses will now be instant!"
        echo ""
        echo "Run JARVIS to test:"
        echo "./start_jarvis_headless.sh"
        echo ""
    else
        echo "❌ Installation failed. Please run manually:"
        echo "sudo apt-get install espeak"
    fi
else
    echo "Skipped. You can install later with:"
    echo "sudo apt-get install espeak"
fi
