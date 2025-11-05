# H:/jarvis/tools/security_tools.py (NEW FILE)

import hashlib
from langchain_core.tools import tool

@tool
def check_password_strength(password: str) -> str:
    """Analyzes a password and provides a strength assessment."""
    score = 0
    feedback = []
    if len(password) >= 8: score += 1
    else: feedback.append("- Too short (should be at least 8 characters)")
    if any(c.isupper() for c in password): score += 1
    else: feedback.append("- Does not contain uppercase letters")
    if any(c.islower() for c in password): score += 1
    else: feedback.append("- Does not contain lowercase letters")
    if any(c.isdigit() for c in password): score += 1
    else: feedback.append("- Does not contain numbers")
    if any(not c.isalnum() for c in password): score += 1
    else: feedback.append("- Does not contain special characters")

    strength = {0: "Very Weak", 1: "Weak", 2: "Moderate", 3: "Strong", 4: "Strong", 5: "Very Strong"}
    return f"Password Strength: {strength[score]}.\nFeedback:\n" + "\n".join(feedback)

@tool
def calculate_file_hash(filepath: str, algorithm: str = "sha256") -> str:
    """
    Calculates the hash of a file using a specified algorithm (e.g., md5, sha256).
    Useful for verifying file integrity.
    """
    hash_func = getattr(hashlib, algorithm, None)
    if not hash_func:
        return "Error: Invalid hash algorithm specified. Use 'md5' or 'sha256'."
    try:
        with open(filepath, 'rb') as f:
            file_hash = hash_func(f.read()).hexdigest()
        return f"{algorithm.upper()} hash of the file is: {file_hash}"
    except FileNotFoundError:
        return f"Error: File not found at '{filepath}'."
    except Exception as e:
        return f"Error calculating hash: {e}"

def get_security_tools():
    return [check_password_strength, calculate_file_hash]