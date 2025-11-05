# H:/jarvis/tools/web_tools.py (Gemini-only version - Tavily removed)

import os
import webbrowser
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

# Simple web search using DuckDuckGo (no external API needed)
@tool
def search_web(query: str) -> str:
    """
    Search the web for information using DuckDuckGo.
    Returns top search results for the given query.
    """
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = soup.find_all('a', class_='result__a', limit=5)
        if results:
            output = f"Search results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                title = result.get_text().strip()
                link = result.get('href', '')
                output += f"{i}. {title}\n   {link}\n\n"
            return output
        return f"No search results found for '{query}'."
    except Exception as e:
        return f"Search failed: {e}. Please check your internet connection."

@tool
def open_website_in_browser(url: str) -> str:
    """
    Opens the given URL in the default web browser.
    Use this when the user asks to see a website.
    Args:
        url (str): The URL to open.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible
        return f"? Successfully opened {url}"
    except Exception as e:
        return f"? Error opening website: {e}"

@tool
def scrape_website_text(url: str) -> str:
    """
    Scrapes the full text content from a given URL.
    Use this when you need to get detailed, real-time information directly from a webpage
    that a search summary might not provide, for analysis or summarization.
    Args:
        url (str): The full URL of the website to scrape.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for bad status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements for cleaner text
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        if len(text) > 8000:
            return f"Successfully scraped the website. Content is too long. Here is the first 8000 characters:\n\n{text[:8000]}"
        
        return f"Successfully scraped the website. Here is the content:\n\n{text}"
    except Exception as e:
        return f"An error occurred while scraping the website: {e}"

def get_web_tools():
    """Returns a list of all web-related tools."""
    return [search_web, open_website_in_browser, scrape_website_text]
