import json
import os
import re
from enum import Enum

import requests
import yaml


class SearchClientInterface:
    def __init__(self):
        """Initialize the Search Client"""
        pass

    def service(self, query: str) -> dict:
        """Create and perform a request to the service and return the JSON response."""
        pass

    def _contains_chinese(self, query: str) -> bool:
        """Check if a string contains Chinese characters using a regular expression."""
        pass

    def extract_components(self, service_response: dict) -> dict:
        """Extract and return organic search results from the service"""
        pass


class SerperPlacesClient(SearchClientInterface):
    def __init__(self, config_path=None):
        # Load configuration from config.yaml file
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "config", "config.yaml"
            )
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Set up the URL and headers for the Serper API
        self.url = "https://google.serper.dev/places"
        self.headers = {
            "X-API-KEY": config["serper_api_key"],  # API key from config file
            "Content-Type": "application/json",
        }

    def serper_places_search(
        self,
        query: str,
        country: str = "us",
        location: str = "us",
        language: str = "en",
        autocorrect: bool = True,
        page=1,
    ):
        # Configure the query parameters for Serper API
        serper_settings = {
            "q": query,
            "gl": country,
            "location": location,
            "hl": language,
            "autocorrect": autocorrect,
            "page": page,
        }

        # Check if the query contains Chinese characters and adjust settings accordingly
        if self._contains_chinese(query):
            serper_settings.update(
                {
                    "gl": "cn",
                    "hl": "zh-cn",
                }
            )

        payload = json.dumps(serper_settings)

        # Perform the POST request to the Serper API and return the JSON response
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )
        return response.json()

    def _contains_chinese(self, query: str):
        # Check if a string contains Chinese characters using a regular expression
        pattern = re.compile(r"[\u4e00-\u9fff]+")
        return bool(pattern.search(query))

    def extract_components(self, service_response: dict) -> dict:

        # Initialize lists to store the extracted components
        titles = []
        addresses = []
        latitudes = []
        longitudes = []
        ratings = []
        rating_counts = []
        categories = []
        phone_numbers = []
        websites = []
        cids = []

        # Iterate through the 'places' section of the response and extract information
        for item in service_response.get("places", []):
            titles.append(item.get("title", ""))
            addresses.append(item.get("address", ""))
            latitudes.append(item.get("latitude", ""))
            longitudes.append(item.get("longitude", ""))
            ratings.append(item.get("rating", ""))
            rating_counts.append(item.get("ratingCount", ""))
            categories.append(item.get("category", ""))
            phone_numbers.append(item.get("phoneNumber", ""))
            websites.append(item.get("website", ""))
            cids.append(item.get("cid", ""))

        # Retrieve additional information from the response
        query = service_response.get("searchParameters", {}).get("q", "")
        search_parameters = service_response.get("searchParameters", {})
        count = len(titles)
        language = "zh-cn" if self._contains_chinese(query) else "en-us"

        # Organize the extracted data into a dictionary and return
        output_dict = {
            "query": query,
            "search_parameters": search_parameters,
            "language": language,
            "count": count,
            "titles": titles,
            "addresses": addresses,
            "latitudes": latitudes,
            "longitudes": longitudes,
            "ratings": ratings,
            "rating_counts": rating_counts,
            "categories": categories,
            "phone_numbers": phone_numbers,
            "websites": websites,
            "cids": cids,
        }

        return output_dict


class SerperClient(SearchClientInterface):
    class DateRanges(Enum):
        ANY_TIME = ""
        PAST_HOUR = "qdr:h"
        PAST_24_HOURS = "qdr:d"
        PAST_WEEK = "qdr:w"
        PAST_MONTH = "qdr:m"
        PAST_YEAR = "qdr:y"

    def __init__(self, config_path=None):
        # Load configuration from config.yaml file
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "config", "config.yaml"
            )
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Set up the URL and headers for the Serper API
        self.url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": config["serper_api_key"],  # API key from config file
            "Content-Type": "application/json",
        }

    def serper(
        self,
        query: str,
        country: str = "us",
        location: str = "us",
        language: str = "en",
        date_range: DateRanges | str = DateRanges.ANY_TIME,
        num_results=10,
        page=1,
    ):
        # Configure the query parameters for Serper API
        serper_settings = {
            "q": query,
            "gl": country,
            "location": location,
            "hl": language,
            "num": num_results,
            "page": page,
        }

        if (
            date_range
            and isinstance(date_range, SerperClient.DateRanges)
            and date_range.value
        ):
            serper_settings["tbs"] = date_range.value

        elif date_range and isinstance(date_range, str):
            serper_settings["tbs"] = date_range

        # Check if the query contains Chinese characters and adjust settings accordingly
        if self._contains_chinese(query):
            serper_settings.update(
                {
                    "gl": "cn",
                    "hl": "zh-cn",
                }
            )

        payload = json.dumps(serper_settings)

        # Perform the POST request to the Serper API and return the JSON response
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )
        return response.json()

    def _contains_chinese(self, query: str):
        # Check if a string contains Chinese characters using a regular expression
        pattern = re.compile(r"[\u4e00-\u9fff]+")
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
            "query": query,
            "language": language,
            "count": count,
            "titles": titles,
            "links": links,
            "snippets": snippets,
        }

        return output_dict


class BingWebSearchClient(SearchClientInterface):
    class Freshness(Enum):
        ANY_TIME = ""
        DAY = "Day"
        WEEK = "Week"
        MONTH = "Month"

    class ResponseFilter(Enum):
        COMPUTATION = "Computation"
        ENTITIES = "Entities"
        IMAGES = "Images"
        NEWS = "News"
        PLACES = "Places"
        RELATEDSEARCHES = "RelatedSearches"
        SPELLSUGGESTIONS = "SpellSuggestions"
        TIMEZONE = "TimeZone"
        TRANSLATIONS = "Translations"
        VIDEOS = "Videos"
        WEBPAGES = "Webpages"

    def __init__(self, config_path=None):
        # Load configuration from config.yaml file
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "config", "config.yaml"
            )
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Set up the URL and headers for the Bing Web Search API
        self.url = config["azure_bing_search_endpoint"] + "/v7.0/search"
        self.headers = {
            "Ocp-Apim-Subscription-Key": config["azure_bing_search_api_key"]
        }

    def bing_web_search(
        self,
        query: str,
        country_code: str = "us",
        count: int = 10,
        freshness: Freshness | str = Freshness.ANY_TIME,
        market: str = "en-us",
        responseFilter: ResponseFilter | str = ResponseFilter.WEBPAGES,
    ):
        # Configure the query parameters for Bing Web Search API
        params = {"q": query, "cc": country_code, "count": count, "mkt": market}

        if (
            freshness
            and isinstance(freshness, BingWebSearchClient.Freshness)
            and freshness.value
        ):
            params["freshness"] = freshness.value

        elif freshness and isinstance(freshness, str):
            params["freshness"] = freshness

        if (
            responseFilter
            and isinstance(responseFilter, BingWebSearchClient.ResponseFilter)
            and responseFilter.value
        ):
            params["responseFilter"] = responseFilter.value

        elif responseFilter and isinstance(responseFilter, str):
            params["responseFilter"] = responseFilter

        # Perform the GET request to the Bing Search API and return the JSON response
        response = requests.get(self.url, headers=self.headers, params=params)
        return response.json()

    def _contains_chinese(self, query: str):
        # Check if a string contains Chinese characters using a regular expression
        pattern = re.compile(r"[\u4e00-\u9fff]+")
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
            "query": query,
            "language": language,
            "count": count,
            "titles": titles,
            "links": links,
            "snippets": snippets,
        }

        return output_dict


class BingNewsSearchClient(SearchClientInterface):
    class Freshness(Enum):
        ANY_TIME = ""
        DAY = "Day"
        WEEK = "Week"
        MONTH = "Month"

    class SortBy(Enum):
        DATE = "Date"
        RELEVANCE = "Relevance"

    def __init__(self, config_path=None):
        # Load configuration from config.yaml file
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "config", "config.yaml"
            )
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Set up the URL and headers for the Bing Web Search API
        self.url = config["azure_bing_search_endpoint"] + "/v7.0/news/search"
        self.headers = {
            "Ocp-Apim-Subscription-Key": config["azure_bing_search_api_key"]
        }

    def bing_news_search(
        self,
        query: str,
        country_code: str = "us",
        count: int = 10,
        freshness: Freshness | str = Freshness.ANY_TIME,
        market="en-us",
        sort_by: str = "",
    ):
        # Configure the query parameters for Bing Web Search API
        params = {
            "q": query,
            "cc": country_code,
            "count": count,
            "mkt": market,
            "textDecorations": False,
        }

        if (
            freshness
            and isinstance(freshness, BingNewsSearchClient.Freshness)
            and freshness.value
        ):
            params["freshness"] = freshness.value

        elif freshness and isinstance(freshness, str):
            params["freshness"] = freshness

        if (
            sort_by
            and isinstance(sort_by, BingNewsSearchClient.SortBy)
            and sort_by.value
        ):
            params["sort_by"] = sort_by.value

        elif sort_by and isinstance(sort_by, str):
            params["sort_by"] = sort_by

        # Perform the GET request to the Bing Search API and return the JSON response
        response = requests.get(self.url, headers=self.headers, params=params)
        return response.json()

    def _contains_chinese(self, query: str):
        # Check if a string contains Chinese characters using a regular expression
        pattern = re.compile(r"[\u4e00-\u9fff]+")
        return bool(pattern.search(query))

    def extract_components(self, bing_response):
        # Initialize lists to store the extracted components
        titles, links, snippets = [], [], []

        # Iterate through all the web pages in the response and extract information
        for item in bing_response.get("value", []):
            titles.append(item.get("name", ""))
            links.append(item.get("url", ""))
            snippets.append(item.get("description", ""))

        # Retrieve additional information from the response
        query = bing_response.get("queryContext", {}).get("originalQuery", "")
        count = len(links)
        language = "zh-cn" if self._contains_chinese(query) else "en-us"

        # Organize the extracted data into a dictionary and return
        output_dict = {
            "query": query,
            "language": language,
            "count": count,
            "titles": titles,
            "links": links,
            "snippets": snippets,
        }

        return output_dict
