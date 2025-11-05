# H:/jarvis/tools/api_tools.py (NEW FILE)

import os
import requests
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """
    Fetches the current weather for a specified city using the OpenWeatherMap API.
    Args:
        city (str): The name of the city for which to get the weather forecast.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key is not set in the .env file."
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric" # Request temperature in Celsius
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raises an error for bad responses (4xx or 5xx)
        data = response.json()
        
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        return (f"The current weather in {city.title()} is {weather_desc}. "
                f"The temperature is {temp}°C, with {humidity}% humidity "
                f"and a wind speed of {wind_speed} m/s.")

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return f"Sorry, I could not find the city '{city}'. Please check the spelling."
        else:
            return f"An HTTP error occurred: {http_err}"
    except Exception as e:
        return f"An error occurred while fetching the weather: {e}"

@tool
def get_news(query: str) -> str:
    """
    Fetches the latest news headlines for a given query using the NewsAPI.
    Args:
        query (str): The topic to search for in the news.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Error: NewsAPI key is not set in the .env file."
    
    base_url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": api_key,
        "sortBy": "publishedAt",
        "pageSize": 5
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        if not articles:
            return f"No news articles found for '{query}'."
            
        headlines = []
        for article in articles:
            headlines.append(f"- {article['title']} ({article['source']['name']})")
        
        return f"Here are the latest headlines for '{query}':\n" + "\n".join(headlines)

    except requests.exceptions.HTTPError as http_err:
        return f"An HTTP error occurred: {http_err}"
    except Exception as e:
        return f"An error occurred while fetching the news: {e}"

def get_api_tools():
    """Returns a list of all API tools."""
    return [get_weather, get_news]