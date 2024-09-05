import os
import yaml
import requests
import re

import search_service

class BingWebSearchClient(search_service.SearchClientInterface):
    def __init__(self):
        # Load configuration from config.yaml file
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Set up the URL and headers for the Bing Web Search API
        self.url = config["azure_bing_search_endpoint"] + "/v7.0/search"
        self.headers = {
            "Ocp-Apim-Subscription-Key": config["azure_bing_search_api_key"]
        }

    def bing_web_search(self, query: str):
        # Configure the query parameters for Bing Web Search API
        params = {"q": query, "mkt": "en-US"}

        # Perform the GET request to the Bing Search API and return the JSON response
        response = requests.get(self.url, headers=self.headers, params=params)
        return response.json()
    
    def _contains_chinese(self, query: str):
        # Check if a string contains Chinese characters using a regular expression
        pattern = re.compile(r'[\u4e00-\u9fff]+')
        return bool(pattern.search(query))
   
    def extract_components(self, bing_response):
        # Initialize lists to store the extracted components
        titles, links, snippets = [], [], []

        # Iterate through all the web pages in the response and extract information
        for item in bing_response.get("webPages", {}).get("value", []):
            titles.append(item.get("name", ""))
            links.append(item.get("url", ""))
            snippets.append(item.get("snippet", ""))

        # Retrieve additional information from the response
        query = bing_response.get("queryContext", {}).get("originalQuery", "")
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
    client = BingWebSearchClient()
    query = "What happened to Silicon Valley Bank"
    response = client.bing_web_search(query)
    components = client.extract_components(response)
    print(components)
