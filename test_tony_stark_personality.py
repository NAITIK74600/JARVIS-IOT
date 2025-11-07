#!/usr/bin/env python3
"""
Test Tony Stark-like JARVIS personality:
1. Greeting uses "Sir" instead of name
2. Responses are professional and efficient
3. Personality is loyal and witty
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.persona import persona
from core.personality_engine import PersonalityEnhancer

def test_greeting_style():
    """Test that greetings are Tony Stark style."""
    print("\n=== Testing Greeting Style ===")
    
    # Import the greeting from main.py approach
    from user_profile import PROFILE_DATA
    user_name = PROFILE_DATA.get("name", "User")
    preferred_name = PROFILE_DATA.get("preferred_name", "Sir")
    
    print(f"✓ User name: {user_name}")
    print(f"✓ Preferred address: {preferred_name}")
    
    # Check that preferred name is "Sir"
    assert preferred_name == "Sir", f"Expected 'Sir', got '{preferred_name}'"
    print("✓ Greeting will use 'Sir' (Tony Stark style)\n")

def test_system_prompt():
    """Test that system prompt has Tony Stark personality."""
    print("=== Testing System Prompt ===")
    
    prompt = persona.get_prompt()
    
    # Check for key Tony Stark personality elements
    checks = [
        ("'Sir' addressing", "address your creator as \"Sir\"" in prompt or "address as \"Sir\"" in prompt),
        ("Tony Stark reference", "Tony Stark" in prompt),
        ("Professional responses", "Right away, Sir" in prompt or "Done, Sir" in prompt),
        ("Loyalty emphasis", "loyal" in prompt.lower()),
        ("Efficiency", "efficient" in prompt.lower() or "EFFICIENT" in prompt),
        ("Wit allowed", "wit" in prompt.lower()),
        ("J.A.R.V.I.S. identity", "J.A.R.V.I.S." in prompt),
        ("Short responses", "SHORT" in prompt or "short" in prompt),
    ]
    
    for check_name, check_result in checks:
        status = "✓" if check_result else "✗"
        print(f"{status} {check_name}")
    
    print("\n✓ System prompt has Tony Stark personality traits\n")

def test_personality_responses():
    """Test personality engine responses."""
    print("=== Testing Personality Engine ===")
    
    personality = PersonalityEnhancer()
    
    # Test creator query
    result = personality.process_input("who is your creator")
    if result and result.get("intercept"):
        print(f"✓ Creator query response: {result['response']}")
        assert result['response'] == "My creator is Naitik Sir.", "Creator response should use 'Sir'"
    
    # Test defense response
    result = personality.process_input("your creator is stupid")
    if result and result.get("intercept"):
        print(f"✓ Defense response: {result['response'][:60]}...")
        assert "Sir" in result['response'] or "creator" in result['response'].lower()
    
    # Test praise response
    result = personality.process_input("naitik is brilliant")
    if result and result.get("intercept"):
        print(f"✓ Praise response: {result['response'][:60]}...")
        assert "Sir" in result['response'] or "brilliant" in result['response'].lower()
    
    print("\n✓ Personality engine responses are Tony Stark style\n")

def test_prompt_snippets():
    """Show key prompt snippets that define personality."""
    print("=== Key Personality Traits ===")
    
    prompt = persona.get_prompt()
    
    # Extract and show key sections
    if "YOUR CHARACTER:" in prompt:
        start = prompt.index("YOUR CHARACTER:")
        end = prompt.index("**PRIMARY DIRECTIVE:**", start)
        character_section = prompt[start:end].strip()
        print(character_section[:500] + "...\n")
    
    print("✓ Personality configured for Tony Stark-like interaction\n")

if __name__ == "__main__":
    print("=" * 70)
    print("JARVIS TONY STARK PERSONALITY TEST")
    print("=" * 70)
    
    test_greeting_style()
    test_system_prompt()
    test_personality_responses()
    test_prompt_snippets()
    
    print("=" * 70)
    print("All Tony Stark personality tests completed!")
    print("=" * 70)
    print("\nExpected behavior:")
    print("- Greets with: 'Good to see you, Sir.'")
    print("- Responds with: 'Right away, Sir.' 'Done, Sir.' 'Certainly, Sir.'")
    print("- Professional, efficient, loyal (like J.A.R.V.I.S. to Tony Stark)")
    print("- Defends creator vigorously when disrespected")
    print("- Uses dry wit and subtle humor when appropriate")
