import requests
import re
import json
import yaml
import os

from enum import Enum

class SerperClient:
    class DateRanges(Enum):
        ANY_TIME = ""
        PAST_HOUR = "qdr:h"
        PAST_24_HOURS = "qdr:d"
        PAST_WEEK = "qdr:w"
        PAST_MONTH = "qdr:m"
        PAST_YEAR = "qdr:y"

    def __init__(self):
        # Load configuration from config.yaml file
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Set up the URL and headers for the Serper API
        self.url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": config["serper_api_key"],  # API key from config file
            "Content-Type": "application/json"
        }

    def serper(self, query: str, country: str ="us", location: str ="us", language: str ="en", date_range: DateRanges | str = DateRanges.ANY_TIME, num_results=10, page=1):
        # Configure the query parameters for Serper API
        serper_settings = {"q": query, "gl": country, "location": location, "hl": language, "num": num_results, "page": page}

        if date_range and isinstance(date_range, SerperClient.DateRanges) and date_range.value:
            serper_settings["tbs"] = date_range.value

        elif date_range and isinstance(date_range, str):
            serper_settings["tbs"] = date_range

        # Check if the query contains Chinese characters and adjust settings accordingly
        if self._contains_chinese(query):
            serper_settings.update({"gl": "cn", "hl": "zh-cn",})

        payload = json.dumps(serper_settings)

        # Perform the POST request to the Serper API and return the JSON response
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        return response.json()

    def _contains_chinese(self, query: str):
        # Check if a string contains Chinese characters using a regular expression
        pattern = re.compile(r'[\u4e00-\u9fff]+')
        return bool(pattern.search(query))

    def extract_components(self, serper_response: dict):
        # Initialize lists to store the extracted components
        titles, links, snippets = [], [], []

        # Iterate through the 'organic' section of the response and extract information
        for item in serper_response.get("organic", []):
            titles.append(item.get("title", ""))
            links.append(item.get("link", ""))
            snippets.append(item.get("snippet", ""))

        # Retrieve additional information from the response
        query = serper_response.get("searchParameters", {}).get("q", "")
        count = len(links)
        language = "zh-cn" if self._contains_chinese(query) else "en-us"

        # Organize the extracted data into a dictionary and return
        output_dict = {
            'query': query, 
            'language': language, 
            'count': count, 
            'titles': titles, 
            'links': links, 
            'snippets': snippets
        }

        return output_dict

# Usage example
if __name__ == "__main__":    
    client = SerperClient()
    query = "What happened to Silicon Valley Bank"
    response = client.serper(query)
    components = client.extract_components(response)
    print(components)
