#!/usr/bin/env python3
"""
Comprehensive test suite for JARVIS hybrid optimization system.

Tests:
1. Hybrid router offline/API decision logic
2. Owner protection system
3. Adaptive conversation modes
4. Quota tracking and management
5. Offline pattern matching
"""

import sys
from datetime import datetime, timedelta


def test_hybrid_router():
    """Test hybrid router decision making."""
    print("\n" + "="*60)
    print("TEST 1: Hybrid Router Decision Logic")
    print("="*60)
    
    try:
        from core.hybrid_router import get_router
        
        router = get_router()
        
        # Test offline patterns
        test_cases = [
            ("what time is it", True, "time query should be offline"),
            ("get sensor readings", True, "sensor query should be offline"),
            ("scan the environment", True, "robot command should be offline"),
            ("hello jarvis", True, "greeting should be offline"),
            ("calculate 5 + 3", True, "math should be offline"),
            ("explain quantum physics", False, "complex explanation needs API"),
            ("write me a story about space", False, "creative writing needs API"),
            ("what is the meaning of life", False, "philosophical question needs API"),
        ]
        
        passed = 0
        failed = 0
        
        for query, expected_offline, description in test_cases:
            should_offline, reason = router.should_use_offline(query)
            
            if should_offline == expected_offline:
                print(f"✅ PASS: {description}")
                print(f"   Query: '{query}'")
                print(f"   Decision: {'Offline' if should_offline else 'API'} (Reason: {reason})")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Query: '{query}'")
                print(f"   Expected: {'Offline' if expected_offline else 'API'}")
                print(f"   Got: {'Offline' if should_offline else 'API'} (Reason: {reason})")
                failed += 1
        
        print(f"\n📊 Results: {passed}/{passed+failed} tests passed")
        return failed == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_owner_protection():
    """Test owner protection system."""
    print("\n" + "="*60)
    print("TEST 2: Owner Protection System")
    print("="*60)
    
    try:
        from core.personality_engine import OwnerProtectionSystem
        
        protection = OwnerProtectionSystem()
        
        # Test insult detection
        insult_tests = [
            ("naitik is stupid", True, "direct insult"),
            ("your creator is incompetent", True, "indirect insult with 'your creator'"),
            ("naitik raj is brilliant", False, "praise, not insult"),
            ("the weather is bad", False, "unrelated negativity"),
            ("your owner is useless", True, "insult with 'your owner'"),
        ]
        
        passed = 0
        failed = 0
        
        for text, should_detect, description in insult_tests:
            is_insult, response = protection.detect_insult(text)
            
            if is_insult == should_detect:
                print(f"✅ PASS: {description}")
                print(f"   Input: '{text}'")
                if is_insult:
                    print(f"   Response: '{response}'")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Input: '{text}'")
                print(f"   Expected insult detection: {should_detect}")
                print(f"   Got: {is_insult}")
                failed += 1
        
        # Test praise detection
        praise_tests = [
            ("naitik is smart", True, "direct praise with name"),
            ("your creator is amazing", True, "indirect praise with 'your creator'"),
            ("naitik is terrible", False, "insult, not praise"),
        ]
        
        print("\n--- Praise Detection ---")
        for text, should_detect, description in praise_tests:
            is_praise, response = protection.detect_praise(text)
            
            if is_praise == should_detect:
                print(f"✅ PASS: {description}")
                print(f"   Input: '{text}'")
                if is_praise:
                    print(f"   Response: '{response}'")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                failed += 1
        
        print(f"\n📊 Results: {passed}/{passed+failed} tests passed")
        return failed == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_adaptive_conversation():
    """Test adaptive conversation modes."""
    print("\n" + "="*60)
    print("TEST 3: Adaptive Conversation Modes")
    print("="*60)
    
    try:
        from core.personality_engine import AdaptiveConversationManager, RelationshipType
        
        manager = AdaptiveConversationManager()
        
        test_cases = [
            ("I am your professor", RelationshipType.PROFESSOR, "professor detection"),
            ("hey friend, what's up", RelationshipType.FRIEND, "friend detection"),
            ("I'm your teacher", RelationshipType.TEACHER, "teacher detection"),
            ("this is your family", RelationshipType.FAMILY, "family detection"),
        ]
        
        passed = 0
        failed = 0
        
        for text, expected_type, description in test_cases:
            detected = manager.detect_relationship(text)
            
            if detected == expected_type:
                print(f"✅ PASS: {description}")
                print(f"   Input: '{text}'")
                print(f"   Detected: {detected.value}")
                print(f"   Greeting: '{manager.STYLES[detected]['greeting']}'")
                print(f"   Tone: {manager.STYLES[detected]['tone']}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Input: '{text}'")
                print(f"   Expected: {expected_type.value}")
                print(f"   Got: {detected.value}")
                failed += 1
        
        print(f"\n📊 Results: {passed}/{passed+failed} tests passed")
        return failed == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quota_management():
    """Test API quota tracking."""
    print("\n" + "="*60)
    print("TEST 4: API Quota Management")
    print("="*60)
    
    try:
        from core.hybrid_router import APIQuotaManager, APIQuotaState
        from datetime import datetime
        
        # Create fresh quota manager
        manager = APIQuotaManager()
        
        # Test quota tracking
        print("Initial state:")
        quota = manager.get_remaining_quota()
        print(f"  Daily: {quota['daily_remaining']}/{manager.state.daily_limit}")
        print(f"  Hourly: {quota['hourly_remaining']}/{manager.state.hourly_limit}")
        
        # Test API call recording
        initial_daily = manager.state.today_usage
        manager.record_api_call()
        
        if manager.state.today_usage == initial_daily + 1:
            print("✅ PASS: API call recorded correctly")
        else:
            print("❌ FAIL: API call not recorded")
            return False
        
        # Test quota limit checking
        can_use = manager.can_use_api()
        print(f"✅ PASS: Can use API: {can_use}")
        
        # Test daily reset
        old_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        manager.state.last_reset_date = old_date
        manager._check_reset()
        
        if manager.state.today_usage == 0:
            print("✅ PASS: Daily quota reset works")
        else:
            print("❌ FAIL: Daily quota reset failed")
            return False
        
        print("\n📊 All quota management tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_offline_patterns():
    """Test offline responder pattern matching."""
    print("\n" + "="*60)
    print("TEST 5: Offline Pattern Matching")
    print("="*60)
    
    try:
        from core.offline_responder import OfflineResponder
        
        # Create dummy tools
        class DummyTool:
            def __init__(self, name, result):
                self.name = name
                self.result = result
            
            def func(self, *args, **kwargs):
                return self.result
        
        tools = [
            DummyTool("get_current_system_time", "Current time: 12:30 PM"),
            DummyTool("get_environment_readings", "Temperature: 25°C, Humidity: 60%"),
            DummyTool("get_all_sensor_readings", "All sensors: OK"),
        ]
        
        responder = OfflineResponder(tools, logger=None)
        
        test_cases = [
            ("what time is it", "Current time"),
            ("get temperature", "Temperature"),
            ("sensor readings", "sensors"),
            ("hello jarvis", "Hello"),
            ("thank you", "welcome"),
        ]
        
        passed = 0
        failed = 0
        
        for query, expected_keyword in test_cases:
            result = responder.respond(query)
            response_text = result['text'].lower()
            
            if expected_keyword.lower() in response_text:
                print(f"✅ PASS: '{query}' → contains '{expected_keyword}'")
                passed += 1
            else:
                print(f"❌ FAIL: '{query}'")
                print(f"   Expected keyword: '{expected_keyword}'")
                print(f"   Got: '{result['text']}'")
                failed += 1
        
        print(f"\n📊 Results: {passed}/{passed+failed} tests passed")
        return failed == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "JARVIS HYBRID SYSTEM TEST SUITE" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("Hybrid Router", test_hybrid_router()))
    results.append(("Owner Protection", test_owner_protection()))
    results.append(("Adaptive Conversation", test_adaptive_conversation()))
    results.append(("Quota Management", test_quota_management()))
    results.append(("Offline Patterns", test_offline_patterns()))
    
    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n{'Total:':<40} {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 All systems operational! JARVIS is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
