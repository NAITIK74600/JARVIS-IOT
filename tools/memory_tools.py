# H:/jarvis/tools/memory_tools.py (FINAL VERSION with DUAL MEMORY)

import json
from langchain_core.tools import tool
from typing import Optional
import chromadb
from datetime import datetime

# === System 1: Structured Key-Value Memory (Your Filing Cabinet) ===
MEMORY_FILE = "jarvis_memory.json"

def _load_memory():
    """Helper function to load the structured memory JSON file."""
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_memory(data):
    """Helper function to save data to the structured memory JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def _remember_impl(key: str, value: str, person: str = "user") -> str:
    """Internal implementation for remembering information."""
    person_key = person.lower().strip()
    memory = _load_memory()
    
    if person_key not in memory:
        memory[person_key] = {}
        
    memory[person_key][key.lower().strip()] = value.strip()
    _save_memory(memory)
    
    return f"Understood. I've remembered that for {person.title()}, '{key}' is '{value}'."

def _recall_impl(key: str, person: str = "user") -> str:
    """Internal implementation for recalling information."""
    person_key = person.lower().strip()
    memory = _load_memory()
    
    person_data = memory.get(person_key, {})
    value = person_data.get(key.lower().strip())
    
    if value:
        return f"For {person.title()}, I recall that '{key}' is '{value}'."
    else:
        return f"I'm sorry, I don't have information stored for the key '{key}' about {person.title()}."

def _delete_impl(key: str, person: str = "user") -> str:
    """Internal implementation for deleting from memory."""
    person_key = person.lower().strip()
    memory = _load_memory()
    
    if person_key in memory and key.lower().strip() in memory[person_key]:
        del memory[person_key][key.lower().strip()]
        _save_memory(memory)
        return f"Successfully deleted '{key}' from memory."
    else:
        return f"Key '{key}' not found in memory."

@tool
def remember_information(key: str, value: str, person: Optional[str] = "user") -> str:
    """
    Saves a specific, labeled piece of information (key-value pair) about a person.
    Use this for structured data like preferences, names, or passwords.
    Args:
        key (str): The label for the information (e.g., 'favorite_color', 'birthday').
        value (str): The information to save.
        person (str, optional): The name of the person this information is about.
    """
    return _remember_impl(key, value, person)

@tool
def recall_information(key: str, person: Optional[str] = "user") -> str:
    """
    Retrieves a specific, labeled piece of information (a value) using its exact key.
    Args:
        key (str): The exact label of the information to recall.
        person (str, optional): The name of the person to recall information about.
    """
    return _recall_impl(key, person)

@tool
def read_from_memory(key: str) -> str:
    """Alias for recall_information for backward compatibility. Reads a value from memory by key."""
    return _recall_impl(key, "user")

@tool
def write_to_memory(key: str, value: str) -> str:
    """Alias for remember_information for backward compatibility. Writes a key-value pair to memory."""
    return _remember_impl(key, value, "user")

@tool
def delete_from_memory(key: str) -> str:
    """Deletes a specific key from memory."""
    return _delete_impl(key, "user")

# === System 2: Semantic Vector Memory (Your Search Engine) ===
client = chromadb.Client()
semantic_collection = client.get_or_create_collection(name="semantic_memory")

@tool
def remember_semantic_fact(fact: str) -> str:
    """
    Stores an unstructured piece of information, a sentence, or a fact in the long-term semantic memory.
    Use this for remembering ideas, conversation points, or general knowledge.
    Args:
        fact (str): The unstructured fact or sentence to remember.
    """
    doc_id = datetime.now().isoformat()
    semantic_collection.add(documents=[fact], ids=[doc_id])
    return "Fact stored successfully in my semantic memory."

@tool
def recall_semantic_facts(query: str) -> str:
    """
    Searches semantic memory for facts related to a conceptual query.
    Use this when asking general questions about things you've discussed before.
    Args:
        query (str): The topic or question to search for in memory.
    """
    results = semantic_collection.query(query_texts=[query], n_results=3)
    if not results['documents'][0]:
        return "No relevant facts found in my semantic memory."
    return "Found these relevant facts in my semantic memory: \n" + "\n".join(results['documents'][0])


# === Final Tool Export ===
def get_memory_tools():
    """Returns a list of all memory-related tools."""
    # Note: We are not including get_user_details here as it's a separate concept
    # but you can add it back if you have a user_profile.json
    return [
        remember_information,
        recall_information,
        read_from_memory,
        write_to_memory,
        delete_from_memory,
        remember_semantic_fact,
        recall_semantic_facts,
    ]