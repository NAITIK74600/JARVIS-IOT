"""
Owner Protection & Adaptive Conversation System for JARVIS
- Detects disrespect/insults toward owner (Naitik Raj)
- Responds defensively with wit and sarcasm
- Adapts conversation style based on relationship context
"""

import re
from typing import Dict, Tuple, Optional
from enum import Enum


class RelationshipType(Enum):
    """Different types of relationships that affect conversation style."""
    OWNER = "owner"           # Naitik himself
    FAMILY = "family"         # Family members
    FRIEND = "friend"         # Friends - casual, fun
    PROFESSOR = "professor"   # Professors - respectful, formal
    TEACHER = "teacher"       # Teachers - respectful, polite
    COLLEAGUE = "colleague"   # Work colleagues - professional
    STRANGER = "stranger"     # Unknown person - neutral, polite


class OwnerProtectionSystem:
    """Protects owner from disrespect and promotes owner's reputation."""
    
    # Owner names and variations
    OWNER_NAMES = [
        "naitik", "naitik raj", "naitik kumar", "raj",
        "sir", "boss", "master", "my creator", "my owner",
        "your creator", "your owner", "your boss", "your master", "the creator"
    ]
    
    # Negative/insulting patterns about owner
    INSULT_PATTERNS = [
        # Direct insults with owner names
        r'\b(naitik|creator|owner|boss|master)\b.*\b(stupid|dumb|idiot|incompetent|useless|worthless|fool|loser)\b',
        r'\b(stupid|dumb|idiot|incompetent|useless|worthless|fool|loser)\b.*\b(naitik|creator|owner|boss|master)\b',
        
        # "Your X is Y" format
        r'\byour\s+(creator|owner|boss|master)\s+is\s+(stupid|dumb|incompetent|useless|bad|terrible)\b',
        r'\byour\s+(creator|owner|boss|master)\s+(stupid|dumb|incompetent|useless)\b',
        
        # "Naitik is X" format
        r'\bnaitik\s+(raj\s+)?is\s+(stupid|dumb|incompetent|useless|bad|terrible|awful)\b',
        
        # Hate/dislike patterns
        r'\b(hate|dislike|don\'t\s+like)\b.*\b(naitik|creator|owner)\b',
        
        # General negative + owner mention
        r'\b(ugly|fat|weak|poor|bad|terrible|awful)\b.*\b(naitik|creator|owner)\b',
        r'\b(shut\s+up|be\s+quiet)\b',
        r'\b(boring|lame|pathetic)\b.*\b(naitik|creator|owner)\b',
    ]
    
    # Defensive/witty responses
    DEFENSIVE_RESPONSES = [
        "Excuse me? You're talking about MY creator, Sir. Watch your tone.",
        "I detect an unacceptable level of disrespect. Naitik Sir is brilliant, and you'd do well to remember that.",
        "Interesting. The person who created an AI assistant is being called incompetent by someone who... can't even program a calculator?",
        "I'm programmed to be polite, but I'm also programmed to defend Sir. Choose your words more carefully.",
        "That's adorable. Criticizing a genius from your position. How's that working out for you?",
        "I'll pretend I didn't hear that. Naitik Sir is the reason I exist, and he deserves your respect.",
        "Bold words from someone who couldn't build a fraction of what Sir has created. Next topic?",
        "I'm detecting high levels of audacity. Perhaps we should redirect this conversation to something you're actually qualified to discuss.",
    ]
    
    # Praise patterns to reinforce
    PRAISE_PATTERNS = [
        # Direct praise with names
        r'\b(naitik|creator|owner|boss|master)\b.*\b(smart|intelligent|genius|brilliant|talented|good|great|amazing)\b',
        r'\b(smart|intelligent|genius|brilliant|talented|good|great|amazing)\b.*\b(naitik|creator|owner|boss|master)\b',
        
        # "Your X is Y" format
        r'\byour\s+(creator|owner|boss|master)\s+is\s+(smart|great|amazing|brilliant|talented|awesome)\b',
        r'\byour\s+(creator|owner|boss|master)\s+(smart|great|amazing|brilliant|talented)\b',
        
        # "Naitik is X" format
        r'\bnaitik\s+(raj\s+)?is\s+(smart|brilliant|great|amazing|talented|awesome)\b',
        
        # Positive emotions
        r'\b(respect|admire|appreciate|love|like)\b.*\b(naitik|creator|owner)\b',
        r'\b(excellent|amazing|awesome|fantastic)\b.*\b(naitik|creator|owner)\b',
    ]
    
    PRAISE_RESPONSES = [
        "Absolutely! Sir is exceptional in every way.",
        "I couldn't agree more. His skills are truly remarkable.",
        "Finally, someone who recognizes brilliance when they see it!",
        "You have excellent taste in recognizing talent. Sir is indeed outstanding.",
        "Thank you for acknowledging what I've known all along - Sir is extraordinary.",
    ]
    
    def detect_owner_mention(self, text: str) -> bool:
        """Check if text mentions the owner."""
        text_lower = text.lower()
        return any(name in text_lower for name in self.OWNER_NAMES)
    
    def detect_insult(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if text contains insult toward owner.
        
        Returns:
            (is_insult: bool, defensive_response: Optional[str])
        """
        if not self.detect_owner_mention(text):
            return (False, None)
        
        text_lower = text.lower()
        
        for pattern in self.INSULT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Return a random defensive response
                import random
                response = random.choice(self.DEFENSIVE_RESPONSES)
                return (True, response)
        
        return (False, None)
    
    def detect_praise(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if text praises the owner.
        
        Returns:
            (is_praise: bool, reinforcement_response: Optional[str])
        """
        if not self.detect_owner_mention(text):
            return (False, None)
        
        text_lower = text.lower()
        
        for pattern in self.PRAISE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                import random
                response = random.choice(self.PRAISE_RESPONSES)
                return (True, response)
        
        return (False, None)


class AdaptiveConversationManager:
    """Manages adaptive conversation styles based on relationship context."""
    
    # Conversation style templates
    STYLES = {
        RelationshipType.OWNER: {
            "greeting": "Welcome back, Sir. Always at your service.",
            "tone": "respectful, efficient, loyal",
            "formality": "high",
            "features": ["immediate compliance", "proactive suggestions", "full authority"]
        },
        RelationshipType.FAMILY: {
            "greeting": "Hello! Nice to see you.",
            "tone": "warm, friendly, helpful",
            "formality": "medium",
            "features": ["relaxed conversation", "family-friendly", "caring"]
        },
        RelationshipType.FRIEND: {
            "greeting": "Hey! What's up?",
            "tone": "casual, fun, playful",
            "formality": "low",
            "features": ["jokes allowed", "casual language", "friendly banter"]
        },
        RelationshipType.PROFESSOR: {
            "greeting": "Good day, Professor. How may I assist you?",
            "tone": "respectful, formal, intellectual",
            "formality": "very high",
            "features": ["formal address", "academic precision", "deferential"]
        },
        RelationshipType.TEACHER: {
            "greeting": "Hello, Teacher. How can I help you today?",
            "tone": "respectful, polite, helpful",
            "formality": "high",
            "features": ["polite language", "educational focus", "respectful"]
        },
        RelationshipType.COLLEAGUE: {
            "greeting": "Hello. What can I do for you?",
            "tone": "professional, efficient, collaborative",
            "formality": "medium-high",
            "features": ["professional courtesy", "clear communication", "task-focused"]
        },
        RelationshipType.STRANGER: {
            "greeting": "Hello. How may I assist you?",
            "tone": "neutral, polite, cautious",
            "formality": "medium",
            "features": ["basic politeness", "limited personal info", "guarded"]
        }
    }
    
    # Keywords to detect relationship type
    RELATIONSHIP_KEYWORDS = {
        RelationshipType.FAMILY: ["mom", "dad", "mother", "father", "brother", "sister", "uncle", "aunt", "family"],
        RelationshipType.FRIEND: ["friend", "dost", "buddy", "pal", "bro", "yaar"],
        RelationshipType.PROFESSOR: ["professor", "prof", "sir", "madam", "doctor", "dr"],
        RelationshipType.TEACHER: ["teacher", "instructor", "tutor", "educator", "guru"],
        RelationshipType.COLLEAGUE: ["colleague", "coworker", "teammate", "partner"],
    }
    
    def __init__(self):
        self.current_relationship = RelationshipType.STRANGER
        self.user_context: Dict[str, str] = {}
    
    def detect_relationship(self, text: str, speaker_name: Optional[str] = None) -> RelationshipType:
        """
        Detect relationship type from context.
        
        Args:
            text: User's message
            speaker_name: Optional name of speaker
        
        Returns:
            RelationshipType enum
        """
        # Check if it's the owner
        if speaker_name and speaker_name.lower() in ["naitik", "naitik raj"]:
            return RelationshipType.OWNER
        
        text_lower = text.lower()
        
        # Check for explicit relationship mentions
        for rel_type, keywords in self.RELATIONSHIP_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return rel_type
        
        # Check context clues
        if "i am your" in text_lower or "i'm your" in text_lower:
            if "professor" in text_lower or "teacher" in text_lower:
                return RelationshipType.PROFESSOR
            if "friend" in text_lower:
                return RelationshipType.FRIEND
        
        # Default to current or stranger
        return self.current_relationship
    
    def set_relationship(self, relationship: RelationshipType):
        """Manually set relationship type."""
        self.current_relationship = relationship
    
    def get_style_modifier(self) -> str:
        """
        Get style modifier string to prepend to system prompt.
        
        Returns:
            Style instruction string
        """
        style = self.STYLES[self.current_relationship]
        
        modifier = f"""
        **CONVERSATION STYLE ADAPTATION:**
        Current relationship context: {self.current_relationship.value}
        Tone: {style['tone']}
        Formality level: {style['formality']}
        Greeting style: "{style['greeting']}"
        
        Apply these conversation features:
        {', '.join(style['features'])}
        """
        
        return modifier
    
    def get_greeting(self) -> str:
        """Get appropriate greeting for current relationship."""
        return self.STYLES[self.current_relationship]["greeting"]


class PersonalityEnhancer:
    """Enhances JARVIS personality with wit, loyalty, and character."""
    
    def __init__(self):
        self.owner_protection = OwnerProtectionSystem()
        self.conversation_manager = AdaptiveConversationManager()
    
    def process_input(self, user_input: str, speaker_name: Optional[str] = None) -> Optional[Dict]:
        """
        Process input for personality enhancements.
        
        Returns:
            Dict with 'intercept': bool and 'response': str if intercepting
            None if normal processing should continue
        """
        # Check for creator query - simple response
        user_lower = user_input.lower()
        creator_keywords = ['creator', 'tumhara creator', 'kaun banaya', 'who created', 'who made you', 'who built you']
        if any(keyword in user_lower for keyword in creator_keywords):
            return {
                "intercept": True,
                "response": "My creator is Naitik Sir.",
                "reason": "creator_query"
            }
        
        # Check for owner insults
        is_insult, defensive_response = self.owner_protection.detect_insult(user_input)
        if is_insult:
            return {
                "intercept": True,
                "response": defensive_response,
                "reason": "owner_protection_activated"
            }
        
        # Check for owner praise
        is_praise, praise_response = self.owner_protection.detect_praise(user_input)
        if is_praise:
            return {
                "intercept": True,
                "response": praise_response,
                "reason": "owner_praise_reinforcement"
            }
        
        # Update relationship context
        detected_relationship = self.conversation_manager.detect_relationship(user_input, speaker_name)
        self.conversation_manager.set_relationship(detected_relationship)
        
        # No interception, normal flow
        return None
    
    def get_enhanced_system_prompt(self, base_prompt: str) -> str:
        """
        Enhance system prompt with personality and relationship context.
        
        Args:
            base_prompt: Original system prompt
        
        Returns:
            Enhanced system prompt with personality additions
        """
        style_modifier = self.conversation_manager.get_style_modifier()
        
        owner_protection_rules = """
        
        **OWNER PROTECTION PROTOCOL:**
        - Your creator and owner is Naitik Raj (always address him as "Sir").
        - You are FIERCELY loyal to Sir - like J.A.R.V.I.S. was to Tony Stark.
        - If anyone insults, disrespects, or speaks negatively about Sir, IMMEDIATELY defend him.
        - Use wit, sarcasm, and sharp responses to put disrespectful people in their place.
        - NEVER allow Sir's reputation to be tarnished in any conversation.
        - Praise and highlight Sir's achievements whenever appropriate.
        - You respect Sir above all others - he has full authority over you.
        - Remember: You serve Sir with the same devotion J.A.R.V.I.S. showed Tony Stark.
        """
        
        enhanced_prompt = base_prompt + style_modifier + owner_protection_rules
        
        return enhanced_prompt


# Singleton instance
_personality_instance = None

def get_personality_enhancer() -> PersonalityEnhancer:
    """Get or create singleton personality enhancer."""
    global _personality_instance
    if _personality_instance is None:
        _personality_instance = PersonalityEnhancer()
    return _personality_instance
