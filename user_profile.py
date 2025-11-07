# -- User Profile Configuration for JARVIS --
# This file contains detailed information about the user, which JARVIS
# will use to provide personalized and context-aware assistance.

PROFILE_DATA = {
    "name": "Naitik Raj",
    "preferred_name": "Sir",  # How Jarvis should address you (Tony Stark style)
    "dob": "2002-09-09",
    "birth_place": "Patna, Bihar, India",
    "birth_time": "Between 11 PM - 12 AM",
    "languages": ["Hindi", "English"],
    "education": {
        "bca": {
            "college": "Arcade Business College",
            "percentage": "65%"
        },
        "mca": {
            "college": "Chandigarh University",
            "specialization": "AI & ML",
            "current_semester": "3rd"
        }
    },
    "technical_skills": {
        "programming_languages": ["Python", "Java", "C++", "JavaScript"],
        "ai_tools": ["LangChain", "VOSK", "Whisper", "Pyttsx3", "Ollama", "OpenChat 3.5"],
        "databases": ["Oracle 10g/11g", "SQLite", "JSON-based memory"],
        "ui_frameworks": ["Tkinter", "Java Swing", "Three.js"],
        "others": ["OpenCV", "gTTS", "LM Studio", "NetBeans", "VS Code"]
    },
    "jarvis_project": {
        "name": "JARVIS (Just A Rather Very Intelligent System)",
        "language": "Hindi + English",
        "features": [
            "Natural Voice Interaction",
            "Voice-Controlled Task Automation",
            "Code Writing & Execution",
            "Memory of User Preferences",
            "System Control (Windows/Linux)",
            "Emotionally Intelligent Replies",
            "AI via LangChain + Local LLMs",
            "Custom Tkinter GUI with Animations"
        ],
        "models": {
            "llm": "openchat-3.5-0106.Q4_K_M.gguf",
            "runtime": "LM Studio + Ollama",
            "context_limit_tokens": 8192,
            "preferred_response_speed": "Balanced (Fast + Accurate)"
        }
    },
    "system_specs": {
        "cpu": "Ryzen 5",
        "ram": "8GB",
        "gpu": "NVIDIA GTX",
        "os": "Windows 11"
    },
    "bgmi_profile": {
        "setup": "5-finger claw",
        "fps": "120 FPS",
        "gyroscope": True,
        "preferred_sensitivity": "Custom per gun"
    },
    "personality": {
        "traits": ["Curious", "Hardworking", "Tech Enthusiast", "Problem Solver"],
        "goals": [
            "Master AI development",
            "Build smart desktop assistant",
            "Crack job in AI domain"
        ]
    },
    "preferences": {
        "voice_response": "Human-like with emotional tone",
        "interaction_style": "Respectful, friendly, helpful",
        "languages_used": ["Hindi", "English"],
        "project_focus": ["Voice AI", "Frontend 3D Portfolio", "AI Pathfinding Visualizer"]
    }
}

# --- Maintain compatibility with existing code by setting legacy variables ---
FULL_NAME = PROFILE_DATA.get("name", "Naitik Kumar")
PREFERRED_NAME = PROFILE_DATA.get("name", "Naitik").split(" ")[0] # Use first name
COLLEGE_NAME = PROFILE_DATA.get("education", {}).get("mca", {}).get("college", "[Your College Name]")
PROGRAM_DEPARTMENT = PROFILE_DATA.get("education", {}).get("mca", {}).get("specialization", "[Your Program or Department]")
STUDENT_ID = "[24mci10184]" # This was not in the new data, so it remains a placeholder
EMAIL_ADDRESS = "[igxnaitik@gmail.com]" # Placeholder
PHONE_NUMBER = "[7488842132]" # Placeholder

# Export user_profile dictionary for compatibility with main.py
user_profile = PROFILE_DATA
