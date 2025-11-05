# H:/jarvis/tools/file_system_tools.py (UPGRADED)
import os
import shutil

from langchain_core.tools import tool

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _get_safe_path(path: str) -> str:
    abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
    if not abs_path.startswith(BASE_DIR):
        raise PermissionError("Access outside of project directory is denied.")
    return abs_path


def _write_file_impl(filename: str, content: str) -> str:
    try:
        safe_path = _get_safe_path(filename)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to '{filename}'."
    except Exception as e:
        return f"Error writing to file: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """List files and folders within a directory relative to the project root."""
    try:
        safe_dir = _get_safe_path(directory)
        if not os.path.isdir(safe_dir):
            return f"'{directory}' is not a directory."
        entries = sorted(os.listdir(safe_dir))
        if not entries:
            return "Directory is empty."
        return "\n".join(entries)
    except Exception as e:
        return f"Error listing files: {e}"


@tool
def read_file(filename: str) -> str:
    """Read the content of a file relative to the project root."""
    try:
        with open(_get_safe_path(filename), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(filename: str, content: str) -> str:
    """Write (overwrite) the content of a file relative to the project root."""
    return _write_file_impl(filename, content)


@tool
def write_to_file(filename: str, content: str) -> str:
    """Alias for write_file for backwards compatibility."""
    return _write_file_impl(filename, content)


@tool
def delete_file(filename: str) -> str:
    """Delete a file within the project directory."""
    try:
        safe_path = _get_safe_path(filename)
        os.remove(safe_path)
        return f"Deleted '{filename}'."
    except FileNotFoundError:
        return f"File '{filename}' not found."
    except Exception as e:
        return f"Error deleting file: {e}"


@tool
def move_file(source_path: str, destination_path: str) -> str:
    """Move a file to a new location within the project directory."""
    try:
        shutil.move(_get_safe_path(source_path), _get_safe_path(destination_path))
        return f"Successfully moved '{source_path}' to '{destination_path}'."
    except Exception as e:
        return f"Error moving file: {e}"


@tool
def search_files(search_query: str) -> str:
    """Search recursively for files whose names contain the given query."""
    results = []
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if search_query.lower() in file.lower():
                results.append(os.path.join(root, file))
    return f"Found files: {results}" if results else "No files found matching the query."


def get_file_system_tools():
    return [
        list_files,
        read_file,
        write_file,
        delete_file,
        move_file,
        search_files,
    ]