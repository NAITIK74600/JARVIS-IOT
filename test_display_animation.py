#!/usr/bin/env python3
"""
JARVIS Display Non-Stop Animation
Continuously animates the display with various effects and faces
Press Ctrl+C to stop
"""

import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from actuators.display import display

def animate_eyes_blink():
    """Blinking animation"""
    # Open eyes
    display.show_face('neutral')
    time.sleep(0.3)
    # Close eyes (clear)
    display.clear()
    time.sleep(0.15)
    # Open eyes
    display.show_face('neutral')
    time.sleep(0.3)

def animate_scanning():
    """Scanning animation with moving text"""
    chars = ['|', '/', '-', '\\']
    for i in range(8):
        display.clear()
        display.write_text(f"Scanning {chars[i % 4]}", row=0, col=3)
        display.write_text(f"[{'=' * (i % 16)}>{' ' * (15 - (i % 16))}]", row=1, col=0)
        time.sleep(0.15)

def animate_heartbeat():
    """Heartbeat animation"""
    for i in range(2):
        display.clear()
        display.write_text("  <3", row=0, col=6)
        display.write_text("      <3", row=1, col=4)
        time.sleep(0.2)
        display.clear()
        display.write_text("<3", row=0, col=7)
        display.write_text("    <3", row=1, col=5)
        time.sleep(0.2)

def animate_thinking():
    """Thinking animation with dots"""
    for dots in range(4):
        display.clear()
        display.show_face('thinking')
        display.write_text('.' * (dots + 1), row=1, col=12)
        time.sleep(0.4)

def animate_wave():
    """Wave animation"""
    wave_frames = [
        ("    ~   ~   ~   ", "   ~   ~   ~    "),
        ("   ~   ~   ~    ", "  ~   ~   ~     "),
        ("  ~   ~   ~     ", " ~   ~   ~      "),
        (" ~   ~   ~      ", "~   ~   ~       "),
    ]
    for frame in wave_frames:
        display.clear()
        display.write_text(frame[0], row=0, col=0)
        display.write_text(frame[1], row=1, col=0)
        time.sleep(0.2)

def animate_loading_bar():
    """Loading bar animation"""
    for i in range(17):
        display.clear()
        display.write_text("Loading...", row=0, col=3)
        bar = f"[{'=' * i}{' ' * (16 - i)}]"
        display.write_text(bar, row=1, col=0)
        time.sleep(0.1)

def animate_matrix_rain():
    """Matrix-style rain effect"""
    for _ in range(10):
        display.clear()
        import random
        line1 = ''.join(random.choice('01') for _ in range(16))
        line2 = ''.join(random.choice('01') for _ in range(16))
        display.write_text(line1, row=0, col=0)
        display.write_text(line2, row=1, col=0)
        time.sleep(0.15)

def animate_emotions():
    """Cycle through all emotions"""
    emotions = ['neutral', 'happy', 'listening', 'thinking', 'sad', 'happy', 'neutral']
    emotion_labels = ['Neutral', 'Happy', 'Listening', 'Thinking', 'Sad', 'Excited', 'Calm']
    
    for emotion, label in zip(emotions, emotion_labels):
        display.show_face(emotion)
        time.sleep(0.15)
        display.write_text(label, row=1, col=int((16 - len(label)) / 2))
        time.sleep(0.8)

def animate_text_scroll(text):
    """Scroll text across display"""
    padded_text = " " * 16 + text + " " * 16
    for i in range(len(padded_text) - 15):
        display.clear()
        display.write_text(padded_text[i:i+16], row=0, col=0)
        time.sleep(0.15)

def animate_jarvis_boot():
    """JARVIS boot sequence"""
    sequences = [
        ("JARVIS", "Initializing.."),
        ("Systems", "Loading...."),
        ("Neural Net", "Active......"),
        ("Voice Engine", "Ready......."),
        ("Sensors", "Online......"),
        ("JARVIS", "ONLINE"),
    ]
    
    for line1, line2 in sequences:
        display.clear()
        display.write_text(line1, row=0, col=int((16 - len(line1)) / 2))
        display.write_text(line2, row=1, col=int((16 - len(line2)) / 2))
        time.sleep(0.5)

def animate_breathing():
    """Breathing effect with custom chars"""
    for _ in range(3):
        # Expand
        for i in range(4):
            display.clear()
            spaces = " " * i
            display.write_text(f"{spaces}> JARVIS <{spaces}", row=0, col=0)
            time.sleep(0.15)
        # Contract
        for i in range(3, -1, -1):
            display.clear()
            spaces = " " * i
            display.write_text(f"{spaces}> JARVIS <{spaces}", row=0, col=0)
            time.sleep(0.15)

def animate_radar():
    """Radar scanning animation"""
    radar_frames = [
        ("    |           ", "                "),
        ("     /          ", "                "),
        ("      -         ", "                "),
        ("       \\        ", "                "),
        ("        |       ", "    Scanning    "),
        ("         /      ", "    Scanning    "),
        ("          -     ", "    Scanning    "),
        ("           \\    ", "    Scanning    "),
    ]
    
    for frame in radar_frames:
        display.clear()
        display.write_text(frame[0], row=0, col=0)
        display.write_text(frame[1], row=1, col=0)
        time.sleep(0.2)

def animate_random_pattern():
    """Random pattern animation"""
    import random
    chars = ['*', '+', 'o', '.', '#', '@', '~']
    
    for _ in range(12):
        display.clear()
        line1 = ''.join(random.choice(chars) for _ in range(16))
        line2 = ''.join(random.choice(chars) for _ in range(16))
        display.write_text(line1, row=0, col=0)
        display.write_text(line2, row=1, col=0)
        time.sleep(0.2)

def main():
    """Main animation loop"""
    print("="*60)
    print("JARVIS Display Non-Stop Animation")
    print("="*60)
    print("\nPress Ctrl+C to stop the animation\n")
    
    animation_sequence = [
        ("JARVIS Boot Sequence", animate_jarvis_boot),
        ("Eyes Blink", animate_eyes_blink),
        ("Emotions Cycle", animate_emotions),
        ("Scanning", animate_scanning),
        ("Loading Bar", animate_loading_bar),
        ("Heartbeat", animate_heartbeat),
        ("Breathing", animate_breathing),
        ("Thinking", animate_thinking),
        ("Wave Effect", animate_wave),
        ("Radar Scan", animate_radar),
        ("Matrix Rain", animate_matrix_rain),
        ("Random Pattern", animate_random_pattern),
    ]
    
    # Add some scrolling text messages
    messages = [
        "JARVIS - Just A Rather Very Intelligent System",
        "Hello! I am your AI assistant",
        "All systems operational",
        "Ready to assist you",
        "Sensors online - Voice active - Systems ready",
    ]
    
    try:
        loop_count = 0
        while True:
            loop_count += 1
            print(f"\n{'='*60}")
            print(f"Animation Loop #{loop_count}")
            print(f"{'='*60}")
            
            for name, animation_func in animation_sequence:
                print(f"→ Playing: {name}")
                try:
                    animation_func()
                    time.sleep(0.3)  # Pause between animations
                except Exception as e:
                    print(f"  Error in {name}: {e}")
                    continue
            
            # Scroll a random message
            import random
            message = random.choice(messages)
            print(f"→ Scrolling: {message[:30]}...")
            animate_text_scroll(message)
            time.sleep(0.5)
            
            # Show happy face between loops
            display.show_face('happy')
            display.write_text("Loop Complete!", row=1, col=2)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n→ Animation stopped by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n→ Cleaning up display...")
        display.clear()
        display.write_text("JARVIS", row=0, col=5)
        display.write_text("Standby", row=1, col=5)
        time.sleep(1)
        display.clear()
        print("✓ Animation complete!\n")

if __name__ == "__main__":
    main()
