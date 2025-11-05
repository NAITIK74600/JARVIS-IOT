# In tools/utility_tools.py

from langchain.tools import Tool
import json
import os

def write_code_to_file(data: str) -> str:
    """
    Writes or creates a file with specific code or text content.
    The input must be a JSON string with two keys: 'filename' and 'content'.
    Example: '{"filename": "app.py", "content": "print(\'Hello, World!\')"}'
    This tool is perfect for writing code, notes, or any text file.
    """
    try:
        params = json.loads(data)
        filename = params['filename']
        content = params['content']
        
        # Ensure directory exists
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Successfully wrote content to {filename}"
    except Exception as e:
        return f"Error writing to file: {e}"

def get_utility_tools():
    # Add this to any existing utility tools you have
    return [
        Tool(
            name="write_code_to_file",
            func=write_code_to_file,
            description="Useful for writing code or text to a file. The input must be a JSON string with 'filename' and 'content' keys.",
        )
    ]